"""Job SQLAlchemy Model"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from backend.database.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    company = Column(String(150), nullable=False)
    department = Column(String(100))
    description = Column(Text, nullable=False)
    required_skills = Column(Text)
    preferred_skills = Column(Text)
    minimum_cgpa = Column(String(10))
    created_at = Column(
        DateTime,
        server_default=func.now(),
    )
