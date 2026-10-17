import json
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
)
from fairlearn.metrics import (
    MetricFrame,
    selection_rate,
    false_positive_rate,
    false_negative_rate,
    count,
)
from ml.common import ROOT, FEATURES, NUMERIC, save_json
from ml.predict import artifacts


def baseline(df):
    return (
        (
            (df.missing_document_count >= 1)
            | (df.conflicting_information == 1)
            | (df.specialist_support_requested == 1)
            | (df.application_completeness_score < 70)
            | (df.housing_situation == "unclear")
        )
        .astype(int)
        .to_numpy()
    )


def metrics(y, p):
    tn, fp, fn, tp = confusion_matrix(y, p, labels=[0, 1]).ravel()
    return dict(
        accuracy=float(accuracy_score(y, p)),
        precision=float(precision_score(y, p, zero_division=0)),
        recall=float(recall_score(y, p, zero_division=0)),
        f1=float(f1_score(y, p, zero_division=0)),
        confusion_matrix=[[int(tn), int(fp)], [int(fn), int(tp)]],
        false_positive_rate=float(fp / (tn + fp)),
        false_negative_rate=float(fn / (fn + tp)),
        positive_support=int(sum(y)),
        human_review_rate=float(np.mean(p)),
        class_distribution={"0": int(sum(y == 0)), "1": int(sum(y == 1))},
    )


def counterfactual(write_csv=False):
    from data.generate_dataset import generate

    candidates = generate(seed=4242)
    source = generate()
    existing = set(map(tuple, source[FEATURES].values))
    candidates = candidates[
        [tuple(row) not in existing for row in candidates[FEATURES].values]
    ]
    pairs = candidates.iloc[:200].copy()
    pairs["application_id"] = ["CF-" + str(i) for i in range(200)]
    pairs["scenario_id"] = ["CF-S-" + str(i) for i in range(200)]
    pairs["pair_id"] = np.arange(200)
    a = pairs.copy()
    b = pairs.copy()
    a.synthetic_audit_group = "Audit A"
    b.synthetic_audit_group = "Audit B"
    if write_csv:
        pd.concat([a, b]).to_csv(
            ROOT / "data/public/counterfactual_400.csv", index=False
        )
    pipe, cfg = artifacts()
    sa = pipe.predict_proba(a[FEATURES])[:, 1]
    sb = pipe.predict_proba(b[FEATURES])[:, 1]
    diff = np.abs(sa - sb)
    return {
        "pairs": 200,
        "rows": 400,
        "differing_classifications": int(
            ((sa >= cfg["threshold"]) != (sb >= cfg["threshold"])).sum()
        ),
        "average_score_difference": float(diff.mean()),
        "maximum_score_difference": float(diff.max()),
        "failure_examples": a.loc[diff > 0, "pair_id"].tolist(),
        "attribute_is_feature": False,
        "limitation": "Audit group is excluded, so equality is expected by construction. This does not test proxy discrimination.",
        "examples": [
            {
                "pair_id": i,
                "attribute_a": "Audit A",
                "attribute_b": "Audit B",
                "score_a": float(sa[i]),
                "score_b": float(sb[i]),
            }
            for i in range(5)
        ],
    }


def fairness_audit():
    """Recompute descriptive audit without retraining or mutating public artifacts."""
    test = pd.read_csv(ROOT / "data/splits/test.csv")
    pipe, cfg = artifacts()
    y = test.case_review_required.to_numpy()
    scores = pipe.predict_proba(test[FEATURES])[:, 1]
    p = (scores >= cfg["threshold"]).astype(int)
    result = metrics(y, p)
    frame = MetricFrame(
        metrics={
            "selection_rate": selection_rate,
            "accuracy": accuracy_score,
            "false_positive_rate": false_positive_rate,
            "false_negative_rate": false_negative_rate,
            "count": count,
        },
        y_true=y,
        y_pred=p,
        sensitive_features=test.synthetic_audit_group,
    )
    groups = []
    for name, row in frame.by_group.iterrows():
        subset = test[test.synthetic_audit_group == name]
        positives = int(subset.case_review_required.sum())
        negatives = len(subset) - positives
        groups.append(
            {
                "group": name,
                **{k: float(v) for k, v in row.items()},
                "positive_count": positives,
                "negative_count": negatives,
                "status": (
                    "Inconclusive due to insufficient data"
                    if min(positives, negatives) < 20
                    else (
                        "Potential concern"
                        if abs(row.false_negative_rate - result["false_negative_rate"])
                        > 0.1
                        else "No concern detected in this test"
                    )
                ),
            }
        )
    # Pearson correlations of one-hot audit memberships with numeric intake inputs.
    correlations = [
        {
            "group": g,
            "feature": f,
            "correlation": float(
                np.corrcoef((test.synthetic_audit_group == g).astype(int), test[f])[
                    0, 1
                ]
            ),
        }
        for g in sorted(test.synthetic_audit_group.unique())
        for f in NUMERIC
    ]
    return {
        "groups": groups,
        "disparities": {k: float(v) for (k, v) in frame.difference().items()},
        "counterfactual": counterfactual(),
        "proxy_correlations": correlations,
        "maximum_absolute_proxy_correlation": max(
            (abs(x["correlation"]) for x in correlations)
        ),
        "warning": "Small synthetic test; error differences are descriptive, unadjusted for multiple tests, and not proof of universal fairness.",
    }


def main():
    test = pd.read_csv(ROOT / "data/splits/test.csv")
    pipe, cfg = artifacts()
    y = test.case_review_required.to_numpy()
    s = pipe.predict_proba(test[FEATURES])[:, 1]
    p = (s >= cfg["threshold"]).astype(int)
    result = metrics(y, p)
    result.update(
        roc_auc=float(roc_auc_score(y, s)),
        routing_review_rate=float(
            np.mean(s >= cfg["threshold"] - cfg["uncertainty_margin"])
        ),
        routing_recall=float(
            recall_score(y, s >= cfg["threshold"] - cfg["uncertainty_margin"])
        ),
        validation_routing_recall=cfg["validation_routing_recall"],
        validation_routing_recall_target=0.90,
        validation_target_met=cfg["validation_routing_recall"] >= 0.90,
        uncertainty_margin=cfg["uncertainty_margin"],
        test_records=len(test),
        threshold=cfg["threshold"],
    )
    save_json("reports/evaluation.json", result)
    save_json(
        "reports/model_comparison.json",
        {"random_forest": result, "checklist": metrics(y, baseline(test))},
    )
    save_json("reports/fairness.json", fairness_audit())
    counterfactual(write_csv=True)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.imshow(result["confusion_matrix"], cmap="Blues")
    for (i, j), v in np.ndenumerate(result["confusion_matrix"]):
        ax.text(j, i, str(v), ha="center", va="center")
    ax.set(
        xticks=[0, 1],
        yticks=[0, 1],
        xlabel="Predicted",
        ylabel="Synthetic label",
        title="Held-out test · 300 synthetic cases",
    )
    fig.tight_layout()
    fig.savefig(ROOT / "reports/confusion_matrix.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
