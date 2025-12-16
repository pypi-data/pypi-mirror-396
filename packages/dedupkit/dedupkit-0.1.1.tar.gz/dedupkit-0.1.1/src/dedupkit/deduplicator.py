from dataclasses import dataclass
from .providers.base import EmbeddingProvider
from .storage.base import StorageBackend, SearchHit, AsyncStorageBackend
from .validation import validate_non_empty_string
import uuid

@dataclass
class DedupResult:
    is_duplicate: bool
    matches: list[SearchHit]


class Deduplicator:
    def __init__(self, embedding: EmbeddingProvider, storage: StorageBackend, threshold: float = 0.85, top_k: int = 5):
        self.embedding = embedding
        self.storage = storage
        self.threshold = threshold
        self.top_k = top_k

    def add(self, text: str, item_id: str | None = None, metadata: dict | None = None) -> str:
        validate_non_empty_string(text, "text")

        embedded = self.embedding.embed(text)

        item_id = str(uuid.uuid4()) if item_id is None else item_id

        self.storage.store(item_id, embedded, metadata)

        return item_id


    def check(self, text: str, threshold: float | None = None) -> DedupResult:
        validate_non_empty_string(text, "text")

        threshold = self.threshold if threshold is None else threshold
        embedded = self.embedding.embed(text)
        hits = self.storage.search(embedded, self.top_k)

        matches = [hit for hit in hits if hit.similarity >= threshold]

        return DedupResult(is_duplicate=len(matches) > 0, matches=matches)


    def remove(self, item_id: str) -> bool:
        validate_non_empty_string(item_id, "item_id")

        return self.storage.delete(item_id)

    def __len__(self) -> int:
        return self.storage.count()


class AsyncDeduplicator:
    def __init__(self, embedding: EmbeddingProvider, storage: AsyncStorageBackend, threshold: float = 0.85, top_k: int = 5):
        self.embedding = embedding
        self.storage = storage
        self.threshold = threshold
        self.top_k = top_k

    async def add(self, text: str, item_id: str | None = None, metadata: dict | None = None) -> str:
        validate_non_empty_string(text, "text")

        embedded = self.embedding.embed(text)

        item_id = str(uuid.uuid4()) if item_id is None else item_id

        await self.storage.store(item_id, embedded, metadata)

        return item_id


    async def check(self, text: str, threshold:  float | None = None) -> DedupResult:
        validate_non_empty_string(text, "text")

        threshold = self.threshold if threshold is None else threshold
        embedded = self.embedding.embed(text)
        hits = await self.storage.search(embedded, self.top_k)

        matches = [hit for hit in hits if hit.similarity >= threshold]

        return DedupResult(is_duplicate=len(matches) > 0, matches=matches)

    async def remove(self, item_id: str) -> bool:
        validate_non_empty_string(item_id, "item_id")
        return await self.storage.delete(item_id)

    async def count(self) -> int:
        return await self.storage.count()

