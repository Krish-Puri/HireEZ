"""
Resume Storage Service

Responsible for generating local resume paths.
"""

from pathlib import Path


# Use /tmp for resumes — Render's filesystem is read-only except /tmp
RESUME_DIRECTORY = Path("/tmp/hireez-resumes")

RESUME_DIRECTORY.mkdir(parents=True, exist_ok=True)


class ResumeStorage:

    def get_resume_path(
        self,
        candidate_id: int
    ) -> Path:

        return RESUME_DIRECTORY / f"candidate_{candidate_id}.pdf"


resume_storage = ResumeStorage()