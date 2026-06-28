"""
Candidate Repository

Handles all database operations for Candidate.
"""

from typing import List

from sqlalchemy.orm import Session

from backend.models.candidate import Candidate
from backend.schemas.candidate_schema import CandidateCreate


class CandidateRepository:

    def create(
        self,
        db: Session,
        candidate: CandidateCreate
    ) -> Candidate:

        db_candidate = Candidate(
            **candidate.model_dump()
        )

        try:
            db.add(db_candidate)
            db.commit()
            db.refresh(db_candidate)
        except Exception:
            db.rollback()
            raise

        return db_candidate

    def create_many(
        self,
        db: Session,
        candidates: List[CandidateCreate]
    ) -> int:
        if not candidates:
            return 0

        db_candidates = [
            Candidate(**candidate.model_dump())
            for candidate in candidates
        ]

        try:
            db.add_all(db_candidates)
            db.commit()
        except Exception:
            db.rollback()
            raise

        return len(db_candidates)

    def get_all(
        self,
        db: Session
    ):

        return (
            db.query(Candidate)
            .order_by(Candidate.id)
            .all()
        )


    def get_by_email(
        self,
        db: Session,
        email: str
    ):

        return (
            db.query(Candidate)
            .filter(Candidate.email == email)
            .first()
        )

    def get_existing_emails(
        self,
        db: Session
    ) -> set[str]:

        rows = db.query(Candidate.email).all()
        return {row[0] for row in rows}

    def exists(
        self,
        db: Session,
        email: str
    ):

        return (
            db.query(Candidate)
            .filter(Candidate.email == email)
            .first()
            is not None
        )


candidate_repository = CandidateRepository()