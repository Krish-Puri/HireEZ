"""Ranking pipeline stage."""

from backend.core.constants import CandidateStatus
from backend.pipeline.stages.base_stage import PipelineStage
from backend.models.candidate import Candidate
from backend.ranking.ranking_engine import ranking_engine
from sqlalchemy.orm import Session


class RankingStage(PipelineStage):

    @property
    def name(self) -> str:
        return "Ranking"

    def execute(self, db: Session, candidate: Candidate) -> Candidate:
        try:
            result = ranking_engine.rank_candidate(db, candidate)
            if result:
                candidate.final_score = result.final_score
                candidate.candidate_rank = 0
                candidate.status = CandidateStatus.RANKED
            else:
                # No evaluation found — do NOT overwrite status (keep FAILED from AI stage)
                pass
        except Exception:
            candidate.status = CandidateStatus.FAILED
            candidate.final_score = 0
            candidate.candidate_rank = None

        db.commit()
        db.refresh(candidate)
        return candidate
