from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class MediaInfo:
    """Simple container for basic audio metadata."""

    title: str
    artist: str
    album: str
    length: float
    bitrate: int


def _get_first(value: Any) -> str | None:
    """Return the first element from a tag value."""
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return str(value[0]) if value else None
    if hasattr(value, "text"):
        text = value.text
        if isinstance(text, list):
            return str(text[0]) if text else None
        return str(text)
    return str(value)


def read_media_info(path: str | Path) -> MediaInfo:
    """Return :class:`MediaInfo` for ``path`` using mutagen when available."""

    filepath = Path(path)
    title = filepath.stem
    album = filepath.parent.name
    artist = filepath.parents[1].name if len(filepath.parents) > 1 else ""
    length = 0.0
    bitrate = 0

    try:
        from mutagen import File as MutagenFile  # type: ignore
    except Exception:
        MutagenFile = None

    if MutagenFile is not None:
        try:
            audio = MutagenFile(filepath)
        except Exception:
            audio = None
        if audio is not None:
            tags = getattr(audio, "tags", None)
            if tags:
                title = _get_first(tags.get("title")) or title
                artist = _get_first(tags.get("artist")) or artist
                album = _get_first(tags.get("album")) or album
            info = getattr(audio, "info", None)
            if info is not None:
                length = getattr(info, "length", length)
                br = getattr(info, "bitrate", None)
                if br:
                    bitrate = int(br / 1000)

    return MediaInfo(title=title, artist=artist, album=album, length=length, bitrate=bitrate)
