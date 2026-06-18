from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock, Thread
from typing import Any, Callable


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class BackendRuntimeState:
    def __init__(self) -> None:
        self._lock = Lock()
        self._warmup_started_at: str | None = None
        self._warmup_completed_at: str | None = None
        self._warmup_in_progress = False
        self._warmup_attempts = 0
        self._db_ready = False
        self._index_ready = False
        self._jobs_loaded = 0
        self._last_error: dict[str, str] | None = None

    def start_warmup(self, worker: Callable[[], None]) -> bool:
        with self._lock:
            if self._warmup_in_progress or self._is_ready_unlocked():
                return False

            self._warmup_in_progress = True
            self._warmup_started_at = _utc_now()
            self._warmup_attempts += 1
            self._last_error = None

        thread = Thread(target=self._run_worker, args=(worker,), daemon=True)
        thread.start()
        return True

    def _run_worker(self, worker: Callable[[], None]) -> None:
        try:
            worker()
        except Exception as exc:  # pragma: no cover - defensive guard
            self.mark_failure(
                stage="runtime",
                message=str(exc) or exc.__class__.__name__,
            )

    def mark_database_ready(self) -> None:
        with self._lock:
            self._db_ready = True

    def mark_index_ready(self, jobs_loaded: int) -> None:
        with self._lock:
            self._index_ready = True
            self._jobs_loaded = jobs_loaded

    def mark_ready(self) -> None:
        with self._lock:
            self._warmup_in_progress = False
            self._warmup_completed_at = _utc_now()
            self._last_error = None

    def mark_failure(self, stage: str, message: str, preserve_database: bool = False) -> None:
        with self._lock:
            self._warmup_in_progress = False
            self._warmup_completed_at = None
            self._db_ready = self._db_ready if preserve_database else False
            self._index_ready = False
            self._jobs_loaded = 0
            self._last_error = {
                "stage": stage,
                "message": message,
                "at": _utc_now(),
            }

    def is_ready(self) -> bool:
        with self._lock:
            return self._is_ready_unlocked()

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            ready = self._is_ready_unlocked()
            status = "ready" if ready else "warming" if self._warmup_in_progress else "degraded"
            message = "Backend is ready."
            if not ready and self._warmup_in_progress:
                message = "Backend warmup is in progress."
            elif not ready and self._last_error:
                message = self._last_error["message"]
            elif not ready:
                message = "Backend warmup has not completed yet."

            return {
                "status": status,
                "ready": ready,
                "db_ready": self._db_ready,
                "index_ready": self._index_ready,
                "jobs_loaded": self._jobs_loaded,
                "warmup_in_progress": self._warmup_in_progress,
                "warmup_attempts": self._warmup_attempts,
                "warmup_started_at": self._warmup_started_at,
                "warmup_completed_at": self._warmup_completed_at,
                "last_error": self._last_error,
                "message": message,
            }

    def _is_ready_unlocked(self) -> bool:
        return self._db_ready and self._index_ready


backend_runtime_state = BackendRuntimeState()
