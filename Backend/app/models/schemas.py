from pydantic import BaseModel


class MatchRequest(BaseModel):
    resume: str
    job_description: str


class MatchResponse(BaseModel):
    match_score: float
    match_label: str


class RecommendationExplanation(BaseModel):
    summary: str
    matched_skills: list[str]
    missing_skills: list[str]
    strengths: list[str]
    weaknesses: list[str]
    improvement_suggestions: list[str]
    source: str


class JobRecommendation(BaseModel):
    id: int
    title: str
    description: str
    match_score: float
    match_label: str
    semantic_score: float
    skill_match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: RecommendationExplanation | None = None


class RecommendationResponse(BaseModel):
    filename: str
    total_jobs_compared: int
    recommendations: list[JobRecommendation]
