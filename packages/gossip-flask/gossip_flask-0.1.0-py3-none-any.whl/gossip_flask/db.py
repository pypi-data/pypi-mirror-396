from __future__ import annotations

import datetime as dt
import os
from typing import Optional

from sqlalchemy import Column, DateTime, LargeBinary, String, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from gossip_flask import __version__

Base = declarative_base()


class Message(Base):
    """
    The message class for the gossip network
    """
    __tablename__ = "messages"

    id = Column("id", LargeBinary, primary_key=True)
    version = Column("version", String, nullable=False)
    timestamp = Column("timestamp", DateTime, default=dt.datetime.now(), nullable=False)
    # Use JSON type for message field; for SQLite, dialect-specific JSON is used.
    message = Column("message", String, nullable=True)

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<Message id={self.id!r} timestampe={self.timestamp} message={self.message}"


_engine: Optional[Engine] = None
_session_local: Optional[sessionmaker] = None


def _ensure_engine() -> None:
    """Lazily create the engine and sessionmaker singletons."""
    global _engine, _session_local, Base
    if _engine is None or _session_local is None:
        database_url = os.environ.get("DATABASE_URL", "sqlite:///./gossip.db")
        _engine = create_engine(database_url, echo=False, future=True)
        _session_local = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
        Base.metadata.create_all(bind=_engine)


def get_db_session():
    """Return a new SQLAlchemy Session using a lazily-created sessionmaker.

    The engine and sessionmaker are created once and reused for subsequent calls.
    """
    _ensure_engine()
    assert _session_local is not None
    return _session_local()
