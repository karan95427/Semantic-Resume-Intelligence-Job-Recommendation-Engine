from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from pydantic import ValidationError

from ..models.schemas import RecommendationExplanation
from ..repositories.explanation_repository import (
    get_cached_explanation,
    save_explanation,
)
from .explanation_fact_service import build_explanation_facts
from .llm_client import ExplanationProvider
from .openai_provider import OpenAIExplanationProvider


PROMPT_VERSION = "recommendation_explanation_v1"


def _format_skill_list(skills: list[str]) -> str:
    if not skills:
        return "the currently detected skills"
    if len(skills) == 1:
        return skills[0]
    return ", ".join(skills[:-1]) + f", and {skills[-1]}"


def _fallback_explanation(recommendation: dict) -> dict:
    matched_skills = list(recommendation.get("matched_skills", []))
    missing_skills = list(recommendation.get("missing_skills", []))
    title = recommendation.get("title", "this role")
    match_label = recommendation.get("match_label", "match")
    match_score = recommendation.get("match_score", 0.0)

    summary = (
        f"{title} is a {match_label.lower()} with a score of {match_score}. "
        f"The match is supported by {_format_skill_list(matched_skills)}."
    )
    if missing_skills:
        summary += f" The main gaps are {_format_skill_list(missing_skills)}."

    strengths = [
        f"Relevant detected skill: {skill}"
        for skill in matched_skills[:3]
    ] or ["The existing match score indicates some alignment with the role."]
    weaknesses = [
        f"Missing detected requirement: {skill}"
        for skill in missing_skills[:3]
    ] or ["No missing skills were detected from the structured match facts."]
    suggestions = [
        f"Add resume evidence for {skill} if you have used it."
        for skill in missing_skills[:3]
    ] or ["Strengthen the resume with measurable project impact for the matched skills."]

    return {
        "summary": summary,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "improvement_suggestions": suggestions,
        "source": "fallback",
    }


def validate_explanation(
    explanation: dict,
    matched_skills: list[str],
    missing_skills: list[str],
) -> RecommendationExplanation:
    parsed = RecommendationExplanation.model_validate(explanation)
    allowed_matched = set(matched_skills)
    allowed_missing = set(missing_skills)

    if set(parsed.matched_skills) - allowed_matched:
        raise ValueError("Explanation contains hallucinated matched skills.")
    if set(parsed.missing_skills) - allowed_missing:
        raise ValueError("Explanation contains hallucinated missing skills.")

    return parsed


def _facts_hash(facts: dict) -> str:
    payload = json.dumps(
        facts,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _provider_name(provider: ExplanationProvider) -> str:
    return str(
        getattr(
            provider,
            "provider_name",
            provider.__class__.__name__.replace("ExplanationProvider", "").lower(),
        )
    )


def _model_name(provider: ExplanationProvider) -> str:
    return str(getattr(provider, "model", "unknown"))


def _read_cached_explanation(
    facts_hash: str,
    provider: ExplanationProvider,
) -> dict | None:
    try:
        return get_cached_explanation(
            facts_hash=facts_hash,
            prompt_version=PROMPT_VERSION,
            provider_name=_provider_name(provider),
            model_name=_model_name(provider),
        )
    except Exception:
        return None


def _write_cached_explanation(
    recommendation: dict,
    facts: dict,
    facts_hash: str,
    provider: ExplanationProvider,
    explanation: RecommendationExplanation,
) -> None:
    try:
        save_explanation(
            job_id=int(recommendation.get("id")),
            facts_hash=facts_hash,
            prompt_version=PROMPT_VERSION,
            provider_name=_provider_name(provider),
            model_name=_model_name(provider),
            input_facts=facts,
            output_json=explanation.model_dump(),
        )
    except Exception:
        return


def _generate_explanation(
    recommendation: dict,
    resume_text: str,
    provider: ExplanationProvider,
) -> RecommendationExplanation:
    matched_skills = list(recommendation.get("matched_skills", []))
    missing_skills = list(recommendation.get("missing_skills", []))
    facts = build_explanation_facts(
        resume_text=resume_text,
        recommendation=recommendation,
    )
    facts_hash = _facts_hash(facts)
    cached_payload = _read_cached_explanation(
        facts_hash=facts_hash,
        provider=provider,
    )
    if cached_payload is not None:
        return validate_explanation(
            cached_payload,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
        )

    explanation_payload = provider.generate_explanation(facts)
    explanation_payload["source"] = "llm"

    explanation = validate_explanation(
        explanation_payload,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
    )
    _write_cached_explanation(
        recommendation=recommendation,
        facts=facts,
        facts_hash=facts_hash,
        provider=provider,
        explanation=explanation,
    )
    return explanation


def explain_recommendations(
    recommendations: list[dict],
    resume_text: str = "",
    provider: ExplanationProvider | None = None,
) -> list[dict]:
    explained = deepcopy(recommendations)
    provider = provider or OpenAIExplanationProvider()

    for recommendation in explained:
        try:
            explanation = _generate_explanation(
                recommendation=recommendation,
                resume_text=resume_text,
                provider=provider,
            )
        except Exception:
            try:
                explanation = validate_explanation(
                    _fallback_explanation(recommendation),
                    matched_skills=list(recommendation.get("matched_skills", [])),
                    missing_skills=list(recommendation.get("missing_skills", [])),
                )
            except (ValidationError, ValueError):
                explanation = RecommendationExplanation(
                    summary="Explanation is unavailable, but the recommendation score is unchanged.",
                    matched_skills=[],
                    missing_skills=[],
                    strengths=[],
                    weaknesses=[],
                    improvement_suggestions=[],
                    source="fallback",
                )
        recommendation["explanation"] = explanation.model_dump()

    return explained
