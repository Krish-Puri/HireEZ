from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException,
    Form,
)

from pathlib import Path

from sqlalchemy.orm import Session

import shutil
import uuid

from backend.database.connection import get_db
from backend.services.import_service import import_service
from backend.repositories.candidate_repository import candidate_repository
from backend.schemas.candidate_schema import CandidateCreate


router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"],
)


# Use /tmp for uploads — Render's filesystem is read-only except /tmp
UPLOAD_FOLDER = Path("/tmp/hireez-uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_candidates(
    file: UploadFile = File(...),
    job_id: str = Form(""),
    db: Session = Depends(get_db),
):
    allowed = (".csv", ".xlsx", ".xls")
    if not any(file.filename.lower().endswith(ext) for ext in allowed):
        raise HTTPException(
            status_code=400,
            detail="Only .csv and .xlsx (Excel) files are supported."
        )

    file_path = UPLOAD_FOLDER / file.filename

    # Seek to start in case the upload stream has been partially consumed
    try:
        file.file.seek(0)
    except Exception:
        pass

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        parsed_job_id = int(job_id) if job_id.strip() else None
        report = import_service.import_candidates_from_csv(db, str(file_path), job_id=parsed_job_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "success": True,
        "summary": {
            "total_rows": report.total_rows,
            "valid_candidates": report.valid_rows,
            "duplicates": report.duplicates,
            "inserted": report.inserted,
            "invalid_rows": report.invalid_rows,
        },
        "errors": report.errors,
    }


@router.get("/")
async def list_candidates(db: Session = Depends(get_db)):
    candidates = candidate_repository.get_all(db)
    return [
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "college": c.college,
            "branch": c.branch,
            "cgpa": c.cgpa,
            "best_ai_project": c.best_ai_project,
            "research_work": c.research_work,
            "github_url": c.github_url,
            "resume_url": c.resume_url,
            "github_score": c.github_score,
            "github_summary": c.github_summary,
            "top_languages": c.top_languages,
            "resume_text": c.resume_text,
            "status": c.status,
            "final_score": c.final_score,
            "candidate_rank": c.candidate_rank,
            "test_la": c.test_la,
            "test_code": c.test_code,
            "job_id": c.job_id,
            "created_at": str(c.created_at) if c.created_at else None,
        }
        for c in candidates
    ]


@router.post("/rank-all")
async def rank_all(db: Session = Depends(get_db)):
    """
    Re-rank all candidates and update their final_score and candidate_rank.
    Should be called after all candidates have been processed through the pipeline.
    """
    from backend.ranking.ranking_engine import ranking_engine
    ranking = ranking_engine.rank_all_candidates(db)
    return {
        "success": True,
        "ranked": len(ranking),
        "results": [
            {
                "id": c.id,
                "name": c.name,
                "final_score": c.final_score,
                "candidate_rank": c.candidate_rank,
            }
            for c, r in ranking
        ]
    }


@router.post("/rerun-github")
async def rerun_github(db: Session = Depends(get_db)):
    """
    Re-run GitHub analysis for all candidates that don't have a github_score yet.
    Useful when GitHub analysis failed previously or needs to be refreshed.
    """
    import threading
    from backend.pipeline.stages.github_stage import GithubStage

    all_candidates = candidate_repository.get_all(db)
    pending = [c for c in all_candidates if c.github_score is None]

    def _run_github_async(candidate_id):
        from backend.database.connection import SessionLocal
        session = SessionLocal()
        try:
            candidate = session.query(type(all_candidates[0])).get(candidate_id)
            if candidate:
                stage = GithubStage()
                stage.execute(session, candidate)
        finally:
            session.close()

    for c in pending:
        t = threading.Thread(target=_run_github_async, args=(c.id,), daemon=True)
        t.start()

    return {
        "success": True,
        "pending_count": len(pending),
        "message": f"GitHub analysis re-started for {len(pending)} candidates in the background.",
    }


@router.post("/rerun-ai")
async def rerun_ai(db: Session = Depends(get_db)):
    """
    Re-run AI evaluation for all candidates that don't have a final_score yet.
    Useful when AI evaluation failed previously or needs to be refreshed.
    """
    import threading
    from backend.pipeline.stages.ai_stage import AIStage

    all_candidates = candidate_repository.get_all(db)
    pending = [c for c in all_candidates if c.final_score is None]

    def _run_ai_async(candidate_id):
        from backend.database.connection import SessionLocal
        session = SessionLocal()
        try:
            candidate = session.query(type(all_candidates[0])).get(candidate_id)
            if candidate:
                stage = AIStage()
                stage.execute(session, candidate)
        finally:
            session.close()

    for c in pending:
        t = threading.Thread(target=_run_ai_async, args=(c.id,), daemon=True)
        t.start()

    return {
        "success": True,
        "pending_count": len(pending),
        "message": f"AI evaluation re-started for {len(pending)} candidates in the background.",
    }


@router.post("/resume-upload")
async def resume_upload(
    resume: UploadFile = File(...),
    name: str = Form(...),
    email: str = Form(...),
    college: str = Form(""),
    branch: str = Form(""),
    cgpa: str = Form(""),
    best_ai_project: str = Form(""),
    research_work: str = Form(""),
    github_url: str = Form(""),
    job_id: str = Form(""),
    db: Session = Depends(get_db),
):
    """
    Candidate-facing resume upload endpoint.
    Accepts a PDF resume and candidate info, creates a candidate record,
    saves the resume to disk, and triggers the AI evaluation pipeline.
    """
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Check for duplicate email
    existing = candidate_repository.get_by_email(db, email.lower())
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"A candidate with email '{email}' already exists. Please use a unique email address."
        )

    # Save PDF resume to /tmp — Render filesystem is read-only except /tmp
    RESUME_FOLDER = Path("/tmp/hireez-resumes")
    RESUME_FOLDER.mkdir(parents=True, exist_ok=True)

    file_ext = ".pdf"
    safe_email = email.lower().replace("@", "_at_").replace(".", "_")
    unique_name = f"{safe_email}_{uuid.uuid4().hex[:6]}{file_ext}"
    file_path = RESUME_FOLDER / unique_name

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)

    # Build candidate
    try:
        cgpa_val = float(cgpa) if cgpa and cgpa.strip() else None
    except ValueError:
        cgpa_val = None

    candidate_create = CandidateCreate(
        name=name.strip(),
        email=email.lower().strip(),
        college=college.strip() or None,
        branch=branch.strip() or None,
        cgpa=cgpa_val,
        best_ai_project=best_ai_project.strip() or None,
        research_work=research_work.strip() or None,
        github_url=github_url.strip() or None,
        resume_url=str(file_path),  # local path to uploaded PDF
    )

    # Insert and run pipeline
    created = candidate_repository.create(db, candidate_create)

    # Trigger pipeline (async in background would be better, but sync for now)
    from backend.pipeline.pipeline_engine import pipeline_engine
    pipeline_engine.run(db, created)

    return {
        "success": True,
        "candidate_id": created.id,
        "message": f"Application submitted! '{name}' is now being evaluated by our AI.",
    }
