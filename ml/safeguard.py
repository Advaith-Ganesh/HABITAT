"""Read-only held-out safeguard measurement, with existing validation-selected settings."""

import numpy as np
import pandas as pd
from ml.common import ROOT, FEATURES
from ml.predict import artifacts


def measure():
    pipe, cfg = artifacts()
    test = pd.read_csv(ROOT / "data/splits/test.csv")
    score = pipe.predict_proba(test[FEATURES])[:, 1]
    labels = test.case_review_required.to_numpy()
    predicted = score >= cfg["threshold"]
    uncertain = np.abs(score - cfg["threshold"]) <= cfg["uncertainty_margin"]

    def summary(escalated):
        remaining = ~escalated
        mistakes = (predicted != labels) & remaining
        return {
            "human_escalation_count": int(escalated.sum()),
            "human_escalation_rate": float(escalated.mean()),
            "remaining_routed_count": int(remaining.sum()),
            "remaining_routing_errors": int(mistakes.sum()),
            "remaining_routing_error_rate": (
                float(mistakes.sum() / remaining.sum()) if remaining.any() else None
            ),
        }

    baseline = summary(predicted)
    safeguarded = summary(predicted | uncertain)
    return {
        "test_records": len(test),
        "before_human_escalation": {
            "routing_errors": int((predicted != labels).sum()),
            "routing_error_rate": float((predicted != labels).mean()),
            "cases": len(test),
        },
        "threshold": cfg["threshold"],
        "uncertainty_margin": cfg["uncertainty_margin"],
        "selection": "Existing settings selected using validation only; no test tuning or retraining.",
        "without_uncertainty": baseline,
        "with_uncertainty": safeguarded,
        "additional_human_rate": safeguarded["human_escalation_rate"]
        - baseline["human_escalation_rate"],
        "remaining_error_rate_difference": safeguarded["remaining_routing_error_rate"]
        - baseline["remaining_routing_error_rate"],
        "limitation": "Simulated routing errors against synthetic labels among cases remaining in the routine route. Every real case still needs human handling. These are not measured housing outcomes or observed cost savings.",
    }
