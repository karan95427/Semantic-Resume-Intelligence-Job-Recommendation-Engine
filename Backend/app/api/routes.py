from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile

from ..models.schemas import RecommendationResponse
from ..services.embedding_service import generate_embedding
from ..services.parser_service import extract_text_from_pdf
from ..services.recommendation_service import load_jobs, recommend_jobs
from ..services.similarity_service import calculate_similarity


router = APIRouter()
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "data" / "uploads"


@router.get("/embedding")
def embedding_test():
    text = "Python FastAPI Machine Learning"
    embedding = generate_embedding(text)

    return {
        "embedding_length": len(embedding),
        "sample": embedding[:5],
    }


@router.post("/resume-match")
async def resume_match(
    file: UploadFile = File(...),
    job_description: str = Form(...),
):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    resume_text = extract_text_from_pdf(str(file_path))

    result = calculate_similarity(
        resume_text,
        job_description,
    )

    return {
        "filename": file.filename,
        "match_score": result["match_score"],
        "extracted_text_preview": resume_text[:500],
    }


@router.post("/job-recommendations", response_model=RecommendationResponse)
async def job_recommendations(
    file: UploadFile = File(...),
    top_k: int = Form(3),
):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    resume_text = extract_text_from_pdf(str(file_path))
    jobs = load_jobs()
    normalized_top_k = max(1, min(top_k, len(jobs)))
    recommendations = recommend_jobs(
        resume_text,
        top_k=normalized_top_k,
    )

    return {
        "filename": file.filename,
        "total_jobs_compared": len(jobs),
        "recommendations": recommendations,
    }

