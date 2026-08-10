"""Skill Parser"""

from backend.intelligence.parsers.base_parser import BaseParser

KNOWN_SKILLS = {
    "python",
    "java",
    "c++",
    "sql",
    "mysql",
    "postgresql",
    "fastapi",
    "flask",
    "streamlit",
    "react",
    "next.js",
    "tailwind",
    "docker",
    "git",
    "github",
    "linux",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "pandas",
    "numpy",
    "opencv",
    "langchain",
    "llm",
    "machine learning",
    "deep learning",
    "nlp",
    "computer vision",
}


class SkillParser(BaseParser):

    def parse(self, text: str) -> list[str]:

        cleaned = self.clean_text(text).lower()

        found = []

        for skill in KNOWN_SKILLS:
            if skill.lower() in cleaned:
                found.append(skill.title())

        return sorted(set(found))
