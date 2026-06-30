from backend.github.analyzer import GitHubRepositoryAnalyzer
from backend.github.github_service import github_service


def test_analyzer_builds_profile_from_user_and_repositories():
    analyzer = GitHubRepositoryAnalyzer()
    user = {
        "login": "ada",
        "name": "Ada Lovelace",
        "public_repos": 4,
        "followers": 20,
        "following": 10,
        "bio": "ML engineer",
    }
    repos = [
        {
            "name": "ml-playground",
            "stargazers_count": 5,
            "forks_count": 1,
            "language": "Python",
            "description": "Machine Learning experiments",
            "topics": ["ai", "ml"],
        },
        {
            "name": "backend-api",
            "stargazers_count": 3,
            "forks_count": 0,
            "language": "Python",
            "description": "FastAPI service",
            "topics": ["backend"],
        },
        {
            "name": "web-ui",
            "stargazers_count": 2,
            "forks_count": 1,
            "language": "JavaScript",
            "description": "Frontend app",
            "topics": ["web"],
        },
    ]

    profile = analyzer.analyze(user, repos)

    assert profile.username == "ada"
    assert profile.name == "Ada Lovelace"
    assert profile.public_repos == 4
    assert profile.followers == 20
    assert profile.following == 10
    assert profile.bio == "ML engineer"
    assert profile.ai_projects == ["ml-playground"]
    assert profile.top_languages == ["Python", "JavaScript"]
    assert profile.dominant_stack == "Python"
    assert "AI projects" in profile.summary
    assert "Dominant Stack" in profile.summary


def test_service_uses_user_and_repositories(monkeypatch):
    user_payload = {
        "login": "grace",
        "name": "Grace Hopper",
        "public_repos": 6,
        "followers": 15,
        "following": 4,
        "bio": "Systems engineer",
    }
    repo_payload = [
        {
            "name": "llm-tools",
            "stargazers_count": 8,
            "forks_count": 2,
            "language": "Python",
            "description": "LLM utilities",
            "topics": ["llm", "ai"],
        }
    ]

    monkeypatch.setattr("backend.github.github_service.github_client.get_user", lambda url: user_payload)
    monkeypatch.setattr("backend.github.github_service.github_client.get_repositories", lambda url: repo_payload)

    profile = github_service.analyze_candidate("https://github.com/grace")

    assert profile is not None
    assert profile.username == "grace"
    assert profile.public_repos == 6
    assert profile.ai_projects == ["llm-tools"]
    assert profile.github_score > 0
    assert "repositories" in profile.summary
