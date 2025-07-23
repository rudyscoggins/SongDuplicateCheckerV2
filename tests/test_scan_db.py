import os
import sys
import sqlite3
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sdc.database import open_db, scan_to_db




def test_scan_to_db_inserts_files(tmp_path):
    db = tmp_path / "test.db"
    engine = open_db(db)
    (tmp_path / "sub").mkdir()
    f1 = tmp_path / "a.mp3"
    f2 = tmp_path / "sub" / "b.flac"
    for f in (f1, f2):
        f.write_text("x")
    scan_to_db(tmp_path, engine)
    with sqlite3.connect(db) as conn:
        rows = sorted(r[0] for r in conn.execute("SELECT path FROM track"))
    assert rows == [str(f1), str(f2)]


def test_scan_to_db_is_idempotent(tmp_path):
    db = tmp_path / "test.db"
    engine = open_db(db)
    f = tmp_path / "song.mp3"
    f.write_text("x")
    scan_to_db(tmp_path, engine)
    scan_to_db(tmp_path, engine)
    with sqlite3.connect(db) as conn:
        rows = list(conn.execute("SELECT path FROM track"))
    assert len(rows) == 1
