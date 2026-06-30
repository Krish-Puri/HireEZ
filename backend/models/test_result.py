"""
TestResult Model

Stores test scores for candidates (Logical Aptitude & Coding Test).
"""

from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    ForeignKey,
    DateTime
)
from sqlalchemy.sql import func

from backend.database.base import Base


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id"),
        nullable=False
    )

    test_la = Column(Float)  # Logical Aptitude Score

    test_code = Column(Float)  # Coding Test Score

    test_link = Column(String(500))  # Test link sent to candidate

    test_link_sent = Column(
        String(20),
        default="Pending"  # Pending / Sent / Completed
    )

    interview_scheduled = Column(
        String(20),
        default="Pending"  # Pending / Scheduled / Cancelled
    )

    interview_link = Column(String(500))  # Google Meet link

    interview_time = Column(DateTime(timezone=True))

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    def __repr__(self):
        return f"<TestResult(candidate_id={self.candidate_id}, test_la={self.test_la}, test_code={self.test_code})>"
