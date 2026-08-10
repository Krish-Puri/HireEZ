"""Evaluation schemas for request and response payloads."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EvaluationCreate(BaseModel):
    candidate_id: int
    job_id: int
    overall_score: float | None = None
    technical_score: float | None = None
    project_score: float | None = None
    education_score: float | None = None
    research_score: float | None = None
    communication_score: float | None = None
    recommendation: str | None = None
    summary: str | None = None
    best_project: str | None = None
    strengths: str | None = None
    concerns: str | None = None
    missing_skills: str | None = None
    interview_questions: str | None = None
    raw_response: str | None = None


class EvaluationResponse(EvaluationCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
