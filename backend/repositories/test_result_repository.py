"""
TestResult Repository

Handles database operations for TestResult.
"""

from typing import Optional

from sqlalchemy.orm import Session

from backend.models.test_result import TestResult


class TestResultRepository:

    def create(self, db: Session, test_result: TestResult) -> TestResult:
        db.add(test_result)
        db.commit()
        db.refresh(test_result)
        return test_result

    def upsert(self, db: Session, candidate_id: int, test_la: Optional[float], test_code: Optional[float]) -> TestResult:
        """
        Create or update test result for a candidate.
        """
        existing = db.query(TestResult).filter(TestResult.candidate_id == candidate_id).first()
        if existing:
            if test_la is not None:
                existing.test_la = test_la
            if test_code is not None:
                existing.test_code = test_code
            db.commit()
            db.refresh(existing)
            return existing
        else:
            tr = TestResult(
                candidate_id=candidate_id,
                test_la=test_la,
                test_code=test_code,
            )
            db.add(tr)
            db.commit()
            db.refresh(tr)
            return tr

    def get_by_candidate(self, db: Session, candidate_id: int) -> Optional[TestResult]:
        return db.query(TestResult).filter(TestResult.candidate_id == candidate_id).first()

    def get_all(self, db: Session):
        return db.query(TestResult).all()

    def get_candidates_with_test_links(self, db: Session):
        """Return candidate_ids that have received test links."""
        rows = db.query(TestResult.candidate_id).filter(
            TestResult.test_link_sent == "Sent"
        ).all()
        return {row[0] for row in rows}

    def update_test_link_sent(self, db: Session, candidate_id: int, test_link: str) -> Optional[TestResult]:
        tr = self.get_by_candidate(db, candidate_id)
        if tr:
            tr.test_link = test_link
            tr.test_link_sent = "Sent"
            db.commit()
            db.refresh(tr)
        return tr

    def update_interview_scheduled(
        self,
        db: Session,
        candidate_id: int,
        interview_link: str,
        interview_time
    ) -> Optional[TestResult]:
        tr = self.get_by_candidate(db, candidate_id)
        if tr:
            tr.interview_link = interview_link
            tr.interview_time = interview_time
            tr.interview_scheduled = "Scheduled"
            db.commit()
            db.refresh(tr)
        return tr


test_result_repository = TestResultRepository()
