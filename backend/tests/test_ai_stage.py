from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.constants import CandidateStatus
from backend.database.base import Base
from backend.models.candidate import Candidate
from backend.models.job import Job
from backend.pipeline.stages.ai_stage import AIStage
from backend.services.job_service import job_service


def test_ai_stage_marks_failed_when_resume_text_missing():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    candidate = Candidate(name="Ada", email="ada@example.com")
    session.add(candidate)
    session.commit()
    session.refresh(candidate)

    stage = AIStage()
    updated = stage.execute(session, candidate)

    assert updated.status == CandidateStatus.FAILED
