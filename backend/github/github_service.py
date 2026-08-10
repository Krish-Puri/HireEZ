"""GitHub service orchestration."""

from typing import Any

from backend.github.github_client import github_client
from backend.github.models import GitHubProfile
from backend.github.analyzer import github_repository_analyzer
from backend.github.score import calculate_github_score


class GitHubService:

    def get_profile(self, github_url: str) -> dict[str, Any] | None:
        return github_client.get_user(github_url)

    def analyze_candidate(self, github_url: str) -> GitHubProfile | None:
        user = github_client.get_user(github_url)
        repos = github_client.get_repositories(github_url)
        if user is None or repos is None:
            return None

        profile = github_repository_analyzer.analyze(user, repos)
        profile.github_score = calculate_github_score(profile)
        return profile


github_service = GitHubService()
