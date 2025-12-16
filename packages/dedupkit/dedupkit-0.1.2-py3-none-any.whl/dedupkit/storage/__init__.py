from .base import StorageBackend, AsyncStorageBackend, SearchHit
from .memory import MemoryStorage

__all__ = ["StorageBackend", "AsyncStorageBackend", "SearchHit", "MemoryStorage"]

try:
    from .postgres import PostgresStorage
    __all__ += ["PostgresStorage"]
except ImportError:
    pass  # asyncpg not installed