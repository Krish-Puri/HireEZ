# HireEZ — System Architecture Document

> AI-Powered Candidate Screening Platform for **Visl AI Labs — Founding AI Engineer Role**

---

## 1. Overview

HireEZ is a full-stack recruitment platform that automates the end-to-end hiring pipeline using AI evaluation, GitHub analysis, and integrated communication tools. The system progresses candidates automatically from upload through to scheduled interviews.

### Workflow

```
Candidate CSV Upload
        ↓
Resume Download & Parsing
        ↓
GitHub Profile Analysis
        ↓
AI Evaluation (Google Gemini)
        ↓
Candidate Ranking
        ↓
Shortlist by Score + Send Test Links (Email)
        ↓
Upload Test Results (Logical Aptitude + Coding)
        ↓
Shortlist Based on Test Performance
        ↓
Schedule Interviews (Google Calendar + Meet)
        ↓
Send Interview Invitations (Email with Meet Links)
```

---

## 2. System Architecture

```
┌─────────────────────┐        ┌─────────────────────┐
│   Streamlit Frontend │◄──────►│     FastAPI API      │
│   (http://localhost │        │  http://localhost:8000│
│    :8501)            │        └──────────┬──────────┘
└─────────────────────┘                   │
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              │                            │                            │
              ▼                            ▼                            ▼
    ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
    │   SQLAlchemy     │         │  Pipeline Engine │         │  External APIs   │
    │   + MySQL        │         │  (4-stage)      │         │  • Google Gemini│
    │  (Persistence)   │         └─────────────────┘         │  • GitHub REST  │
    └─────────────────┘                   │                   │  • Google Calendar
                                          │                   │  • SMTP Email    │
                          ┌───────────────┼───────────────┐   └─────────────────┘
                          ▼               ▼               ▼
                    ┌──────────┐  ┌────────────┐  ┌──────────┐  ┌────────────┐
                    │ Resume   │  │  GitHub    │  │   AI     │  │  Ranking   │
                    │ Stage    │  │  Stage     │  │  Stage   │  │  Stage     │
                    └──────────┘  └────────────┘  └──────────┘  └────────────┘
```

---

## 3. Component Details

### 3.1 Frontend — Streamlit

**Stack:** Streamlit 1.x, requests, pandas

**Pages:**
| Page | Route | Purpose |
|------|-------|---------|
| Upload Candidates | `📤` | CSV upload with format preview |
| Manage Jobs | `💼` | Create / list / delete jobs |
| Candidate Pipeline | `👥` | Filterable candidate table |
| Upload Test Results | `📊` | CSV upload for test scores |
| Shortlist & Send Tests | `✅` | Shortlist + email test links |
| Schedule Interviews | `📅` | Auto-schedule with Meet links |
| Interview Status | `📋` | View all interview statuses |

---

### 3.2 Backend API — FastAPI

**Stack:** FastAPI, SQLAlchemy 2.x, uvicorn

**Routers:**

| Router | Prefix | Methods | Purpose |
|--------|--------|---------|---------|
| `candidate_routes` | `/candidates` | POST, GET | Upload CSV, list candidates |
| `job_routes` | `/jobs` | POST, GET, GET/:id, DELETE | Job CRUD |
| `test_routes` | `/tests` | POST `/upload-results`, POST `/send-test-links`, GET `/shortlisted` | Test score management |
| `interview_routes` | `/interviews` | POST `/schedule`, GET `/` | Interview scheduling |

---

### 3.3 Database — MySQL + SQLAlchemy

**Models:**

| Model | Table | Purpose |
|-------|-------|---------|
| `Candidate` | `candidates` | Core candidate record |
| `Job` | `jobs` | Job postings |
| `Evaluation` | `evaluations` | AI evaluation results |
| `TestResult` | `test_results` | Test scores + interview state |

**Candidate Schema (from CSV):**
```
Name, Email, College, Branch, CGPA,
Best AI Project, Research Work, GitHub Profile, Resume Link
```

**Test Results Schema:**
```
Email, test_la (Logical Aptitude), test_code (Coding Test)
```

---

### 3.4 Pipeline Engine — 4-Stage Processor

The pipeline runs synchronously after each candidate is inserted:

```
PipelineEngine.run(db, candidate)
    │
    ├─[1] ResumeStage
    │       ↓ candidate.resume_text extracted from resume_url
    │
    ├─[2] GithubStage
    │       ↓ GitHubClient fetches repos + languages
    │       ↓ GitHubRepositoryAnalyzer scores AI projects
    │
    ├─[3] AIStage  (most intensive)
    │       ↓ CandidateIntelligenceEngine extracts profile from resume text
    │       ↓ AIEvaluator calls Gemini (gemini-2.5-flash)
    │       ↓ EvaluationResult stored in DB
    │
    └─[4] RankingStage
            ↓ RankingEngine computes weighted score:
               AI Score (60%) + GitHub (25%) + CGPA (10%) + Research (5%)
```

