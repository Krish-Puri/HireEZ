"""
Test Result Routes

Handles test result CSV upload and shortlisting candidates for interviews.
"""

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException,
    Query,
)

from pathlib import Path
from sqlalchemy.orm import Session
import shutil
from typing import Optional

from backend.database.connection import get_db
from backend.services.csv_service import csv_service
from backend.repositories.candidate_repository import candidate_repository
from backend.repositories.test_result_repository import test_result_repository
from backend.services.email_service import email_service


router = APIRouter(
    prefix="/tests",
    tags=["Tests"],
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
UPLOAD_FOLDER = PROJECT_ROOT / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Tracks candidate IDs already matched during this upload request
_matched_candidate_ids: set[int] = set()


@router.post("/upload-results")
async def upload_test_results(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    global _matched_candidate_ids
    _matched_candidate_ids = set()  # Reset for each upload batch
    """
    Upload a CSV with test scores (Email, test_la, test_code).
    Updates candidate records and their TestResult entries.
    """
    allowed = (".csv", ".xlsx", ".xls")
    if not any(file.filename.lower().endswith(ext) for ext in allowed):
        raise HTTPException(status_code=400, detail="Only .csv and .xlsx (Excel) files are supported.")

    file_path = UPLOAD_FOLDER / f"test_results_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        report = csv_service.parse_test_results(str(file_path))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    updated = 0
    not_found = 0

    for result in report.results:
        # Use ordered matching: match candidates with the same base email,
        # in insertion order (lowest ID first), skipping already-matched ones.
        candidate = candidate_repository.get_by_base_email_ordered(
            db, result["email"]
        )
        if not candidate:
            not_found += 1
            continue

        # Update candidate test scores
        if result["test_la"] is not None:
            candidate.test_la = result["test_la"]
        if result["test_code"] is not None:
            candidate.test_code = result["test_code"]
        db.commit()

        # Upsert test result record
        test_result_repository.upsert(
            db,
            candidate.id,
            result["test_la"],
            result["test_code"],
        )
        updated += 1

    return {
        "success": True,
        "summary": {
            "total_rows": report.statistics["total_rows"],
            "updated": updated,
            "not_found": not_found,
        },
        "errors": report.errors,
    }


@router.post("/send-test-links")
async def send_test_links(
    threshold: float = Query(50.0, ge=0, le=100),
    job_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Shortlist candidates who passed the AI evaluation (final_score >= threshold)
    and send them test links via email.

    Query params:
    - threshold: minimum final_score to be shortlisted (default 50.0)
    - job_id: (optional) filter by specific job
    """
    import time

    test_link = "https://hireez.app/assessment"  # Default placeholder

    candidates = candidate_repository.get_all(db)
    shortlisted = [
        c for c in candidates
        if c.final_score is not None
        and c.final_score >= threshold
    ]

    results = []
    for candidate in shortlisted:
        success = email_service.send_test_link(
            to_email=candidate.email,
            candidate_name=candidate.name,
            test_link=test_link,
        )
        test_result_repository.upsert(db, candidate.id, None, None)
        test_result_repository.update_test_link_sent(db, candidate.id, test_link)
        results.append({
            "candidate_id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "test_link_sent": success,
        })
        # Small delay between sends to avoid SMTP rate limiting
        time.sleep(0.5)

    return {
        "success": True,
        "shortlisted_count": len(results),
        "results": results,
    }


@router.get("/shortlisted")
async def get_shortlisted(
    threshold: float = Query(50.0, ge=0, le=100),
    db: Session = Depends(get_db),
):
    """
    Get candidates shortlisted based on their final_score threshold.
    """
    candidates = candidate_repository.get_all(db)
    shortlisted = [
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "college": c.college,
            "branch": c.branch,
            "final_score": c.final_score,
            "candidate_rank": c.candidate_rank,
            "test_la": c.test_la,
            "test_code": c.test_code,
            "status": c.status,
        }
        for c in candidates
        if c.final_score is not None and c.final_score >= threshold
    ]
    shortlisted.sort(key=lambda x: x["candidate_rank"] or 999)
    return shortlisted


@router.get("/shortlisted-after-test")
async def get_shortlisted_after_test(
    min_total: float = Query(50.0, ge=0, le=200),
    db: Session = Depends(get_db),
):
    """
    Get candidates who:
    1. Have received test links (test_link_sent == 'Sent')
    2. Have completed their test (test_la and test_code are not null)
    3. Combined test score (test_la + test_code) >= min_total

    This is used AFTER test results are uploaded to shortlist based on test performance.
    """
    candidates_with_links = test_result_repository.get_candidates_with_test_links(db)
    candidates = candidate_repository.get_all(db)

    shortlisted = [
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "college": c.college,
            "branch": c.branch,
            "test_la": c.test_la,
            "test_code": c.test_code,
            "final_score": c.final_score,
            "candidate_rank": c.candidate_rank,
            "total_test_score": (c.test_la or 0) + (c.test_code or 0),
            "status": c.status,
        }
        for c in candidates
        if c.id in candidates_with_links
        and c.test_la is not None
        and c.test_code is not None
        and (c.test_la + c.test_code) >= min_total
    ]
    shortlisted.sort(key=lambda x: x["total_test_score"], reverse=True)
    return shortlisted
