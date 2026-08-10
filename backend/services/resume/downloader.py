"""
Resume Downloader
"""

import requests

from backend.services.resume.storage import resume_storage


class ResumeDownloader:

    def download_resume(
        self,
        candidate_id: int,
        resume_url: str,
    ) -> str:

        response = requests.get(
            resume_url,
            timeout=30,
        )

        response.raise_for_status()

        save_path = resume_storage.get_resume_path(
            candidate_id
        )

        with open(save_path, "wb") as file:

            file.write(response.content)

        return str(save_path)


resume_downloader = ResumeDownloader()