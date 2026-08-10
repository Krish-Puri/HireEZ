"""
Score Calculator

Calculates the final candidate score using weighted metrics.
"""

from backend.models.candidate import Candidate
from backend.models.evaluation import Evaluation


class ScoreCalculator:

    # -----------------------------
    # Weights
    # -----------------------------

    AI_WEIGHT = 0.60

    GITHUB_WEIGHT = 0.25

    CGPA_WEIGHT = 0.10

    RESEARCH_WEIGHT = 0.05

    def calculate(
        self,
        candidate: Candidate,
        evaluation: Evaluation,
    ) -> float:

        # -----------------------------
        # AI Score (0-100)
        # -----------------------------

        ai_score = evaluation.overall_score or 0

        # -----------------------------
        # GitHub Score (0-100)
        # -----------------------------

        github_score = candidate.github_score or 0

        # -----------------------------
        # CGPA Normalization
        # Example:
        # 9.1 CGPA -> 91
        # -----------------------------

        cgpa_score = 0

        if candidate.cgpa is not None:

            cgpa_score = min(
                candidate.cgpa * 10,
                100,
            )

        # -----------------------------
        # Research Score
        # -----------------------------

        research_score = 0

        if (
            candidate.research_work
            and candidate.research_work.strip()
        ):
            research_score = 100

        # -----------------------------
        # Final Weighted Score
        # -----------------------------

        final_score = (

            ai_score * self.AI_WEIGHT

            + github_score * self.GITHUB_WEIGHT

            + cgpa_score * self.CGPA_WEIGHT

            + research_score * self.RESEARCH_WEIGHT

        )

        return round(final_score, 2)


score_calculator = ScoreCalculator()