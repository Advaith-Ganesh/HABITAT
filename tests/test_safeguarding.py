"""Declarations persist without becoming model features or invented verification."""
import hashlib
import json
import uuid
import pytest
from backend import main as backend
from backend.main import Application, Case, Session, SubmissionRequest
from ml.common import FEATURES


def scenario():
    return Case().model_dump() | {
        'safe_to_stay_tonight': 'no', 'evidence_help_needed': ['income'],
        'income_document_available': 0, 'identity_document_available': 0,
        'missing_document_count': 2,
    }


def test_safeguarding_saved_without_model_and_reviewable(client, monkeypatch):
    def unavailable(*args):
        raise OSError('model unavailable')
    monkeypatch.setattr(backend, 'predict', unavailable)
    h={'X-Sandbox-Session':str(uuid.uuid4()), 'Idempotency-Key':str(uuid.uuid4())}
    response=client.post('/api/applications',json=scenario(),headers=h)
    assert response.status_code==201
    aid=response.json()['id']; assert aid.startswith('HAB-')
    assert response.json()['documents']['help_needed']==['Income evidence']
    assert response.json()['documents']['present_count']==1
    assert 'Not verified' in response.json()['documents']['verification_status']
    with Session() as db:
        assert json.loads(db.get(Application,aid).payload)['safe_to_stay_tonight']=='no'
    assert aid in [r['id'] for r in client.get('/api/applications').json()]
    a=client.post(f'/api/applications/{aid}/assess').json()
    assert a['score'] is None and a['failure']=='InputCompatibilityUnavailable'
    reason='Follow up on immediate housing concern and help obtain income evidence; identity evidence remains unavailable.'
    assert client.post(f'/api/reviews/{aid}/resolve',json={'outcome':'escalate','reason':reason}).status_code==200
    saved=client.get(f'/api/applications/{aid}').json()
    assert saved['latest_review']['reason']==reason
    assert saved['status']=='pending' and saved['payload']['evidence_help_needed']==['income']
    retry=client.post('/api/applications',json=scenario(),headers=h)
    assert retry.json()['id']==aid and retry.headers['Idempotency-Replayed']=='true'
    assert len(saved['history'])==3
    assert client.post('/api/applications',json=scenario()|{'safe_to_stay_tonight':'yes'},headers=h).status_code==409


@pytest.mark.parametrize('change', [
    {'safe_to_stay_tonight':'emergency'}, {'evidence_help_needed':['passport']},
    {'evidence_help_needed':['income','income']},
    {'income_document_available':1,'missing_document_count':1},
])
def test_invalid_or_inconsistent_declarations_rejected(client,change):
    assert client.post('/api/applications',json=scenario()|change).status_code==422


@pytest.mark.parametrize('legacy_score',[None,82])
def test_pre_safeguarding_retry_hashes_remain_compatible(client,legacy_score):
    old=Case.model_validate(Case().model_dump()|{'application_completeness_score':legacy_score}).model_dump(exclude=backend.SAFEGUARD_FIELDS)
    aid='HAB-OLD-'+uuid.uuid4().hex[:8]
    h={'X-Sandbox-Session':str(uuid.uuid4()),'Idempotency-Key':str(uuid.uuid4())}
    digest=lambda v: hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    key=hashlib.sha256(f"{h['X-Sandbox-Session']}:{h['Idempotency-Key']}".encode()).hexdigest()
    with Session() as db:
        db.add(Application(id=aid,payload=json.dumps(old),status='unassessed'));db.flush()
        db.add(SubmissionRequest(key_hash=key,payload_hash=digest(old),application_id=aid));db.commit()
    replay=client.post('/api/applications',json=old,headers=h)
    assert replay.status_code==201 and replay.json()['id']==aid
    assert replay.headers['Idempotency-Replayed']=='true'
    assert client.post('/api/applications',json=old|{'safe_to_stay_tonight':'no'},headers=h).status_code==409
    with Session() as db:
        assert json.loads(db.get(Application,aid).payload)==old


def test_non_model_metadata_preserves_genuine_prediction_and_shap(client,historical_case):
    assert not backend.SAFEGUARD_FIELDS.intersection(FEATURES)
    base=Case().model_dump()|{'application_completeness_score':82}
    first=historical_case(base)
    second=historical_case(base|{'safe_to_stay_tonight':'no'})
    a=client.post(f'/api/applications/{first}/assess').json()
    b=client.post(f'/api/applications/{second}/assess').json()
    assert a['score'] is not None and a['score']==b['score']
    shap=client.get(f'/api/applications/{second}/explanation').json()
    assert shap['additivity_error']<1e-6 and abs(shap['score']-b['score'])<1e-12
