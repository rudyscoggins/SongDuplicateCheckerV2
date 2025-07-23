from __future__ import annotations

from hashlib import sha1
from pathlib import Path


def path_hash(path: str | Path) -> str:
    """Return SHA-1 hexdigest of the relative ``path``.

    The function normalizes path separators so that the result is
    platform independent.
    """
    p = Path(path)
    rel = p.as_posix()
    return sha1(rel.encode("utf-8")).hexdigest()


__all__ = ["path_hash"]
