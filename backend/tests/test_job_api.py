import tempfile
import json

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_job_crud():
    payload = {
        "title": "Software Engineer",
        "company": "HireEZ",
        "department": "Engineering",
        "description": "Build AI hiring tools.",
        "required_skills": "Python, FastAPI",
        "preferred_skills": "Docker, SQL",
        "minimum_cgpa": "7.0",
    }

    response = client.post("/jobs/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Software Engineer"

    response = client.get("/jobs/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    job_id = data["id"]
    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["company"] == "HireEZ"
