import numpy as np
import pandas as pd
import shap
from ml.predict import artifacts
from ml.common import FEATURES, NUMERIC


def explain(record):
    pipe, cfg = artifacts()
    transformed = pipe["transform"].transform(pd.DataFrame([record])[FEATURES])
    explainer = shap.TreeExplainer(pipe["classifier"])
    raw = explainer.shap_values(transformed)
    if isinstance(raw, list):
        values = np.asarray(raw[1])[0]
    else:
        raw = np.asarray(raw)
        values = raw[0, :, 1] if raw.ndim == 3 else raw[0]
    if len(values) != transformed.shape[1]:
        raise ValueError("SHAP features do not match the transformed pipeline")
    contributions = [
        {
            "feature": name,
            "value": record[name],
            "attribution": float(values[i]),
            "direction": (
                "toward additional review"
                if values[i] > 0
                else "toward routine workflow"
            ),
        }
        for i, name in enumerate(NUMERIC)
    ]
    contributions.append(
        {
            "feature": "housing_situation",
            "value": record["housing_situation"],
            "attribution": float(values[len(NUMERIC) :].sum()),
            "direction": (
                "toward additional review"
                if values[len(NUMERIC) :].sum() > 0
                else "toward routine workflow"
            ),
        }
    )
    contributions.sort(key=lambda x: abs(x["attribution"]), reverse=True)
    base = float(np.asarray(explainer.expected_value)[1])
    score = float(pipe.predict_proba(pd.DataFrame([record])[FEATURES])[0, 1])
    return {
        "base_value": base,
        "score": score,
        "attributions": contributions,
        "additivity_error": abs(
            base + sum(x["attribution"] for x in contributions) - score
        ),
        "summary": "; ".join(
            f"{x['feature'].replace('_',' ')} pushes {x['direction']}"
            for x in contributions[:3]
        ),
        "warning": "Model attributions are associations, not causes, policy evidence or legal eligibility.",
    }
