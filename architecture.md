# HireEZ — System Architecture Document

> AI-Powered Candidate Screening Platform — Complete System Documentation

---

## 1. Overview

HireEZ is a full-stack recruitment platform that automates the end-to-end hiring pipeline: from candidate CSV upload, through AI evaluation and GitHub analysis, to automated interview scheduling with real Google Meet links.

The system is built as two separate deployments:
- **Backend API** — FastAPI on Render.com (free tier)
- **Frontend** — Streamlit on Streamlit Cloud (separate `HireEZ-Frontend` GitHub repo)

---

## 2. System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Streamlit Cloud                                │
│                    HireEZ-Frontend repo (main)                        │
│                    share.streamlit.io/{app}                           │
│                                                                      │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐ │
│   │ Upload   │  │ Job Desc │  │ Resume   │  │ AI Evaluation        │ │
│   │ Dataset  │  │          │  │ Parsing  │  │ (Gemini 2.5 Flash)   │ │
│   └──────────┘  └──────────┘  └──────────┘  └──────────────────────┘ │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐ │
│   │ GitHub   │  │ Score &  │  │ Send     │  │ Schedule Interviews  │ │
│   │ Analysis │  │ Rank     │  │ Test     │  │ (Google Calendar     │ │
│   │          │  │          │  │ Links    │  │  + Meet links)       │ │
│   └──────────┘  └──────────┘  └──────────┘  └──────────────────────┘ │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │ HTTPS
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        Render.com (Free Tier)                         │
│                    hireez-backend.onrender.com                        │
│                                                                      │
│   FastAPI (uvicorn)                                                  │
│                                                                      │
│   ┌──────────────────────────────────────────────────────────────┐   │
│   │                    API Routes                                 │   │
│   │   POST /candidates/upload    GET /candidates/                 │   │
│   │   POST /candidates/rerun-ai  POST /candidates/rerun-github    │   │
│   │   POST /jobs/                GET /jobs/                       │   │
│   │   POST /tests/upload-results  POST /tests/send-test-links      │   │
│   │   POST /interviews/schedule  GET /interviews/                 │   │
│   └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│   ┌──────────────────────────────────────────────────────────────┐   │
│   │                 Pipeline Engine (4 stages)                     │   │
│   │   1. ResumeStage  →  2. GithubStage  →  3. AIStage  →  4.   │   │
│   │      (download/         (repo analysis)   (Gemini       Ranking│   │
│   │       extract text)                         evaluation)  Stage  │   │
│   └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│   ┌──────────────────────────────────────────────────────────────┐   │
│   │                 External Service Integrations                  │   │
│   │   Google Gemini (AI)  │  GitHub REST API  │  Google Calendar  │   │
│   │   SMTP Email          │  TiDB MySQL       │  (Meet links)     │   │
│   └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                              ▼
         ┌─────────────────────┐       ┌─────────────────────────┐
         │    TiDB Cloud       │       │   Google Calendar API   │
         │    MySQL 8.0        │       │   (OAuth 2.0 refresh   │
         │    (Persistence)     │       │    token flow)         │
         └─────────────────────┘       └─────────────────────────┘
```

---

## 3. Frontend — Streamlit

Single `app.py` file (~1000 lines) with 11 sections/pages implemented via sidebar navigation.

| Section | Purpose |
|---------|---------|
| Upload Dataset | CSV upload with format preview |
| Job Description | Create/list/delete job postings |
| Parse Resumes | Trigger resume download + text extraction |
| AI Evaluation | View AI scores, re-run evaluation |
| GitHub Analysis | View GitHub scores, re-run analysis |
| Score & Rank | View composite rankings |
| Send Test Links | Email test links to shortlisted candidates |
| Upload Test Results | Import Logical Aptitude + Coding scores |
| Shortlist | Filter candidates by test performance |
| Schedule Interviews | Auto-schedule via Google Calendar + Meet |
| Interview Status | View scheduled interview details |

### Frontend-backend Communication

- Frontend calls backend REST API at `API_BASE` (set via Streamlit secrets)
- All pipeline stages run **server-side** in the FastAPI backend
- Frontend polls or reloads page to see updated results after pipeline runs
- Re-run buttons trigger background threads in the API for async reprocessing

---

## 4. Backend API — FastAPI

### Database Models

| Model | Table | Description |
|-------|-------|-------------|
| `Candidate` | `candidates` | Core record: name, email, college, branch, CGPA, GitHub URL, resume URL, all scores, status, rank |
| `Job` | `jobs` | Job title, required/preferred skills, min CGPA, min test score |
| `Evaluation` | `evaluations` | AI evaluation results: scores (technical, projects, education, research, communication), summary, strengths, concerns |
| `TestResult` | `test_results` | test_la, test_code, test_link_sent, interview_scheduled, interview_link, interview_time |

### Candidate Status Flow

```
Uploaded → Resume Parsing → Resume Parsed →
GitHub Analysis → AI Evaluation → AI Evaluated → Ranked
              (or Failed at any stage)
