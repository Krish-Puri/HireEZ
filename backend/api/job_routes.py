"""Job API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.schemas.job_schema import JobCreate, JobResponse
from backend.services.job_service import job_service


router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)


@router.post("/", response_model=JobResponse)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
):
    return job_service.create_job(db, job_data)


@router.get("/", response_model=list[JobResponse])
def list_jobs(
    db: Session = Depends(get_db),
):
    return job_service.get_jobs(db)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    deleted = job_service.delete_job(db, job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"deleted": True, "job_id": job_id}
