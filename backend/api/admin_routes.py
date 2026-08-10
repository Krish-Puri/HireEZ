"""
Admin Routes

Data management endpoints (clear candidates, test results, etc.)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.database.connection import get_db


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/clear-candidates")
async def clear_candidates(db: Session = Depends(get_db)):
    """Delete all candidates and their evaluations and reset auto_increment."""
    from backend.models.candidate import Candidate
    from backend.models.evaluation import Evaluation
    cur = db.execute(text("SELECT id FROM candidates"))
    candidate_ids = [row[0] for row in cur.fetchall()]
    if candidate_ids:
        placeholders = ",".join([f":id{i}" for i in range(len(candidate_ids))])
        params = {f"id{i}": cid for i, cid in enumerate(candidate_ids)}
        db.execute(text(f"DELETE FROM evaluations WHERE candidate_id IN ({placeholders})"), params)
    db.execute(text("DELETE FROM candidates"))
    db.execute(text("ALTER TABLE candidates AUTO_INCREMENT = 1"))
    db.execute(text("ALTER TABLE evaluations AUTO_INCREMENT = 1"))
    db.commit()
    return {"success": True, "message": f"Deleted {len(candidate_ids)} candidates"}


@router.post("/clear-test-results")
async def clear_test_results(db: Session = Depends(get_db)):
    """Delete all test results and reset auto_increment."""
    db.execute(text("DELETE FROM test_results"))
    db.execute(text("UPDATE candidates SET test_la = NULL, test_code = NULL"))
    db.execute(text("ALTER TABLE test_results AUTO_INCREMENT = 1"))
    db.commit()
    return {"success": True}


@router.post("/clear-all")
async def clear_all(db: Session = Depends(get_db)):
    """Delete all candidates, test results, and evaluations and reset auto_increment."""
    db.execute(text("DELETE FROM test_results"))
    db.execute(text("DELETE FROM evaluations"))
    db.execute(text("DELETE FROM candidates"))
    db.execute(text("ALTER TABLE candidates AUTO_INCREMENT = 1"))
    db.execute(text("ALTER TABLE evaluations AUTO_INCREMENT = 1"))
    db.execute(text("ALTER TABLE test_results AUTO_INCREMENT = 1"))
    db.commit()
    return {"success": True}