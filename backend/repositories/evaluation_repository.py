"""Evaluation repository for database operations."""

from typing import List

from sqlalchemy.orm import Session

from backend.models.evaluation import Evaluation
from backend.schemas.evaluation_schema import EvaluationCreate


class EvaluationRepository:

    def create(self, db: Session, evaluation: EvaluationCreate) -> Evaluation:
        db_evaluation = Evaluation(**evaluation.model_dump())
        try:
            db.add(db_evaluation)
            db.commit()
            db.refresh(db_evaluation)
        except Exception:
            db.rollback()
            raise
        return db_evaluation

    def get_latest_for_candidate(self, db: Session, candidate_id: int) -> Evaluation | None:
        return (
            db.query(Evaluation)
            .filter(Evaluation.candidate_id == candidate_id)
            .order_by(Evaluation.created_at.desc())
            .first()
        )

    def get_all_for_job(self, db: Session, job_id: int) -> List[Evaluation]:
        return (
            db.query(Evaluation)
            .filter(Evaluation.job_id == job_id)
            .order_by(Evaluation.created_at.desc())
            .all()
        )

def get_latest_for_candidate(
    self,
    db: Session,
    candidate_id: int,
):

    return (

        db.query(Evaluation)

        .filter(
            Evaluation.candidate_id == candidate_id
        )

        .order_by(
            Evaluation.created_at.desc()
        )

        .first()

    )

evaluation_repository = EvaluationRepository()
