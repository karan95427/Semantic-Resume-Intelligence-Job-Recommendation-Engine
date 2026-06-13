from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


_PROJECT_DIR = Path(__file__).resolve().parents[2]
_BACKEND_DIR = Path(__file__).resolve().parents[1]
_ENV_CANDIDATES = (
    _PROJECT_DIR / ".env",
    _BACKEND_DIR / ".env",
)

_database_url_override: str | None = None
_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def _load_env_file() -> None:
    for env_path in _ENV_CANDIDATES:
        if not env_path.exists():
            continue

        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def get_database_url() -> str:
    if _database_url_override:
        return _database_url_override

    _load_env_file()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured. Set it in the environment or .env."
        )
    if database_url.startswith("postgresql://"):
        return database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )
    return database_url


def _build_engine(database_url: str) -> Engine:
    connect_args: dict[str, object] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(
        database_url,
        future=True,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = _build_engine(get_database_url())
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autoflush=False,
            autocommit=False,
            future=True,
        )
    return _session_factory


def get_session() -> Session:
    return get_session_factory()()


def init_database() -> None:
    from .models.job import Base

    Base.metadata.create_all(bind=get_engine())


def configure_database(database_url: str) -> None:
    global _database_url_override
    _database_url_override = database_url
    reset_database_state()


def reset_database_state() -> None:
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None
