from pydantic import BaseModel


class MatchRequest(BaseModel):
    resume: str
    job_description: str


class MatchResponse(BaseModel):
    match_score: float


class JobRecommendation(BaseModel):
    id: int
    title: str
    description: str
    match_score: float
    semantic_score: float
    skill_match_score: float
    matched_skills: list[str]
    missing_skills: list[str]


class RecommendationResponse(BaseModel):
    filename: str
    total_jobs_compared: int
    recommendations: list[JobRecommendation]
