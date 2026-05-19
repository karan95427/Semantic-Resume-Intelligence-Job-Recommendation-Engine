from __future__ import annotations

from typing import Any

import faiss
import numpy as np

from .embedding_service import generate_embedding


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


def build_faiss_index(jobs: list[dict]) -> dict[str, Any]:
    signature = _jobs_signature(jobs)

    if _INDEX_CACHE["signature"] == signature:
        return {
            "index": _INDEX_CACHE["index"],
            "jobs": _INDEX_CACHE["jobs"],
            "embeddings": _INDEX_CACHE["embeddings"],
        }

    embedding_matrix = _build_embedding_matrix(jobs)

    if embedding_matrix.size == 0:
        index = None
    else:
        dimension = embedding_matrix.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embedding_matrix)

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
    for distance, index_position in zip(distances[0], indices[0]):
        if index_position < 0:
            continue

        job = jobs[index_position]
        results.append(
            {
                "job": job,
                "distance": float(distance),
                "index_position": int(index_position),
                "embedding": embeddings[index_position].tolist(),
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
