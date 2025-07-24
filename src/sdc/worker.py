# src/sdc/worker.py
"""Background scan runner utilities."""

from __future__ import annotations

import concurrent.futures
import threading
import sqlite3
from pathlib import Path
from typing import Iterable

from .database import open_db, ScanJob
from .scanner import yield_audio_files
from hash import path_hash


def _db_path(engine: object) -> Path:
    url = getattr(engine, "url", engine)
    if hasattr(url, "database"):
        return Path(url.database)
    if isinstance(url, str) and url.startswith("sqlite:///"):
        return Path(url.replace("sqlite:///", ""))
    return Path(str(url))


def _ensure_tables(engine: object) -> None:
    path = _db_path(engine)
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS scan_job ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "root TEXT, "
            "total INTEGER, "
            "done INTEGER, "
            "status TEXT"
            ")"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS track ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "path TEXT UNIQUE, "
            "path_hash TEXT"
            ")"
        )
        conn.commit()


def start_scan(root: str | Path, engine: object | None = None) -> int:
    """Start scanning ``root`` in a background thread.

    Returns the created job id.
    """
    engine = engine or open_db()
    _ensure_tables(engine)
    db_path = _db_path(engine)
    root_path = Path(root)

    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO scan_job(root, total, done, status) VALUES (?, 0, 0, ?)",
            (str(root_path), "running"),
        )
        job_id = cur.lastrowid
        conn.commit()

    def worker(paths: Iterable[Path]):
        total = len(paths)
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "UPDATE scan_job SET total=? WHERE id=?", (total, job_id)
            )
            conn.commit()

        def process(p: Path):
            rel_hash = path_hash(p.relative_to(root_path))
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO track(path, path_hash) VALUES (?, ?)",
                    (str(p), rel_hash),
                )
                conn.execute(
                    "UPDATE scan_job SET done=done+1 WHERE id=?", (job_id,)
                )
                conn.commit()

        with concurrent.futures.ThreadPoolExecutor() as ex:
            list(ex.map(process, paths))
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "UPDATE scan_job SET status='done' WHERE id=?", (job_id,)
            )
            conn.commit()

    paths = list(yield_audio_files(root_path))
    thread = threading.Thread(target=worker, args=(paths,), daemon=True)
    thread.start()
    return job_id


def get_status(job_id: int, engine: object | None = None) -> dict[str, object]:
    """Return progress information for ``job_id``."""
    engine = engine or open_db()
    db_path = _db_path(engine)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, root, total, done, status FROM scan_job WHERE id=?",
            (job_id,),
        ).fetchone()
    if not row:
        raise ValueError("job not found")
    keys = ["id", "root", "total", "done", "status"]
    return dict(zip(keys, row))


__all__ = ["start_scan", "get_status"]
