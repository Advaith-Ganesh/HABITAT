"""Regression evidence for issues found during the V2 audit."""

import hashlib
import json
import numpy as np
import pytest
from backend import main as backend
from backend.main import Case
from ml.common import ROOT
from ml.predict import predict
from ml.evaluate import fairness_audit


def new_case(client, historical_case):
    aid = historical_case(Case(conflicting_information=1).model_dump())
    assert client.post(f"/api/applications/{aid}/assess", json={}).status_code == 200
    return aid


def test_review_follow_up_remains_in_queue(client, historical_case):
    aid = new_case(client, historical_case)
    for outcome in ["request_evidence", "escalate", "additional_review"]:
        response = client.post(
            f"/api/reviews/{aid}/resolve",
            json={
                "outcome": outcome,
                "reason": "Fictional evidence requires further caseworker clarification.",
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "pending"
        assert aid in [r["id"] for r in client.get("/api/reviews").json()]
    assert (
        client.post(
            f"/api/reviews/{aid}/resolve",
            json={
                "outcome": "routine",
                "reason": "Caseworker completed fictional evidence checks.",
            },
        ).json()["status"]
        == "resolved"
    )
    history = client.get(f"/api/applications/{aid}").json()["history"]
    assert len(history) == 6
    assert (
        client.post(
            f"/api/reviews/{aid}/resolve",
            json={
                "outcome": "routine",
                "reason": "This duplicate completion must be rejected.",
            },
        ).status_code
        == 409
    )
    assert client.post(f"/api/applications/{aid}/assess", json={}).status_code == 409
    assert len(client.get(f"/api/applications/{aid}").json()["history"]) == 6


@pytest.mark.parametrize("failure", [OSError, EOFError, KeyError])
def test_health_reflects_artifact_failure(client, monkeypatch, failure):
    healthy = client.get("/health").json()
    assert healthy["model"]["ready"] is True and healthy["model"]["trees"] == 180

    def unavailable():
        raise failure("Test-only artifact outage, no file changed")

    monkeypatch.setattr(backend, "artifacts", unavailable)
    assert client.get("/health").status_code == 503
    assert client.get("/health").json()["model"]["ready"] is False


def test_explanation_io_failure_returns_useful_error(client, monkeypatch, historical_case):
    aid = new_case(client, historical_case)

    def unavailable(_record):
        raise OSError("private filesystem diagnostic")

    monkeypatch.setattr(backend, "explain", unavailable)
    result = client.get(f"/api/applications/{aid}/explanation")
    assert result.status_code == 503
    assert "private filesystem" not in result.text
    assert "human review" in result.text


def test_failed_assessment_has_no_misleading_explanation(client, monkeypatch, historical_case):
    monkeypatch.setattr(backend, "predict", lambda _record: predict({}))
    aid = new_case(client, historical_case)
    record = client.get(f"/api/applications/{aid}").json()
    assert record["assessment"]["score"] is None
    assert record["status"] == "pending"
    assert client.get(f"/api/applications/{aid}/explanation").status_code == 409


def test_explanation_cannot_silently_change_recorded_score(client, monkeypatch, historical_case):
    aid = new_case(client, historical_case)
    score = client.get(f"/api/applications/{aid}").json()["assessment"]["score"]
    monkeypatch.setattr(backend, "explain", lambda _: {"score": score + 0.1})
    assert client.get(f"/api/applications/{aid}/explanation").status_code == 409


def test_audit_reruns_preserve_public_artifacts(client):
    paths = [
        ROOT / "data/public/counterfactual_400.csv",
        ROOT / "reports/fairness.json",
        ROOT / "reports/evaluation.json",
        ROOT / "models/habitat_review_model.joblib",
    ]
    before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
    assert client.post("/api/fairness/counterfactual", json={}).status_code == 200
    rerun = client.post("/api/fairness/run", json={})
    assert rerun.status_code == 200
    stored = json.loads((ROOT / "reports/fairness.json").read_text())
    assert rerun.json()["groups"] == stored["groups"]
    assert rerun.json()["counterfactual"] == stored["counterfactual"]
    assert before == [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]


def test_dataset_metadata_comes_from_actual_source(client):
    meta = client.get("/api/dataset/metadata").json()
    assert meta["records"] == 2000 and meta["scenario_families"] == 1000
    assert sum(v["count"] for v in meta["class_balance"]) == 2000
    assert len(meta["dictionary"]) == 22
    assert (
        meta["sha256"]
        == hashlib.sha256(
            (ROOT / "data/public/habitat_synthetic_2000.csv").read_bytes()
        ).hexdigest()
    )
    for endpoint, name in [
        ("card", "DATASET_CARD.md"),
        ("dictionary", "DATA_DICTIONARY.md"),
    ]:
        result = client.get("/api/dataset/" + endpoint)
        assert result.status_code == 200
        assert result.content == (ROOT / "data" / name).read_bytes()


def test_api_security_headers_and_cors(client):
    result = client.get("/api/dashboard")
    assert result.headers["x-content-type-options"] == "nosniff"
    assert result.headers["x-frame-options"] == "DENY"
    assert result.headers["cache-control"] == "no-store"
    allowed = client.options(
        "/api/applications",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
    denied = client.options(
        "/api/applications",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert denied.status_code == 400
    assert "access-control-allow-origin" not in denied.headers


def test_database_failure_does_not_leak_internal_detail(client, monkeypatch):
    from sqlalchemy.exc import SQLAlchemyError

    def unavailable():
        raise SQLAlchemyError("private db path and fake-secret")

    monkeypatch.setattr(backend, "Session", unavailable)
    result = client.get("/api/dashboard")
    assert result.status_code == 503
    assert "fake-secret" not in result.text
    assert result.headers["retry-after"] == "5"


def test_unexpected_counterfactual_attributes_rejected(client):
    assert (
        client.post(
            "/api/fairness/counterfactual", json={"unexpected": "ignored before V2"}
        ).status_code
        == 422
    )


def test_case_identifiers_do_not_become_sql(client):
    count = len(client.get("/api/applications").json())
    assert client.get("/api/applications/'%20OR%201=1--").status_code == 404
    assert len(client.get("/api/applications").json()) == count


def test_shap_legacy_output_has_correct_feature_alignment(monkeypatch):
    import ml.explain as module
    from ml.predict import artifacts

    pipe, _ = artifacts()
    real = module.shap.TreeExplainer(pipe["classifier"])

    class LegacyOutput:
        expected_value = real.expected_value

        def shap_values(self, x):
            values = np.asarray(real.shap_values(x))
            return [values[:, :, 0], values[:, :, 1]]

    monkeypatch.setattr(module.shap, "TreeExplainer", lambda _model: LegacyOutput())
    result = module.explain(Case().model_dump())
    assert result["additivity_error"] < 1e-6


def test_frontend_entrypoint_security_headers(client):
    for path in ["/", "/index.html"]:
        response = client.get(path)
        assert response.status_code == 200
        assert "frame-ancestors 'none'" in response.headers["content-security-policy"]


def test_partial_artifact_failure_escalates_without_file_mutation(monkeypatch):
    import ml.predict as module

    def corrupt():
        raise EOFError("Injected truncated artifact; actual model untouched")

    monkeypatch.setattr(module, "artifacts", corrupt)
    result = module.predict(Case().model_dump())
    assert result["score"] is None and result["requires_review"]
