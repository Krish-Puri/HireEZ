"""
Resume Storage Service

Responsible for generating local resume paths.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

RESUME_DIRECTORY = PROJECT_ROOT / "storage" / "resumes"

RESUME_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True
)


class ResumeStorage:

    def get_resume_path(
        self,
        candidate_id: int
    ) -> Path:

        return RESUME_DIRECTORY / f"candidate_{candidate_id}.pdf"


resume_storage = ResumeStorage()