import asyncpg
import json
from pgvector.asyncpg import register_vector
from ..exceptions import StorageConnectionError, StorageError
from ..validation import validate_non_empty_string, validate_dimensions, validate_embedding_dimensions, \
    validate_positive_integer

from .base import AsyncStorageBackend, SearchHit

class PostgresStorage(AsyncStorageBackend):

    def __init__(self, pool: asyncpg.Pool, dimensions: int):
        """Private constructor. Use create() instead."""
        self.pool = pool
        self.dimensions = dimensions

    @staticmethod
    async def setup_extension(connection_string: str):
        try:
            temp_pool = await asyncpg.create_pool(connection_string, min_size=1, max_size=1)
            async with temp_pool.acquire() as conn:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await temp_pool.close()
        except Exception as e:
            raise StorageConnectionError(f"Failed to set up vector extension: {e}") from e


    @classmethod
    async def create(cls, connection_string: str, dimensions: int, auto_initialize: bool = True) -> "PostgresStorage":
        """
        Factory method to create PostgresStorage.

        Args:
            connection_string: PostgreSQL connection string
            dimensions: Embedding vector dimensions
            auto_initialize: If True, creates tables automatically
        """
        validate_non_empty_string(connection_string, "connection_string")
        validate_dimensions(dimensions)

        await PostgresStorage.setup_extension(connection_string)

        try:
            async def init_connection(conn):
                await register_vector(conn)

            pool: asyncpg.Pool = await asyncpg.create_pool(connection_string, init=init_connection)
            instance = cls(pool, dimensions)

            if auto_initialize:
                await instance.initialize()

            return instance
        except Exception as e:
            raise StorageConnectionError(f"Failed to connect to PostgreSQL: {e}") from e


    async def close(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()

    async def create_table_embeddings(self, conn):
        # Create table with vector column
        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS embeddings (
                item_id VARCHAR(255) PRIMARY KEY,
                embedding vector({self.dimensions}),
                metadata JSONB
            )
        """)


    async def initialize(self):
        """Create vector extension and embeddings table."""
        try:
            async with self.pool.acquire() as conn:
                await self.create_table_embeddings(conn)
        except Exception as e:
            raise StorageError(f"Failed to initialize storage: {e}") from e


    async def drop_table(self):
        """Drop the embeddings table. Useful for testing."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("DROP TABLE IF EXISTS embeddings")
        except Exception as e:
            raise StorageError(f"Failed to drop embeddings table: {e}") from e


    async def store(self, item_id: str, embedding: list[float], metadata: dict | None) -> None:
        validate_non_empty_string(item_id, "item_id")
        validate_embedding_dimensions(embedding, self.dimensions)

        try:
            metadata_json = json.dumps(metadata) if metadata else None

            async with self.pool.acquire() as conn:
                await conn.execute("""
                                   INSERT INTO embeddings (item_id, embedding, metadata)
                                   VALUES ($1, $2, $3) ON CONFLICT (item_id) DO
                                   UPDATE SET
                                       embedding = EXCLUDED.embedding,
                                       metadata = EXCLUDED.metadata
                                   """, item_id, embedding, metadata_json)
        except Exception as e:
            raise StorageError(f"Failed to store embedding: {e}") from e


    async def look_up(self, embedding: list[float], top_k: int) -> list[asyncpg.Record]:
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
                                SELECT item_id, 1 - (embedding <=> $1) AS similarity, metadata
                                FROM embeddings
                                ORDER BY embedding <=> $1
                                    LIMIT $2
                                """, embedding, top_k)

    @staticmethod
    def row_to_search_hit(row: asyncpg.Record) -> SearchHit:
        return SearchHit(
                id=row["item_id"],
                similarity=float(row["similarity"]),
                metadata=json.loads(row["metadata"]) if row["metadata"] else None
            )

    async def search(self, embedding: list[float], top_k: int) -> list[SearchHit]:
        """Find most similar embeddings."""
        validate_embedding_dimensions(embedding, self.dimensions)
        validate_positive_integer(top_k, "top_k")

        try:
            rows = await self.look_up(embedding, top_k)
            return [
                self.row_to_search_hit(row)
                for row in rows
            ]
        except Exception as e:
            raise StorageError(f"Failed to search embeddings: {e}") from e


    async def delete(self, item_id: str) -> bool:
        """Delete by ID. Returns True if deleted."""
        validate_non_empty_string(item_id, "item_id")

        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute("""
                                            DELETE
                                            FROM embeddings
                                            WHERE item_id = $1
                                            """, item_id)
        except Exception as e:
            raise StorageError(f"Failed to delete embedding: {e}") from e


        # result is "DELETE 1" or "DELETE 0"
        return result == "DELETE 1"

    async def count(self) -> int:
        """Return total number of embeddings."""
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetchval("SELECT COUNT(*) FROM embeddings")
        except Exception as e:
            raise StorageError(f"Failed to count embeddings: {e}") from e
