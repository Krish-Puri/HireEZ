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
    DateTime
)

from sqlalchemy.sql import func

from backend.database.base import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(String(150), unique=True, nullable=False)

    college = Column(String(150))

    branch = Column(String(100))

    cgpa = Column(Float)

    best_ai_project = Column(Text)

    research_work = Column(Text)

    github_url = Column(String(300))

    resume_url = Column(String(500))

    resume_text = Column(Text)

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