```

### API Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/candidates/upload` | POST | Upload candidate CSV |
| `/candidates/` | GET | List all candidates |
| `/candidates/{id}` | GET | Get single candidate |
| `/candidates/rerun-ai` | POST | Re-run AI evaluation for candidates with no score (background thread) |
| `/candidates/rerun-github` | POST | Re-run GitHub analysis for candidates with no score (background thread) |
| `/jobs/` | GET/POST | List/create jobs |
| `/jobs/{id}` | GET/DELETE | Get/delete job |
| `/tests/upload-results` | POST | Upload test score CSV |
| `/tests/send-test-links` | POST | Email test links to shortlisted candidates (background threads) |
| `/tests/shortlisted` | GET | Get candidates with AI score above threshold |
| `/tests/shortlisted-after-test` | GET | Get candidates shortlisted by test performance |
| `/interviews/schedule` | POST | Schedule interviews via Google Calendar (ThreadPoolExecutor for concurrency) |
| `/interviews/` | GET | List scheduled interviews |
| `/google/oauth/login` | GET | Initiate Google OAuth flow |
| `/google/oauth/callback` | GET | OAuth callback |

---

## 5. Database — SQLAlchemy 2.0 + TiDB Cloud MySQL

### Connection

```python
# backend/database/connection.py
engine = create_engine(DB_URL, pool_pre_ping=True, pool_recycle=3600)
```

- SSL enabled (`DB_SSL=true`) for TiDB Cloud connection
- `pool_pre_ping=True` to handle connection drops
- Each background thread creates its own `SessionLocal()` to avoid shared state

### Key Indexes

- `Candidate.email` — unique index for candidate matching
- `Candidate.status` — for filtered queries
- `Candidate.candidate_rank` — for ordering

---

## 6. Pipeline Engine — 4 Stages

```
PipelineEngine.run(db, candidate_id, job_id)
        │
        ├─[1] ResumeStage
        │       Downloads PDF from resume_url
        │       Extracts text via PyMuPDF (fitz)
        │       Stores in candidate.resume_text
        │
        ├─[2] GithubStage
        │       Fetches GitHub profile via REST API
        │       Lists repositories, detects AI/ML projects
        │       Scores: (AI_projects × 40) + (total_repos × 10) + diversity_bonus
        │       Stores github_score, best_ai_project
        │
        ├─[3] AIStage (most intensive)
        │       CandidateIntelligenceEngine extracts structured profile from resume text
        │       AIEvaluator builds 5-dimension prompt + rubric
        │       Gemini 2.5 Flash returns structured JSON scores
        │       ResponseParser validates + stores Evaluation record
        │       Scores: Technical Skills, Project Quality, Education, Research, Communication
        │
        └─[4] RankingStage
                RankingEngine computes weighted final_score:
                  final_score = (ai_score × 0.60) +
                                (github_score × 0.25) +
                                (cgpa_normalized × 0.10) +
                                (research_present × 0.05)
                Assigns candidate_rank (1 = best)
```

### Concurrency

- `concurrent.futures.ThreadPoolExecutor(max_workers=10)` in `interview_routes.py`
- Each scheduling thread: creates its own DB session + `asyncio.new_event_loop()` for async Google Calendar API calls
- Daemon `threading.Thread` for background AI/GitHub re-runs

---

## 7. Google Calendar + Meet Integration

### OAuth 2.0 Flow

