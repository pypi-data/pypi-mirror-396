from abc import abstractmethod, ABC

class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Return the dimensionality of embeddings."""
        ...

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Embed a single text into a vector."""
        ...

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts. Override for batch optimization."""
        return [self.embed(text) for text in texts]
