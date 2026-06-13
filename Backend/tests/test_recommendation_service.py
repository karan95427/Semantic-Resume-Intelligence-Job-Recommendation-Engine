from __future__ import annotations

import importlib
import json
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path


class RecommendationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="recommendation-service-"))
        self.db_file = self.temp_dir / "jobs.sqlite3"
        self.mapping_file = self.temp_dir / "job_mapping.json"

        fake_embedding_module = types.ModuleType(
            "Backend.app.services.embedding_service"
        )
        fake_embedding_module.generate_embedding = lambda text: [float(len(text)), 1.0]
        self._original_embedding_module = sys.modules.get(
            "Backend.app.services.embedding_service"
        )
        sys.modules["Backend.app.services.embedding_service"] = (
            fake_embedding_module
        )

        for module_name in [
            "Backend.app.services.recommendation_service",
            "Backend.app.repositories.job_repository",
            "Backend.app.models.job",
            "Backend.app.db",
        ]:
            sys.modules.pop(module_name, None)

        self.db_module = importlib.import_module("Backend.app.db")
        self.db_module.configure_database(f"sqlite:///{self.db_file}")
        self.db_module.init_database()

        self.job_repository = importlib.import_module(
            "Backend.app.repositories.job_repository"
        )
        self.recommendation_service = importlib.import_module(
            "Backend.app.services.recommendation_service"
        )
        self.recommendation_service.ensure_job_mapping.__globals__["JOB_MAPPING_FILE"] = (
            self.mapping_file
        )

    def tearDown(self) -> None:
        sys.modules.pop("Backend.app.services.recommendation_service", None)
        sys.modules.pop("Backend.app.repositories.job_repository", None)
        sys.modules.pop("Backend.app.models.job", None)
        sys.modules.pop("Backend.app.db", None)
        if self._original_embedding_module is None:
            sys.modules.pop("Backend.app.services.embedding_service", None)
        else:
            sys.modules["Backend.app.services.embedding_service"] = (
                self._original_embedding_module
            )
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_jobs_reads_jobs_from_database_and_creates_mapping_file(self) -> None:
        self.job_repository.import_jobs(
            [
                {
                    "id": 2,
                    "title": "ML Engineer",
                    "company": "Acme",
                    "location": "Remote",
                    "description": "Python machine learning pipelines",
                },
                {
                    "id": 1,
                    "title": "Backend Engineer",
                    "company": "Beta",
                    "location": "Pune",
                    "description": "FastAPI services and APIs",
                },
            ]
        )

        jobs = self.recommendation_service.load_jobs()

        self.assertEqual([job["id"] for job in jobs], [1, 2])
        mapping = json.loads(self.mapping_file.read_text(encoding="utf-8"))
        self.assertEqual(mapping, {"0": 1, "1": 2})

    def test_import_jobs_updates_existing_rows_without_duplicates(self) -> None:
        self.job_repository.import_jobs(
            [
                {
                    "id": 1,
                    "title": "Backend Engineer",
                    "company": "Acme",
                    "location": "Remote",
                    "description": "FastAPI services",
                }
            ]
        )

        self.job_repository.import_jobs(
            [
                {
                    "id": 1,
                    "title": "Senior Backend Engineer",
                    "company": "Acme",
                    "location": "Remote",
                    "description": "FastAPI services and PostgreSQL",
                }
            ]
        )

        jobs = self.recommendation_service.load_jobs()

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["title"], "Senior Backend Engineer")
        self.assertIn("PostgreSQL", jobs[0]["description"])


if __name__ == "__main__":
    unittest.main()
