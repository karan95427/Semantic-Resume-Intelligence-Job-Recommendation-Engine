from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from Backend.app import db
from Backend.app.models.job import Base
from Backend.app.services.explanation_service import (
    explain_recommendations,
    validate_explanation,
)


class FakeFailingProvider:
    def generate_explanation(self, facts: dict) -> dict:
        raise RuntimeError("provider unavailable")


class FakeSuccessfulProvider:
    provider_name = "fake"
    model = "fake-model"

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def generate_explanation(self, facts: dict) -> dict:
        self.calls.append(facts)
        return {
            "summary": "The role matches because Python and FastAPI are present.",
            "matched_skills": ["python", "fastapi"],
            "missing_skills": ["docker"],
            "strengths": ["Python API experience is aligned."],
            "weaknesses": ["Docker is not visible in the supplied facts."],
            "improvement_suggestions": ["Add a Docker deployment bullet if accurate."],
        }


class FakeHallucinatingProvider:
    provider_name = "fake"
    model = "fake-model"

    def generate_explanation(self, facts: dict) -> dict:
        return {
            "summary": "The role matches.",
            "matched_skills": ["python", "kubernetes"],
            "missing_skills": ["docker"],
            "strengths": ["Python experience is aligned."],
            "weaknesses": ["Docker is missing."],
            "improvement_suggestions": ["Add Docker evidence."],
        }


class ExplanationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="explanation-cache-"))
        self.db_file = self.temp_dir / "cache.sqlite3"
        db.configure_database(f"sqlite:///{self.db_file}")
        Base.metadata.create_all(bind=db.get_engine())

    def tearDown(self) -> None:
        db.reset_database_state()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_fallback_explanation_uses_existing_match_facts(self) -> None:
        recommendations = [
            {
                "id": 1,
                "title": "Backend Engineer",
                "match_score": 88.5,
                "match_label": "Strong Match",
                "matched_skills": ["python", "fastapi"],
                "missing_skills": ["docker"],
            }
        ]

        explained = explain_recommendations(
            recommendations,
            provider=FakeFailingProvider(),
        )

        self.assertNotIn("explanation", recommendations[0])
        explanation = explained[0]["explanation"]
        self.assertEqual(explanation["source"], "fallback")
        self.assertEqual(explanation["matched_skills"], ["python", "fastapi"])
        self.assertEqual(explanation["missing_skills"], ["docker"])
        self.assertIn("docker", explanation["improvement_suggestions"][0])

    def test_validation_rejects_hallucinated_skills(self) -> None:
        explanation = {
            "summary": "Good fit.",
            "matched_skills": ["python", "kubernetes"],
            "missing_skills": ["docker"],
            "strengths": ["Python experience"],
            "weaknesses": ["Docker gap"],
            "improvement_suggestions": ["Add Docker evidence."],
            "source": "llm",
        }

        with self.assertRaises(ValueError):
            validate_explanation(
                explanation,
                matched_skills=["python"],
                missing_skills=["docker"],
            )

    def test_provider_success_adds_validated_llm_explanation(self) -> None:
        provider = FakeSuccessfulProvider()
        recommendations = [
            {
                "id": 1,
                "title": "Backend Engineer",
                "description": "Full job description should not be sent.",
                "match_score": 88.5,
                "match_label": "Strong Match",
                "semantic_score": 90.0,
                "skill_match_score": 80.0,
                "matched_skills": ["python", "fastapi"],
                "missing_skills": ["docker"],
            }
        ]

        explained = explain_recommendations(
            recommendations,
            resume_text="Python FastAPI project with PostgreSQL",
            provider=provider,
        )

        explanation = explained[0]["explanation"]
        self.assertEqual(explanation["source"], "llm")
        self.assertEqual(explanation["matched_skills"], ["python", "fastapi"])
        self.assertEqual(explanation["missing_skills"], ["docker"])
        self.assertEqual(provider.calls[0]["job_signals"]["title"], "Backend Engineer")
        self.assertNotIn("description", provider.calls[0]["job_signals"])

    def test_cached_explanation_bypasses_provider_calls(self) -> None:
        first_provider = FakeSuccessfulProvider()
        second_provider = FakeSuccessfulProvider()
        recommendations = [
            {
                "id": 1,
                "title": "Backend Engineer",
                "match_score": 88.5,
                "match_label": "Strong Match",
                "semantic_score": 90.0,
                "skill_match_score": 80.0,
                "matched_skills": ["python", "fastapi"],
                "missing_skills": ["docker"],
            }
        ]

        first = explain_recommendations(
            recommendations,
            resume_text="Python FastAPI project",
            provider=first_provider,
        )
        second = explain_recommendations(
            recommendations,
            resume_text="Python FastAPI project",
            provider=second_provider,
        )

        self.assertEqual(len(first_provider.calls), 1)
        self.assertEqual(len(second_provider.calls), 0)
        self.assertEqual(first[0]["explanation"], second[0]["explanation"])

    def test_hallucinated_provider_skills_fall_back(self) -> None:
        recommendations = [
            {
                "id": 1,
                "title": "Backend Engineer",
                "match_score": 88.5,
                "match_label": "Strong Match",
                "matched_skills": ["python"],
                "missing_skills": ["docker"],
            }
        ]

        explained = explain_recommendations(
            recommendations,
            provider=FakeHallucinatingProvider(),
        )

        explanation = explained[0]["explanation"]
        self.assertEqual(explanation["source"], "fallback")
        self.assertEqual(explanation["matched_skills"], ["python"])
        self.assertEqual(explanation["missing_skills"], ["docker"])


if __name__ == "__main__":
    unittest.main()
