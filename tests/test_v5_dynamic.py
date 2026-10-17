"""Independent V5 regression checks for live counts, preserved follow-ups and provenance."""

import hashlib
import json
import sqlite3
import numpy as np
import pandas as pd
from backend import main as backend
from backend.main import Case
from ml.common import ROOT, FEATURES
from ml.predict import artifacts, predict


def test_live_counts_follow_real_persisted_mutations(client):
    with sqlite3.connect(backend.engine.url.database) as db:
        expected = dict(
            db.execute(
                "SELECT status, COUNT(*) FROM applications GROUP BY status"
            ).fetchall()
        )
    before = client.get("/api/dashboard").json()
    assert before["applications"] == sum(expected.values())
    for key, status in [
        ("awaiting_assessment", "unassessed"),
        ("pending_reviews", "pending"),
        ("resolved_reviews", "resolved"),
    ]:
        assert before[key] == expected.get(status, 0)
    aid = client.post(
        "/api/applications", json=Case(conflicting_information=1).model_dump()
    ).json()["id"]
    new = client.get("/api/dashboard").json()
    assert new["applications"] == before["applications"] + 1
    assert new["awaiting_assessment"] == before["awaiting_assessment"] + 1
    client.post(f"/api/applications/{aid}/assess", json={})
    assessed = client.get("/api/dashboard").json()
    assert assessed["awaiting_assessment"] == before["awaiting_assessment"]
    assert assessed["pending_reviews"] == before["pending_reviews"] + 1
    client.post(
        f"/api/reviews/{aid}/resolve",
        json={
            "outcome": "request_evidence",
            "reason": "Please clarify the declared housing evidence for this demo.",
        },
    )
    requested = client.get("/api/dashboard").json()
    assert requested["information_requests"] == before["information_requests"] + 1
    for endpoint in ["/api/applications", "/api/reviews"]:
        listed = next(r for r in client.get(endpoint).json() if r["id"] == aid)
        assert listed["latest_review"]["outcome"] == "request_evidence"
    client.post(
        f"/api/reviews/{aid}/resolve",
        json={
            "outcome": "routine",
            "reason": "Administrative intake review is complete in this test.",
        },
    )
    completed = client.get("/api/dashboard").json()
    assert completed["resolved_reviews"] == before["resolved_reviews"] + 1
    assert completed["information_requests"] == before["information_requests"]
    assert completed["pending_reviews"] == before["pending_reviews"]


def test_reassessment_preserves_caseworker_information_request(client):
    aid = client.post("/api/applications", json=Case().model_dump()).json()["id"]
    first = client.post(f"/api/applications/{aid}/assess", json={}).json()
    assert not first["requires_review"]
    client.post(
        f"/api/reviews/{aid}/resolve",
        json={
            "outcome": "request_evidence",
            "reason": "Caseworker requires clarification despite routine model routing.",
        },
    )
    reassessed = client.post(f"/api/applications/{aid}/assess", json={}).json()
    assert reassessed["score"] == first["score"] and not reassessed["requires_review"]
    record = client.get(f"/api/applications/{aid}").json()
    assert record["status"] == "pending"
    assert record["latest_review"]["outcome"] == "request_evidence"
    assert [e["action"] for e in record["history"]] == [
        "submitted",
        "assessed",
        "human_override",
        "assessed",
    ]


def test_metadata_matches_actual_artifacts_and_verification(client):
    metadata = client.get("/api/model/metadata").json()
    assert metadata["model_version"] == "rf-1.0"
    assert [
        metadata[k] for k in ["training_records", "validation_records", "test_records"]
    ] == [1400, 300, 300]
    assert metadata["trees"] == 180
    for path, digest in metadata["artifact_hashes"].items():
        assert digest == hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
    verification = json.loads(
        (ROOT / "reports/evaluation_verification.json").read_text()
    )
    assert metadata["evaluation_verified_at"] == verification["verified_at"]
    assert metadata["verification_status"] == "verified"
    assert verification["original_evaluation_created_at"] is None


def test_changed_verification_is_not_presented_as_current(client, monkeypatch):
    # Swap only the sidecar reader; never change model or reports on disk.
    from pathlib import Path

    original = Path.read_text

    def read(path, *args, **kwargs):
        if path.name == "evaluation_verification.json":
            return json.dumps({"artifact_hashes": {}, "verified_at": "2000-01-01"})
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read)
    metadata = client.get("/api/model/metadata").json()
    assert metadata["verification_status"] == "not_verified_for_current_artifacts"
    assert metadata["evaluation_verified_at"] is None


def test_real_input_mapping_changes_without_forced_difference(client):
    base = Case(conflicting_information=0).model_dump()
    cases = [
        base,
        {**base, "conflicting_information": 1},
        {**base, "monthly_income": 9000},
    ]
    scores = []
    for payload in cases:
        aid = client.post("/api/applications", json=payload).json()["id"]
        result = client.post(f"/api/applications/{aid}/assess", json={}).json()
        assert result["score"] == predict(payload)["score"]
        explanation = client.get(f"/api/applications/{aid}/explanation").json()
        assert (
            explanation["score"] == result["score"]
            and explanation["additivity_error"] < 1e-6
        )
        scores.append(result["score"])
    assert scores[0] != scores[1]
    assert (
        scores[0] == scores[2]
    )  # Income is legitimately excluded; never force a difference.


def test_error_before_any_escalation_is_recomputed(client):
    result = client.get("/api/model/safeguard").json()
    pipe, cfg = artifacts()
    test = pd.read_csv(ROOT / "data/splits/test.csv")
    p = pipe.predict_proba(test[FEATURES])[:, 1] >= cfg["threshold"]
    mistakes = p != test.case_review_required.to_numpy()
    assert result["before_human_escalation"]["routing_errors"] == int(mistakes.sum())
    assert result["before_human_escalation"]["routing_error_rate"] == float(
        np.mean(mistakes)
    )
