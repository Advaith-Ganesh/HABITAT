"""Prepare a disposable browser-test clone; never alter the original demo database."""

import sqlite3
from ml.common import ROOT

folder = ROOT / ".test-runtime"
folder.mkdir(exist_ok=True)
target = folder / "browser.db"
for suffix in ["", "-wal", "-shm"]:
    p = folder / ("browser.db" + suffix)
    if p.exists():
        p.unlink()
source = ROOT / "habitat.db"
if source.exists():
    with sqlite3.connect(source) as original, sqlite3.connect(target) as copy:
        original.backup(copy)
print("Disposable browser database ready; original workspace preserved.")
