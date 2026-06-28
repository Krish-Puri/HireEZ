from backend.intelligence.extractor import candidate_intelligence_engine

resume = """
Krish Puri

B.Tech in Computer Science

Skills

Python

FastAPI

Machine Learning

Docker

Git

Projects

HireEZ

BookMate

"""

profile = candidate_intelligence_engine.extract(resume)

print(profile)
