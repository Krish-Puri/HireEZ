"""
Candidate Schemas

Defines request and response models for the Candidate API.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


# -----------------------------
# Base Schema
# -----------------------------

class CandidateBase(BaseModel):
    name: str
    email: EmailStr
    college: Optional[str] = None
    branch: Optional[str] = None
    cgpa: Optional[float] = None
    best_ai_project: Optional[str] = None
    research_work: Optional[str] = None
    github_url: Optional[str] = None
    resume_url: Optional[str] = None
    job_id: Optional[int] = None


# -----------------------------
# Create Schema
# -----------------------------

class CandidateCreate(CandidateBase):
    pass


# -----------------------------
# Response Schema
# -----------------------------

class CandidateResponse(CandidateBase):
    id: int
    github_score: Optional[float] = None
    github_summary: Optional[str] = None
    top_languages: Optional[str] = None
    final_score: Optional[float] = None
    candidate_rank: Optional[int] = None
    test_la: Optional[float] = None
    test_code: Optional[float] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)