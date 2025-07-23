"""Database utilities for the ``sdc`` package."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

try:  # pragma: no cover - when ``sqlmodel`` is installed
    from sqlmodel import SQLModel, Field, Session, create_engine
    
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

    def orm_model(cls):
        return dataclass(cls)


@orm_model
class Track(SQLModel, table=True):
    """Minimal track model."""

    path: str
    id: Optional[int] = Field(default=None, primary_key=True)


def open_db(db_path: str | Path = "sdc.db") -> object:
    """Return an engine connected to ``db_path``.

    The database and tables are created if needed.
    """
    engine = create_engine(f"sqlite:///{Path(db_path)}")
    try:
        SQLModel.metadata.create_all(engine)
    except Exception:
        pass
    return engine


__all__ = ["open_db", "Track"]
