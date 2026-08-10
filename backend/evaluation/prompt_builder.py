"""Prompt builder for the evaluation engine."""

from backend.evaluation.rubric import EvaluationRubric
from backend.intelligence.profile import CandidateProfile
from backend.models.job import Job


class PromptBuilder:

    def build(self, profile: CandidateProfile, job: Job, rubric: EvaluationRubric) -> str:
        return (
            f"Job Title: {job.title}\n"
            f"Company: {job.company}\n"
            f"Department: {job.department or 'N/A'}\n"
            f"Description: {job.description}\n"
            f"Required Skills: {job.required_skills or 'N/A'}\n"
            f"Preferred Skills: {job.preferred_skills or 'N/A'}\n"
            f"Minimum CGPA: {job.minimum_cgpa or 'N/A'}\n\n"
            f"Candidate Skills: {', '.join(profile.skills) or 'N/A'}\n"
            f"Candidate Education: {', '.join(profile.education) or 'N/A'}\n"
            f"Candidate Projects: {', '.join(profile.projects) or 'N/A'}\n"
            f"Candidate Research: {', '.join(profile.research) or 'N/A'}\n"
            f"Rubric: Technical Skills {rubric.technical_skills}%, Projects {rubric.projects}%, "
            f"Education {rubric.education}%, Research {rubric.research}%, Communication {rubric.communication}%\n"
            f"Return STRICT JSON."
        )
