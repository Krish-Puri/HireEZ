"""GitHub scoring model."""

from backend.github.models import GitHubProfile


def calculate_github_score(profile: GitHubProfile) -> float:
    score = 0.0

    if profile.public_repos >= 5:
        score += 20
    else:
        score += 20 * (profile.public_repos / 5)

    score += min(len(profile.ai_projects) * 8, 25)

    score += min(len(profile.top_languages) * 5, 15)
    score += min(profile.total_stars, 15)

    completeness = 0
    if profile.name:
        completeness += 1
    if profile.bio:
        completeness += 1
    if profile.top_languages:
        completeness += 1
    if profile.public_repos:
        completeness += 1
    if profile.followers is not None:
        completeness += 1

    score += min(completeness * 2, 10)

    return min(score, 100.0)
