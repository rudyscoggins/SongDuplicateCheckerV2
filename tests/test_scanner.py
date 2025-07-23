import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sdc.scanner import yield_audio_files


def test_yield_audio_files(tmp_path):
    files = [
        tmp_path / "a.mp3",
        tmp_path / "b.flac",
        tmp_path / "sub" / "c.wav",
        tmp_path / "d.txt",
        tmp_path / "e.m4a",
    ]
    (tmp_path / "sub").mkdir()
    for f in files:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x")
    result = list(yield_audio_files(tmp_path))
    expected = [files[0], files[1], files[2], files[4]]
    assert result == sorted(expected)
