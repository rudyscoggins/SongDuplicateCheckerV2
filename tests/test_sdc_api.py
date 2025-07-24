import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi.testclient import TestClient
import sdc.api as api
from duplicate_finder import DuplicateGroup

client = TestClient(api.app)

def test_duplicates_endpoint(monkeypatch):
    monkeypatch.setattr(api, "open_db", lambda: None)
    class DummySession:
        def __init__(self, engine):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            pass
    monkeypatch.setattr(api, "Session", DummySession)
    group = DuplicateGroup(files=["/a.mp3", "/b.mp3"], score=0.95)
    monkeypatch.setattr(api, "find_duplicates", lambda session: [group])

    class DummyInfo:
        title = "T"
        artist = "A"
        album = "AL"
        length = 1.0
        bitrate = 256

    monkeypatch.setattr(api, "read_media_info", lambda p: DummyInfo())
    resp = client.get("/duplicates")
    assert resp == {
        "groups": [
            {
                "files": [
                    {
                        "path": "/a.mp3",
                        "title": 'T',
                        "artist": 'A',
                        "album": 'AL',
                        "length": 1.0,
                        "bitrate": 256,
                    },
                    {
                        "path": "/b.mp3",
                        "title": 'T',
                        "artist": 'A',
                        "album": 'AL',
                        "length": 1.0,
                        "bitrate": 256,
                    },
                ],
                "confidence": 0.95,
            }
        ]
    }
