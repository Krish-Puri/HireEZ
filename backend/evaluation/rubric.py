"""Evaluation rubric definition."""

from dataclasses import dataclass


@dataclass
class EvaluationRubric:
    technical_skills: int = 40
    projects: int = 25
    education: int = 15
    research: int = 10
    communication: int = 10
