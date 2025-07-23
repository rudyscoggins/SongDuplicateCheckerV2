import os
import sys
import types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from songripper.media import read_media_info, MediaInfo


def test_read_media_info_uses_mutagen(monkeypatch, tmp_path):
    class DummyAudio:
        def __init__(self):
            self.tags = {
                "title": ["Title"],
                "artist": ["Artist"],
                "album": ["Album"],
            }
            self.info = types.SimpleNamespace(length=123.4, bitrate=256000)

    def fake_file(path):
        return DummyAudio()

    monkeypatch.setitem(sys.modules, "mutagen", types.SimpleNamespace(File=fake_file))

    p = tmp_path / "song.mp3"
    p.write_text("x")
    info = read_media_info(p)
    assert isinstance(info, MediaInfo)
    assert info.title == "Title"
    assert info.artist == "Artist"
    assert info.album == "Album"
    assert info.length == 123.4
    assert info.bitrate == 256


def test_read_media_info_fallback(monkeypatch, tmp_path):
    def fake_file(path):
        raise RuntimeError("boom")

    monkeypatch.setitem(sys.modules, "mutagen", types.SimpleNamespace(File=fake_file))

    path = tmp_path / "Artist" / "Album" / "Song.mp3"
    path.parent.mkdir(parents=True)
    path.write_text("x")
    info = read_media_info(path)
    assert info.artist == "Artist"
    assert info.album == "Album"
    assert info.title == "Song"
    assert info.length == 0.0
    assert info.bitrate == 0
