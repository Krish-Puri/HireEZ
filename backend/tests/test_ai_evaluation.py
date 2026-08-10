import json

import pytest

from backend.ai.evaluator import AIEvaluator
from backend.ai.prompt_builder import prompt_builder
from backend.ai.response_parser import response_parser
from backend.evaluation.rubric import EvaluationRubric
from backend.evaluation.result import EvaluationResult
from backend.intelligence.profile import CandidateProfile
from backend.models.job import Job


class DummyProvider:
    def generate(self, prompt: str) -> str:
        assert 'Job Title:' in prompt
        assert 'Candidate Skills:' in prompt
        return json.dumps({
            "overall_score": 82.5,
            "technical_score": 40,
            "project_score": 20,
            "education_score": 10,
            "research_score": 7.5,
            "communication_score": 5,
            "strengths": ["Strong Python skills", "Relevant research experience"],
            "concerns": ["Limited cloud experience"],
            "missing_skills": ["AWS", "Docker"],
            "interview_questions": ["Describe your Python debugging process."],
            "recommendation": "Strong consider",
            "summary": "Candidate shows a solid engineering foundation with room to grow in cloud skills."
        })


def test_prompt_builder_includes_sections():
    job = Job(
        id=1,
        title="Machine Learning Engineer",
        company="HireEZ",
        description="Build ML models.",
        required_skills="Python, ML",
        preferred_skills="TensorFlow, Docker",
    )
    profile = CandidateProfile(skills=["Python", "ML"], education=["MS Computer Science"], projects=["Resume parser"], research=["NLP paper"], achievements=["Dean's list"])
    rubric = EvaluationRubric()

    prompt = prompt_builder.build(profile, job, rubric)

    assert "You are an experienced Senior Technical Recruiter" in prompt
    assert "Rubric:" in prompt
    assert "Candidate Skills:" in prompt
    assert "overall_score" in prompt


def test_response_parser_returns_evaluation_result():
    raw_json = json.dumps({
        "overall_score": 75,
        "technical_score": 30,
        "project_score": 20,
        "education_score": 10,
        "research_score": 5,
        "communication_score": 10,
        "strengths": ["Good teamwork"],
        "concerns": ["No cloud experience"],
        "missing_skills": ["AWS"],
        "interview_questions": ["How do you handle deployment?"],
        "recommendation": "Consider",
        "summary": "Candidate is promising but missing cloud expertise."
    })

    evaluation = response_parser.parse(raw_json)

    assert isinstance(evaluation, EvaluationResult)
    assert evaluation.overall_score == 75
    assert evaluation.missing_skills == ["AWS"]
    assert evaluation.interview_questions[0].startswith("How do you handle")


def test_ai_evaluator_integration():
    evaluator = AIEvaluator(provider=DummyProvider())

    job = Job(
        id=2,
        title="Backend Engineer",
        company="HireEZ",
        description="Develop backend services.",
        required_skills="Python, FastAPI",
        preferred_skills="Docker",
    )
    profile = CandidateProfile(skills=["Python", "FastAPI"], education=["BS Computer Science"], projects=["API platform"], research=[], achievements=[])
    rubric = EvaluationRubric()

    artifact = evaluator.evaluate(profile, job, rubric)

    assert artifact.prompt
    assert artifact.raw_response
    assert artifact.result.overall_score == 82.5
    assert "Docker" in artifact.result.missing_skills
