"""Thin service layer for evaluations."""

from typing import List

from sqlalchemy.orm import Session

from backend.evaluation.result import EvaluationResult
from backend.models.candidate import Candidate
from backend.models.job import Job
from backend.repositories.evaluation_repository import evaluation_repository
from backend.schemas.evaluation_schema import EvaluationCreate


class EvaluationService:

    def save_evaluation(
        self,
        db: Session,
        candidate: Candidate,
        job: Job,
        result: EvaluationResult,
        raw_response: str | None = None,
    ):
        evaluation_data = EvaluationCreate(
            candidate_id=candidate.id,
            job_id=job.id,
            overall_score=result.overall_score,
            technical_score=result.technical_score,
            project_score=result.project_score,
            education_score=result.education_score,
            research_score=result.research_score,
            communication_score=result.communication_score,
            recommendation=result.recommendation,
            summary=result.summary,
            strengths="|".join(result.strengths),
            concerns="|".join(result.concerns),
            missing_skills="|".join(result.missing_skills),
            interview_questions="|".join(result.interview_questions),
            raw_response=raw_response,
        )
        return evaluation_repository.create(db, evaluation_data)

    def get_latest_evaluation(self, db: Session, candidate_id: int):
        return evaluation_repository.get_latest_for_candidate(db, candidate_id)

    def get_evaluations_for_job(self, db: Session, job_id: int) -> List:
        return evaluation_repository.get_all_for_job(db, job_id)


evaluation_service = EvaluationService()
