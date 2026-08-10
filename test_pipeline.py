"""Test pipeline on one candidate directly."""
import sys
sys.path.insert(0, '.')

from backend.database.connection import SessionLocal
from backend.repositories.candidate_repository import candidate_repository
from backend.pipeline.pipeline_engine import pipeline_engine

db = SessionLocal()
try:
    # Get candidate 1
    candidate = candidate_repository.get_by_id(db, 1)
    print("Candidate:", candidate.id, candidate.name, candidate.status, candidate.job_id)
    print("Resume text (first 100):", candidate.resume_text[:100] if candidate.resume_text else None)
    print("GitHub URL:", candidate.github_url)

    # Run pipeline
    print("\nRunning pipeline...")
    result = pipeline_engine.run(db, candidate)
    print("After pipeline:")
    print("  status:", result.status)
    print("  final_score:", result.final_score)
    print("  candidate_rank:", result.candidate_rank)

    # Check evaluations
    from backend.repositories.evaluation_repository import evaluation_repository
    ev = evaluation_repository.get_latest_for_candidate(db, candidate.id)
    print("\nEvaluation:", ev)
    if ev:
        print("  overall_score:", ev.overall_score)
        print("  technical_score:", ev.technical_score)
        print("  project_score:", ev.project_score)
finally:
    db.close()
