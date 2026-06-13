from .matching_engine import score_job_from_texts


def calculate_similarity(text1: str, text2: str):
    result = score_job_from_texts(
        resume_text=text1,
        job_text=text2,
    )

    return {
        "match_score": float(result["match_score"]),
        "match_label": result["match_label"],
        "semantic_score": float(result["semantic_score"]),
        "skill_match_score": float(result["skill_match_score"]),
        "matched_skills": result["matched_skills"],
        "final_score": float(result["final_score"]),
    }
