from __future__ import annotations

import importlib
import json
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path


def _embedding_values(text: str) -> list[float]:
    ascii_total = sum(ord(char) for char in text)
    text_length = len(text)
    word_count = len(text.split())
    return [
        float((ascii_total % 97) + 1),
        float(text_length + 1),
        float(word_count + 1),
    ]


class FaissPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="faiss-persist-"))
        self.index_file = self.temp_dir / "jobs.index"
        self.meta_file = self.temp_dir / "jobs.index.meta.json"
        self.embedding_calls: list[str] = []

        fake_embedding_module = types.ModuleType(
            "Backend.app.services.embedding_service"
        )

        def fake_generate_embedding(text: str) -> list[float]:
            self.embedding_calls.append(text)
            return _embedding_values(text)

        fake_embedding_module.generate_embedding = fake_generate_embedding
        self._original_embedding_module = sys.modules.get(
            "Backend.app.services.embedding_service"
        )
        sys.modules["Backend.app.services.embedding_service"] = (
            fake_embedding_module
        )

        sys.modules.pop("Backend.app.services.faiss_service", None)
        self.faiss_service = importlib.import_module(
            "Backend.app.services.faiss_service"
        )
        self.faiss_service.INDEX_FILE = self.index_file
        self.faiss_service.INDEX_META_FILE = self.meta_file
        self.faiss_service._INDEX_CACHE.update(
            {
                "signature": None,
                "index": None,
                "jobs": None,
                "embeddings": None,
            }
        )

        self.jobs = [
            {
                "id": 1,
                "title": "Python Developer",
                "description": "Python APIs and FastAPI services",
            },
            {
                "id": 2,
                "title": "Data Scientist",
                "description": "Machine learning and vector search",
            },
        ]

    def tearDown(self) -> None:
        sys.modules.pop("Backend.app.services.faiss_service", None)
        if self._original_embedding_module is None:
            sys.modules.pop("Backend.app.services.embedding_service", None)
        else:
            sys.modules["Backend.app.services.embedding_service"] = (
                self._original_embedding_module
            )
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _reset_runtime_cache(self) -> None:
        self.faiss_service._INDEX_CACHE.update(
            {
                "signature": None,
                "index": None,
                "jobs": None,
                "embeddings": None,
            }
        )

    def test_build_saves_index_and_metadata(self) -> None:
        bundle = self.faiss_service.build_faiss_index(self.jobs)

        self.assertTrue(self.index_file.exists())
        self.assertTrue(self.meta_file.exists())
        self.assertEqual(bundle["index"].ntotal, len(self.jobs))
        self.assertEqual(len(self.embedding_calls), len(self.jobs))

        metadata = json.loads(self.meta_file.read_text(encoding="utf-8"))
        self.assertEqual(
            metadata["signature"],
            [list(item) for item in self.faiss_service._jobs_signature(self.jobs)],
        )

    def test_existing_index_loads_without_reembedding(self) -> None:
        self.faiss_service.build_faiss_index(self.jobs)
        self.assertEqual(len(self.embedding_calls), len(self.jobs))

        self._reset_runtime_cache()

        def fail_on_embedding(_: str) -> list[float]:
            raise AssertionError("embedding generation should not run")

        self.faiss_service.generate_embedding = fail_on_embedding
        bundle = self.faiss_service.build_faiss_index(self.jobs)

        self.assertIsNotNone(bundle["index"])
        self.assertIsNone(bundle["embeddings"])
        self.assertEqual(bundle["index"].ntotal, len(self.jobs))

    def test_search_reconstructs_embeddings_after_disk_load(self) -> None:
        self.faiss_service.build_faiss_index(self.jobs)
        self._reset_runtime_cache()

        results = self.faiss_service.search_similar_jobs(
            resume_embedding=_embedding_values(self.jobs[0]["description"]),
            jobs=self.jobs,
            top_k=1,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["job"]["id"], 1)
        self.assertEqual(
            results[0]["embedding"],
            _embedding_values(self.jobs[0]["description"]),
        )

    def test_signature_change_rebuilds_index(self) -> None:
        self.faiss_service.build_faiss_index(self.jobs)
        self._reset_runtime_cache()
        self.embedding_calls.clear()

        updated_jobs = [dict(job) for job in self.jobs]
        updated_jobs[1]["description"] = (
            "Machine learning, FAISS persistence, and vector search"
        )

        bundle = self.faiss_service.build_faiss_index(updated_jobs)

        self.assertIsNotNone(bundle["embeddings"])
        self.assertEqual(len(self.embedding_calls), len(updated_jobs))

        metadata = json.loads(self.meta_file.read_text(encoding="utf-8"))
        self.assertEqual(
            metadata["signature"],
            [
                list(item)
                for item in self.faiss_service._jobs_signature(updated_jobs)
            ],
        )


if __name__ == "__main__":
    unittest.main()
