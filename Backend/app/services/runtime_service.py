from __future__ import annotations

from fastapi import HTTPException

from ..db import init_database
from ..runtime_state import backend_runtime_state
from .faiss_service import ensure_faiss_index
from .recommendation_service import load_jobs


def warmup_backend_dependencies() -> None:
    try:
        init_database()
        backend_runtime_state.mark_database_ready()
    except Exception as exc:
        backend_runtime_state.mark_failure(
            stage="database",
            message=str(exc) or exc.__class__.__name__,
        )
        return

    try:
        jobs = load_jobs()
        ensure_faiss_index(jobs)
        backend_runtime_state.mark_index_ready(len(jobs))
        backend_runtime_state.mark_ready()
    except Exception as exc:
        backend_runtime_state.mark_failure(
            stage="index",
            message=str(exc) or exc.__class__.__name__,
            preserve_database=True,
        )


def trigger_backend_warmup() -> None:
    backend_runtime_state.start_warmup(warmup_backend_dependencies)


def get_backend_status() -> dict:
    return backend_runtime_state.snapshot()


def ensure_backend_ready() -> None:
    trigger_backend_warmup()

    if backend_runtime_state.is_ready():
        return

    snapshot = backend_runtime_state.snapshot()
    raise HTTPException(
        status_code=503,
        detail=snapshot["message"],
    )
