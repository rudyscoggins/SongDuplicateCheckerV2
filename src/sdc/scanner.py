"""Utilities for scanning directories for audio files."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

AUDIO_EXTS: set[str] = {".mp3", ".flac", ".wav", ".m4a"}


def yield_audio_files(root: str | Path) -> Iterator[Path]:
    """Yield audio file paths found under ``root``.

    Only files with extensions listed in :data:`AUDIO_EXTS` are returned. The
    search is recursive and results are yielded in sorted order.
    """
    path = Path(root)
    for p in sorted(path.rglob("*")):
        if p.is_file() and p.suffix.lower() in AUDIO_EXTS:
            yield p


__all__ = ["yield_audio_files", "AUDIO_EXTS"]
