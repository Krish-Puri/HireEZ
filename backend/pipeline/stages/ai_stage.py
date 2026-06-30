"""AI processing stage."""

from backend.ai.evaluator import ai_evaluator
from backend.core.constants import CandidateStatus
from backend.evaluation.defaults import DEFAULT_RUBRIC
from backend.intelligence.extractor import candidate_intelligence_engine
from backend.pipeline.stages.base_stage import PipelineStage
from backend.models.candidate import Candidate
from backend.services.evaluation_service import evaluation_service
from backend.services.job_service import job_service
from sqlalchemy.orm import Session


class AIStage(PipelineStage):

    @property
    def name(self) -> str:
        return "AI Evaluation"

    def execute(self, db: Session, candidate: Candidate) -> Candidate:
        candidate.status = CandidateStatus.AI_EVALUATION
        db.commit()

        if not candidate.resume_text:
            candidate.status = CandidateStatus.FAILED
            db.commit()
            return candidate

        try:
            profile = candidate_intelligence_engine.extract(candidate.resume_text)
            job = job_service.get_first_job(db)

            if job is None:
                candidate.status = CandidateStatus.FAILED
                candidate.resume_text = f"[No job created] {candidate.resume_text[:500]}"
                db.commit()
                return candidate

            result = ai_evaluator.evaluate(
                candidate_profile=profile,
                job=job,
                rubric=DEFAULT_RUBRIC,
            )
            evaluation_service.save_evaluation(
                db=db,
                candidate=candidate,
                job=job,
                result=result.result,
                raw_response=result.raw_response,
            )
            candidate.status = CandidateStatus.AI_EVALUATED
        except Exception as e:
            candidate.status = CandidateStatus.FAILED
            candidate.resume_text = f"[AI Error: {str(e)[:200]}] {candidate.resume_text[:300]}"

        db.commit()
        db.refresh(candidate)
        return candidate