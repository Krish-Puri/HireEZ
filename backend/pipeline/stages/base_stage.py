"""
Base Pipeline Stage
"""

from abc import ABC, abstractmethod

from backend.models.candidate import Candidate
from sqlalchemy.orm import Session


class PipelineStage(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable stage name."""
        pass

    @abstractmethod
    def execute(
        self,
        db: Session,
        candidate: Candidate
    ) -> Candidate:
        """
        Executes one stage of the pipeline.

        Returns the updated candidate.
        """
        pass