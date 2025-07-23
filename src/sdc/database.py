"""Database utilities for the ``sdc`` package."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator, Optional

import sqlite3

from .scanner import yield_audio_files
from hash import path_hash

try:  # pragma: no cover - when ``sqlmodel`` is installed
    from sqlalchemy import MetaData
    from sqlmodel import SQLModel, Field, Session, create_engine

    metadata_obj = MetaData()

    def orm_model(cls):
        return cls
except Exception:  # pragma: no cover - allow running without dependency
    from dataclasses import dataclass, field
    from types import SimpleNamespace

    class SQLModel:  # type: ignore
        def __init_subclass__(cls, **kwargs):
            return super().__init_subclass__()

    def Field(default=None, primary_key=False):  # type: ignore
        return field(default=default)

    def create_engine(url: str, echo: bool = False):  # type: ignore
        return SimpleNamespace(url=url)

    class Session:  # type: ignore
        def __init__(self, engine):
            self.engine = engine
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            pass

    metadata_obj = None

    def orm_model(cls):
        return dataclass(cls)


@orm_model
class Track(SQLModel, table=True, metadata=metadata_obj):
    """Minimal track model."""

    __table_args__ = {"extend_existing": True}

    path: str
    path_hash: str
    id: Optional[int] = Field(default=None, primary_key=True)


def open_db(db_path: str | Path = "sdc.db") -> object:
    """Return an engine connected to ``db_path``.

    The database and tables are created if needed.
    """
    engine = create_engine(f"sqlite:///{Path(db_path)}")
    try:
        if metadata_obj is not None:
            metadata_obj.create_all(engine)
        else:
            SQLModel.metadata.create_all(engine)
    except Exception:
        pass
    return engine


def scan_to_db(root: str | Path, engine: object) -> None:
    """Insert or update :class:`Track` rows for files under ``root``.

    Parameters
    ----------
    root:
        Directory to scan recursively for audio files.
    engine:
        Database engine returned by :func:`open_db`.
    """

    url = getattr(engine, "url", engine)
    if hasattr(url, "database"):
        db_path = Path(url.database)
    elif isinstance(url, str) and url.startswith("sqlite:///"):
        db_path = Path(url.replace("sqlite:///", ""))
    else:
        db_path = Path(str(url))

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS track ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "path TEXT UNIQUE, "
            "path_hash TEXT"
            ")"
        )
        for file in yield_audio_files(root):
            conn.execute(
                "INSERT OR IGNORE INTO track(path, path_hash) VALUES (?, ?)",
                (
                    str(file),
                    path_hash(Path(file).relative_to(root)),
                ),
            )
        conn.commit()


__all__ = ["open_db", "scan_to_db", "Track"]
