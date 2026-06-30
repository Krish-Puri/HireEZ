"""AI prompt builder."""

from backend.evaluation.rubric import EvaluationRubric
from backend.intelligence.profile import CandidateProfile
from backend.models.job import Job


class PromptBuilder:

    def _build_system_prompt(self) -> str:
        return (
            "You are an experienced Senior Technical Recruiter. "
            "Evaluate the candidate ONLY against the supplied job description. "
            "Use the supplied rubric. Never invent information. "
            "Do not assume missing skills. Return STRICT JSON. "
            "Do not use markdown. Do not wrap the JSON inside code blocks. "
            "Your output must be valid JSON."
        )

    def _build_job_section(self, job: Job) -> str:
        return (
            f"Job Title: {job.title}\n"
            f"Company: {job.company}\n"
            f"Department: {job.department or 'N/A'}\n"
            f"Description: {job.description}\n"
            f"Required Skills: {job.required_skills or 'N/A'}\n"
            f"Preferred Skills: {job.preferred_skills or 'N/A'}\n"
            f"Minimum CGPA: {job.minimum_cgpa or 'N/A'}\n"
        )

    def _build_rubric_section(self, rubric: EvaluationRubric) -> str:
        return (
            "Rubric:\n"
            f"  Technical Skills: {rubric.technical_skills}%\n"
            f"  Projects: {rubric.projects}%\n"
            f"  Education: {rubric.education}%\n"
            f"  Research: {rubric.research}%\n"
            f"  Communication: {rubric.communication}%\n"
        )

    def _build_candidate_section(self, profile: CandidateProfile) -> str:
        return (
            f"Candidate Skills: {', '.join(profile.skills) or 'N/A'}\n"
            f"Candidate Education: {', '.join(profile.education) or 'N/A'}\n"
            f"Candidate Projects: {', '.join(profile.projects) or 'N/A'}\n"
            f"Candidate Research: {', '.join(profile.research) or 'N/A'}\n"
            f"Candidate Achievements: {', '.join(profile.achievements) or 'N/A'}\n"
            f"Candidate Summary: {profile.summary or 'N/A'}\n"
        )

    def _build_output_schema(self) -> str:
        return (
            "Return strictly valid JSON with the following schema:\n"
            "{\n"
            "  \"overall_score\": 0,\n"
            "  \"technical_score\": 0,\n"
            "  \"project_score\": 0,\n"
            "  \"education_score\": 0,\n"
            "  \"research_score\": 0,\n"
            "  \"communication_score\": 0,\n"
            "  \"best_project\": \"\",\n"
            "  \"strengths\": [],\n"
            "  \"concerns\": [],\n"
            "  \"missing_skills\": [],\n"
            "  \"interview_questions\": [],\n"
            "  \"recommendation\": \"\",\n"
            "  \"summary\": \"\"\n"
            "}"
        )

    def build(
        self,
        candidate_profile: CandidateProfile,
        job: Job,
        rubric: EvaluationRubric,
    ) -> str:
        sections = [
            self._build_system_prompt(),
            self._build_job_section(job),
            self._build_candidate_section(candidate_profile),
            self._build_rubric_section(rubric),
            self._build_output_schema(),
        ]
        return "\n\n".join(sections)


prompt_builder = PromptBuilder()
