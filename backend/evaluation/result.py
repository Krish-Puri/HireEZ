"""Evaluation Result Domain Object"""

from dataclasses import dataclass, field


@dataclass
class EvaluationResult:
    overall_score: float
    technical_score: float
    project_score: float
    education_score: float
    research_score: float
    communication_score: float
    strengths: list[str] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    interview_questions: list[str] = field(default_factory=list)
    recommendation: str = ""
    summary: str = ""
