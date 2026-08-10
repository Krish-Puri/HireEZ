"""
Candidate Mapper
"""

from backend.schemas.candidate_schema import CandidateCreate


class CandidateMapper:

    @staticmethod
    def clean(value):

        if value is None:

            return None

        value = str(value).strip()

        return value or None


    def map_dataframe(
        self,
        dataframe
    ) -> list[CandidateCreate]:

        candidates = []

        for _, row in dataframe.iterrows():

            candidates.append(

                CandidateCreate(

                    name=self.clean(row["Name"]),

                    email=self.clean(row["Email"]).lower(),

                    college=self.clean(row["College"]),

                    branch=self.clean(row["Branch"]),

                    cgpa=float(row["CGPA"]) if self.clean(row["CGPA"]) else None,

                    best_ai_project=self.clean(row["Best AI Project"]),

                    research_work=self.clean(row["Research Work"]),

                    github_url=self.clean(row["GitHub Profile"]),

                    resume_url=self.clean(row["Resume Link"]),

                )

            )

        return candidates


candidate_mapper = CandidateMapper()