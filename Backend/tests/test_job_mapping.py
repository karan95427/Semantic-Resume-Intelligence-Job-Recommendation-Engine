from __future__ import annotations

import importlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


class JobMappingServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="job-mapping-"))
        self.mapping_file = self.temp_dir / "job_mapping.json"

        sys.modules.pop("Backend.app.services.job_mapping_service", None)
        self.job_mapping_service = importlib.import_module(
            "Backend.app.services.job_mapping_service"
        )
        self.job_mapping_service.JOB_MAPPING_FILE = self.mapping_file

        self.jobs = [
            {
                "id": 0,
                "title": "Backend Engineer",
                "company": "Acme",
                "location": "Remote",
                "description": "Python APIs",
            },
            {
                "id": 1,
                "title": "ML Engineer",
                "company": "Beta",
                "location": "Bengaluru",
                "description": "Vector search",
            },
        ]

    def tearDown(self) -> None:
        sys.modules.pop("Backend.app.services.job_mapping_service", None)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ensure_job_mapping_writes_expected_mapping(self) -> None:
        mapping = self.job_mapping_service.ensure_job_mapping(self.jobs)

        self.assertEqual(mapping["0"], 0)
        self.assertEqual(mapping["1"], 1)

        on_disk = json.loads(self.mapping_file.read_text(encoding="utf-8"))
        self.assertEqual(on_disk, mapping)

    def test_ensure_job_mapping_refreshes_stale_mapping(self) -> None:
        self.mapping_file.write_text(
            json.dumps({"0": 999}),
            encoding="utf-8",
        )

        mapping = self.job_mapping_service.ensure_job_mapping(self.jobs)

        self.assertEqual(mapping, self.job_mapping_service.build_job_mapping(self.jobs))
        on_disk = json.loads(self.mapping_file.read_text(encoding="utf-8"))
        self.assertEqual(on_disk["1"], 1)


if __name__ == "__main__":
    unittest.main()
