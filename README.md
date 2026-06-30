# HireEZ — AI-Powered Recruitment Platform

An end-to-end AI recruitment platform that automates candidate screening, evaluation, and interview scheduling using Google Gemini for AI evaluation, GitHub for technical profiling, and Google Calendar for interview scheduling.

## Features

- **CSV Upload** — Bulk upload candidate datasets
- **Job Description** — Define roles with required/preferred skills and minimum CGPA
- **Resume Processing** — Download and extract text from PDF resumes
- **AI Evaluation** — Gemini-powered scoring against job requirements
- **GitHub Analysis** — Repository-level analysis for AI/ML projects, languages, and contributions
- **Candidate Ranking** — Weighted scoring (AI 60%, GitHub 25%, CGPA 10%, Research 5%)
- **Automated Emailing** — Send test links to shortlisted candidates via SMTP
- **Test Result Upload** — Import test scores (Logical Aptitude + Coding)
- **Interview Scheduling** — Auto-schedule interviews via Google Calendar
- **Google Meet Integration** — Real Meet links generated via Google Calendar API

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit 1.58 |
| Backend | FastAPI 0.138 + SQLAlchemy 2.0 |
| Database | MySQL 8.0 |
| AI | Google Gemini 2.5 Flash |
| APIs | GitHub REST API v3, Google Calendar API v3 |

## Quick Start (Docker)

```bash
# 1. Clone the repository
git clone https://github.com/Krish-Puri/HireEZ.git
cd HireEZ

# 2. Copy environment variables
cp .env.example .env
# Edit .env with your API keys (see Configuration below)

# 3. Start all services
docker-compose up --build

# 4. Open the app
# Frontend: http://localhost:8501
# Backend API: http://localhost:8002
```

## Quick Start (Local Development)

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up MySQL database
# Create a database named 'hireez'

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 5. Start backend
uvicorn backend.main:app --port 8002 --reload

# 6. Start frontend (new terminal)
streamlit run frontend/app.py
```

## Configuration

Copy `.env.example` to `.env` and fill in:

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=hireez
DB_USER=root
DB_PASSWORD=your_password

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key

# GitHub
GITHUB_TOKEN=your_github_pat

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com

# Google OAuth (for Google Calendar / Meet)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8002/google/oauth/callback
```

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project → Enable Google Calendar API
3. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
4. Application type: **Web application**
5. Add authorized redirect URI: `http://localhost:8002/google/oauth/callback`
6. Copy Client ID and Secret to `.env`
7. Add test user in OAuth consent screen (for unverified apps)

### GitHub Token Setup

1. Go to [GitHub Settings](https://github.com/settings/tokens)
2. **Generate new token (classic)**
3. Scopes: `repo` (full), `read:user`, `user:email`
4. Copy token to `GITHUB_TOKEN` in `.env`

## Pipeline Workflow

```
Upload Dataset → Job Description → Parse Resumes → AI Evaluation
    → GitHub Analysis → Score & Rank → Send Test Links
    → Upload Test Results → Shortlist → Schedule Interviews
    → Google Meet Sent
```

## Deployment (Render + PlanetScale)

### Using Render (Free Python Hosting)

1. Push code to GitHub
2. Go to [render.com](https://render.com) → Sign up with GitHub
3. Click **New** → **Web Service** → Connect your `Krish-Puri/HireEZ` repo
4. Configure:
   - **Name:** `hireez-backend`
   - **Region:** Singapore
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port 10000`
   - **Plan:** Free
5. Add all environment variables from `.env.example` (set `DB_SSL=true` for PlanetScale)
6. Click **Create Web Service** → wait for build to complete
7. Your backend will be live at `https://hireez-backend.onrender.com`

### Using PlanetScale (Free MySQL)

1. Go to [planetscale.com](https://planetscale.com) → Sign up with GitHub
2. Click **New database** → Name: `hireez` → Choose free tier
3. Click **Connect** → **General** → Copy the connection string
4. Add these values to Render environment variables:
   - `DB_HOST` = host from connection string
   - `DB_USER` = username
   - `DB_PASSWORD` = password
   - `DB_NAME` = `hireez`
   - `DB_PORT` = `3306`
   - `DB_SSL` = `true`

### Using Streamlit Cloud (Free Frontend)

1. Create a new GitHub repo called `HireEZ-Frontend`
2. Push the `frontend/` folder, `.streamlit/`, and `Dockerfile.frontend` to it:
   ```bash
   git subtree push --prefix frontend origin frontend
   ```
3. Go to [share.streamlit.io](https://share.streamlit.io) → Sign up with GitHub
4. Click **New app** → Select `HireEZ-Frontend` repo
5. Set **Main file path:** `app.py`
6. In **Advanced settings**, add:
   - `API_BASE` = `https://hireez-backend.onrender.com` (your Render URL)
7. Click **Deploy**

### Updating Google OAuth for Production

After deploying, update the Google Cloud Console redirect URI:

1. Go to [console.cloud.google.com](https://console.cloud.google.com) → **APIs & Services** → **Credentials**
2. Click your **OAuth 2.0 Client ID**
3. Under **Authorized redirect URIs**, add:
   ```
   https://hireez-backend.onrender.com/google/oauth/callback
   ```
4. Save

## Project Structure

```
HireEZ/
├── backend/
│   ├── api/              # FastAPI route handlers
│   ├── core/             # Constants, exceptions, handlers
│   ├── database/          # SQLAlchemy connection
│   ├── github/           # GitHub API client and analyzer
│   ├── interview/        # Google Calendar / Meet integration
│   ├── intelligence/     # Resume text extraction
│   ├── models/           # SQLAlchemy ORM models
│   ├── pipeline/         # 4-stage pipeline engine
│   ├── ranking/          # Ranking and scoring logic
│   ├── repositories/     # Data access layer
│   ├── schemas/         # Pydantic schemas
│   └── services/         # Business logic (CSV, email, import)
├── frontend/
│   └── app.py           # Streamlit single-page app
├── .streamlit/
│   └── config.toml      # Streamlit server config
├── docker-compose.yml    # Full stack containerization
├── Dockerfile           # FastAPI backend container
├── Dockerfile.frontend  # Streamlit frontend container
├── requirements.txt     # Python dependencies
└── README.md
```

## License

MIT
