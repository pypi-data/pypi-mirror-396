from .base import EmbeddingProvider
from .embedding import EmbeddingModel

__all__ = ["EmbeddingProvider", "EmbeddingModel"]

try:
    from .openai import OpenAIProvider, EmbeddingModels
    __all__ += ["OpenAIProvider", "EmbeddingModels"]
except ImportError:
    pass  # openai not installed

try:
    from .local import LocalEmbeddingProvider, SentenceTransformerEmbeddingModels
    __all__ += ["LocalEmbeddingProvider", "SentenceTransformerEmbeddingModels"]
except ImportError:
    pass  # sentence-transformers not installed