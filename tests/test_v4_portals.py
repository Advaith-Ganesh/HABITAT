"""V4 applicant/admin workflow and read-only sensitivity checks."""

import itertools
import json
import numpy as np
import pandas as pd
import pytest
from backend.main import Case
from ml.common import ROOT, FEATURES
from ml.predict import artifacts, predict


@pytest.mark.parametrize("states", list(itertools.product([0, 1], repeat=3)))
def test_document_percentage_matches_all_declared_states(client, states):
    payload = Case(
        income_document_available=states[0],
        identity_document_available=states[1],
        housing_evidence_available=states[2],
        missing_document_count=3 - sum(states),
    ).model_dump()
    result = client.post("/api/applications", json=payload).json()
    docs = result["documents"]
    assert docs["required"] == 3 and docs["present_count"] == sum(states)
    assert docs["percentage"] == 100 * sum(states) / 3
    assert len(docs["missing"]) == 3 - sum(states)
    assert len(docs["present"]) + len(docs["missing"]) == 3


def test_complete_applicant_admin_roundtrip(client):
    start = client.get("/api/dashboard").json()
    payload = Case(
        conflicting_information=1,
        housing_evidence_available=0,
        missing_document_count=1,
        application_completeness_score=200 / 3,
    ).model_dump()
    created = client.post("/api/applications", json=payload)
    assert created.status_code == 201
    record = created.json()
    aid = record["id"]
    assert record["status"] == "unassessed" and not record.get("assessment")
    assert aid in [a["id"] for a in client.get("/api/applications").json()]
    assert (
        client.get("/api/dashboard").json()["awaiting_assessment"]
        == start["awaiting_assessment"] + 1
    )
    assessed = client.post(f"/api/applications/{aid}/assess", json={}).json()
    assert assessed["score"] == predict(payload)["score"]
    explanation = client.get(f"/api/applications/{aid}/explanation").json()
    assert (
        abs(explanation["score"] - assessed["score"]) < 1e-12
        and explanation["additivity_error"] < 1e-6
    )
    response = client.post(
        f"/api/reviews/{aid}/resolve",
        json={
            "outcome": "request_evidence",
            "reason": "Please clarify the missing housing evidence in this demo.",
        },
    )
    assert response.status_code == 200
    applicant = client.get(f"/api/applications/{aid}").json()
    assert applicant["status"] == "pending"
    assert applicant["history"][-1]["detail"]["outcome"] == "request_evidence"
    assert (
        client.get("/api/dashboard").json()["information_requests"]
        == start["information_requests"] + 1
    )
    for outcome in ["additional_review", "routine"]:
        assert (
            client.post(
                f"/api/reviews/{aid}/resolve",
                json={
                    "outcome": outcome,
                    "reason": "Caseworker has reviewed the demo intake information.",
                },
            ).status_code
            == 200
        )
    applicant = client.get(f"/api/applications/{aid}").json()
    assert applicant["status"] == "resolved"
    assert (
        applicant["history"][-1]["detail"]["reason"]
        == "Caseworker has reviewed the demo intake information."
    )
    assert (
        client.get("/api/dashboard").json()["information_requests"]
        == start["information_requests"]
    )
    assert len(applicant["history"]) == 5


def test_sandbox_real_predictions_explanations_and_no_writes(client):
    record = client.post(
        "/api/applications", json=Case(conflicting_information=0).model_dump()
    ).json()
    aid = record["id"]
    before = client.get(f"/api/applications/{aid}").json()
    audit = client.post(
        "/api/sandbox/compare",
        json={
            "application_id": aid,
            "field": "synthetic_audit_group",
            "value": "Audit B",
        },
    ).json()
    assert (
        audit["changed"]
        and audit["before"]["prediction"]["score"]
        == audit["after"]["prediction"]["score"]
    )
    response = client.post(
        "/api/sandbox/compare",
        json={"application_id": aid, "field": "conflicting_information", "value": 1},
    )
    assert response.status_code == 200
    result = response.json()
    expected = predict({**before["payload"], "conflicting_information": 1})
    assert result["after"]["prediction"]["score"] == expected["score"]
    assert (
        result["before"]["prediction"]["score"]
        != result["after"]["prediction"]["score"]
    )
    for k in ["before", "after"]:
        assert result[k]["explanation"]["additivity_error"] < 1e-6
        assert result[k]["explanation"]["score"] == result[k]["prediction"]["score"]
    assert client.get(f"/api/applications/{aid}").json() == before
    same = client.post(
        "/api/sandbox/compare",
        json={"application_id": aid, "field": "conflicting_information", "value": 0},
    ).json()
    assert not same["changed"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("monthly_income", 1),
        ("conflicting_information", "1"),
        ("conflicting_information", 2),
        ("synthetic_audit_group", "Unknown"),
    ],
)
def test_sandbox_rejects_invalid_changes(client, field, value):
    assert (
        client.post(
            "/api/sandbox/compare",
            json={"application_id": "HAB-0023", "field": field, "value": value},
        ).status_code
        == 422
    )


def test_safeguard_is_actual_held_out_measurement(client):
    result = client.get("/api/model/safeguard").json()
    pipe, cfg = artifacts()
    test = pd.read_csv(ROOT / "data/splits/test.csv")
    score = pipe.predict_proba(test[FEATURES])[:, 1]
    p = score >= cfg["threshold"]
    y = test.case_review_required.to_numpy()
    for key, escalated in [
        ("without_uncertainty", p),
        (
            "with_uncertainty",
            p | (np.abs(score - cfg["threshold"]) <= cfg["uncertainty_margin"]),
        ),
    ]:
        expected_errors = int(((p != y) & ~escalated).sum())
        assert result[key]["human_escalation_count"] == int(escalated.sum())
        assert result[key]["remaining_routing_errors"] == expected_errors
        assert result[key]["remaining_routing_error_rate"] == expected_errors / int(
            (~escalated).sum()
        )
    assert (
        result["threshold"] == cfg["threshold"]
        and result["uncertainty_margin"] == cfg["uncertainty_margin"]
    )
    assert (
        json.loads((ROOT / "reports/evaluation.json").read_text())[
            "validation_target_met"
        ]
        is False
    )
