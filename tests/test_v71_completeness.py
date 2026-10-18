"""New untrusted submissions cannot manufacture the missing training feature."""
import hashlib
import json
import uuid
import pytest
from backend import main as backend
from backend.main import Case, Session, Application, SubmissionRequest

@pytest.mark.parametrize('supplied', ['omitted', None, 0, 37, 95, 100])
def test_authoritative_missing_feature_cannot_be_injected(client, supplied):
    body=Case().model_dump();body.pop('application_completeness_score')
    if supplied != 'omitted':body['application_completeness_score']=supplied
    r=client.post('/api/applications',json=body)
    assert r.status_code==201
    assert r.json()['payload'].get('application_completeness_score') is None
    with Session() as db:
        payload=json.loads(db.get(Application,r.json()['id']).payload)
        assert payload['application_completeness_score'] is None
    assert r.json()['documents']['percentage']==100


def test_no_prediction_imputation_shap_or_sandbox_for_incompatible_input(client,monkeypatch):
    aid=client.post('/api/applications',json=Case().model_dump()).json()['id']
    def forbidden(*_):raise AssertionError('Must not invoke the saved model or SHAP for incompatible inputs')
    monkeypatch.setattr(backend,'predict',forbidden);monkeypatch.setattr(backend,'explain',forbidden)
    a=client.post(f'/api/applications/{aid}/assess').json()
    assert a['score'] is None and a['classification'] is None and a['requires_review']
    assert a['failure']=='InputCompatibilityUnavailable'
    assert not a['input_validation']['imputed_features']
    assert client.get(f'/api/applications/{aid}/explanation').status_code==409
    result=client.post('/api/sandbox/compare',json={'application_id':aid,'field':'conflicting_information','value':1}).json()
    for k in ['before','after']:
        assert result[k]['prediction']['score'] is None and result[k]['explanation'] is None


def test_injected_score_changes_do_not_create_retry_duplicates(client):
    h={'X-Sandbox-Session':str(uuid.uuid4()),'Idempotency-Key':str(uuid.uuid4())}
    body=Case().model_dump();first=client.post('/api/applications',json=body|{'application_completeness_score':1},headers=h)
    for value in [95,100,None]:
        r=client.post('/api/applications',json=body|{'application_completeness_score':value},headers=h)
        assert r.status_code==201 and r.json()['id']==first.json()['id'] and r.headers['Idempotency-Replayed']=='true'
    assert len(client.get('/api/applications/'+first.json()['id']).json()['history'])==1


def test_pre_upgrade_retry_retains_saved_features_and_assessment(client,historical_case):
    aid=historical_case(Case().model_dump());old=client.get('/api/applications/'+aid).json()
    payload=old['payload'];h={'X-Sandbox-Session':str(uuid.uuid4()),'Idempotency-Key':str(uuid.uuid4())}
    key=hashlib.sha256(f"{h['X-Sandbox-Session']}:{h['Idempotency-Key']}".encode()).hexdigest()
    digest=hashlib.sha256(json.dumps(Case.model_validate(payload).model_dump(),sort_keys=True,separators=(',',':')).encode()).hexdigest()
    with Session() as db:
        db.add(SubmissionRequest(key_hash=key,payload_hash=digest,application_id=aid));db.commit()
    response=client.post('/api/applications',json=payload,headers=h)
    assert response.status_code==201 and response.json()['id']==aid
    assert response.headers['Idempotency-Replayed']=='true'
    assert response.json()['payload']==payload
    assert client.post('/api/applications',json=payload|{'household_size':12},headers=h).status_code==409
    a=client.post(f'/api/applications/{aid}/assess').json()
    assert a['score'] is not None
    shap=client.get(f'/api/applications/{aid}/explanation').json()
    assert abs(shap['score']-a['score'])<1e-12 and shap['additivity_error']<1e-6
