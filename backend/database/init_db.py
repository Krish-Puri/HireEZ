"""
Initializes the database.

Creates every table defined in models.
"""

from backend.database.base import Base
from backend.database.connection import engine

# Import every model here
from backend.models.candidate import Candidate


def init_database():
    print("Creating database tables...")

    Base.metadata.create_all(bind=engine)

    print("Database initialized successfully!")


if __name__ == "__main__":
    init_database()