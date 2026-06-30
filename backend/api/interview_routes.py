"""
Interview Routes

Schedules interviews for shortlisted candidates who have completed assessments.
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import pytz

from backend.database.connection import get_db
from backend.repositories.candidate_repository import candidate_repository
from backend.repositories.test_result_repository import test_result_repository
from backend.services.email_service import email_service
from backend.interview.google_calendar import google_calendar_service


router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"],
)


@router.post("/schedule")
async def schedule_interviews(
    min_test_score: float = Query(30.0, ge=0, le=100),
    # How long should the test be? default 60 min
    interview_duration_minutes: int = Query(60, ge=15, le=240),
    # ISO format datetime for interview start (UTC) — e.g. 2026-07-01T10:00:00Z
    start_time_str: Optional[str] = Query(None),
    # Candidate IDs to schedule (if not all shortlisted)
    candidate_ids: Optional[str] = Query(None),  # comma-separated
    db: Session = Depends(get_db),
):
    """
    Schedule interviews for candidates who:
    1. Have a final_score >= min_test_score (AI evaluation)
    2. Have completed their test (test_la and test_code are not null)

    Creates Google Meet links and sends email invitations.
    """
    candidates = candidate_repository.get_all(db)

    # Only consider candidates who received test links and have completed their test
    test_linked_ids = test_result_repository.get_candidates_with_test_links(db)
    eligible = [
        c for c in candidates
        if c.id in test_linked_ids
        and c.test_la is not None
        and c.test_code is not None
    ]

    if candidate_ids:
        ids = [int(x.strip()) for x in candidate_ids.split(",")]
        eligible = [c for c in eligible if c.id in ids]

    results = []
    timezone = pytz.UTC

    # Determine interview start time
    if start_time_str:
        start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
    else:
        # Default: tomorrow at 10 AM UTC
        start_time = datetime.now(timezone).replace(
            hour=10, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)

    for i, candidate in enumerate(eligible):
        cand_start = start_time + timedelta(minutes=i * (interview_duration_minutes + 15))
        cand_end = cand_start + timedelta(minutes=interview_duration_minutes)

        try:
            event = await google_calendar_service.create_interview_event(
                candidate_email=candidate.email,
                candidate_name=candidate.name,
                job_title=None,  # could be passed in from job context
                start_time=cand_start,
                end_time=cand_end,
            )
            meet_link = event["meet_link"]
            raw_start = event.get("start", "")
            if raw_start:
                try:
                    interview_time = datetime.fromisoformat(raw_start.replace("Z", "+00:00"))
                except ValueError:
                    interview_time = cand_start
            else:
                interview_time = cand_start

            # Save in DB
            test_result_repository.update_interview_scheduled(
                db, candidate.id, meet_link, interview_time
            )
            candidate.status = "Interview Scheduled"
            db.commit()

            # Send email
            time_str = cand_start.strftime("%A, %B %d at %I:%M %p UTC")
            email_sent = email_service.send_interview_invite(
                to_email=candidate.email,
                candidate_name=candidate.name,
                interview_link=meet_link,
                interview_time=time_str,
            )

            results.append({
                "candidate_id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
                "interview_time": event["start"],
                "meet_link": meet_link,
                "email_sent": email_sent,
                "status": "Scheduled",
            })
        except Exception as e:
            results.append({
                "candidate_id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
                "error": str(e),
                "status": "Failed",
            })

    return {
        "success": True,
        "scheduled_count": sum(1 for r in results if r["status"] == "Scheduled"),
        "failed_count": sum(1 for r in results if r["status"] == "Failed"),
        "results": results,
    }


@router.get("/")
async def list_interviews(db: Session = Depends(get_db)):
    """List all interview scheduling statuses."""
    all_results = test_result_repository.get_all(db)
    return [
        {
            "candidate_id": tr.candidate_id,
            "test_link_sent": tr.test_link_sent,
            "test_link": tr.test_link,
            "interview_scheduled": tr.interview_scheduled,
            "interview_link": tr.interview_link,
            "interview_time": tr.interview_time,
        }
        for tr in all_results
    ]
