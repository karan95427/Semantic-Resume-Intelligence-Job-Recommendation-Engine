from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from .embedding_service import generate_embedding


INDEX_FILE = Path(__file__).resolve().parents[2] / "data" / "jobs" / "jobs.index"
INDEX_META_FILE = INDEX_FILE.with_suffix(".index.meta.json")

_INDEX_CACHE: dict[str, Any] = {
    "signature": None,
    "index": None,
    "jobs": None,
    "embeddings": None,
}


def _jobs_signature(jobs: list[dict]) -> tuple[tuple[Any, ...], ...]:
    return tuple(
        (
            job.get("id"),
            job.get("title", ""),
            job.get("description", ""),
        )
        for job in jobs
    )


def _build_embedding_matrix(jobs: list[dict]) -> np.ndarray:
    embeddings = [
        generate_embedding(job.get("description", ""))
        for job in jobs
    ]

    if not embeddings:
        return np.empty((0, 0), dtype="float32")

    return np.asarray(embeddings, dtype="float32")


def _signature_to_serializable(signature: tuple[tuple[Any, ...], ...]) -> list[list[Any]]:
    return [list(item) for item in signature]


def _load_index_from_disk(
    jobs: list[dict],
    signature: tuple[tuple[Any, ...], ...],
) -> dict[str, Any] | None:
    if not INDEX_FILE.exists() or not INDEX_META_FILE.exists():
        return None

    try:
        metadata = json.loads(INDEX_META_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    stored_signature = tuple(
        tuple(item) for item in metadata.get("signature", [])
    )

    if stored_signature != signature:
        return None

    try:
        index = faiss.read_index(str(INDEX_FILE))
    except RuntimeError:
        return None

    if index.ntotal != len(jobs):
        return None

    _INDEX_CACHE["signature"] = signature
    _INDEX_CACHE["index"] = index
    _INDEX_CACHE["jobs"] = jobs
    _INDEX_CACHE["embeddings"] = None

    return {
        "index": index,
        "jobs": jobs,
        "embeddings": None,
    }


def _save_index_to_disk(
    index: faiss.Index | None,
    signature: tuple[tuple[Any, ...], ...],
) -> None:
    if index is None:
        return

    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_FILE))
    INDEX_META_FILE.write_text(
        json.dumps(
            {"signature": _signature_to_serializable(signature)},
            ensure_ascii=True,
            indent=2,
        ),
        encoding="utf-8",
    )


def build_faiss_index(jobs: list[dict]) -> dict[str, Any]:
    signature = _jobs_signature(jobs)

    if _INDEX_CACHE["signature"] == signature:
        return {
            "index": _INDEX_CACHE["index"],
            "jobs": _INDEX_CACHE["jobs"],
            "embeddings": _INDEX_CACHE["embeddings"],
        }

    disk_bundle = _load_index_from_disk(jobs=jobs, signature=signature)
    if disk_bundle is not None:
        return disk_bundle

    embedding_matrix = _build_embedding_matrix(jobs)

    if embedding_matrix.size == 0:
        index = None
    else:
        dimension = embedding_matrix.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embedding_matrix)
        _save_index_to_disk(index=index, signature=signature)

    _INDEX_CACHE["signature"] = signature
    _INDEX_CACHE["index"] = index
    _INDEX_CACHE["jobs"] = jobs
    _INDEX_CACHE["embeddings"] = embedding_matrix

    return {
        "index": index,
        "jobs": jobs,
        "embeddings": embedding_matrix,
    }


def search_similar_jobs(
    resume_embedding: list[float],
    jobs: list[dict],
    top_k: int = 3,
) -> list[dict]:
    bundle = build_faiss_index(jobs)
    index = bundle["index"]
    embeddings = bundle["embeddings"]

    if index is None or top_k <= 0:
        return []

    normalized_top_k = min(top_k, len(jobs))
    query_vector = np.asarray([resume_embedding], dtype="float32")

    distances, indices = index.search(query_vector, normalized_top_k)

    results = []
    should_reconstruct = embeddings is None
    for distance, index_position in zip(distances[0], indices[0]):
        if index_position < 0:
            continue

        job = jobs[index_position]
        if should_reconstruct:
            job_embedding = index.reconstruct(int(index_position)).tolist()
        else:
            job_embedding = embeddings[index_position].tolist()
        results.append(
            {
                "job": job,
                "distance": float(distance),
                "index_position": int(index_position),
                "embedding": job_embedding,
            }
        )

    return results


def retrieve_top_job_ids(
    resume_text: str,
    jobs: list[dict],
    top_k: int = 3,
) -> list[int]:
    resume_embedding = generate_embedding(resume_text)
    search_results = search_similar_jobs(
        resume_embedding=resume_embedding,
        jobs=jobs,
        top_k=top_k,
    )

    return [item["job"]["id"] for item in search_results]


def ensure_faiss_index(jobs: list[dict]) -> dict[str, Any]:
    return build_faiss_index(jobs)
