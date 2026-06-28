"""AI response parser."""

import json

from backend.evaluation.result import EvaluationResult


class ResponseParser:

    def parse(self, response: str) -> EvaluationResult:
        cleaned = (
            response
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError("Failed to parse AI response as JSON") from exc

        required_keys = {
            "overall_score",
            "technical_score",
            "project_score",
            "education_score",
            "research_score",
            "communication_score",
            "strengths",
            "concerns",
            "missing_skills",
            "interview_questions",
            "recommendation",
            "summary",
        }

        missing = required_keys - data.keys()
        if missing:
            raise ValueError(f"AI response is missing required fields: {sorted(missing)}")

        if not isinstance(data["strengths"], list) or not isinstance(data["concerns"], list):
            raise ValueError("AI response strengths and concerns must be lists")

        if not isinstance(data["missing_skills"], list) or not isinstance(data["interview_questions"], list):
            raise ValueError("AI response missing_skills and interview_questions must be lists")

        return EvaluationResult(**data)


response_parser = ResponseParser()
