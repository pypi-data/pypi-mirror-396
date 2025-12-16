from .deduplicator import Deduplicator, DedupResult, AsyncDeduplicator
from .providers import EmbeddingProvider
from .storage import StorageBackend, SearchHit, MemoryStorage
from .exceptions import (
    DedupKitError,
    StorageConnectionError,
    StorageError,
    EmbeddingError,
    ValidationError,
)

__all__ = [
    "Deduplicator",
    "AsyncDeduplicator",
    "DedupResult",
    "EmbeddingProvider",
    "StorageBackend",
    "SearchHit",
    "MemoryStorage",
    "DedupKitError",
    "StorageConnectionError",
    "StorageError",
    "EmbeddingError",
    "ValidationError",
]

# Optional exports
try:
    from .storage import AsyncStorageBackend, PostgresStorage
    __all__ += ["AsyncStorageBackend", "PostgresStorage"]
except ImportError:
    pass