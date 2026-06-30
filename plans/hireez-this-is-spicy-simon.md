# HireEZ — Assignment Verification & Deployment Plan

## Context
The project is functionally complete — all 11 assignment requirements are implemented. This plan addresses the deployment gaps needed for assignment submission: public hosting setup, containerization, and documentation.

---

## Assignment Requirements — Verification

| # | Requirement | Status |
|---|-------------|--------|
| 1 | Upload Candidate Dataset | ✅ |
| 2 | Job Description Input | ✅ |
| 3 | Resume Processing | ✅ |
| 4 | AI-Based Candidate Evaluation (Gemini) | ✅ |
| 5 | GitHub Profile Analysis (repo-level) | ✅ |
| 6 | Candidate Ranking (AI 60%, GitHub 25%, CGPA 10%, Research 5%) | ✅ |
| 7 | Automated Emailing (SMTP test links) | ✅ |
| 8 | Test Result Upload (test_la, test_code) | ✅ |
| 9 | Interview Scheduling (Google Calendar) | ✅ |
| 10 | Real Google Meet Link Generation | ✅ |
| 11 | Frontend 11-step pipeline UI | ✅ |

---

## What's Missing for Submission

### 1. Dockerfile for FastAPI backend
Create `Dockerfile` to containerize the FastAPI backend.

### 2. docker-compose.yml for full stack
Containerize FastAPI + Streamlit + MySQL together.

### 3. .streamlit/config.toml
Create Streamlit config for public deployment.

### 4. README.md with setup instructions
Write clear instructions for: local setup, Docker deployment, environment variables, Google OAuth setup.

### 5. Production API_BASE and GOOGLE_REDIRECT_URI
Make these configurable via environment variables instead of hardcoded localhost.

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `Dockerfile` | Create — multi-stage build for FastAPI backend |
| `docker-compose.yml` | Create — FastAPI + Streamlit + MySQL services |
| `.streamlit/config.toml` | Create — Streamlit server config |
| `frontend/app.py` | Modify — make `API_BASE` read from `os.environ` or Streamlit secrets |
| `backend/interview/google_calendar.py` | Modify — make redirect URI configurable |
| `README.md` | Create — setup + deployment instructions |
| `.env.example` | Create — template with all required env vars (secrets redacted) |

---

## Deployment Steps (Railway recommended)

1. Create `Dockerfile` — Python 3.11, install requirements, run uvicorn on port 8002
2. Create `docker-compose.yml` — backend + frontend + MySQL
3. Create `.streamlit/config.toml` — headless=true, port=8501
4. Update `frontend/app.py` — `API_BASE = os.environ.get("API_BASE", "http://localhost:8002")`
5. Update `google_calendar.py` — use env var for redirect URI
6. Create `README.md` with step-by-step setup
7. Update `.gitignore` to exclude `.env` (already done)
8. Push to GitHub → connect to Railway/Render → deploy
