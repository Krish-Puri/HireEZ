"""
Initializes the database.

Creates every table defined in models.
"""

from backend.database.base import Base
from backend.database.connection import engine

from backend.models.candidate import Candidate
from backend.models.job import Job
from backend.models.evaluation import Evaluation
from backend.models.test_result import TestResult


def init_database():
    print("Creating database tables...")

    Base.metadata.create_all(bind=engine)

    print("Database initialized successfully!")


if __name__ == "__main__":
    init_database()
