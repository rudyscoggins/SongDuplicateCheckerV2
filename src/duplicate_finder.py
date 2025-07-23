from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List
import sqlite3

from audio import fingerprint


@dataclass
class DuplicateGroup:
    """Collection of files considered duplicates."""

    files: List[str]


def _get_db_path(session: object) -> Path:
    """Return the SQLite database path for ``session`` or ``engine``."""
    engine = getattr(session, "engine", session)
    url = getattr(engine, "url", engine)
    if hasattr(url, "database"):
        return Path(url.database)
    if isinstance(url, str) and url.startswith("sqlite:///"):
        return Path(url.replace("sqlite:///", ""))
    return Path(str(url))


def find_duplicates(session: object) -> List[DuplicateGroup]:
    """Return groups of files with matching audio fingerprints."""
    db_path = _get_db_path(session)
    with sqlite3.connect(db_path) as conn:
        rows = list(conn.execute("SELECT path FROM track"))
    fps: dict[int, List[str]] = {}
    for (path,) in rows:
        try:
            fp = fingerprint(path)
        except Exception:
            fp = 0
        fps.setdefault(fp, []).append(path)

    groups = [DuplicateGroup(sorted(paths)) for paths in fps.values() if len(paths) > 1]
    groups.sort(key=lambda g: g.files)
    return groups

__all__ = ["DuplicateGroup", "find_duplicates"]
