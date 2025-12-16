import asyncio
from dedupkit import AsyncDeduplicator
from dedupkit.providers import LocalEmbeddingProvider
from dedupkit.storage import PostgresStorage


async def main():
    # Setup
    provider = LocalEmbeddingProvider()
    storage = await PostgresStorage.create(
        connection_string="postgresql://postgres:postgres@localhost:5433/postgres",
        dimensions=provider.dimensions,
        auto_initialize=False  # Don't init yet
    )

    # Fresh start for test
    await storage.drop_table()
    await storage.initialize()

    dedup = AsyncDeduplicator(
        embedding=provider,
        storage=storage,
        threshold=0.80
    )

    # Add items
    await dedup.add("Login button is broken", item_id="BUG-001")
    await dedup.add("Payment form crashes", item_id="BUG-002")
    print(f"Count: {await dedup.count()}")

    # Check for duplicate
    result = await dedup.check("Login button not working")
    print(f"Is duplicate: {result.is_duplicate}")
    if result.matches:
        print(f"Best match: {result.matches[0].id} ({result.matches[0].similarity:.1%})")

    # Cleanup
    await storage.close()


asyncio.run(main())