"""Thin service layer for jobs."""

from typing import List

from sqlalchemy.orm import Session

from backend.repositories.job_repository import job_repository
from backend.schemas.job_schema import JobCreate


class JobService:

    def create_job(self, db: Session, job_data: JobCreate):
        return job_repository.create(db, job_data)

    def get_job(self, db: Session, job_id: int):
        return job_repository.get(db, job_id)

    def get_jobs(self, db: Session) -> List:
        return job_repository.get_all(db)

    def get_first_job(self, db: Session):
        return job_repository.get_first(db)

    def delete_job(self, db: Session, job_id: int) -> bool:
        return job_repository.delete(db, job_id)


job_service = JobService()