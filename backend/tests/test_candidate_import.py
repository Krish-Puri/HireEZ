import os
import tempfile
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.base import Base
from backend.models.candidate import Candidate
from backend.repositories.candidate_repository import CandidateRepository
from backend.schemas.candidate_schema import CandidateCreate
from backend.services.csv_service import CSVService


class CandidateImportTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_csv_service_returns_statistics(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="", encoding="utf-8") as handle:
            handle.write(
                "Name,Email,College,Branch,CGPA,Best AI Project,Research Work,GitHub Profile,Resume Link\n"
                "Alice,alice@example.com,MIT,CS,8.9,Alpha,Research A,https://github.com/alice,https://resume/alice\n"
                "Bob,not-an-email,State,EE,7.5,Bravo,Research B,https://github.com/bob,https://resume/bob\n"
                "Charlie,charlie@example.com,Stanford,ME,9.1,Gamma,Research C,https://github.com/charlie,https://resume/charlie\n"
            )
            path = handle.name

        try:
            service = CSVService()
            report = service.parse_candidates(path)

            self.assertEqual(len(report.candidates), 2)
            self.assertEqual(report.statistics["total_rows"], 3)
            self.assertEqual(report.statistics["valid_rows"], 2)
            self.assertEqual(report.statistics["invalid_rows"], 1)
        finally:
            os.remove(path)

    def test_repository_create_many_inserts_multiple_candidates(self):
        repository = CandidateRepository()
        candidates = [
            CandidateCreate(
                name="Alice",
                email="alice@example.com",
                college="MIT",
                branch="CS",
                cgpa=8.9,
                best_ai_project="Alpha",
                research_work="Research A",
                github_url="https://github.com/alice",
                resume_url="https://resume/alice",
            ),
            CandidateCreate(
                name="Bob",
                email="bob@example.com",
                college="State",
                branch="EE",
                cgpa=7.5,
                best_ai_project="Bravo",
                research_work="Research B",
                github_url="https://github.com/bob",
                resume_url="https://resume/bob",
            ),
        ]

        inserted_count = repository.create_many(self.session, candidates)

        self.assertEqual(inserted_count, 2)
        self.assertEqual(self.session.query(Candidate).count(), 2)


if __name__ == "__main__":
    unittest.main()
