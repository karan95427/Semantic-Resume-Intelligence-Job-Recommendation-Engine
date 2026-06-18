from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

from ..models.schemas import RecommendationResponse
from ..services.embedding_service import generate_embedding
from ..services.explanation_service import explain_recommendations
from ..services.parser_service import extract_text_from_pdf
from ..services.recommendation_service import load_jobs, recommend_jobs
from ..services.runtime_service import ensure_backend_ready, get_backend_status, trigger_backend_warmup
from ..services.similarity_service import calculate_similarity


router = APIRouter()
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "data" / "uploads"


@router.get("/health")
def health_check():
    snapshot = get_backend_status()
    return {
        "status": "ok",
        "service": "ai-job-matcher-api",
        "ready": snapshot["ready"],
    }


@router.get("/ready")
def readiness_check():
    trigger_backend_warmup()
    snapshot = get_backend_status()
    status_code = 200 if snapshot["ready"] else 503
    return JSONResponse(status_code=status_code, content=snapshot)


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
    ensure_backend_ready()
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
        "match_label": result["match_label"],
        "extracted_text_preview": resume_text[:500],
    }


@router.post(
    "/job-recommendations",
    response_model=RecommendationResponse,
    response_model_exclude_none=True,
)
async def job_recommendations(
    file: UploadFile = File(...),
    top_k: int = Form(3),
    explain: bool = Form(False),
):
    ensure_backend_ready()
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
    if explain:
        recommendations = explain_recommendations(
            recommendations,
            resume_text=resume_text,
        )

    return {
        "filename": file.filename,
        "total_jobs_compared": len(jobs),
        "recommendations": recommendations,
    }
