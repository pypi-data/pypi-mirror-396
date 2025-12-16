from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class SearchHit:
    """A single search result."""
    id: str
    similarity: float
    metadata: dict | None

class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def store(self, item_id: str, embedding: list[float], metadata: dict | None) -> None:
        """Store an embedding with its ID and optional metadata."""
        import json

    @abstractmethod
    def search(self, embedding: list[float], top_k: int) -> list[SearchHit]:
        """Find top_k most similar embeddings."""
        ...

    @abstractmethod
    def delete(self, item_id: str) -> bool:
        """Delete by ID. Returns True if found and deleted."""
        ...

    @abstractmethod
    def count(self) -> int:
        """Return total number of stored embeddings."""
        ...


class AsyncStorageBackend(ABC):
    """Async storage interface."""

    @abstractmethod
    async def store(self, item_id: str, embedding: list[float], metadata: dict | None) -> None:
        """Store an embedding with its ID and optional metadata."""
        ...

    @abstractmethod
    async def search(self, embedding: list[float], top_k: int) -> list[SearchHit]:
        """Find top_k most similar embeddings."""
        ...

    @abstractmethod
    async def delete(self, item_id: str) -> bool:
        """Delete by ID. Returns True if found and deleted."""
        ...

    @abstractmethod
    async def count(self) -> int:
        """Return total number of stored embeddings."""
        ...
