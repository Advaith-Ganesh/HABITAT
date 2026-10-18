"""Real PDFs, subprocess parser, SQLite association and append-only human review."""
from io import BytesIO
import json
from pathlib import Path
import uuid
import pytest
from reportlab.pdfgen import canvas
from backend.main import Case, Session, EvidenceDocument, Application, engine
from backend.document_analysis import analyse, MAX_BYTES
from backend.document_service import process_pdf

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'evidence_benchmark'

def headers():return {'X-Sandbox-Session':str(uuid.uuid4()),'X-Synthetic-Only':'true','Content-Type':'application/pdf'}
def upload(client,name='dev/dev-income.pdf',h=None,category='income'):
    return client.post('/api/evidence/analyse?category='+category,content=(FIX/name).read_bytes(),headers=h or headers())


def test_real_pdf_grounding_and_scoped_human_review(client):
    h=headers();r=upload(client,h=h);assert r.status_code==201
    document=r.json();a=document['analysis'];eid=document['id']
    assert a['detected_category']=='income' and a['readable'] and not a['abstained']
    assert a['human_handoff'] and not document['raw_pdf_retained']
    assert {o['field'] for o in a['observations']}=={'employer','pay_period','gross_pay'}
    for o in a['observations']:
        assert o['value'] in o['excerpt'] and o['excerpt'] in a['pages'][o['page']-1]['text']
    assert client.get('/api/evidence/'+eid,headers=headers()).status_code==404
    key=str(uuid.uuid4());body=Case().model_dump()|{'evidence_ids':[eid],'safe_to_stay_tonight':'no'}
    postheaders={'X-Sandbox-Session':h['X-Sandbox-Session'],'Idempotency-Key':key}
    first=client.post('/api/applications',json=body,headers=postheaders);assert first.status_code==201
    aid=first.json()['id']
    assert client.post('/api/applications',json=body,headers=postheaders).json()['id']==aid
    assert client.post('/api/applications',json=body,headers={'X-Sandbox-Session':h['X-Sandbox-Session']}).status_code==409
    observations=a['observations'];obs=observations[0]['id']
    for action in ['confirm','correct','insufficient','request_clarification','escalate']:
        review={'action':action,'observation_id':obs if action in ['confirm','correct'] else None,'corrected_value':'SIM-ORG-CORRECTION' if action=='correct' else None,'reason':'Synthetic caseworker reviewed the extracted source; authenticity is not established.'}
        response=client.post(f'/api/evidence/{eid}/review',json=review);assert response.status_code==200
    assert client.post(f'/api/evidence/{eid}/review',json={'action':'confirm','observation_id':'invented','reason':'Synthetic review reason'}).status_code==422
    engine.dispose()
    saved=client.get(f'/api/applications/{aid}/evidence').json()[0]
    assert len(saved['reviews'])==5 and saved['analysis']==a
    record=client.get('/api/applications/'+aid).json()
    assert record['status']=='unassessed' and len(record['history'])==6
    assessed=client.post(f'/api/applications/{aid}/assess').json()
    assert assessed['score'] is None and assessed['failure']=='InputCompatibilityUnavailable'
    with Session() as db:
        assert db.get(EvidenceDocument,eid).application_id==aid
        assert json.loads(db.get(Application,aid).payload)['income_document_available']==1
        assert 'pdf' not in {c.name.lower() for c in EvidenceDocument.__table__.columns}


@pytest.mark.parametrize('name',['security/encrypted.pdf','security/corrupt.pdf','security/six-pages.pdf'])
def test_real_invalid_pdf_rejected_without_persistence(client,name):
    with Session() as db:before=db.query(EvidenceDocument).count()
    r=upload(client,name);assert r.status_code==422 and 'PDF rejected' in r.json()['detail']
    with Session() as db:assert db.query(EvidenceDocument).count()==before


def test_byte_limits_media_type_and_synthetic_gate(client):
    h=headers();data=(FIX/'dev/dev-income.pdf').read_bytes()
    assert client.post('/api/evidence/analyse?category=income',content=data,headers=h|{'Content-Type':'text/plain'}).status_code==415
    assert client.post('/api/evidence/analyse?category=income',content=data,headers=h|{'X-Synthetic-Only':'false'}).status_code==422
    assert client.post('/api/evidence/analyse?category=income',content=b'%PDF-'+b'x'*MAX_BYTES,headers=h).status_code==413
    output=BytesIO();c=canvas.Canvas(output,invariant=1);c.drawString(50,700,'Unmarked document with readable information.');c.save()
    assert client.post('/api/evidence/analyse?category=income',content=output.getvalue(),headers=h).status_code==422
    assert client.post('/api/evidence/analyse?category=income',content=b'not pdf',headers=h).status_code==422


@pytest.mark.parametrize('name,issue',[('dev-blank','unreadable'),('dev-injection','prompt_injection'),('dev-missing','missing_fields')])
def test_real_failures_abstain_and_do_not_make_housing_decisions(client,name,issue):
    r=upload(client,'dev/'+name+'.pdf');assert r.status_code==201
    a=r.json()['analysis'];assert issue in a['issues'] and a['abstained'] and a['human_handoff']
    assert 'eligibility' not in a and 'approved' not in a and 'model_score' not in a
    if issue=='unreadable':assert a['status']=='Insufficient readable evidence' and not a['observations']


def test_page_two_conflict_and_ambiguity_are_genuine():
    for name,expected in [('heldout-10','conflicting_values'),('heldout-13','ambiguous_values')]:
        a=process_pdf((FIX/'heldout'/f'{name}.pdf').read_bytes(),'income')
        assert expected in a['issues']
    two=process_pdf((FIX/'heldout/heldout-19.pdf').read_bytes(),'income')
    assert {o['page'] for o in two['observations']}=={1,2}


def test_heldout_manifest_and_recorded_report_match_actual_results():
    m=json.loads((FIX/'manifest.json').read_text());report=json.loads((ROOT/'reports/document_assurance.json').read_text())
    assert len(m['heldout'])==24 and len(m['development'])==6
    assert not {x['document_id'] for x in m['heldout']} & {x['document_id'] for x in m['development']}
    for method,baseline in [('baseline',True),('structured',False)]:
        recorded={x['document_id']:x for x in report[method]['documents']}
        correct=0
        for truth in m['heldout']:
            data=(FIX/truth['path']).read_bytes();actual=analyse(data,truth['claimed_category'],baseline).model_dump()
            expected=recorded[truth['document_id']]['result']
            expected={**expected,'processing_ms':0}
            assert actual==expected
            correct+=actual['detected_category']==truth['expected_category']
        assert correct==report[method]['correct_classifications']


def test_worker_timeout_and_capacity_failure_are_clear(monkeypatch):
    import subprocess
    from backend import document_service as s
    def timeout(*args,**kwargs):raise subprocess.TimeoutExpired('parser',6)
    monkeypatch.setattr(s.subprocess,'run',timeout)
    with pytest.raises(ValueError,match='resource limits'):s.process_pdf(b'%PDF-','income')
    assert s._slots.acquire(False) and s._slots.acquire(False)
    try:
        with pytest.raises(RuntimeError,match='busy'):s.process_pdf(b'%PDF-','income')
    finally:s._slots.release();s._slots.release()
