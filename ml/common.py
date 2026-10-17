from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
FEATURES = [
    "missing_document_count",
    "income_document_available",
    "identity_document_available",
    "housing_evidence_available",
    "conflicting_information",
    "application_completeness_score",
    "housing_situation",
    "specialist_support_requested",
    "housing_insecurity_reported",
]
NUMERIC = [x for x in FEATURES if x != "housing_situation"]
EXCLUDED = [
    "case_review_required",
    "application_id",
    "scenario_id",
    "synthetic_audit_group",
    "age_band",
    "reported_residency_context",
    "monthly_income",
    "monthly_housing_cost",
    "accessibility_support_requested",
]


def save_json(path, data):
    (ROOT / path).write_text(json.dumps(data, indent=2, allow_nan=False))


# Inputs bound to a successful read-only evaluation verification.
EVALUATION_INPUTS = [
    "models/habitat_review_model.joblib",
    "models/config.json",
    "data/public/habitat_synthetic_2000.csv",
    "data/public/counterfactual_400.csv",
    "data/splits/train.csv",
    "data/splits/validation.csv",
    "data/splits/test.csv",
    "reports/evaluation.json",
    "reports/model_comparison.json",
    "reports/fairness.json",
]
