"""Job schemas for API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobCreate(BaseModel):
    title: str
    company: str
    department: str | None = None
    description: str | None = None
    required_skills: str | None = None
    preferred_skills: str | None = None
    minimum_cgpa: float | None = None


class JobResponse(JobCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
