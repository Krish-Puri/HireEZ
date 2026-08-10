"""Education Parser"""

from backend.intelligence.parsers.base_parser import BaseParser

DEGREES = [
    "B.Tech",
    "Bachelor",
    "BE",
    "M.Tech",
    "Master",
    "PhD",
    "Diploma",
]


class EducationParser(BaseParser):

    def parse(self, text: str) -> list[str]:
        cleaned = self.clean_text(text)

        found = []

        for degree in DEGREES:
            if degree.lower() in cleaned.lower():
                found.append(degree)

        return sorted(set(found))
