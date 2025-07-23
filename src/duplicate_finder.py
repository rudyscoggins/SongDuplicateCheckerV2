from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List
import sqlite3
from difflib import SequenceMatcher

from audio import fingerprint
from heuristics import FP_WEIGHT, TAG_WEIGHT, FUZZY_WEIGHT


@dataclass
class DuplicateGroup:
    """Collection of files considered duplicates."""

    files: List[str]
    score: float

    @property
    def is_confident(self) -> bool:
        """Return ``True`` when ``score`` meets the duplicate threshold."""
        return self.score >= 0.8


def _get_db_path(session: object) -> Path:
    """Return the SQLite database path for ``session`` or ``engine``."""
    engine = getattr(session, "engine", None)
    if engine is None and hasattr(session, "get_bind"):
        engine = session.get_bind()
    if engine is None:
        engine = session
    url = getattr(engine, "url", engine)
    if hasattr(url, "database"):
        return Path(url.database)
    if isinstance(url, str) and url.startswith("sqlite:///"):
        return Path(url.replace("sqlite:///", ""))
    return Path(str(url))


def _extract_tags(path: str | Path) -> tuple[str, str, str]:
    """Return ``artist``, ``album`` and ``title`` extracted from ``path``."""
    p = Path(path)
    artist = p.parents[1].name if len(p.parents) > 1 else ""
    album = p.parent.name
    title = p.stem
    return artist.lower(), album.lower(), title.lower()


def _score_pair(p1: str, p2: str, fp1: int, fp2: int) -> float:
    """Return similarity score for two tracks."""
    diff = bin(fp1 ^ fp2).count("1")
    fp_sim = 1.0 - diff / 32.0
    a1, alb1, t1 = _extract_tags(p1)
    a2, alb2, t2 = _extract_tags(p2)
    tag_sim = 1.0 if (a1 == a2 and alb1 == alb2 and t1 == t2) else 0.0
    fuzzy_sim = SequenceMatcher(None, t1, t2).ratio()
    return FP_WEIGHT * fp_sim + TAG_WEIGHT * tag_sim + FUZZY_WEIGHT * fuzzy_sim


def calculate_score(paths: List[str], fps: List[int]) -> float:
    """Return average pairwise similarity for ``paths``."""
    n = len(paths)
    if n < 2:
        return 0.0
    total = 0.0
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            total += _score_pair(paths[i], paths[j], fps[i], fps[j])
            count += 1
    return round(total / count, 4) if count else 0.0


def find_duplicates(session: object) -> List[DuplicateGroup]:
    """Return groups of files with matching audio fingerprints."""
    db_path = _get_db_path(session)
    with sqlite3.connect(db_path) as conn:
        rows = list(conn.execute("SELECT path FROM track"))
    by_fp: dict[int, List[tuple[str, int]]] = {}
    for (path,) in rows:
        try:
            fp = fingerprint(path)
        except Exception:
            fp = 0
        by_fp.setdefault(fp, []).append((path, fp))

    groups: List[DuplicateGroup] = []
    for entries in by_fp.values():
        if len(entries) <= 1:
            continue
        files = [p for p, _ in entries]
        fps = [fp for _, fp in entries]
        score = calculate_score(files, fps)
        if score >= 0.8:
            groups.append(DuplicateGroup(sorted(files), score))

    groups.sort(key=lambda g: g.files)
    return groups

__all__ = ["DuplicateGroup", "find_duplicates", "calculate_score"]
