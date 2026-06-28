"""
Pipeline Engine
"""

from backend.pipeline.stages.resume_stage import ResumeStage

from backend.pipeline.stages.github_stage import GithubStage

from backend.pipeline.stages.ai_stage import AIStage

from backend.pipeline.stages.ranking_stage import RankingStage


class PipelineEngine:

    def __init__(self):

        self.stages = [

            ResumeStage(),

            GithubStage(),

            AIStage(),

            RankingStage(),

        ]

    def run(
        self,
        db,
        candidate,
    ):

        for stage in self.stages:

            candidate = stage.execute(
                db,
                candidate,
            )

        return candidate


pipeline_engine = PipelineEngine()