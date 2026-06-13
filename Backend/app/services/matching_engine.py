from __future__ import annotations

from sklearn.metrics.pairwise import cosine_similarity

from .embedding_service import generate_embedding
from .skill_extractor_service import extract_skills


SEMANTIC_WEIGHT = 0.7
SKILL_WEIGHT = 0.3
STRONG_MATCH_MIN_SCORE = 85.0
MODERATE_MATCH_MIN_SCORE = 70.0


def calculate_semantic_score(
    resume_embedding: list[float],
    job_embedding: list[float],
) -> float:
    similarity = cosine_similarity(
        [resume_embedding],
        [job_embedding],
    )[0][0]

    return round(float(similarity) * 100, 2)


def calculate_skill_details(
    resume_text: str,
    job_text: str,
) -> dict:
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_text))
    matched_skills = sorted(resume_skills.intersection(job_skills))
    missing_skills = sorted(job_skills - resume_skills)

    if job_skills:
        skill_match_score = (len(matched_skills) / len(job_skills)) * 100
    else:
        skill_match_score = 0.0

    return {
        "resume_skills": sorted(resume_skills),
        "job_skills": sorted(job_skills),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_match_score": round(float(skill_match_score), 2),
    }


def calculate_final_score(
    semantic_score: float,
    skill_match_score: float,
) -> float:
    return round(
        (semantic_score * SEMANTIC_WEIGHT) +
        (skill_match_score * SKILL_WEIGHT),
        2,
    )


def determine_match_label(final_score: float) -> str:
    if final_score >= STRONG_MATCH_MIN_SCORE:
        return "Strong Match"
    if final_score >= MODERATE_MATCH_MIN_SCORE:
        return "Moderate Match"
    return "Low Match"


def score_job(
    resume_text: str,
    job_text: str,
    resume_embedding: list[float] | None = None,
    job_embedding: list[float] | None = None,
) -> dict:
    resume_embedding = resume_embedding or generate_embedding(resume_text)
    job_embedding = job_embedding or generate_embedding(job_text)

    semantic_score = calculate_semantic_score(
        resume_embedding=resume_embedding,
        job_embedding=job_embedding,
    )
    skill_details = calculate_skill_details(
        resume_text=resume_text,
        job_text=job_text,
    )
    final_score = calculate_final_score(
        semantic_score=semantic_score,
        skill_match_score=skill_details["skill_match_score"],
    )
    match_label = determine_match_label(final_score)

    return {
        "match_score": final_score,
        "match_label": match_label,
        "semantic_score": semantic_score,
        "skill_match_score": skill_details["skill_match_score"],
        "matched_skills": skill_details["matched_skills"],
        "missing_skills": skill_details["missing_skills"],
        "resume_skills": skill_details["resume_skills"],
        "job_skills": skill_details["job_skills"],
        "final_score": final_score,
    }

def score_job_from_texts(
    resume_text: str,
    job_text: str,
) -> dict:
    return score_job(
        resume_text=resume_text,
        job_text=job_text,
    )
