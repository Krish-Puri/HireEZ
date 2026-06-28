"""Abstract AI Provider"""

from abc import ABC, abstractmethod


class AIProvider(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str,
    ) -> str:
        """
        Returns raw LLM response.
        """
        pass
