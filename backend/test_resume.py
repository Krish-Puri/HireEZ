from backend.services.resume.downloader import resume_downloader
from backend.services.resume.extractor import resume_extractor

url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

path = resume_downloader.download_resume(
    candidate_id=1,
    resume_url=url,
)

print(path)

document = resume_extractor.extract_document(path)

print(document.raw_text[:1000])