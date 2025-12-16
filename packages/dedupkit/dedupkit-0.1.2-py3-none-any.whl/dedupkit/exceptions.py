class DedupKitError(Exception):
    """Base exception for DedupKit."""
    pass


class StorageConnectionError(DedupKitError):
    """Failed to connect to storage backend."""
    pass


class StorageError(DedupKitError):
    """Storage operation failed."""
    pass


class EmbeddingError(DedupKitError):
    """Embedding generation failed."""
    pass


class ValidationError(DedupKitError):
    """Invalid input data."""
    pass