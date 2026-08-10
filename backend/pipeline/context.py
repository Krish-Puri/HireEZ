"""Pipeline context object for staged processing."""

from dataclasses import dataclass

from backend.evaluation.result import EvaluationResult
from backend.intelligence.profile import CandidateProfile
from backend.models.candidate import Candidate
from backend.models.job import Job


@dataclass
class PipelineContext:
    candidate: Candidate
    job: Job | None = None
    profile: CandidateProfile | None = None
    evaluation: EvaluationResult | None = None
