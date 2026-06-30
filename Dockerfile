# HireEZ — FastAPI Backend Dockerfile (Render + PlanetScale compatible)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# PORT env var is set by Render (10000); fallback to 8002 for local dev
ENV PORT=8002

EXPOSE $PORT

# Run uvicorn — reads PORT from environment (Render sets this)
CMD uvicorn backend.main:app --host 0.0.0.0 --port $PORT
