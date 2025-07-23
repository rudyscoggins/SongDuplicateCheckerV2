import types
from pathlib import Path

import numpy as np
from pydub.generators import Sine

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import audio


def test_fingerprint_same_audio(tmp_path, monkeypatch):
    seg = Sine(440).to_audio_segment(duration=1000)
    flac = tmp_path / "test.flac"
    mp3 = tmp_path / "test.mp3"
    flac.touch()
    mp3.touch()

    def fake_from_file(path):
        assert Path(path) in {flac, mp3}
        return seg

    monkeypatch.setattr(audio, "AudioSegment", types.SimpleNamespace(from_file=fake_from_file))

    h1 = audio.fingerprint(flac)
    h2 = audio.fingerprint(mp3)
    diff = bin(h1 ^ h2).count("1")
    assert diff <= 5


