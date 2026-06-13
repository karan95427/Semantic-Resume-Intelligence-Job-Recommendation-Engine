from __future__ import annotations

import importlib
import sys
import types
import unittest


class MatchingEngineTests(unittest.TestCase):
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
        sys.modules.pop("Backend.app.services.matching_engine", None)
        sys.modules.pop("Backend.app.services.similarity_service", None)
        cls.matching_engine = importlib.import_module(
            "Backend.app.services.matching_engine"
        )
        cls.similarity_service = importlib.import_module(
            "Backend.app.services.similarity_service"
        )

    @classmethod
    def tearDownClass(cls) -> None:
        sys.modules.pop("Backend.app.services.matching_engine", None)
        sys.modules.pop("Backend.app.services.similarity_service", None)
        if cls._original_embedding_module is None:
            sys.modules.pop("Backend.app.services.embedding_service", None)
        else:
            sys.modules["Backend.app.services.embedding_service"] = (
                cls._original_embedding_module
            )

    @staticmethod
    def _fake_generate_embedding(text: str) -> list[float]:
        normalized = text.lower()
        python_score = 5.0 if "python" in normalized else 1.0
        ml_score = 5.0 if "machine learning" in normalized else 1.0
        api_score = 5.0 if "fastapi" in normalized else 1.0
        return [python_score, ml_score, api_score]

    def test_calculate_skill_details_tracks_matches_and_missing(self) -> None:
        result = self.matching_engine.calculate_skill_details(
            resume_text="Python FastAPI machine learning",
            job_text="Python machine learning nlp",
        )

        self.assertEqual(result["matched_skills"], ["machine learning", "python"])
        self.assertEqual(result["missing_skills"], ["nlp"])
        self.assertEqual(result["skill_match_score"], 66.67)

    def test_calculate_skill_details_normalizes_skill_aliases(self) -> None:
        result = self.matching_engine.calculate_skill_details(
            resume_text="Built ML systems with Postgres and REST API design",
            job_text="Need machine learning, postgresql, and rest apis experience",
        )

        self.assertEqual(
            result["matched_skills"],
            ["machine learning", "postgresql", "rest apis"],
        )
        self.assertEqual(result["missing_skills"], [])
        self.assertEqual(result["skill_match_score"], 100.0)

    def test_score_job_uses_weighted_semantic_and_skill_scores(self) -> None:
        result = self.matching_engine.score_job(
            resume_text="Python FastAPI machine learning",
            job_text="Python FastAPI nlp",
        )

        self.assertIn("match_score", result)
        self.assertIn("match_label", result)
        self.assertIn("semantic_score", result)
        self.assertIn("skill_match_score", result)
        self.assertEqual(result["missing_skills"], ["nlp"])
        self.assertGreater(result["semantic_score"], 0)
        self.assertAlmostEqual(
            result["match_score"],
            result["final_score"],
            places=2,
        )
        self.assertEqual(result["match_label"], "Moderate Match")

    def test_determine_match_label_uses_score_bands(self) -> None:
        self.assertEqual(
            self.matching_engine.determine_match_label(92.0),
            "Strong Match",
        )
        self.assertEqual(
            self.matching_engine.determine_match_label(75.0),
            "Moderate Match",
        )
        self.assertEqual(
            self.matching_engine.determine_match_label(62.0),
            "Low Match",
        )

    def test_similarity_service_returns_api_friendly_payload(self) -> None:
        result = self.similarity_service.calculate_similarity(
            "Python FastAPI machine learning",
            "Python machine learning nlp",
        )

        self.assertEqual(
            sorted(result.keys()),
            [
                "final_score",
                "match_label",
                "match_score",
                "matched_skills",
                "semantic_score",
                "skill_match_score",
            ],
        )
        self.assertEqual(result["matched_skills"], ["machine learning", "python"])
        self.assertEqual(result["match_label"], "Moderate Match")

    def test_similarity_service_uses_canonical_skill_names(self) -> None:
        result = self.similarity_service.calculate_similarity(
            "ML with Postgres and REST API integrations",
            "Looking for machine learning, postgresql, and rest apis",
        )

        self.assertEqual(
            result["matched_skills"],
            ["machine learning", "postgresql", "rest apis"],
        )


if __name__ == "__main__":
    unittest.main()
