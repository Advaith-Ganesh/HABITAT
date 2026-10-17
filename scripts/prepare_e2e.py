"""Reset ONLY the disposable E2E database; fresh startup uses independent UI fixtures."""
from ml.common import ROOT
folder = ROOT / '.test-runtime'
folder.mkdir(exist_ok=True)
for suffix in ['', '-wal', '-shm', '-journal']:
    (folder / ('browser.db' + suffix)).unlink(missing_ok=True)
print('Fresh disposable browser DB; no held-out fixture or original database copied.')
