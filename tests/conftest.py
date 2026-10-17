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
