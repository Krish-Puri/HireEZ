"""Base Parser

Common functionality shared by all parsers.
"""

import re
from abc import ABC, abstractmethod


class BaseParser(ABC):

    def clean_text(self, text: str) -> str:
        """Normalize whitespace."""
        return re.sub(r"\s+", " ", text).strip()

    def lines(self, text: str) -> list[str]:
        """Return cleaned non-empty lines."""
        return [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

    @abstractmethod
    def parse(self, text: str):
        """Implemented by child parsers."""
        pass
