"""
Interview Routes

Schedules interviews for shortlisted candidates who have completed assessments.
"""

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import pytz
import asyncio
import concurrent.futures

from backend.database.connection import get_db
from backend.repositories.candidate_repository import candidate_repository
from backend.repositories.test_result_repository import test_result_repository
from backend.services.email_service import email_service
from backend.interview.google_calendar import google_calendar_service


router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"],
)


def _schedule_one_sync(candidate_id, candidate_email, candidate_name, cand_start, cand_end):
    """Synchronous scheduling logic — runs in a background thread with its own event loop."""
    # Each thread gets its own DB session and a fresh event loop for the async calendar call
    from backend.database.connection import SessionLocal

    def _run_async():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                google_calendar_service.create_interview_event(
                    candidate_email=candidate_email,
                    candidate_name=candidate_name,
                    job_title=None,
                    start_time=cand_start,
                    end_time=cand_end,
                )
            )
        finally:
            loop.close()

    session = SessionLocal()
    try:
        event = _run_async()

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
            session, candidate_id, meet_link, interview_time
        )
        candidate = session.query(type(candidate_id)).get(candidate_id)
        if candidate:
            candidate.status = "Interview Scheduled"
            session.commit()

        # Send email
        time_str = cand_start.strftime("%A, %B %d at %I:%M %p UTC")
        email_sent = email_service.send_interview_invite(
            to_email=candidate_email,
            candidate_name=candidate_name,
            interview_link=meet_link,
            interview_time=time_str,
        )

        return {
            "candidate_id": candidate_id,
            "name": candidate_name,
            "email": candidate_email,
            "interview_time": event["start"],
            "meet_link": meet_link,
            "email_sent": email_sent,
            "status": "Scheduled",
        }
    except Exception as e:
        return {
            "candidate_id": candidate_id,
            "name": candidate_name,
            "email": candidate_email,
            "error": str(e),
            "status": "Failed",
        }
    finally:
        session.close()


@router.post("/schedule")
async def schedule_interviews(
    interview_duration_minutes: int = Query(60, ge=15, le=240),
    start_time_str: Optional[str] = Query(None),
    candidate_ids: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Schedule interviews for candidates who received test links and have completed their test.
    All scheduling runs in background threads — the request returns immediately.
    """
    candidates = candidate_repository.get_all(db)
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

    timezone = pytz.UTC

    if start_time_str:
        start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
    else:
        start_time = datetime.now(timezone).replace(
            hour=10, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)

    # Dispatch all candidates concurrently via ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for i, candidate in enumerate(eligible):
            cand_start = start_time + timedelta(minutes=i * (interview_duration_minutes + 15))
            cand_end = cand_start + timedelta(minutes=interview_duration_minutes)
            futures.append(
                executor.submit(
                    _schedule_one_sync,
                    candidate.id, candidate.email, candidate.name,
                    cand_start, cand_end,
                )
            )
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

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
