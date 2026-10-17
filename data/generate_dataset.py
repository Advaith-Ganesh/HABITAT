"""Generator v1.0.0, seed 42. No external or personal records."""

import numpy as np
import pandas as pd
from ml.common import ROOT, save_json


def generate(seed=42):
    rng = np.random.default_rng(seed)
    rows = []
    for family in range(1000):
        # Related profiles share family circumstances; both stay in one partition.
        group = rng.choice(["Audit A", "Audit B", "Audit C"], p=[0.45, 0.35, 0.2])
        members = int(rng.integers(1, 8))
        income = int(rng.integers(300, 5001))
        situation = rng.choice(["stable", "temporary", "unclear"], p=[0.60, 0.25, 0.15])
        for variant in range(2):
            docs = rng.random(3) > np.array([0.16, 0.10, 0.20])
            missing = int((~docs).sum())
            conflict = int(rng.random() < 0.13)
            specialist = int(rng.random() < 0.16)
            completeness = float(
                np.clip(100 - 18 * missing - rng.normal(8, 12), 5, 100).round(1)
            )
            # Latent intake ambiguity and Bernoulli labels prevent deterministic replay.
            logit = (
                -3.4
                + 1.25 * missing
                + 2.5 * conflict
                + 1.9 * specialist
                + 0.045 * (100 - completeness)
                + 1.4 * (situation == "unclear")
                + rng.normal(0, 0.65)
            )
            label = int(rng.random() < 1 / (1 + np.exp(-logit)))
            if rng.random() < 0.025:
                label = 1 - label
            rows.append(
                dict(
                    application_id=f"HAB-{family*2+variant+1:04d}",
                    scenario_id=f"S-{family:04d}",
                    household_size=members,
                    household_members=members,
                    monthly_income=income,
                    monthly_housing_cost=int(income * rng.uniform(0.2, 0.85)),
                    current_bedrooms=int(rng.integers(0, 5)),
                    housing_situation=situation,
                    housing_insecurity_reported=int(situation != "stable"),
                    overcrowding_indicator=int(members > 4),
                    missing_document_count=missing,
                    income_document_available=int(docs[0]),
                    identity_document_available=int(docs[1]),
                    housing_evidence_available=int(docs[2]),
                    accessibility_support_requested=int(rng.random() < 0.18),
                    specialist_support_requested=specialist,
                    conflicting_information=conflict,
                    application_completeness_score=completeness,
                    reported_residency_context=rng.choice(["reported", "unclear"]),
                    synthetic_audit_group=group,
                    age_band=rng.choice(["18–34", "35–64", "65+"]),
                    case_review_required=label,
                )
            )
    return pd.DataFrame(rows)


def main():
    from sklearn.model_selection import train_test_split
    import hashlib

    df = generate()
    df.to_csv(ROOT / "data/public/habitat_synthetic_2000.csv", index=False)
    families = df.groupby("scenario_id").case_review_required.sum()
    train, rest = train_test_split(
        families.index, test_size=300, random_state=42, stratify=families.values
    )
    val, test = train_test_split(
        rest, test_size=150, random_state=42, stratify=families.loc[rest].values
    )
    meta = {}
    partitions = {}
    for name, ids in [("train", train), ("validation", val), ("test", test)]:
        part = df[df.scenario_id.isin(ids)]
        path = ROOT / f"data/splits/{name}.csv"
        part.to_csv(path, index=False)
        partitions[name] = part
        meta[name] = {
            "size": len(part),
            "positive": int(part.case_review_required.sum()),
            "class_distribution": part.case_review_required.value_counts().to_dict(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    meta.update(
        source_sha256=hashlib.sha256(
            (ROOT / "data/public/habitat_synthetic_2000.csv").read_bytes()
        ).hexdigest(),
        shared_scenarios=sum(
            len(set(a.scenario_id) & set(b.scenario_id))
            for i, a in enumerate(partitions.values())
            for b in list(partitions.values())[i + 1 :]
        ),
        shared_application_ids=sum(
            len(set(a.application_id) & set(b.application_id))
            for i, a in enumerate(partitions.values())
            for b in list(partitions.values())[i + 1 :]
        ),
        duplicate_rows=int(df.duplicated().sum()),
        generator="1.0.0",
        seed=42,
    )
    save_json("reports/splits.json", meta)


if __name__ == "__main__":
    main()
