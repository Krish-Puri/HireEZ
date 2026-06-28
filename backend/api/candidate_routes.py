from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException,
)

from pathlib import Path

from sqlalchemy.orm import Session

import shutil
import os

from backend.database.connection import get_db

from backend.repositories.candidate_repository import (
    candidate_repository
)

from backend.services.csv_service import csv_service


router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"],
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
UPLOAD_FOLDER = PROJECT_ROOT / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_candidates(

    file: UploadFile = File(...),

    db: Session = Depends(get_db),

):

    if not file.filename.endswith(".csv"):

        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed."
        )

    file_path = UPLOAD_FOLDER / file.filename

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer,
        )

    try:
        report = csv_service.parse_candidates(file_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    valid_candidates = []
    duplicates = 0

    existing_emails = candidate_repository.get_existing_emails(db)

    for candidate in report.candidates:
        if candidate.email in existing_emails:
            duplicates += 1
            continue

        valid_candidates.append(candidate)
        existing_emails.add(candidate.email)

    inserted = candidate_repository.create_many(
        db,
        valid_candidates,
    )

    return {
        "success": True,
        "summary": {
            "total_rows": report.statistics["total_rows"],
            "valid_candidates": report.statistics["valid_rows"],
            "duplicates": duplicates,
            "inserted": inserted,
            "invalid_rows": report.statistics["invalid_rows"],
            "processing_time": report.statistics["processing_time"],
        },
        "errors": report.errors,
    }