from backend.evaluation.result import EvaluationResult
from backend.intelligence.profile import CandidateProfile
from backend.models.candidate import Candidate
from backend.models.job import Job
from backend.pipeline.context import PipelineContext


def test_pipeline_context_can_hold_pipeline_state():
    candidate = Candidate(id=1, name="Ada", email="ada@example.com")
    job = Job(id=2, title="Engineer", company="HireEZ", description="Build software")
    profile = CandidateProfile(skills=["Python"], summary="Strong backend profile")
    evaluation = EvaluationResult(
        overall_score=85.0,
        technical_score=40.0,
        project_score=20.0,
        education_score=10.0,
        research_score=10.0,
        communication_score=5.0,
        strengths=["Strong Python"],
        concerns=[],
        missing_skills=["Docker"],
        interview_questions=["Tell me about testing"],
        recommendation="Strong consider",
        summary="Good fit",
    )

    context = PipelineContext(
        candidate=candidate,
        job=job,
        profile=profile,
        evaluation=evaluation,
    )

    assert context.candidate is candidate
    assert context.job is job
    assert context.profile is profile
    assert context.evaluation is evaluation
