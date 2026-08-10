"""
Resume Text Extractor
"""

import fitz

from backend.services.resume.document import ResumeDocument


class ResumeExtractor:

    def extract_document(
        self,
        pdf_path: str
    ) -> ResumeDocument:

        document = fitz.open(pdf_path)

        pages = []

        for page in document:
            pages.append(page.get_text())

        page_count = len(document)
        document.close()

        raw_text = "\n".join(pages).strip()

        return ResumeDocument(
            file_path=pdf_path,
            raw_text=raw_text,
            page_count=page_count,
            character_count=len(raw_text),
        )


resume_extractor = ResumeExtractor()