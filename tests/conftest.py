import os
from pathlib import Path
import tempfile

# API tests use their own SQLite database, never the demo workspace.
_tmp = tempfile.TemporaryDirectory(prefix="habitat-tests-")
os.environ["HABITAT_DATABASE_URL"] = "sqlite:///" + str(Path(_tmp.name) / "test.db")
import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def historical_case(client):
    """Stored pre-V7.1 record for regression tests of genuine legacy RF/SHAP.
    Inserts only into the isolated test DB; never a trusted-input production API.
    """
    import json
    import uuid
    from backend.main import Application, Session, log
    from ml.common import ROOT
    def create(payload):
        payload = dict(payload)
        if payload.get('application_completeness_score') is None:
            payload['application_completeness_score'] = json.loads((ROOT/'data/demo/applications.json').read_text())[0]['payload']['application_completeness_score']
        aid = 'HAB-LEGACY-' + uuid.uuid4().hex[:8]
        with Session() as db:
            db.add(Application(id=aid,payload=json.dumps(payload),status='unassessed'))
            db.flush();log(db,aid,'submitted',{'synthetic_only':True});db.commit()
        return aid
    return create
