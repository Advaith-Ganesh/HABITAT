import hashlib
import json
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import confusion_matrix
from ml.common import ROOT, FEATURES, EXCLUDED
from data.generate_dataset import generate
from ml.predict import predict, artifacts
from ml.explain import explain
from ml.evaluate import metrics, counterfactual, baseline


def test_source_reproducible():
    df = generate()
    assert len(df) == 2000
    assert df.application_id.is_unique
    assert (
        df.to_csv(index=False)
        == (ROOT / "data/public/habitat_synthetic_2000.csv").read_text()
    )
    assert set(df.case_review_required) == {0, 1}


def test_split_isolation():
    parts = [
        pd.read_csv(ROOT / f"data/splits/{s}.csv")
        for s in ["train", "validation", "test"]
    ]
    assert [len(p) for p in parts] == [1400, 300, 300]
    for i, a in enumerate(parts):
        for b in parts[i + 1 :]:
            assert not set(a.application_id) & set(b.application_id)
            assert not set(a.scenario_id) & set(b.scenario_id)
    assert sum(len(p) for p in parts) == 2000
    meta = json.loads((ROOT / "reports/splits.json").read_text())
    for name in ["train", "validation", "test"]:
        assert (
            meta[name]["sha256"]
            == hashlib.sha256(
                (ROOT / f"data/splits/{name}.csv").read_bytes()
            ).hexdigest()
        )


def test_no_outcome_or_sensitive_features():
    pipe, cfg = artifacts()
    assert not set(FEATURES) & set(EXCLUDED)
    assert list(pipe.feature_names_in_) == FEATURES
    train = pd.read_csv(ROOT / "data/splits/train.csv")
    np.testing.assert_allclose(
        pipe["transform"].named_transformers_["numeric"].statistics_,
        train[[x for x in FEATURES if x != "housing_situation"]].median().values,
    )


def test_inference_and_shap():
    row = generate().iloc[12].to_dict()
    p = predict(row)
    assert 0 <= p["score"] <= 1
    ex = explain(row)
    assert len(ex["attributions"]) == len(FEATURES)
    assert ex["additivity_error"] < 1e-6
    assert ex["score"] == p["score"]


def test_failure_fallback():
    p = predict({})
    assert p["failure"] == "KeyError"
    assert p["requires_review"]
    assert p["score"] is None


def test_metrics_recompute():
    df = pd.read_csv(ROOT / "data/splits/test.csv")
    pipe, cfg = artifacts()
    s = pipe.predict_proba(df[FEATURES])[:, 1]
    p = s >= cfg["threshold"]
    computed = metrics(df.case_review_required.to_numpy(), p)
    saved = json.loads((ROOT / "reports/evaluation.json").read_text())
    for key, value in computed.items():
        assert saved[key] == value
    comparison = json.loads((ROOT / "reports/model_comparison.json").read_text())
    assert comparison["checklist"] == metrics(
        df.case_review_required.to_numpy(), baseline(df)
    )


def test_counterfactuals_separate():
    result = counterfactual()
    assert result["pairs"] == 200
    assert result["rows"] == 400
    assert result["maximum_score_difference"] == 0
    pairs = pd.read_csv(ROOT / "data/public/counterfactual_400.csv")
    source = generate()
    assert not set(pairs.application_id) & set(source.application_id)
    assert not set(pairs.scenario_id) & set(source.scenario_id)
    for _, group in pairs.groupby("pair_id"):
        assert len(group) == 2
        assert (
            group.drop(columns=["synthetic_audit_group"])
            .iloc[0]
            .equals(group.drop(columns=["synthetic_audit_group"]).iloc[1])
        )
    # The independent seed must not reproduce task-feature rows from the source benchmark.
    assert not set(map(tuple, pairs[FEATURES].values)) & set(
        map(tuple, source[FEATURES].values)
    )


def test_uncertainty_escalation():
    df = generate()
    pipe, cfg = artifacts()
    s = pipe.predict_proba(df[FEATURES])[:, 1]
    idx = np.argmin(abs(s - cfg["threshold"]))
    p = predict(df.iloc[idx].to_dict())
    assert p["uncertain"]
    assert p["requires_review"]


def test_fairlearn_group_metrics():
    from fairlearn.metrics import false_negative_rate, false_positive_rate

    fair = json.loads((ROOT / "reports/fairness.json").read_text())
    df = pd.read_csv(ROOT / "data/splits/test.csv")
    pipe, cfg = artifacts()
    for group in fair["groups"]:
        subset = df[df.synthetic_audit_group == group["group"]]
        pred = pipe.predict_proba(subset[FEATURES])[:, 1] >= cfg["threshold"]
        assert group["count"] == len(subset)
        assert group["false_negative_rate"] == false_negative_rate(
            subset.case_review_required, pred
        )
        assert group["false_positive_rate"] == false_positive_rate(
            subset.case_review_required, pred
        )
    assert all(-1 <= x["correlation"] <= 1 for x in fair["proxy_correlations"])


@pytest.mark.parametrize(
    "kind", ["normal", "borderline", "incomplete", "contradictory", "unusual"]
)
def test_representative_scenarios(kind):
    from backend.main import Case

    row = Case().model_dump()
    if kind == "borderline":
        row.update(application_completeness_score=70, housing_situation="unclear")
    if kind == "incomplete":
        row.update(
            missing_document_count=3,
            income_document_available=0,
            identity_document_available=0,
            housing_evidence_available=0,
            application_completeness_score=15,
        )
    if kind == "contradictory":
        row["conflicting_information"] = 1
    if kind == "unusual":
        row.update(
            household_size=20,
            monthly_income=100000,
            monthly_housing_cost=0,
            current_bedrooms=0,
        )
    Case(**row)
    assert predict(row)["failure"] is None


def test_artifact_failure_fallback(monkeypatch):
    import ml.predict as module

    def unavailable():
        raise OSError("Deliberate test-only artifact failure")

    monkeypatch.setattr(module, "artifacts", unavailable)
    result = module.predict(generate().iloc[0].to_dict())
    assert result["category"] == "Human review fallback"
    assert result["requires_review"]
    assert result["score"] is None


def test_proxy_statistics_recompute():
    df = pd.read_csv(ROOT / "data/splits/test.csv")
    audit = json.loads((ROOT / "reports/fairness.json").read_text())
    for entry in audit["proxy_correlations"]:
        expected = float(
            np.corrcoef(
                (df.synthetic_audit_group == entry["group"]).astype(int),
                df[entry["feature"]],
            )[0, 1]
        )
        assert entry["correlation"] == pytest.approx(expected)
    rates = [g["false_negative_rate"] for g in audit["groups"]]
    assert audit["disparities"]["false_negative_rate"] == pytest.approx(
        max(rates) - min(rates)
    )
    assert any(g["status"] == "Potential concern" for g in audit["groups"])
