from backend.intelligence.profile import CandidateProfile

from backend.intelligence.parsers.skill_parser import SkillParser
from backend.intelligence.parsers.education_parser import EducationParser


class CandidateIntelligenceEngine:

    def __init__(self):
        self.skill_parser = SkillParser()
        self.education_parser = EducationParser()

    def extract(
        self,
        resume_text: str,
    ) -> CandidateProfile:

        profile = CandidateProfile()

        profile.skills = self.skill_parser.parse(resume_text)
        profile.education = self.education_parser.parse(resume_text)

        return profile


candidate_intelligence_engine = CandidateIntelligenceEngine()