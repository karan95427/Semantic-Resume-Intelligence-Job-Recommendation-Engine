from __future__ import annotations

from .skill_extractor_service import extract_skills


def build_explanation_facts(
    resume_text: str,
    recommendation: dict,
) -> dict:
    matched_skills = list(recommendation.get("matched_skills", []))
    missing_skills = list(recommendation.get("missing_skills", []))

    return {
        "resume_signals": {
            "detected_skills": extract_skills(resume_text),
        },
        "job_signals": {
            "id": recommendation.get("id"),
            "title": recommendation.get("title", ""),
        },
        "match_facts": {
            "match_score": recommendation.get("match_score", 0.0),
            "match_label": recommendation.get("match_label", ""),
            "semantic_score": recommendation.get("semantic_score", 0.0),
            "skill_match_score": recommendation.get("skill_match_score", 0.0),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
        },
    }
