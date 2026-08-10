"""
GitHub API Client
"""

try:
    import requests
except ImportError:  # pragma: no cover - environment fallback
    requests = None

from backend.config import config


class GitHubClient:

    BASE_URL = "https://api.github.com"

    def __init__(self):

        self.headers = {
            "Accept": "application/vnd.github+json",
        }
        token = getattr(config, "GITHUB_TOKEN", None)
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def extract_username(
        self,
        github_url: str,
    ) -> str:

        return github_url.rstrip("/").split("/")[-1]

    def get_user(
        self,
        github_url: str,
    ):

        if requests is None:
            raise RuntimeError("requests package is required for GitHub API access")

        username = self.extract_username(github_url)

        response = requests.get(
            f"{self.BASE_URL}/users/{username}",
            headers=self.headers,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def get_repositories(
        self,
        github_url: str,
    ):

        if requests is None:
            raise RuntimeError("requests package is required for GitHub API access")

        username = self.extract_username(github_url)

        response = requests.get(
            f"{self.BASE_URL}/users/{username}/repos",
            headers=self.headers,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def get_languages(
        self,
        github_url: str,
    ):

        if requests is None:
            raise RuntimeError("requests package is required for GitHub API access")

        username = self.extract_username(github_url)

        response = requests.get(
            f"{self.BASE_URL}/users/{username}/repos",
            headers=self.headers,
            timeout=30,
        )

        response.raise_for_status()

        repos = response.json()
        languages: dict[str, int] = {}
        for repo in repos:
            repo_name = repo.get("name")
            if not repo_name:
                continue
            lang_response = requests.get(
                f"{self.BASE_URL}/repos/{username}/{repo_name}/languages",
                headers=self.headers,
                timeout=30,
            )
            if lang_response.ok:
                for lang, count in lang_response.json().items():
                    languages[lang] = languages.get(lang, 0) + count
        return languages


github_client = GitHubClient()