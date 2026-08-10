from dataclasses import dataclass


@dataclass
class ResumeDocument:

    file_path: str

    raw_text: str

    page_count: int

    character_count: int