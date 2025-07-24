import os
import sys
from pathlib import Path

import pytest

# Ensure src is importable for all tests
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

@pytest.fixture
def mp3_file(tmp_path):
    path = tmp_path / "test.mp3"
    path.write_bytes(b"mp3")
    return path

@pytest.fixture
def flac_file(tmp_path):
    path = tmp_path / "test.flac"
    path.write_bytes(b"flac")
    return path

@pytest.fixture
def mock_fingerprinter(monkeypatch):
    def apply(value=123):
        monkeypatch.setattr("audio.fingerprint", lambda p: value)
        monkeypatch.setattr("duplicate_finder.fingerprint", lambda p: value)
        return value
    apply()
    return apply
