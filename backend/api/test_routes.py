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


# Use /tmp for uploads — Render's filesystem is read-only except /tmp
UPLOAD_FOLDER = Path("/tmp/hireez-test-uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

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
    and send them test links via email. Emails are sent asynchronously in
    background threads to avoid timeout on large candidate lists.
    """
    import threading

    test_link = "https://hireez.app/assessment"  # Default placeholder

    candidates = candidate_repository.get_all(db)
    shortlisted = [
        c for c in candidates
        if c.final_score is not None
        and c.final_score >= threshold
    ]

    def _send_email_async(candidate_data):
        from backend.database.connection import SessionLocal
        session = SessionLocal()
        try:
            cid, name, email = candidate_data
            success = email_service.send_test_link(
                to_email=email,
                candidate_name=name,
                test_link=test_link,
            )
            # Update test result record in background
            test_result_repository.upsert(session, cid, None, None)
            test_result_repository.update_test_link_sent(session, cid, test_link)
        finally:
            session.close()

    # Spawn background threads for each email — do NOT wait
    candidate_data = [(c.id, c.name, c.email) for c in shortlisted]
    for data in candidate_data:
        t = threading.Thread(target=_send_email_async, args=(data,), daemon=True)
        t.start()

    return {
        "success": True,
        "shortlisted_count": len(shortlisted),
        "message": f"Emails are being sent to {len(shortlisted)} candidates in the background.",
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
