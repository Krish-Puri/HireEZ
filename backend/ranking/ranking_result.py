"""
Ranking Result Domain Model

Represents the final computed ranking of a candidate.
"""

from dataclasses import dataclass


@dataclass
class RankingResult:

    final_score: float

    ai_score: float

    github_score: float

    cgpa_score: float

    research_score: float

    rank: int = 0