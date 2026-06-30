# HireEZ — FastAPI Backend Dockerfile
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
COPY .env.example .env 2>/dev/null || true

# Expose port
EXPOSE 8002

# Run uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8002"]