```
User's Browser → Google Consent Screen
                      │
                      ▼ (authorization code)
              OAuth Playground / Local Server
                      │
                      ▼ (code exchange)
              Google Token Endpoint
                      │
                      ▼
              Refresh Token (stored in env var)
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
  Render Backend              Local Development
  (GOOGLE_REFRESH_TOKEN)      (same env var)
        │                           │
        ▼                           ▼
  _refresh_access_token() ────► Valid Access Token
        │                           │
        └───────────┬───────────────┘
                    ▼
            Google Calendar API v3
            POST /calendars/primary/events
            + conferenceData.createRequest
                    │
                    ▼
            Real Google Meet Link
            (hangoutLink in response)
```

### Key Implementation Details

**`backend/interview/google_calendar.py`** — `GoogleCalendarService`

- `_refresh_access_token()` — POSTs to `https://oauth2.googleapis.com/token` with `grant_type=refresh_token`, exchanges refresh token for fresh access token. Cached in instance.
- `_get_valid_access_token()` — called before every API request, auto-refreshes if missing
- `create_meet_link(start_time, end_time)` — creates calendar event with `conferenceData.createRequest` → Google returns real Meet link. Requires `start`/`end` in ISO format.
- `create_interview_event(...)` — full calendar event with attendees, description, and optional pre-generated Meet link
- Falls back to random Meet-format ID only if `GOOGLE_REFRESH_TOKEN` is not configured

### Google Meet Link Response

```json
{
  "hangoutLink": "https://meet.google.com/abc-defg-hij",
  "id": "event_id_123",
  "start": {"dateTime": "2026-07-05T10:00:00Z"},
  "end":   {"dateTime": "2026-07-05T11:00:00Z"}
}
```

---

## 8. AI Evaluation — Gemini 2.5 Flash

### Provider — `google-genai`

```python
from google import genai
client = genai.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=EvaluationResult
    )
)
```

### Prompt Structure — 5 Sections

1. **Candidate Profile** — extracted from resume text (skills, projects, education, research)
2. **Job Description** — role, required skills, preferred skills, min CGPA
3. **Evaluation Rubric** — score breakdowns for each dimension (1–100)
4. **Scoring Instructions** — weight allocation, how to handle missing data
5. **Output Schema** — required JSON structure with scores + free-text feedback

### Scoring Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Technical Skills | 60% of AI score | Proficiency in required/preferred skills |
| Project Quality | major factor | Relevance, depth, impact of AI/ML projects |
| Education | contextual | CGPA vs requirements, institution reputation |
| Research Work | bonus | Publications, papers, research contributions |
| Communication | qualitative | Clarity in resume/answers |

### Output Schema

```json
{
  "technical_score": 85,
  "project_score": 80,
  "education_score": 75,
  "research_score": 60,
  "communication_score": 70,
  "overall_assessment": "Strong candidate with...",
  "strengths": ["...", "..."],
  "concerns": ["...", "..."],
  "missing_skills": ["...", "..."],
  "suggested_interview_questions": ["?", "?"]
}
```

---

## 9. GitHub Analysis

### REST API Endpoints Used

- `GET /users/{username}` — profile info (public_repos, followers)
- `GET /users/{username}/repos?per_page=100&sort=updated` — repository list
- `GET /repos/{owner}/{repo}/languages` — language byte counts

### AI/ML Project Detection

Keywords detected in repo names and descriptions:
`machine learning, deep learning, neural network, NLP, LLM, large language model, computer vision, artificial intelligence, TensorFlow, PyTorch, Keras, scikit-learn, reinforcement learning, generative AI, transformers, BERT, GPT`

### GitHub Score Formula

```
github_score = (ai_ml_project_count × 40)
             + (total_repo_count × 10)
             + (unique_language_count × 5)
             + (has_ai_ml_top_language ? 20 : 0)
             + (followers > 50 ? 10 : 0)
```

Capped at 100.

---

## 10. Ranking Formula

```
final_score = (ai_score × 0.60) + (github_score × 0.25) + (cgpa_normalized × 0.10) + (research_present × 0.05)
```

Where:
- `ai_score` — 0–100 from Gemini evaluation
- `github_score` — 0–100 from GitHub analysis
- `cgpa_normalized` — (candidate_cgpa / 10.0) × 100
- `research_present` — 100 if research work exists, else 0

Candidates sorted by `final_score DESC` → assigned `candidate_rank` starting at 1.

---

## 11. Email Sending

