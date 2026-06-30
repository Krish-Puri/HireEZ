"""
TestResult Schemas

Pydantic models for test result upload and response.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TestResultBase(BaseModel):
    candidate_id: int
    test_la: Optional[float] = None
    test_code: Optional[float] = None
    test_link: Optional[str] = None
    test_link_sent: str = "Pending"
    interview_scheduled: str = "Pending"
    interview_link: Optional[str] = None
    interview_time: Optional[datetime] = None


class TestResultCreate(TestResultBase):
    pass


class TestResultResponse(TestResultBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
