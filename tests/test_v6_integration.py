"""Applicant-session integration backed by SQLite, not browser mock records."""
import json
from datetime import datetime
import uuid
import pytest
from backend.main import Case, Application, ApplicantSessionApplication, Session, engine
from ml.predict import predict


def session():
    return {"X-Sandbox-Session": str(uuid.uuid4())}


def test_multiple_applications_shared_workflow_survives_connection_restart(client):
    headers = session()
    other = session()
    before = client.get('/api/dashboard').json()
    ids = []
    for household in [3, 5]:
        payload = Case(household_size=household, conflicting_information=1).model_dump()
        response = client.post('/api/applications', json=payload, headers=headers)
        assert response.status_code == 201
        ids.append(response.json()['id'])
    assert len(set(ids)) == 2
    assert [r['id'] for r in client.get('/api/applicant/applications', headers=headers).json()] == ids
    assert client.get('/api/applicant/applications', headers=other).json() == []
    assert set(ids) <= {r['id'] for r in client.get('/api/applications').json()}
    assert client.get('/api/dashboard').json()['applications'] == before['applications'] + 2
    aid = ids[0]
    payload = client.get(f'/api/applications/{aid}').json()['payload']
    first = client.post(f'/api/applications/{aid}/assess', json={}).json()
    second = client.post(f'/api/applications/{aid}/assess', json={}).json()
    assert first['score'] is None and second['score'] is None
    assert first['failure'] == 'InputCompatibilityUnavailable'
    assert first['model_version'] == 'rf-1.0'
    assert 'model_sha256' not in first
    assert datetime.fromisoformat(second['assessed_at']) > datetime.fromisoformat(first['assessed_at'])
    assert client.get(f'/api/applications/{aid}/explanation').status_code == 409
    for outcome in ['request_evidence', 'escalate', 'additional_review', 'routine']:
        response = client.post(f'/api/reviews/{aid}/resolve', json={'outcome':outcome, 'reason':'Caseworker verified the synthetic intake information.'})
        assert response.status_code == 200
        applicant = client.get('/api/applicant/applications', headers=headers).json()[0]
        assert applicant['latest_review']['outcome'] == outcome
        assert datetime.fromisoformat(applicant['latest_review']['timestamp']).tzinfo is not None
    engine.dispose()  # fresh connections; separate live-browser run verifies OS process restart
    rows = client.get('/api/applicant/applications', headers=headers).json()
    assert [r['id'] for r in rows] == ids
    assert rows[0]['status'] == 'resolved' and rows[1]['status'] == 'unassessed'
    detail = client.get(f'/api/applications/{aid}').json()
    assert detail['assessment'] == second
    assert len(detail['history']) == 7
    assert client.post(f'/api/applications/{aid}/assess', json={}).status_code == 409
    with Session() as db:
        assert db.get(Application, aid).status == 'resolved'
        assert db.get(ApplicantSessionApplication, aid).session_id == headers['X-Sandbox-Session']


@pytest.mark.parametrize('missing', [k for k in Case.model_fields if k != 'application_completeness_score'])
def test_every_submission_field_required(client, missing):
    payload = Case().model_dump()
    del payload[missing]
    before = client.get('/api/dashboard').json()['applications']
    assert client.post('/api/applications', json=payload, headers=session()).status_code == 422
    assert client.get('/api/dashboard').json()['applications'] == before


@pytest.mark.parametrize('field,value', [('household_size',0),('monthly_income',-1),('housing_situation','unknown'),('income_document_available',2),('synthetic_only',False),('current_bedrooms',50)])
def test_invalid_submission_not_saved(client, field, value):
    payload = Case().model_dump() | {field:value}
    assert client.post('/api/applications', json=payload, headers=session()).status_code == 422


def test_session_validation_and_optional_api_compatibility(client):
    assert client.get('/api/applicant/applications').status_code == 422
    assert client.get('/api/applicant/applications',headers={'X-Sandbox-Session':'bad'}).status_code == 422
    assert client.post('/api/applications', json=Case().model_dump(),headers={'X-Sandbox-Session':'bad'}).status_code == 422
    assert client.post('/api/applications', json={}).status_code == 422
    assert client.post('/api/applications', json=Case().model_dump()).status_code == 201
