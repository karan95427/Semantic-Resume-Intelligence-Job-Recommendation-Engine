from __future__ import annotations

import json
from pathlib import Path
from typing import Any


JOBS_DIR = Path(__file__).resolve().parents[2] / "data" / "jobs"
JOB_MAPPING_FILE = JOBS_DIR / "job_mapping.json"


def build_job_mapping(jobs: list[dict]) -> dict[str, Any]:
    return {
        str(index): job.get("id")
        for index, job in enumerate(jobs)
    }


def load_job_mapping() -> dict[str, Any] | None:
    if not JOB_MAPPING_FILE.exists():
        return None

    try:
        payload = json.loads(JOB_MAPPING_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    if not isinstance(payload, dict):
        return None

    mapping: dict[str, Any] = {}
    for key, value in payload.items():
        if not isinstance(key, str):
            return None
        mapping[key] = value

    return mapping


def save_job_mapping(job_mapping: dict[str, Any]) -> None:
    JOB_MAPPING_FILE.parent.mkdir(parents=True, exist_ok=True)
    JOB_MAPPING_FILE.write_text(
        json.dumps(job_mapping, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def ensure_job_mapping(jobs: list[dict]) -> dict[str, Any]:
    expected_mapping = build_job_mapping(jobs)
    current_mapping = load_job_mapping()

    if current_mapping == expected_mapping:
        return current_mapping

    save_job_mapping(expected_mapping)
    return expected_mapping
