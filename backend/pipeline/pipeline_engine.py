"""Pipeline Engine"""

import logging
import time

from backend.pipeline.stages.resume_stage import ResumeStage
from backend.pipeline.stages.github_stage import GithubStage
from backend.pipeline.stages.ai_stage import AIStage
from backend.pipeline.stages.ranking_stage import RankingStage

logger = logging.getLogger(__name__)


class PipelineEngine:

    def __init__(self):
        self.stages = [
            ResumeStage(),
            GithubStage(),
            AIStage(),
            RankingStage(),
        ]

    def run(self, db, candidate):
        for stage in self.stages:
            logger.info(f"Starting {stage.name}")
            start = time.perf_counter()
            candidate = stage.execute(db, candidate)
            elapsed = time.perf_counter() - start
            logger.info(f"Finished {stage.name} in {elapsed:.2f}s")
        return candidate


pipeline_engine = PipelineEngine()