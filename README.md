# HireEZ — AI-Powered Recruitment Platform

An end-to-end AI recruitment platform that automates candidate screening, evaluation, and interview scheduling using Google Gemini for AI evaluation, GitHub for technical profiling, and Google Calendar with real Meet links for interview scheduling.

**🔗 Live Demo:** [https://hireez-frontend.streamlit.app](https://hireez-frontend.streamlit.app)

## Features

- **CSV Upload** — Bulk upload candidate datasets with name, email, college, branch, CGPA, GitHub profile, and resume link
- **Job Descriptions** — Define roles with required/preferred skills and minimum CGPA threshold
- **Resume Processing** — Download and extract text from PDF resumes via direct URL
- **AI Evaluation** — Gemini 2.5 Flash-powered scoring against job requirements across 5 dimensions
- **GitHub Analysis** — Repository-level analysis for AI/ML projects, languages, and contribution history
- **Candidate Ranking** — Weighted composite scoring (AI 60%, GitHub 25%, CGPA 10%, Research 5%)
- **Automated Emailing** — Send test links to shortlisted candidates via SMTP
- **Test Result Upload** — Import test scores (Logical Aptitude + Coding) via CSV
- **Interview Scheduling** — Auto-schedule interviews via Google Calendar API with concurrent processing
- **Google Meet Integration** — Real Meet links generated automatically via Google Calendar API

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit 1.58 (deployed on Streamlit Cloud) |
| Backend | FastAPI 0.138 + SQLAlchemy 2.0 (deployed on Render) |
| Database | MySQL 8.0 (TiDB Cloud — free tier) |
| AI | Google Gemini 2.5 Flash via `google-genai` |
| APIs | GitHub REST API v3, Google Calendar API v3, Gmail SMTP |
| OAuth | Google OAuth 2.0 (Web Application type) |

## Architecture

```
┌─────────────────────────┐       ┌──────────────────────────┐
│   Streamlit Cloud        │       │   Render.com (Free Tier) │
│   HireEZ-Frontend repo   │──────►│   HireEZ Backend API     │
│   share.streamlit.io     │       │   FastAPI + SQLAlchemy   │
└─────────────────────────┘       └───────────┬──────────────┘
                                              │
                         ┌────────────────────┼────────────────────┐
                         │                    │                    │
                         ▼                    ▼                    ▼
               ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
               │  TiDB Cloud     │  │ Google Gemini   │  │ Google Calendar │
               │  MySQL 8.0      │  │ AI Evaluation   │  │ + Meet Links    │
               │  (Persistence)  │  │                 │  │                 │
               └─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Pipeline Workflow

```
Upload Dataset (CSV)
        ↓
Parse Resumes (download + extract text)
        ↓
GitHub Analysis (AI/ML project scoring)
        ↓
AI Evaluation (Gemini 2.5 Flash)
        ↓
Candidate Ranking (weighted composite score)
        ↓
Shortlist by Score + Send Test Links (SMTP)
        ↓
Upload Test Results (Logical Aptitude + Coding scores)
        ↓
Shortlist Based on Test Performance
        ↓
Schedule Interviews (Google Calendar + real Meet links)
        ↓
Send Interview Invitations (email with Meet links)
```

## Deployment

### Backend — Render.com (Free Tier)

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New → Web Service → Connect `Krish-Puri/HireEZ`
3. Configure:
   - **Name:** `hireez-backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port 10000`
   - **Plan:** Free
4. Add environment variables (see `.env.example`)
5. Deploy

> **Note:** Render's free tier has an ephemeral filesystem — uploads and temp files must use `/tmp`.

### Database — TiDB Cloud (Free Tier)

1. Sign up at [tidbcloud.com](https://tidbcloud.com)
2. Create a serverless cluster (free tier)
3. Copy connection details to Render environment variables:
   - `DB_HOST`, `DB_PORT=4000`, `DB_NAME=hireez`, `DB_USER`, `DB_PASSWORD`
   - `DB_SSL=true`

### Frontend — Streamlit Cloud (Separate Repo)

The frontend deploys from a **separate GitHub repository** (`HireEZ-Frontend`):

```bash
# Sync frontend from HireEZ repo
git subtree push --prefix frontend origin frontend
```

Streamlit Cloud reads from `frontend/app.py`. Any changes to the frontend must be pushed to the `HireEZ-Frontend` repo separately.

In Streamlit Cloud advanced settings:
- `API_BASE` = `https://hireez-backend.onrender.com`

## Configuration

### Environment Variables

```env
# Database (TiDB Cloud)
DB_HOST=gateway01.ap-southeast-1.prod.aws.tidbcloud.com
DB_PORT=4000
DB_NAME=hireez
DB_USER=<username>
DB_PASSWORD=<password>
DB_SSL=true

# Gemini AI
GEMINI_API_KEY=<your-gemini-api-key>

# GitHub
GITHUB_TOKEN=github_pat_...

# Email (SMTP — Gmail with App Password)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your@gmail.com

# Google OAuth (for Calendar + Meet)
GOOGLE_CLIENT_ID=<from-google-cloud-console>
GOOGLE_CLIENT_SECRET=<from-google-cloud-console>
GOOGLE_REFRESH_TOKEN=<obtained-via-oauth-flow>
GOOGLE_REDIRECT_URI=https://hireez-backend.onrender.com/google/oauth/callback

# App
FRONTEND_URL=https://hireez-frontend.streamlit.app
API_BASE=https://hireez-backend.onrender.com
```

### Google OAuth Setup (Required for Meet Links)

1. Go to [Google Cloud Console](https://console.cloud.google.com) → create a new project
2. Enable **Google Calendar API**
3. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
4. Application type: **Web application**
5. Add authorized redirect URIs:
   - `http://localhost:8090` (for local token generation)
   - `https://developers.google.com/oauthplayground/callback`
   - `https://hireez-backend.onrender.com/google/oauth/callback`
6. In **OAuth consent screen** → add your email as a **Test user**
7. Download the client JSON or use the credentials directly

### Obtaining a Refresh Token

OAuth Playground is the recommended tool:

1. Open [OAuth Playground](https://developers.google.com/oauthplayground)
2. Click gear icon → fill in **your** OAuth Client ID and Client Secret
3. Step 2 → expand **Calendar API v3** → check `https://www.googleapis.com/auth/calendar.events`
4. Click **Authorize** → sign in with your Google account → Allow
5. Click **Exchange authorization code for tokens**
6. Copy the **refresh_token** from the response

### GitHub Token Setup

1. Go to [GitHub Settings → Personal Access Tokens](https://github.com/settings/tokens)
2. Generate new token (classic) with scopes: `repo`, `read:user`, `user:email`
3. Copy to `GITHUB_TOKEN`

## Project Structure

```
HireEZ/
├── backend/
│   ├── api/                    # FastAPI route handlers
│   │   ├── candidate_routes.py # Upload, list, rerun AI/GitHub
│   │   ├── interview_routes.py# Schedule interviews + Meet links
│   │   └── test_routes.py     # Test results + shortlisting
│   ├── core/                  # Constants, exceptions
│   ├── database/              # SQLAlchemy connection + session
│   ├── github/                # GitHub REST API client + analyzer
│   ├── interview/             # Google Calendar + Meet integration
│   ├── intelligence/          # Resume text extraction from URLs
│   ├── models/                # SQLAlchemy ORM models
│   │   ├── candidate.py       # Candidate model
│   │   ├── job.py            # Job model
│   │   └── test_result.py    # TestResult + Evaluation models
│   ├── pipeline/              # 4-stage pipeline engine
│   │   ├── pipeline_engine.py # Orchestrates all 4 stages
│   │   ├── resume_stage.py   # Stage 1: resume download/parsing
│   │   ├── github_stage.py   # Stage 2: GitHub profile analysis
│   │   ├── ai_stage.py       # Stage 3: Gemini evaluation
│   │   └── ranking_stage.py  # Stage 4: weighted scoring
│   ├── ranking/               # Ranking formula + score computation
│   ├── repositories/          # Data access layer
│   ├── schemas/              # Pydantic request/response schemas
│   └── services/             # Business logic (CSV, email)
├── frontend/
│   └── app.py                # Streamlit single-page app (11 sections)
├── .streamlit/
│   └── config.toml            # Streamlit server configuration
├── requirements.txt          # Python dependencies
├── README.md                  # This file
└── architecture.md           # Detailed system architecture
```

## Known Limitations

### Render Free Tier — Email

Render's free tier blocks outbound SMTP connections (`[Errno 101] Network is unreachable`). Email sending (test links, interview invitations) will fail on the free plan. Workarounds:

- Upgrade to a paid Render plan
- Use a transactional email API (SendGrid, Mailgun, Postmark)
- Use a different hosting provider for the backend

### Render Free Tier — Concurrency

Free tier Web Services on Render spin down after 15 minutes of inactivity and can take ~30 seconds to wake up. The first request after dormancy may timeout. The frontend timeout is set to 300s to accommodate slow cold starts.

### OAuth Refresh Token Expiry

Google OAuth refresh tokens can expire after ~7 days of non-use. If Meet links stop working, obtain a new refresh token using the OAuth Playground flow described above.

## License

MIT
