from __future__ import annotations

import importlib
import io
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


class ApiRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        fake_embedding_module = types.ModuleType(
            "Backend.app.services.embedding_service"
        )
        fake_embedding_module.generate_embedding = cls._fake_generate_embedding
        cls._original_embedding_module = sys.modules.get(
            "Backend.app.services.embedding_service"
        )
        sys.modules["Backend.app.services.embedding_service"] = (
            fake_embedding_module
        )

        for module_name in [
            "Backend.app.services.faiss_service",
            "Backend.app.services.recommendation_service",
            "Backend.app.services.matching_engine",
            "Backend.app.services.similarity_service",
            "Backend.app.services.explanation_service",
            "Backend.app.api.routes",
            "Backend.app.main",
        ]:
            sys.modules.pop(module_name, None)

        cls.main_module = importlib.import_module("Backend.app.main")

    @classmethod
    def tearDownClass(cls) -> None:
        for module_name in [
            "Backend.app.main",
            "Backend.app.api.routes",
            "Backend.app.services.similarity_service",
            "Backend.app.services.matching_engine",
            "Backend.app.services.recommendation_service",
            "Backend.app.services.faiss_service",
            "Backend.app.services.explanation_service",
        ]:
            sys.modules.pop(module_name, None)

        if cls._original_embedding_module is None:
            sys.modules.pop("Backend.app.services.embedding_service", None)
        else:
            sys.modules["Backend.app.services.embedding_service"] = (
                cls._original_embedding_module
            )

    @staticmethod
    def _fake_generate_embedding(text: str) -> list[float]:
        return [float(len(text) + 1), 2.0, 3.0]

    def test_embedding_route_returns_embedding_metadata(self) -> None:
        with patch.object(
            self.main_module,
            "init_database",
            return_value=None,
        ), patch.object(
            self.main_module,
            "ensure_faiss_index",
            return_value={"index": None, "jobs": [], "embeddings": None},
        ), patch.object(self.main_module, "load_jobs", return_value=[]):
            with TestClient(self.main_module.app) as client:
                response = client.get("/embedding")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["embedding_length"], 3)
        self.assertEqual(payload["sample"], [32.0, 2.0, 3.0])

    def test_resume_match_route_processes_uploaded_resume(self) -> None:
        with tempfile.TemporaryDirectory(prefix="api-upload-") as temp_dir:
            with patch.object(
                self.main_module,
                "init_database",
                return_value=None,
            ), patch.object(
                self.main_module,
                "ensure_faiss_index",
                return_value={"index": None, "jobs": [], "embeddings": None},
            ), patch.object(self.main_module, "load_jobs", return_value=[]), patch(
                "Backend.app.api.routes.UPLOAD_DIR",
                Path(temp_dir),
            ), patch(
                "Backend.app.api.routes.extract_text_from_pdf",
                return_value="Python FastAPI SQL resume",
            ), patch(
                "Backend.app.api.routes.calculate_similarity",
                return_value={
                    "match_score": 91.5,
                    "match_label": "Strong Match",
                    "semantic_score": 95.0,
                    "skill_match_score": 83.0,
                    "matched_skills": ["python", "sql"],
                    "final_score": 91.5,
                },
            ):
                with TestClient(self.main_module.app) as client:
                    response = client.post(
                        "/resume-match",
                        files={
                            "file": ("resume.pdf", io.BytesIO(b"fake pdf"), "application/pdf")
                        },
                        data={"job_description": "Python SQL Docker"},
                    )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["filename"], "resume.pdf")
        self.assertEqual(payload["match_score"], 91.5)
        self.assertEqual(payload["match_label"], "Strong Match")
        self.assertIn("Python FastAPI SQL resume", payload["extracted_text_preview"])

    def test_job_recommendations_route_returns_ranked_results(self) -> None:
        fake_jobs = [
            {"id": 1, "title": "Backend Engineer", "description": "Python APIs"},
            {"id": 2, "title": "ML Engineer", "description": "Machine learning"},
        ]
        fake_recommendations = [
            {
                "id": 2,
                "title": "ML Engineer",
                "description": "Machine learning",
                "match_score": 96.2,
                "match_label": "Strong Match",
                "semantic_score": 98.0,
                "skill_match_score": 92.0,
                "matched_skills": ["python"],
                "missing_skills": ["docker"],
            }
        ]

        with tempfile.TemporaryDirectory(prefix="api-upload-") as temp_dir:
            with patch.object(
                self.main_module,
                "init_database",
                return_value=None,
            ), patch.object(
                self.main_module,
                "ensure_faiss_index",
                return_value={"index": None, "jobs": fake_jobs, "embeddings": None},
            ), patch.object(
                self.main_module,
                "load_jobs",
                return_value=fake_jobs,
            ), patch(
                "Backend.app.api.routes.UPLOAD_DIR",
                Path(temp_dir),
            ), patch(
                "Backend.app.api.routes.extract_text_from_pdf",
                return_value="resume text",
            ), patch(
                "Backend.app.api.routes.load_jobs",
                return_value=fake_jobs,
            ), patch(
                "Backend.app.api.routes.recommend_jobs",
                return_value=fake_recommendations,
            ), patch.dict(
                os.environ,
                {"OPENAI_API_KEY": ""},
            ):
                with TestClient(self.main_module.app) as client:
                    response = client.post(
                        "/job-recommendations",
                        files={
                            "file": ("resume.pdf", io.BytesIO(b"fake pdf"), "application/pdf")
                        },
                        data={"top_k": "5"},
                    )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["filename"], "resume.pdf")
        self.assertEqual(payload["total_jobs_compared"], 2)
        self.assertEqual(len(payload["recommendations"]), 1)
        self.assertEqual(payload["recommendations"][0]["id"], 2)
        self.assertEqual(payload["recommendations"][0]["match_label"], "Strong Match")
        self.assertNotIn("explanation", payload["recommendations"][0])

    def test_job_recommendations_route_can_add_explanations_without_changing_scores(self) -> None:
        fake_jobs = [
            {"id": 1, "title": "Backend Engineer", "description": "Python APIs"},
            {"id": 2, "title": "ML Engineer", "description": "Machine learning"},
        ]
        fake_recommendations = [
            {
                "id": 2,
                "title": "ML Engineer",
                "description": "Machine learning",
                "match_score": 96.2,
                "match_label": "Strong Match",
                "semantic_score": 98.0,
                "skill_match_score": 92.0,
                "matched_skills": ["python"],
                "missing_skills": ["docker"],
            }
        ]

        with tempfile.TemporaryDirectory(prefix="api-upload-") as temp_dir:
            with patch.object(
                self.main_module,
                "init_database",
                return_value=None,
            ), patch.object(
                self.main_module,
                "ensure_faiss_index",
                return_value={"index": None, "jobs": fake_jobs, "embeddings": None},
            ), patch.object(
                self.main_module,
                "load_jobs",
                return_value=fake_jobs,
            ), patch(
                "Backend.app.api.routes.UPLOAD_DIR",
                Path(temp_dir),
            ), patch(
                "Backend.app.api.routes.extract_text_from_pdf",
                return_value="resume text",
            ), patch(
                "Backend.app.api.routes.load_jobs",
                return_value=fake_jobs,
            ), patch(
                "Backend.app.api.routes.recommend_jobs",
                return_value=fake_recommendations,
            ), patch.dict(
                os.environ,
                {"OPENAI_API_KEY": ""},
            ):
                with TestClient(self.main_module.app) as client:
                    response = client.post(
                        "/job-recommendations",
                        files={
                            "file": ("resume.pdf", io.BytesIO(b"fake pdf"), "application/pdf")
                        },
                        data={"top_k": "5", "explain": "true"},
                    )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        recommendation = payload["recommendations"][0]
        self.assertEqual(recommendation["id"], 2)
        self.assertEqual(recommendation["match_score"], 96.2)
        self.assertEqual(recommendation["semantic_score"], 98.0)
        self.assertEqual(recommendation["skill_match_score"], 92.0)
        self.assertEqual(recommendation["explanation"]["source"], "fallback")
        self.assertEqual(recommendation["explanation"]["missing_skills"], ["docker"])


if __name__ == "__main__":
    unittest.main()
