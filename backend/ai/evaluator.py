"""AI evaluation orchestration."""

from dataclasses import dataclass

from backend.ai.providers.gemini_provider import GeminiProvider
from backend.ai.prompt_builder import prompt_builder
from backend.ai.response_parser import response_parser
from backend.evaluation.rubric import EvaluationRubric
from backend.evaluation.result import EvaluationResult
from backend.intelligence.profile import CandidateProfile
from backend.models.job import Job


@dataclass
class EvaluationArtifact:
    prompt: str
    raw_response: str
    result: EvaluationResult


class AIEvaluator:

    def __init__(self, provider: GeminiProvider | None = None):
        self.provider = provider or GeminiProvider()

    def evaluate(
        self,
        candidate_profile: CandidateProfile,
        job: Job,
        rubric: EvaluationRubric,
    ) -> EvaluationArtifact:
        prompt = prompt_builder.build(candidate_profile, job, rubric)
        raw_response = self.provider.generate(prompt)
        result = response_parser.parse(raw_response)
        return EvaluationArtifact(
            prompt=prompt,
            raw_response=raw_response,
            result=result,
        )


ai_evaluator = AIEvaluator()
