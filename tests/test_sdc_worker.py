import os
import sys
import time
import sqlite3
from pathlib import Path
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sdc.worker import start_scan, get_status, _db_path
from sdc.database import open_db


def wait_done(job_id, engine):
    for _ in range(100):
        status = get_status(job_id, engine)
        if status["status"] == "done":
            return status
        time.sleep(0.01)
    return status


def test_start_scan_adds_tracks(tmp_path, mp3_file, flac_file):
    engine = open_db(tmp_path / "db.sqlite")
    job_id = start_scan(tmp_path, engine)
    status = wait_done(job_id, engine)
    assert status["done"] == 2
    assert status["total"] == 2
    db_path = _db_path(engine)
    with sqlite3.connect(db_path) as conn:
        rows = {row[0] for row in conn.execute("SELECT path FROM track")}
    assert rows == {str(mp3_file), str(flac_file)}


def test_get_status_missing_job(tmp_path):
    engine = open_db(tmp_path / "db.sqlite")
    with pytest.raises(ValueError):
        get_status(999, engine)
