"""Analyze GitHub repositories for candidate signals."""

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from backend.github.models import GitHubProfile

AI_KEYWORDS = [
    "AI",
    "Machine Learning",
    "Deep Learning",
    "NLP",
    "Computer Vision",
    "LLM",
    "GenAI",
    "Transformer",
    "TensorFlow",
    "PyTorch",
    "OpenCV",
    "Scikit-Learn",
]


@dataclass
class RepositorySummary:
    name: str
    stars: int
    forks: int
    primary_language: str | None
    description: str | None
    topics: list[str]
    is_ai_project: bool


class GitHubRepositoryAnalyzer:

    def analyze(self, user: dict, repositories: Iterable[dict]) -> GitHubProfile:
        profile = GitHubProfile(
            username=user["login"],
            name=user.get("name") or "",
            public_repos=user["public_repos"],
            followers=user["followers"],
            following=user["following"],
            bio=user.get("bio"),
        )

        language_counter: Counter[str] = Counter()
        stack_counts: dict[str, int] = {}

        for repo in repositories:
            summary = self._summarize_repository(repo)
            if summary.primary_language:
                language_counter[summary.primary_language] += 1
                stack_counts[summary.primary_language] = stack_counts.get(summary.primary_language, 0) + 1

            if summary.is_ai_project:
                profile.ai_projects.append(summary.name)

            profile.total_stars += summary.stars

        profile.top_languages = [language for language, _ in language_counter.most_common(5)]
        profile.dominant_stack = self._determine_dominant_stack(stack_counts)
        profile.summary = self._build_summary(profile)
        return profile

    def _summarize_repository(self, repo: dict) -> RepositorySummary:
        name = repo.get("name", "")
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        primary_language = repo.get("language")
        description = repo.get("description")
        topics = repo.get("topics", []) or []
        is_ai_project = self._detect_ai_project(name, description, topics)

        return RepositorySummary(
            name=name,
            stars=stars,
            forks=forks,
            primary_language=primary_language,
            description=description,
            topics=topics,
            is_ai_project=is_ai_project,
        )

    def _detect_ai_project(self, name: str, description: str | None, topics: list[str]) -> bool:
        haystack = " ".join(
            [name, description or "", " ".join(topics)]
        ).lower()

        return any(keyword.lower() in haystack for keyword in AI_KEYWORDS)

    def _determine_dominant_stack(self, stack_counts: dict[str, int]) -> str | None:
        if not stack_counts:
            return None
        return max(stack_counts, key=stack_counts.get)

    def _build_summary(self, profile: GitHubProfile) -> str:
        dominant_stack = profile.dominant_stack or "N/A"
        return (
            f"{profile.public_repos} repositories, "
            f"{len(profile.ai_projects)} AI projects, "
            f"Top languages: {', '.join(profile.top_languages) if profile.top_languages else 'N/A'}. "
            f"Dominant Stack: {dominant_stack}"
        )


github_repository_analyzer = GitHubRepositoryAnalyzer()
