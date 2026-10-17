"""Read-only ML verification: no fitting, threshold tuning or artifact replacement."""

import hashlib
import json
from itertools import combinations
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, roc_auc_score
from data.generate_dataset import generate
from ml.common import ROOT, FEATURES, EXCLUDED, save_json
from ml.predict import artifacts, predict
from ml.explain import explain
from ml.evaluate import metrics, baseline, fairness_audit


def main(output_path="reports/v2-ml-audit.json"):
    source = pd.read_csv(ROOT / "data/public/habitat_synthetic_2000.csv")
    parts = {
        k: pd.read_csv(ROOT / f"data/splits/{k}.csv")
        for k in ["train", "validation", "test"]
    }
    pipe, cfg = artifacts()
    test = parts["test"]
    validation = parts["validation"]
    scores = pipe.predict_proba(test[FEATURES])[:, 1]
    computed = metrics(test.case_review_required.to_numpy(), scores >= cfg["threshold"])
    stored = json.loads((ROOT / "reports/evaluation.json").read_text())
    assert all(stored[k] == v for k, v in computed.items())
    val_scores = pipe.predict_proba(validation[FEATURES])[:, 1]
    thresholds = np.arange(0.3, 0.71, 0.025)
    validation_choice = float(
        max(
            thresholds,
            key=lambda t: f1_score(validation.case_review_required, val_scores >= t),
        )
    )
    assert validation_choice == cfg["threshold"]
    gaps = {
        f"{a}/{b}": {
            "shared_application_ids": len(
                set(parts[a].application_id) & set(parts[b].application_id)
            ),
            "shared_scenarios": len(
                set(parts[a].scenario_id) & set(parts[b].scenario_id)
            ),
        }
        for a, b in combinations(parts, 2)
    }
    assert not any(any(v.values()) for v in gaps.values())
    assert len(source) == 2000 and [len(p) for p in parts.values()] == [1400, 300, 300]
    assert (
        generate().to_csv(index=False)
        == (ROOT / "data/public/habitat_synthetic_2000.csv").read_text()
    )
    assert not set(FEATURES) & set(EXCLUDED)
    example = test.iloc[0].to_dict()
    prediction = predict(example)
    explanation = explain(example)
    assert (
        abs(prediction["score"] - explanation["score"]) < 1e-12
        and explanation["additivity_error"] < 1e-6
    )
    audit = fairness_audit()
    saved_audit = json.loads((ROOT / "reports/fairness.json").read_text())
    assert audit == saved_audit
    fallback = predict({})
    assert fallback["requires_review"] and fallback["score"] is None
    result = {
        "retrained": False,
        "model_sha256": hashlib.sha256(
            (ROOT / "models/habitat_review_model.joblib").read_bytes()
        ).hexdigest(),
        "source_sha256": hashlib.sha256(
            (ROOT / "data/public/habitat_synthetic_2000.csv").read_bytes()
        ).hexdigest(),
        "source_records": len(source),
        "split_sizes": {k: len(v) for k, v in parts.items()},
        "split_isolation": gaps,
        "source_byte_reproducible": True,
        "fitted_classifier": type(pipe["classifier"]).__name__,
        "fitted_trees": len(pipe["classifier"].estimators_),
        "features": FEATURES,
        "test_metrics_recomputed": computed,
        "test_roc_auc_recomputed": float(
            roc_auc_score(test.case_review_required, scores)
        ),
        "baseline_recomputed": metrics(
            test.case_review_required.to_numpy(), baseline(test)
        ),
        "validation_only_threshold_reproduced": validation_choice,
        "validation_recall_target_met": cfg["validation_routing_recall"] >= 0.9,
        "example_prediction": prediction,
        "example_explanation": explanation,
        "fairness_recomputed_matches_saved": True,
        "fairness": audit,
        "failure_fallback": fallback,
    }
    save_json(output_path, result)
    print(
        json.dumps(
            {
                k: result[k]
                for k in [
                    "retrained",
                    "model_sha256",
                    "source_records",
                    "split_sizes",
                    "fitted_classifier",
                    "fitted_trees",
                    "fairness_recomputed_matches_saved",
                ]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
