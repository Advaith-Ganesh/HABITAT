import json
import pytest
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError
from backend.main import Case, Session, Event, engine
from ml.common import ROOT


@pytest.mark.parametrize(
    "path",
    [
        "/health",
        "/api/dashboard",
        "/api/model/metrics",
        "/api/model/baseline",
        "/api/applications",
        "/api/fairness/metrics",
        "/api/reviews",
        "/api/policies",
        "/api/dataset/metadata",
    ],
)
def test_read_endpoints(client, path):
    assert client.get(path).status_code == 200


def test_complete_review_flow(client):
    body = Case(conflicting_information=1).model_dump()
    r = client.post("/api/applications", json=body)
    assert r.status_code == 201
    aid = r.json()["id"]
    assert client.get(f"/api/applications/{aid}/explanation").status_code == 409
    result = client.post(f"/api/applications/{aid}/assess", json={})
    assert result.status_code == 200
    assert 0 <= result.json()["score"] <= 1
    assert (
        client.get(f"/api/applications/{aid}/explanation").json()["additivity_error"]
        < 1e-6
    )
    assert (
        client.post(
            f"/api/reviews/{aid}/resolve",
            json={"outcome": "routine", "reason": " " * 10},
        ).status_code
        == 422
    )
    resolved = client.post(
        f"/api/reviews/{aid}/resolve",
        json={
            "outcome": "routine",
            "reason": "Human checked synthetic evidence and recorded follow-up.",
        },
    )
    assert resolved.status_code == 200
    assert resolved.json()["status"] == "resolved"
    assert [e["action"] for e in resolved.json()["history"]] == [
        "submitted",
        "assessed",
        "human_override",
    ]
    # A fresh DB session confirms durable persisted events.
    with Session() as db:
        assert len(db.query(Event).filter_by(application_id=aid).all()) == 3
    assert (
        client.get(f"/api/applications/{aid}")
        .json()["history"][-1]["detail"]["reason"]
        .startswith("Human checked")
    )


@pytest.mark.parametrize(
    "change",
    [
        {"household_size": 0},
        {"monthly_income": -1},
        {"application_completeness_score": 101},
        {"synthetic_only": False},
        {"name": "Real person"},
        {"housing_situation": "invalid"},
        {"missing_document_count": 3},
    ],
)
def test_input_and_sandbox_restrictions(client, change):
    assert (
        client.post(
            "/api/applications", json={**Case().model_dump(), **change}
        ).status_code
        == 422
    )


@pytest.mark.parametrize("verb", ["UPDATE", "DELETE"])
def test_append_only_history(client, verb):
    with pytest.raises(DatabaseError):
        with engine.begin() as conn:
            conn.execute(
                text(
                    "UPDATE events SET action='altered'"
                    if verb == "UPDATE"
                    else "DELETE FROM events"
                )
            )


def test_missing_case(client):
    assert client.get("/api/applications/not-found").status_code == 404


def test_no_destructive_routes(client):
    assert client.delete("/api/applications/anything").status_code == 405


def test_download(client):
    response = client.get("/api/dataset/download")
    assert response.status_code == 200
    assert len(response.text.splitlines()) == 2001


def test_counterfactual_api(client):
    assert client.post("/api/fairness/counterfactual", json={}).json()["pairs"] == 200
    assert (
        client.post(
            "/api/fairness/counterfactual", json={"attribute": "monthly_income"}
        ).status_code
        == 422
    )


def test_policy_pack(client):
    pack = json.loads((ROOT / "policy_packs/england-demo.json").read_text())
    schema = json.loads((ROOT / "policy_packs/schema.json").read_text())
    assert set(schema["required"]) <= set(pack)
    assert pack["source_url"].startswith("https://www.gov.uk/")
    assert pack["effective_date"] is None
    policies = client.get("/api/policies").json()
    assert sum(p["functional"] for p in policies) == 1
    assert policies[0]["name"] == "England Intake Framework"
    assert policies[0]["id"] == "england-demo"


def test_policy_interface():
    from backend.policy import load_policy

    result = load_policy().evaluate(
        {
            "missing_document_count": 2,
            "conflicting_information": 1,
            "housing_situation": "unclear",
        }
    )
    assert len(result["prompts"]) == 3
    assert "Project-defined" in result["origin"]
    assert "not extracted statutory rules" in result["origin"]
    with pytest.raises(ValueError):
        load_policy("india")
