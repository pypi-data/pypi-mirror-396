import pytest

from dedupkit import ValidationError
from dedupkit.storage import PostgresStorage

pytestmark = pytest.mark.asyncio

TEST_CONNECTION = "postgresql://postgres:postgres@localhost:5433/postgres"
TEST_DIMENSIONS = 3  # Small for testing


@pytest.fixture
async def postgres_storage():
    """Fresh PostgreSQL storage for each test."""
    storage = await PostgresStorage.create(
        connection_string=TEST_CONNECTION,
        dimensions=TEST_DIMENSIONS,
        auto_initialize=False
    )
    await storage.drop_table()
    await storage.initialize()

    yield storage

    await storage.close()


async def test_create_and_count(postgres_storage):
    assert await postgres_storage.count() == 0
    await postgres_storage.store("id-1", [1.0, 0.0, 0.0], None)
    assert await postgres_storage.count() == 1


async def test_store_and_search(postgres_storage):
    await postgres_storage.store("id-1", [1.0, 0.0, 0.0], None)
    found = await postgres_storage.search([1.0, 0.0, 0.0], top_k=1)
    assert len(found) == 1
    assert found[0].id == "id-1"


async def test_delete(postgres_storage):
    await postgres_storage.store("id-1", [1.0, 0.0, 0.0], None)
    assert await postgres_storage.count() == 1
    deleted = await postgres_storage.delete("id-1")
    assert deleted is True
    assert await postgres_storage.count() == 0


async def test_store_empty_id_raises(postgres_storage):
    with pytest.raises(ValidationError):
        await postgres_storage.store("", [1.0, 0.0, 0.0], None)


async def test_store_wrong_dimensions_raises(postgres_storage):
    with pytest.raises(ValidationError):
        await postgres_storage.store("id-1", [], None)


async def test_search_wrong_dimensions_raises(postgres_storage):
    with pytest.raises(ValidationError):
        await postgres_storage.search([], top_k=1)


async def test_search_invalid_top_k_raises(postgres_storage):
    with pytest.raises(ValidationError):
        await postgres_storage.search([1.0, 0.0, 0.0], top_k=0)


async def test_delete_empty_id_raises(postgres_storage):
    with pytest.raises(ValidationError):
        await postgres_storage.delete("")


async def test_create_empty_connection_raises():
    with pytest.raises(ValidationError):
        await PostgresStorage.create(connection_string="", dimensions=3)


async def test_create_invalid_dimensions_raises():
    with pytest.raises(ValidationError):
        await PostgresStorage.create(
            connection_string="postgresql://postgres:postgres@localhost:5433/postgres",
            dimensions=0
        )


async def test_search_returns_most_similar_first(postgres_storage):
    await postgres_storage.store("right", [1.0, 0.0, 0.0], None)
    await postgres_storage.store("up", [0.0, 1.0, 0.0], None)
    await postgres_storage.store("forward", [0.0, 0.0, 1.0], None)

    # Search for something close to "right"
    results = await postgres_storage.search([0.9, 0.1, 0.0], top_k=3)

    assert results[0].id == "right"
    assert results[0].similarity > 0.9

