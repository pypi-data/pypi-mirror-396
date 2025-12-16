from enum import Enum
from sentence_transformers import SentenceTransformer
from .base import EmbeddingProvider
from .embedding import EmbeddingModel
from ..exceptions import EmbeddingError
from ..validation import validate_non_empty_string, validate_non_empty_list_of_strings


class SentenceTransformerEmbeddingModels(Enum):
    MINILM_L6_V2 = EmbeddingModel("all-MiniLM-L6-v2", 384)
    MPNET_BASE_V2 = EmbeddingModel("all-mpnet-base-v2", 768)
    MINILM_L12_V2 = EmbeddingModel("all-MiniLM-L12-v2", 384)


class LocalEmbeddingProvider(EmbeddingProvider):

    def __init__(self, model: EmbeddingModel = SentenceTransformerEmbeddingModels.MINILM_L6_V2.value):
        self.model = model
        self.transformer = SentenceTransformer(model.name)

    @property
    def dimensions(self) -> int:
        return self.model.dimensions

    def embed(self, text: str) -> list[float]:
        validate_non_empty_string(text, "text")

        try:
            embedded = self.transformer.encode(text)
            return embedded.tolist()
        except Exception as e:
            raise EmbeddingError(f"Failed to generate embedding: {e}") from e


    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        validate_non_empty_list_of_strings(texts, "texts")

        try:
            embedded_list = self.transformer.encode(texts)
            return [embedded.tolist() for embedded in embedded_list]
        except Exception as e:
            raise EmbeddingError(f"Failed to generate batch embeddings: {e}") from e
