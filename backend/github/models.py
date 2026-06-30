from dataclasses import dataclass, field


@dataclass
class GitHubRepository:

    name: str

    description: str

    language: str

    stars: int

    forks: int

    topics: list[str] = field(default_factory=list)

    is_ai_project: bool = False


@dataclass
class GitHubProfile:

    username: str

    name: str

    public_repos: int

    followers: int

    following: int

    bio: str | None

    repositories: list[GitHubRepository] = field(default_factory=list)

    top_languages: list[str] = field(default_factory=list)

    ai_projects: list[str] = field(default_factory=list)

    dominant_stack: str | None = None

    total_stars: int = 0

    github_score: float = 0

    summary: str = ""