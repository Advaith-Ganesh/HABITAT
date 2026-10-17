"""Independent remediation checks: retry safety, independent seeds, input alignment and local boundaries."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
import stat
import uuid
import numpy as np
import pandas as pd
import pytest
from sqlalchemy.exc import OperationalError
from backend import main as backend
from backend.main import Case, Session, Application, Event, SubmissionRequest, engine
from ml.common import ROOT, FEATURES, EVALUATION_INPUTS
from ml.predict import predict, artifacts
from ml.input_audit import training_profile
from ml.audit_v7 import investigate


def headers(key=None, session=None):
    return {'Idempotency-Key': key or str(uuid.uuid4()), 'X-Sandbox-Session': session or str(uuid.uuid4())}


def test_lost_response_retry_conflict_and_restart(client):
    h=headers(); body=Case().model_dump()
    before=client.get('/api/dashboard').json()['applications']
    first=client.post('/api/applications',json=body,headers=h)
    assert first.status_code == 201 and first.headers['Idempotency-Replayed'] == 'false'
    aid=first.json()['id']  # response could be lost after this database commit
    engine.dispose()
    replay=client.post('/api/applications',json=body,headers=h)
    assert replay.status_code == 201 and replay.json()['id']==aid
    assert replay.headers['Idempotency-Replayed']=='true'
    assert client.get('/api/dashboard').json()['applications']==before+1
    assert len(client.get(f'/api/applications/{aid}').json()['history'])==1
    assert client.post('/api/applications',json=body | {'household_size':4},headers=h).status_code==409
    # Different session namespace and a genuinely new request key are separate submissions.
    assert client.post('/api/applications',json=body,headers=headers(key=h['Idempotency-Key'])).json()['id']!=aid
    assert client.post('/api/applications',json=body,headers=headers(session=h['X-Sandbox-Session'])).json()['id']!=aid


def test_simultaneous_retries_commit_once(client):
    h=headers(); body=Case().model_dump();before=client.get('/api/dashboard').json()['applications']
    with ThreadPoolExecutor(max_workers=8) as pool:
        responses=list(pool.map(lambda _:client.post('/api/applications',json=body,headers=h),range(8)))
    assert all(r.status_code==201 for r in responses)
    assert len({r.json()['id'] for r in responses})==1
    assert sum(r.headers['Idempotency-Replayed']=='false' for r in responses)==1
    assert client.get('/api/dashboard').json()['applications']==before+1


def test_simultaneous_distinct_submissions(client):
    body=Case().model_dump();before=client.get('/api/dashboard').json()['applications']
    with ThreadPoolExecutor(max_workers=4) as pool:
        responses=list(pool.map(lambda _:client.post('/api/applications',json=body,headers=headers()),range(4)))
    assert all(r.status_code==201 for r in responses)
    assert len({r.json()['id'] for r in responses})==4
    assert client.get('/api/dashboard').json()['applications']==before+4


def test_storage_failure_rolls_back_then_same_key_succeeds(client,monkeypatch):
    body=Case().model_dump();h=headers();before=client.get('/api/dashboard').json()['applications']
    original=backend.log
    def unavailable(*args):raise OperationalError('write',{},Exception('controlled storage outage'))
    monkeypatch.setattr(backend,'log',unavailable)
    failed=client.post('/api/applications',json=body,headers=h)
    assert failed.status_code==503 and 'successful' in failed.json()['detail']
    monkeypatch.setattr(backend,'log',original)
    assert client.get('/api/dashboard').json()['applications']==before
    created=client.post('/api/applications',json=body,headers=h)
    assert created.status_code==201 and created.headers['Idempotency-Replayed']=='false'
    assert client.post('/api/applications',json=body,headers=h).json()['id']==created.json()['id']


def test_invalid_data_does_not_reserve_key(client):
    h=headers();body=Case().model_dump()
    assert client.post('/api/applications',json=body|{'monthly_income':-1},headers=h).status_code==422
    assert client.post('/api/applications',json={},headers=h).status_code==422
    assert client.post('/api/applications',json=body,headers=h).headers['Idempotency-Replayed']=='false'
    assert client.post('/api/applications',json=body,headers=headers(key='invalid')).status_code==422


def test_independent_ui_scenarios_not_evaluation_fixtures(client):
    rows=json.loads((ROOT/'data/demo/applications.json').read_text())
    assert len(rows)==12 and len({r['id'] for r in rows})==12
    source=pd.read_csv(ROOT/'data/public/habitat_synthetic_2000.csv')
    pairs=pd.read_csv(ROOT/'data/public/counterfactual_400.csv')
    fixture=pd.DataFrame([r['payload'] for r in rows])
    assert not set(r['id'] for r in rows)&set(source.application_id)
    for other in [source,pairs]:
        assert not set(map(tuple,fixture[FEATURES].values)) & set(map(tuple,other[FEATURES].values))
    assert all('case_review_required' not in row['payload'] for row in rows)
    case=client.get('/api/applications/DEMO-SEED-001').json()
    assert 'Independent hand-authored' in case['history'][0]['detail']['provenance']
    assert case['assessment']['score']==predict(case['payload'])['score']


def test_training_input_audit_and_ood_handoff():
    pipe,cfg=artifacts();profile=training_profile()
    assert profile['feature_order']==list(pipe.feature_names_in_)==FEATURES
    for change in [{'application_completeness_score':0},{'housing_situation':'new_category'},{'application_completeness_score':None}]:
        body=Case().model_dump()|change
        result=predict(body)
        assert result['score'] is not None and result['requires_review']
        assert result['input_validation']['out_of_distribution']
        assert result['input_validation']['warnings']
        np.testing.assert_allclose(result['score'],pipe.predict_proba(pd.DataFrame([body])[FEATURES])[0,1],rtol=0,atol=0)
    assert predict(Case().model_dump())['input_validation']['warnings']==[]
    assert predict({})['score'] is None


def test_fairness_investigation_counts_and_preserved_artifacts(client):
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in EVALUATION_INPUTS}
    result=client.get('/api/audit/investigation').json()
    assert [g['false_negative_count'] for g in result['groups']]==[14,3,9]
    assert [g['routing_missed_positive_count'] for g in result['groups']]==[9,1,2]
    assert sum(g['extra_review_count'] for g in result['groups'])==172
    assert result['input_consistency']['encoding_feature_order_verified']
    assert result['input_consistency']['training_numeric_medians_match_fitted_imputer']
    assert result['paired_warning']=='Identical paired predictions do not establish absence of proxy discrimination.'
    assert hashes=={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in EVALUATION_INPUTS}


def test_local_only_security_boundaries(client):
    assert client.get('/health',headers={'Host':'public.example'}).status_code==400
    bad=client.options('/api/applications',headers={'Origin':'https://public.example','Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'idempotency-key'})
    assert 'access-control-allow-origin' not in bad.headers
    good=client.options('/api/applications',headers={'Origin':'http://127.0.0.1:5173','Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'idempotency-key,x-sandbox-session,content-type'})
    assert good.status_code==200
    if os.name=='posix':assert stat.S_IMODE(os.stat(engine.url.database).st_mode)==0o600
    # Deliberately unauthenticated local actions remain a disclosed limitation.
    assert client.get('/api/applications').status_code==200
    assert '127.0.0.1' in (ROOT/'scripts/start_backend.sh').read_text()
