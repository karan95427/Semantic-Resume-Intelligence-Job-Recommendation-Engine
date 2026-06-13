from __future__ import annotations

from sqlalchemy import select

from ..db import get_session
from ..models.job import ExplanationCache


def get_cached_explanation(
    facts_hash: str,
    prompt_version: str,
    provider_name: str,
    model_name: str,
) -> dict | None:
    with get_session() as session:
        record = session.execute(
            select(ExplanationCache).where(
                ExplanationCache.facts_hash == facts_hash,
                ExplanationCache.prompt_version == prompt_version,
                ExplanationCache.provider_name == provider_name,
                ExplanationCache.model_name == model_name,
            )
        ).scalar_one_or_none()

        if record is None:
            return None
        return dict(record.output_json)


def save_explanation(
    job_id: int,
    facts_hash: str,
    prompt_version: str,
    provider_name: str,
    model_name: str,
    input_facts: dict,
    output_json: dict,
) -> None:
    with get_session() as session:
        record = session.execute(
            select(ExplanationCache).where(
                ExplanationCache.facts_hash == facts_hash,
                ExplanationCache.prompt_version == prompt_version,
                ExplanationCache.provider_name == provider_name,
                ExplanationCache.model_name == model_name,
            )
        ).scalar_one_or_none()

        if record is None:
            record = ExplanationCache(
                job_id=job_id,
                facts_hash=facts_hash,
                prompt_version=prompt_version,
                provider_name=provider_name,
                model_name=model_name,
                input_facts=input_facts,
                output_json=output_json,
            )
            session.add(record)
        else:
            record.job_id = job_id
            record.input_facts = input_facts
            record.output_json = output_json

        session.commit()
