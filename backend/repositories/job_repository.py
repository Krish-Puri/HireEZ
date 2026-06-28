"""Job repository for database operations."""

from typing import List

from sqlalchemy.orm import Session

from backend.models.job import Job
from backend.schemas.job_schema import JobCreate


class JobRepository:

    def create(self, db: Session, job: JobCreate) -> Job:
        db_job = Job(**job.model_dump())
        try:
            db.add(db_job)
            db.commit()
            db.refresh(db_job)
        except Exception:
            db.rollback()
            raise
        return db_job

    def get(self, db: Session, job_id: int) -> Job | None:
        return db.query(Job).filter(Job.id == job_id).first()

    def get_all(self, db: Session) -> List[Job]:
        return db.query(Job).order_by(Job.id).all()

    def delete(self, db: Session, job_id: int) -> bool:
        job = self.get(db, job_id)
        if not job:
            return False
        try:
            db.delete(job)
            db.commit()
        except Exception:
            db.rollback()
            raise
        return True


job_repository = JobRepository()