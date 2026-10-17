import joblib
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from ml.common import ROOT, FEATURES, NUMERIC, save_json


def main():
    train = pd.read_csv(ROOT / "data/splits/train.csv")
    val = pd.read_csv(ROOT / "data/splits/validation.csv")
    transform = ColumnTransformer(
        [
            ("numeric", SimpleImputer(strategy="median"), NUMERIC),
            (
                "category",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        (
                            "encode",
                            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                        ),
                    ]
                ),
                ["housing_situation"],
            ),
        ]
    )
    # One production classifier; threshold selection uses validation only.
    pipe = Pipeline(
        [
            ("transform", transform),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=180,
                    max_depth=8,
                    min_samples_leaf=8,
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=1,
                ),
            ),
        ]
    )
    pipe.fit(train[FEATURES], train.case_review_required)
    scores = pipe.predict_proba(val[FEATURES])[:, 1]
    candidates = np.arange(0.3, 0.71, 0.025)
    threshold = float(
        max(candidates, key=lambda t: f1_score(val.case_review_required, scores >= t))
    )
    margins = [0.04, 0.08, 0.12, 0.16]
    # Choose smallest uncertainty margin achieving >=90% recall in validation routing.
    margin = next(
        (
            m
            for m in margins
            if ((scores >= threshold - m) & (val.case_review_required == 1)).sum()
            / val.case_review_required.sum()
            >= 0.9
        ),
        margins[-1],
    )
    joblib.dump(pipe, ROOT / "models/habitat_review_model.joblib")
    save_json(
        "models/config.json",
        {
            "threshold": threshold,
            "uncertainty_margin": margin,
            "selection": "Validation F1 threshold; smallest candidate margin achieving 90% validation routing recall, otherwise maximum margin.",
            "validation_f1": float(
                f1_score(val.case_review_required, scores >= threshold)
            ),
            "validation_routing_recall": float(
                ((scores >= threshold - margin) & (val.case_review_required == 1)).sum()
                / val.case_review_required.sum()
            ),
            "training_records": len(train),
            "features": FEATURES,
        },
    )


if __name__ == "__main__":
    main()
