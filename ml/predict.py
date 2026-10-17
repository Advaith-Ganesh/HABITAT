from functools import lru_cache
import json
import joblib
import pandas as pd
from ml.common import ROOT, FEATURES
from ml.input_audit import check_inputs


@lru_cache
def artifacts():
    return joblib.load(ROOT / "models/habitat_review_model.joblib"), json.loads(
        (ROOT / "models/config.json").read_text()
    )


def predict(record):
    try:
        pipe, cfg = artifacts()
        score = float(pipe.predict_proba(pd.DataFrame([record])[FEATURES])[0, 1])
        input_check = check_inputs(record)
        uncertain = abs(score - cfg["threshold"]) <= cfg["uncertainty_margin"]
        additional = score >= cfg["threshold"]
        return dict(
            score=score,
            classification=int(additional),
            category=(
                "Additional human review"
                if additional
                else "Routine human review workflow"
            ),
            uncertain=uncertain,
            requires_review=bool(additional or uncertain or input_check["out_of_distribution"]),
            input_validation=input_check,
            threshold=cfg["threshold"],
            failure=None,
            limitations="Synthetic-label agreement only. Neither approval nor rejection; score is not a guarantee.",
        )
    except (
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
        OSError,
        EOFError,
        RuntimeError,
    ) as exc:
        return dict(
            score=None,
            classification=None,
            category="Human review fallback",
            uncertain=True,
            requires_review=True,
            failure=type(exc).__name__,
            limitations="Inference unavailable; a human must review this case.",
        )
