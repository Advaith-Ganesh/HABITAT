"""Reset the named local sandbox with a recoverable backup; never overwrite habitat.db."""
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from ml.common import ROOT


def main():
    folder = ROOT / '.test-runtime'
    folder.mkdir(exist_ok=True)
    target = folder / 'sandbox.db'
    if target.exists():
        backups = folder / 'backups'
        backups.mkdir(exist_ok=True)
        backup = backups / ('sandbox-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8] + '.db')
        with sqlite3.connect(target) as source, sqlite3.connect(backup) as destination:
            source.backup(destination)
        os.chmod(backup, 0o600)
        print('Recoverable backup:', backup)
    # Run with this sandbox's backend stopped; backup is complete before reset.
    for suffix in ['', '-wal', '-shm', '-journal']:
        (folder / ('sandbox.db' + suffix)).unlink(missing_ok=True)
    os.environ['HABITAT_DATABASE_URL'] = 'sqlite:///' + str(target)
    from backend.main import init
    init()
    print('Independent UI scenarios restored:', target)
    print('Start backend with HABITAT_DATABASE_URL=sqlite:///./.test-runtime/sandbox.db')


if __name__ == '__main__':
    main()
