import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi.testclient import TestClient
import songripper.api as api

client = TestClient(api.app)


def test_home_returns_first_file(tmp_path, monkeypatch):
    # Create a couple of files and patch NAS_PATH
    (tmp_path / "sub").mkdir()
    first = tmp_path / "a" / f"first{api.AUDIO_EXT}"
    first.parent.mkdir(parents=True, exist_ok=True)
    first.write_text("x")
    second = tmp_path / "sub" / f"second{api.AUDIO_EXT}"
    second.write_text("y")
    monkeypatch.setattr(api, "NAS_PATH", tmp_path)
    resp = client.get("/")
    assert resp.status_code == 200
    assert str(first) in resp.text


def test_home_no_files(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "NAS_PATH", tmp_path)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "No files found" in resp.text
