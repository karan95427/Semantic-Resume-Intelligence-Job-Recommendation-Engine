from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import select

from ..db import get_session
from ..models.job import Job


def _job_to_dict(job: Job) -> dict:
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "description": job.description,
    }


def list_jobs() -> list[dict]:
    with get_session() as session:
        rows = session.execute(
            select(Job).order_by(Job.id.asc())
        ).scalars()
        return [_job_to_dict(job) for job in rows]


def import_jobs(jobs: Iterable[dict]) -> int:
    payload = list(jobs)
    if not payload:
        return 0

    job_ids = [int(job["id"]) for job in payload]

    with get_session() as session:
        existing_jobs = session.execute(
            select(Job).where(Job.id.in_(job_ids))
        ).scalars()
        existing_by_id = {job.id: job for job in existing_jobs}

        imported_count = 0
        for item in payload:
            job_id = int(item["id"])
            record = existing_by_id.get(job_id)
            if record is None:
                record = Job(id=job_id)
                session.add(record)

            record.title = str(item.get("title", ""))
            record.company = str(item.get("company", ""))
            record.location = str(item.get("location", ""))
            record.description = str(item.get("description", ""))
            imported_count += 1

        session.commit()
        return imported_count
