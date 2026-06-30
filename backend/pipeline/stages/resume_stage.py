"""
Resume Stage — downloads and parses candidate resumes.

Supports:
- Google Drive shared links (publicly accessible)
- Regular PDF URLs
- Gracefully handles missing or inaccessible URLs
"""

import re
import requests

from backend.core.constants import CandidateStatus
from backend.pipeline.stages.base_stage import PipelineStage
from backend.models.candidate import Candidate
from backend.services.resume.extractor import resume_extractor
from backend.services.resume.storage import resume_storage
from sqlalchemy.orm import Session


def extract_google_drive_id(url: str) -> str | None:
    """Extract file ID from a Google Drive link."""
    patterns = [
        r"/file/d/([a-zA-Z0-9_-]+)",
        r"id=([a-zA-Z0-9_-]+)",
        r"/open\?id=([a-zA-Z0-9_-]+)",
        r"/folders/([a-zA-Z0-9_-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_google_drive_download_url(url: str) -> str | None:
    """Convert a Google Drive share link to a direct download URL."""
    file_id = extract_google_drive_id(url)
    if not file_id:
        return None
    return f"https://drive.google.com/uc?export=download&id={file_id}"


class ResumeStage(PipelineStage):

    @property
    def name(self) -> str:
        return "Resume Stage"

    def execute(self, db: Session, candidate: Candidate) -> Candidate:
        candidate.status = CandidateStatus.RESUME_PARSING
        db.commit()

        resume_url = candidate.resume_url or ""

        if not resume_url:
            candidate.status = CandidateStatus.FAILED
            candidate.resume_text = "No resume URL provided"
            db.commit()
            return candidate

        resume_url = resume_url.strip()
        file_id = extract_google_drive_id(resume_url)

        # Determine download URL
        if file_id:
            # Google Drive link
            download_url = get_google_drive_download_url(resume_url)
        else:
            download_url = resume_url

        if not download_url:
            candidate.status = CandidateStatus.FAILED
            candidate.resume_text = f"Could not parse resume URL: {resume_url}"
            db.commit()
            return candidate

        # Download the PDF
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(download_url, headers=headers, timeout=30, allow_redirects=True)
            response.raise_for_status()
        except requests.RequestException as e:
            candidate.status = CandidateStatus.FAILED
            candidate.resume_text = f"Failed to download resume: {str(e)}"
            candidate.resume_file_path = resume_url
            db.commit()
            return candidate

        content = response.content
        if len(content) < 100:
            candidate.status = CandidateStatus.FAILED
            candidate.resume_text = f"Downloaded file too small (possibly a Google Drive warning page)"
            candidate.resume_file_path = resume_url
            db.commit()
            return candidate

        # Save to local storage
        save_path = resume_storage.get_resume_path(candidate.id)
        with open(save_path, "wb") as f:
            f.write(content)
        candidate.resume_file_path = str(save_path)

        # Extract text
        try:
            doc = resume_extractor.extract_document(str(save_path))
            candidate.resume_text = doc.raw_text or "(No text extracted from PDF)"
        except Exception as e:
            candidate.status = CandidateStatus.FAILED
            candidate.resume_text = f"Failed to extract text: {str(e)}"
            db.commit()
            return candidate

        if not candidate.resume_text or candidate.resume_text == "(No text extracted from PDF)":
            candidate.status = CandidateStatus.FAILED
            db.commit()
            return candidate

        candidate.status = CandidateStatus.RESUME_PARSED
        db.commit()
        db.refresh(candidate)
        return candidate
