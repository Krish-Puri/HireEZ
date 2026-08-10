from sqlalchemy import (
    Column,
    Integer,
    Float,
    Text,
    ForeignKey,
    DateTime,
)

from sqlalchemy.sql import func

from backend.database.base import Base


class Evaluation(Base):

    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True)

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id"),
        nullable=False,
    )

    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=False,
    )

    overall_score = Column(Float)
    technical_score = Column(Float)
    project_score = Column(Float)
    education_score = Column(Float)
    research_score = Column(Float)
    communication_score = Column(Float)

    recommendation = Column(Text)
    summary = Column(Text)
    strengths = Column(Text)
    concerns = Column(Text)
    missing_skills = Column(Text)
    interview_questions = Column(Text)
    raw_response = Column(Text)

    created_at = Column(
        DateTime,
        server_default=func.now(),
    )