### Implementation — `backend/services/email_service.py`

- Uses Python `smtplib` with Gmail SMTP (`smtp.gmail.com:587`)
- App Password authentication (not regular password)
- HTML email templates for test links and interview invitations
- All sending runs in background `threading.Thread` to avoid API timeouts

### Render Free Tier Limitation

Gmail SMTP is **blocked** on Render's free tier — outbound connections to port 587 fail with `[Errno 101] Network is unreachable`. Email sending will not work without:
- Upgrading to Render paid plan, or
- Using a transactional email API (SendGrid, Mailgun, etc.)

---

## 12. Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `DB_HOST` | Yes | TiDB Cloud gateway host |
| `DB_PORT` | Yes | Usually `4000` for TiDB |
| `DB_NAME` | Yes | Database name (`hireez`) |
| `DB_USER` | Yes | Database username |
| `DB_PASSWORD` | Yes | Database password |
| `DB_SSL` | Yes | Must be `true` for TiDB Cloud |
| `GEMINI_API_KEY` | Yes | From Google AI Studio |
| `GITHUB_TOKEN` | Yes | GitHub PAT (classic) with repo, read:user, user:email scopes |
| `SMTP_HOST` | Yes | `smtp.gmail.com` |
| `SMTP_PORT` | Yes | `587` |
| `SMTP_USER` | Yes | Gmail address |
| `SMTP_PASSWORD` | Yes | Gmail App Password |
| `EMAIL_FROM` | Yes | Same as SMTP_USER |
| `GOOGLE_CLIENT_ID` | Yes | Web application OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Yes | Web application OAuth client secret |
| `GOOGLE_REFRESH_TOKEN` | Yes | OAuth refresh token for Calendar API |
| `GOOGLE_REDIRECT_URI` | No | Defaults to `http://localhost:8501/oauth/callback` |
| `FRONTEND_URL` | No | Streamlit Cloud app URL |
| `API_BASE` | No | Render backend URL |

---

## 13. Deployment Checklist

### Pre-deployment

- [ ] Google Cloud project created + Calendar API enabled
- [ ] OAuth 2.0 Web application client created
- [ ] All 3 redirect URIs added to OAuth client
- [ ] Test user added to OAuth consent screen
- [ ] Refresh token obtained via OAuth Playground
- [ ] Gemini API key from AI Studio
- [ ] GitHub PAT with required scopes
- [ ] Gmail App Password for SMTP
- [ ] TiDB Cloud cluster created + connection string

### Render Setup

- [ ] Connect `Krish-Puri/HireEZ` repo
- [ ] Add all environment variables (including `GOOGLE_REFRESH_TOKEN`)
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `uvicorn backend.main:app --host 0.0.0.0 --port 10000`
- [ ] Wait for first deploy to complete

### Streamlit Cloud Setup

- [ ] Create `HireEZ-Frontend` GitHub repo
- [ ] Push `frontend/` folder, `.streamlit/`, `requirements.txt`
- [ ] Connect repo at share.streamlit.io
- [ ] Set `API_BASE` in advanced settings

### Post-deployment Verification

- [ ] Upload a test CSV — candidates appear in list
- [ ] Trigger AI evaluation — scores populate
- [ ] Click Schedule Interviews — real Meet links generated
- [ ] Check Render logs for any errors

---

## 14. Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| Dummy Meet links | `GOOGLE_REFRESH_TOKEN` missing or from wrong OAuth client | Obtain refresh token using your own OAuth client credentials |
| `401 unauthorized_client` | Refresh token was obtained via OAuth Playground's client, used with different client | Obtain fresh refresh token with correct client credentials |
| `redirect_uri_mismatch` | OAuth redirect URI not registered in Google Cloud Console | Add `https://developers.google.com/oauthplayground/callback` to authorized URIs |
| Email fails with `Network unreachable` | Render free tier blocks outbound SMTP | Upgrade Render plan or use SendGrid/Mailgun |
| Cold start timeout | Render free tier spins down after 15 min | Frontend timeout set to 300s; consider paid tier |
| SQLAlchemy `type(int)` error | Using `type(candidate_id)` in `session.query()` | Use `session.query(Candidate).get(candidate_id)` |
| Missing start/end time error | Calendar API called without time range | Always include `start.dateTime` and `end.dateTime` in event body |
