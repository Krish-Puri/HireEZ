from backend.pipeline.stages.base_stage import PipelineStage

from backend.models.candidate import Candidate

from sqlalchemy.orm import Session


class ResumeStage(PipelineStage):

    @property
    def name(self):

        return "Resume Stage"

    def execute(
        self,
        db: Session,
        candidate: Candidate
    ):

        candidate.status = "Resume Parsing"

        db.commit()

        db.refresh(candidate)

        return candidate