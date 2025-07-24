import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sdc.database import open_db, scan_to_db, Session
from duplicate_finder import find_duplicates, DuplicateGroup, calculate_score
import audio


def test_find_duplicates_detects_copies(tmp_path, mock_fingerprinter):
    db = tmp_path / "test.db"
    engine = open_db(db)
    song_dir = tmp_path / "music"
    song_dir.mkdir()
    f1 = song_dir / "song1.m4a"
    f2 = song_dir / "copy" / "song1.m4a"
    f2.parent.mkdir()
    f1.write_text("x")
    f2.write_text("x")


    scan_to_db(tmp_path, engine)

    with Session(engine) as session:
        groups = find_duplicates(session)

    assert len(groups) == 1
    g = groups[0]
    assert g.files == sorted([str(f1), str(f2)])
    assert g.score >= 0.8


def test_calculate_score_low_for_different_songs(tmp_path):
    f1 = tmp_path / "a" / "song1.m4a"
    f2 = tmp_path / "b" / "song2.m4a"
    f1.parent.mkdir(parents=True, exist_ok=True)
    f2.parent.mkdir(parents=True, exist_ok=True)
    fps = [123, 456]
    score = calculate_score([str(f1), str(f2)], fps)
    assert score < 0.7
