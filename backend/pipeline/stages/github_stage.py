"""GitHub analysis pipeline stage."""

from backend.core.constants import CandidateStatus
from backend.pipeline.stages.base_stage import PipelineStage
from backend.models.candidate import Candidate
from backend.github.github_service import github_service
from sqlalchemy.orm import Session


class GithubStage(PipelineStage):

    @property
    def name(self) -> str:
        return "GitHub Analysis"

    def execute(self, db: Session, candidate: Candidate) -> Candidate:
        candidate.status = CandidateStatus.GITHUB_ANALYSIS
        db.commit()

        if not candidate.github_url:
            # No GitHub URL — skip but don't fail
            candidate.github_score = 0.0
            candidate.github_summary = "No GitHub URL provided"
            candidate.top_languages = ""
            db.commit()
            return candidate

        try:
            profile = github_service.analyze_candidate(candidate.github_url)
            if profile:
                candidate.github_score = profile.github_score or 0.0
                candidate.github_summary = profile.summary or ""
                candidate.top_languages = ",".join(profile.top_languages) if profile.top_languages else ""
            else:
                candidate.github_score = 0.0
                candidate.github_summary = "GitHub profile not found or inaccessible"
                candidate.top_languages = ""
        except Exception as e:
            candidate.github_score = 0.0
            candidate.github_summary = f"GitHub API error: {str(e)[:100]}"
            candidate.top_languages = ""

        db.commit()
        db.refresh(candidate)
        return candidate
