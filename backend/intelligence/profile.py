from dataclasses import dataclass, field


@dataclass
class CandidateProfile:

    skills: list[str] = field(default_factory=list)

    projects: list[str] = field(default_factory=list)

    education: list[str] = field(default_factory=list)

    research: list[str] = field(default_factory=list)

    achievements: list[str] = field(default_factory=list)

    certifications: list[str] = field(default_factory=list)

    experience: list[str] = field(default_factory=list)

    languages: list[str] = field(default_factory=list)

    summary: str = ""