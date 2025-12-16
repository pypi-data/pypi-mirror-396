from .base import StorageBackend, SearchHit
import numpy as np
from ..validation import validate_non_empty_string, validate_dimensions, validate_embedding_dimensions, \
    validate_positive_integer


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    a_arr = np.array(a)
    b_arr = np.array(b)

    dot_product = np.dot(a_arr, b_arr.T)
    magnitude_a = np.linalg.norm(a_arr)
    magnitude_b = np.linalg.norm(b_arr)

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


class MemoryStorage(StorageBackend):

    def __init__(self):
        self._storage: dict[str, dict] = {}

    def store(self, item_id: str, embedding: list[float], metadata: dict | None) -> None:
        validate_non_empty_string(item_id, "item_id")
        validate_embedding_dimensions(embedding, len(embedding))

        self._storage[item_id] = { "embedding": embedding, "metadata": metadata }

    def search(self, embedding: list[float], top_k: int) -> list[SearchHit]:
        if not self._storage:
            return []

        validate_embedding_dimensions(embedding, len(embedding))
        validate_positive_integer(top_k, "top_k")

        results = []
        for embed_id, data in self._storage.items():
            similarity = cosine_similarity(embedding, data["embedding"])
            results.append(SearchHit(id=embed_id, similarity=similarity, metadata=data["metadata"]))

        results.sort(key=lambda x: x.similarity, reverse=True)

        return results[:top_k]

    def delete(self, item_id: str) -> bool:
        validate_non_empty_string(item_id, "item_id")

        if not self._storage:
            return False

        deleted = self._storage.pop(item_id, None)

        return deleted is not None

    def count(self) -> int:
        return len(self._storage)
