from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.base import Base
from backend.models.candidate import Candidate
from backend.models.evaluation import Evaluation
from backend.models.job import Job
from backend.pipeline.stages.resume_stage import ResumeStage
from backend.repositories.job_repository import job_repository
from backend.schemas.evaluation_schema import EvaluationCreate
from backend.services.evaluation_service import evaluation_service
from backend.evaluation.result import EvaluationResult


def test_job_repository_get_first_returns_oldest_job():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    session.add_all([
        Job(title="First", company="HireEZ", description="One"),
        Job(title="Second", company="HireEZ", description="Two"),
    ])
    session.commit()

    first_job = job_repository.get_first(session)

    assert first_job is not None
    assert first_job.title == "First"


def test_resume_stage_updates_resume_fields_and_save_eval():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    candidate = Candidate(name="Ada", email="ada@example.com")
    candidate.resume_text = "Python developer"
    candidate.resume_file_path = "uploads/ada.pdf"
    session.add(candidate)
    session.commit()
    session.refresh(candidate)

    resume_stage = ResumeStage()
    updated = resume_stage.execute(session, candidate)

    assert updated.resume_text == "Python developer"
    assert updated.resume_file_path == "uploads/ada.pdf"

    job = Job(title="Engineer", company="HireEZ", description="Build software")
    session.add(job)
    session.commit()
    session.refresh(job)

    evaluation_result = EvaluationResult(
        overall_score=88.0,
        technical_score=40.0,
        project_score=20.0,
        education_score=10.0,
        research_score=10.0,
        communication_score=8.0,
        strengths=["Strong Python"],
        concerns=[],
        missing_skills=["Docker"],
        interview_questions=["Tell me about your testing"],
        recommendation="Strong consider",
        summary="Good fit",
    )

    saved = evaluation_service.save_evaluation(
        db=session,
        candidate=candidate,
        job=job,
        result=evaluation_result,
    )

    assert isinstance(saved, Evaluation)
    assert saved.candidate_id == candidate.id
    assert saved.job_id == job.id
    assert saved.overall_score == 88.0
