import pytest

from dedupkit import Deduplicator
from dedupkit.providers import LocalEmbeddingProvider
from dedupkit.storage import MemoryStorage


@pytest.fixture(scope="session")
def local_embedding_provider() -> LocalEmbeddingProvider:
    """Shared embedding provider for all tests."""
    return LocalEmbeddingProvider()

@pytest.fixture
def memory_storage() -> MemoryStorage:
    """Fresh storage for each test."""
    return MemoryStorage()

@pytest.fixture
def deduplicator(local_embedding_provider, memory_storage) -> Deduplicator:
    """Deduplicator with local provider and fresh storage."""
    return Deduplicator(local_embedding_provider, memory_storage)
