import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sdc.database import open_db, scan_to_db, Session
from duplicate_finder import find_duplicates, DuplicateGroup
import audio


def test_find_duplicates_detects_copies(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    engine = open_db(db)
    song_dir = tmp_path / "music"
    song_dir.mkdir()
    f1 = song_dir / "song1.m4a"
    f2 = song_dir / "copy" / "song1.m4a"
    f2.parent.mkdir()
    f1.write_text("x")
    f2.write_text("x")

    # Monkeypatch fingerprint to avoid ffmpeg dependency
    monkeypatch.setattr(audio, "fingerprint", lambda p: 123)

    scan_to_db(tmp_path, engine)

    with Session(engine) as session:
        groups = find_duplicates(session)

    assert groups == [DuplicateGroup(files=sorted([str(f1), str(f2)]))]
