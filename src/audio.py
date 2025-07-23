from __future__ import annotations

from pathlib import Path

from pydub import AudioSegment
import numpy as np


def _dct(x: np.ndarray) -> np.ndarray:
    """Return a DCT-II transform of ``x`` using FFT."""
    N = len(x)
    if N == 0:
        return np.array([])
    y = np.concatenate([x, x[::-1]])
    Y = np.fft.fft(y)
    factor = np.exp(-1j * np.pi * np.arange(N) / (2 * N))
    return np.real(Y[:N] * factor)


def fingerprint(path: str | Path) -> int:
    """Return a 32-bit perceptual hash for an audio file."""
    audio = AudioSegment.from_file(path)
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(8000)
    if len(audio) > 30000:
        audio = audio[:30000]
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
    if samples.size == 0:
        return 0
    samples -= samples.mean()
    if np.max(np.abs(samples)):
        samples /= np.max(np.abs(samples))
    spec = np.abs(np.fft.rfft(samples))
    spec = spec[:64]
    coeffs = _dct(spec)
    coeffs = coeffs[1:33]
    med = np.median(coeffs)
    bits = coeffs > med
    value = 0
    for bit in bits:
        value = (value << 1) | int(bit)
    return value & 0xFFFFFFFF


__all__ = ["fingerprint"]

