"""Evaluation engine orchestration."""

from dataclasses import dataclass

from backend.evaluation.prompt_builder import PromptBuilder
from backend.evaluation.rubric import EvaluationRubric
from backend.intelligence.profile import CandidateProfile
from backend.models.job import Job


@dataclass
class EvaluationResult:
    overall_score: float
    technical_score: float
    project_score: float
    education_score: float
    research_score: float
    communication_score: float
    strengths: list[str]
    concerns: list[str]
    recommendation: str


class Evaluator:

    def __init__(self):
        self.prompt_builder = PromptBuilder()

    def evaluate(
        self,
        profile: CandidateProfile,
        job: Job,
        rubric: EvaluationRubric,
    ) -> EvaluationResult:
        prompt = self.prompt_builder.build(profile, job, rubric)
        # TODO: integrate Gemini / LLM here
        return EvaluationResult(
            overall_score=0.0,
            technical_score=0.0,
            project_score=0.0,
            education_score=0.0,
            research_score=0.0,
            communication_score=0.0,
            strengths=[],
            concerns=[],
            recommendation="Pending",
        )


evaluator = Evaluator()