**Status Flow:**
```
Uploaded → Resume Parsing → Resume Parsed →
GitHub Analysis → AI Evaluation → AI Evaluated → Ranked
                (or Failed at any stage)
```

---

### 3.5 AI Evaluation

**Provider:** Google Gemini (`gemini-2.5-flash`) via `google-genai`

**Prompt Strategy:**
1. Build prompt from `CandidateProfile` (skills, projects, education, research)
2. Include `Job` description and required/preferred skills
3. Include `EvaluationRubric` with score breakdowns
4. Send to Gemini with structured output instructions

**Scoring Dimensions:**
- Technical Skills
- Project Quality
- Education / CGPA
- Research Work
- Communication

**Output:** Structured `EvaluationResult` with scores, summary, strengths, concerns, missing skills, and suggested interview questions.

---

### 3.6 GitHub Analysis

**Tool:** GitHub REST API v3 (no GraphQL)

**Analysis per repository:**
- Detect AI/ML keywords: Machine Learning, Deep Learning, NLP, LLM, TensorFlow, PyTorch, etc.
- Count and weight AI projects
- Top languages by byte-count

**GitHub Score Formula:** (AI projects × 40) + (total repos × 10) + language diversity bonus

---

### 3.7 Ranking Engine

**Weighted Score:**
```
final_score = (ai_score × 0.60) +
              (github_score × 0.25) +
              (cgpa_normalized × 0.10) +
              (research_present × 0.05)
```

Candidates are then sorted and assigned `candidate_rank` (1 = best).

---

### 3.8 Test & Interview Flow

**Test Results:**
- `test_la` (Logical Aptitude, 0–100)
- `test_code` (Coding Test, 0–100)
- Stored on both `Candidate` and `TestResult` models

**Shortlisting Logic:**
```
AI final_score >= threshold (default 50)
        ↓
Email sent with test link
        ↓
Test results uploaded via CSV
        ↓
(min_test_la + min_test_code) >= threshold
        ↓
Interview scheduled
```

**Interview Scheduling:**
1. For each eligible candidate: create Google Calendar event via Google Calendar API v3
2. `conferenceData.createRequest` automatically generates a Google Meet link
3. Save `interview_link` and `interview_time` to `TestResult`
4. Send email invitation via SMTP with Meet link and time

---

## 4. AI Evaluation Approach

HireEZ uses **Google Gemini 2.5 Flash** for multi-dimensional candidate evaluation:

1. **Profile Extraction:** Resume text is parsed by `CandidateIntelligenceEngine` into structured data (skills, projects, education, research)
2. **Context-Aware Prompting:** The prompt includes the specific job description, required skills, and a scoring rubric
3. **Structured Output:** Gemini returns scores + free-text feedback (strengths, concerns, missing skills, interview questions)
4. **Explainability:** Each score dimension is returned separately so recruiters can see WHY a candidate scored as they did

**Why Gemini?**
- Fast enough for per-candidate synchronous calls during pipeline execution
- 1M token context window handles long resumes + job descriptions
- Function-calling compatible for structured output
- Cost-effective at scale

---

## 5. Environment Variables

| Variable | Description |
|----------|-------------|
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | MySQL connection |
| `GEMINI_API_KEY` | Google Gemini API key |
| `GITHUB_TOKEN` | GitHub PAT for higher API rate limits |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_FROM` | Email sending |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI` | Google OAuth for Calendar |
| `FRONTEND_URL` | Public URL of Streamlit app |

---

## 6. Scalability Considerations

- **Async Pipeline:** Pipeline stages can be made async and run on a task queue (Celery/ARQ) for high throughput
- **GitHub API Rate Limits:** GitHub REST API has a 5,000 req/hr limit for authenticated users — the current implementation respects this
- **Database:** MySQL with proper indexes on `email`, `status`, and `candidate_rank`
- **AI Cost:** Gemini Flash pricing is optimal; batch evaluation can be added for bulk reprocessing
- **Frontend:** Streamlit is suitable for internal tools; for public deployment, consider a React/Next.js frontend

---

## 7. Deliverables Status

| Deliverable | Status |
|-------------|--------|
| Hosted Application | ✅ Streamlit + FastAPI (local; deploy to Railway/Render) |
| GitHub Repository | ✅ Source code with setup instructions |
| Architecture Document | ✅ This document |
| Demo Video | ⏳ Pending |
