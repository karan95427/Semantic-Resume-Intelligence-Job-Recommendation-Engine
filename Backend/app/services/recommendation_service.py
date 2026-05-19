import json
from pathlib import Path

from .embedding_service import generate_embedding
from .faiss_service import search_similar_jobs
from .matching_engine import score_job


JOBS_FILE = Path(__file__).resolve().parents[2] / "data" / "jobs" / "jobs.json"


def load_jobs() -> list[dict]:
    with JOBS_FILE.open("r", encoding="utf-8") as file:
        jobs = json.load(file)

    if not isinstance(jobs, list):
        raise ValueError("jobs.json must contain a list of jobs")

    return jobs


def recommend_jobs(resume_text: str, top_k: int = 3) -> list[dict]:
    jobs = load_jobs()
    resume_embedding = generate_embedding(resume_text)
    search_results = search_similar_jobs(
        resume_embedding=resume_embedding,
        jobs=jobs,
        top_k=top_k,
    )
    recommendations = []

    for item in search_results:
        job = item["job"]
        job_description = job.get("description", "")
        job_embedding = item["embedding"]
        score = score_job(
            resume_text=resume_text,
            job_text=job_description,
            resume_embedding=resume_embedding,
            job_embedding=job_embedding,
        )

        recommendations.append(
            {
                "id": job["id"],
                "title": job["title"],
                "description": job_description,
                "match_score": score["match_score"],
                "semantic_score": score["semantic_score"],
                "skill_match_score": score["skill_match_score"],
                "matched_skills": score["matched_skills"],
                "missing_skills": score["missing_skills"],
            }
        )

    recommendations.sort(
        key=lambda item: (-item["match_score"], item["id"])
    )

    return recommendations[:top_k]
