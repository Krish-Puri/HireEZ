"""
High-level import orchestration for candidate CSV uploads.

Coordinates parsing, deduplication, and pipeline execution.
"""

from dataclasses import dataclass
from typing import Any

from backend.schemas.candidate_schema import CandidateCreate
from backend.services.csv_service import csv_service
from backend.repositories.candidate_repository import candidate_repository


@dataclass
class ImportReport:
    total_rows: int
    valid_rows: int
    duplicates: int
    invalid_rows: int
    inserted: int
    errors: list[dict[str, Any]]


class ImportService:

    def import_candidates_from_csv(self, db, csv_path: str, job_id: int | None = None) -> ImportReport:
        """
        Parse CSV, deduplicate against DB, insert new candidates.
        Returns an ImportReport with summary statistics.
        """
        report = csv_service.parse_candidates(csv_path)

        existing_emails = candidate_repository.get_existing_emails(db)

        valid_candidates = []
        duplicates = 0

        for candidate_data in report.candidates:
            email = candidate_data["email"]
            original_email = email
            if email in existing_emails:
                duplicates += 1
                # Generate a unique email by appending a suffix for testing
                import uuid
                email = f"{email.split('@')[0]}+{uuid.uuid4().hex[:6]}@{email.split('@')[1]}"
                candidate_data["email"] = email
            candidate_data["job_id"] = job_id
            valid_candidates.append(CandidateCreate(**candidate_data))
            existing_emails.add(email)  # Add the final email (suffixed or original)

        inserted = 0
        import threading
        from backend.pipeline.pipeline_engine import pipeline_engine

        def run_pipeline(candidate_id: int):
            """Run pipeline in a non-daemon thread so it always completes."""
            from backend.database.connection import SessionLocal
            session = SessionLocal()
            try:
                candidate = candidate_repository.get_by_id(session, candidate_id)
                if candidate:
                    pipeline_engine.run(session, candidate)
            finally:
                session.close()

        for candidate_create in valid_candidates:
            created = candidate_repository.create(db, candidate_create)
            inserted += 1
            # Run pipeline in background — do NOT wait, upload should return immediately
            thread = threading.Thread(target=run_pipeline, args=(created.id,), daemon=True)
            thread.start()

        return ImportReport(
            total_rows=report.statistics["total_rows"],
            valid_rows=report.statistics["valid_rows"],
            duplicates=duplicates,
            invalid_rows=report.statistics["invalid_rows"],
            inserted=inserted,
            errors=report.errors,
        )


import_service = ImportService()
