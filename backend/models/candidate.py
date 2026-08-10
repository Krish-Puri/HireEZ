"""
Candidate Model

Represents a candidate throughout the hiring pipeline.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
)

from sqlalchemy.sql import func

from backend.database.base import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(String(150), unique=True, nullable=False)

    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)

    college = Column(String(150))

    branch = Column(String(100))

    cgpa = Column(Float)

    best_ai_project = Column(Text)

    research_work = Column(Text)

    github_url = Column(String(300))

    resume_url = Column(String(500))

    github_score = Column(Float, default=0)

    github_summary = Column(Text)

    top_languages = Column(Text)

    resume_file_path = Column(String(500))

    resume_text = Column(Text)

    # Test scores
    test_la = Column(Float)  # Logical Aptitude Score
    test_code = Column(Float)  # Coding Test Score

    final_score = Column(Float, default=0)

    candidate_rank = Column(Integer)

    status = Column(
        String(50),
        default="Uploaded"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    def __repr__(self):
        return f"<Candidate(name='{self.name}', email='{self.email}')>"