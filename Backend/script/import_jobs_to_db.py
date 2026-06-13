from __future__ import annotations

import json
from pathlib import Path
import sys


PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from Backend.app.db import init_database
from Backend.app.repositories.job_repository import import_jobs


BACKEND_DIR = Path(__file__).resolve().parent.parent
JOBS_FILE = BACKEND_DIR / "data" / "jobs" / "jobs.json"


def load_jobs_file(path: Path = JOBS_FILE) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("jobs.json must contain a list of jobs")
    return payload


def main() -> None:
    init_database()
    jobs = load_jobs_file()
    imported_count = import_jobs(jobs)
    print(f"Imported {imported_count} jobs into PostgreSQL from {JOBS_FILE}.")


if __name__ == "__main__":
    main()
