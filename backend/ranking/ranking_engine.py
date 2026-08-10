"""
Ranking Engine

Ranks candidates using AI evaluation,
GitHub intelligence and academic profile.
"""

from sqlalchemy.orm import Session

from backend.models.candidate import Candidate

from backend.repositories.evaluation_repository import (
    evaluation_repository,
)

from backend.ranking.score_calculator import (
    score_calculator,
)

from backend.ranking.ranking_result import (
    RankingResult,
)


class RankingEngine:

    def rank_candidate(
        self,
        db: Session,
        candidate: Candidate,
    ) -> RankingResult | None:

        evaluation = (
            evaluation_repository.get_latest_for_candidate(
                db,
                candidate.id,
            )
        )

        # Compute GitHub, CGPA, research scores regardless of AI evaluation
        github_score = candidate.github_score or 0.0
        cgpa_score = (candidate.cgpa * 10) if candidate.cgpa else 0.0
        research_score = 100 if (candidate.research_work and candidate.research_work.strip()) else 0.0

        if evaluation is None:
            # No AI evaluation — compute score from GitHub + CGPA + Research only
            # (GitHub 25% + CGPA 10% + Research 5% = 40% max instead of full 100%)
            github_contrib = github_score * (0.25 / 0.40) if github_score else 0.0  # renormalize to 100
            cgpa_contrib = cgpa_score * (0.10 / 0.40) if cgpa_score else 0.0
            research_contrib = research_score * (0.05 / 0.40) if research_score else 0.0
            final_score = round(github_contrib + cgpa_contrib + research_contrib, 2)
            return RankingResult(
                final_score=final_score,
                ai_score=0.0,
                github_score=github_score,
                cgpa_score=cgpa_score,
                research_score=research_score,
                rank=0,
            )

        final_score = score_calculator.calculate(
            candidate,
            evaluation,
        )

        cgpa_score = (
            candidate.cgpa * 10
            if candidate.cgpa
            else 0
        )

        research_score = (
            100
            if candidate.research_work
            else 0
        )

        result = RankingResult(

            final_score=final_score,

            ai_score=evaluation.overall_score,

            github_score=candidate.github_score,

            cgpa_score=cgpa_score,

            research_score=research_score,

        )

        return result

    def rank_all_candidates(
        self,
        db: Session,
    ):

        candidates = (
            db.query(Candidate)
            .all()
        )

        ranking = []

        for candidate in candidates:

            result = self.rank_candidate(
                db,
                candidate,
            )

            if result is None or result.final_score is None:
                continue

            ranking.append(
                (
                    candidate,
                    result,
                )
            )

        ranking.sort(

            key=lambda item: item[1].final_score,

            reverse=True,

        )

        for rank, (candidate, result) in enumerate(
            ranking,
            start=1,
        ):

            result.rank = rank

            # Persist score for dashboard
            candidate.final_score = result.final_score
            candidate.candidate_rank = rank

        db.commit()

        return ranking


ranking_engine = RankingEngine()