import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sdc.database import open_db, Track
from hash import path_hash


def test_open_db_returns_engine(tmp_path):
    db = tmp_path / "test.db"
    engine = open_db(db)
    assert str(db) in str(getattr(engine, "url", engine))


def test_track_model_has_fields():
    t = Track(path="x", path_hash=path_hash("x"))
    assert hasattr(t, "id")
    assert hasattr(t, "path")
    assert hasattr(t, "path_hash")

