"""
Application Configuration

Loads all environment variables from .env and exposes
them through a single Config object.

Author: HireEZ
"""

from pathlib import Path

from dotenv import load_dotenv
import os

# Locate the project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env
load_dotenv(BASE_DIR / ".env")


class Config:
    """
    Central configuration class.
    """

    # -------------------------
    # Database
    # -------------------------

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    # -------------------------
    # Gemini
    # -------------------------

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # -------------------------
    # Security
    # -------------------------

    SECRET_KEY = os.getenv("SECRET_KEY")

    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN")

    # -------------------------
    # Email (SMTP)
    # -------------------------

    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    EMAIL_FROM = os.getenv("EMAIL_FROM")

    # -------------------------
    # Google Calendar / OAuth
    # -------------------------

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501/oauth/callback")

    # -------------------------
    # App
    # -------------------------

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8501")


config = Config()
