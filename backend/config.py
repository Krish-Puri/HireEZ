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


config = Config()