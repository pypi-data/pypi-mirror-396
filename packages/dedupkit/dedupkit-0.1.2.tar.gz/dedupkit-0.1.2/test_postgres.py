import asyncio
from dedupkit.storage import PostgresStorage


async def main():
    # Connect
    storage = await PostgresStorage.create(
        connection_string="postgresql://postgres:postgres@localhost:5433/postgres",
        dimensions=3  # Small for testing
    )

    print(f"Connected! Count: {await storage.count()}")

    # Store
    await storage.store("item-1", [1.0, 0.0, 0.0], {"name": "first"})
    await storage.store("item-2", [0.0, 1.0, 0.0], {"name": "second"})
    await storage.store("item-3", [0.0, 0.0, 1.0], {"name": "third"})

    print(f"After insert: {await storage.count()}")

    # Search
    results = await storage.search([0.9, 0.1, 0.0], top_k=2)
    print(f"Search results:")
    for hit in results:
        print(f"  {hit.id}: {hit.similarity:.2%} - {hit.metadata}")

    # Delete
    deleted = await storage.delete("item-2")
    print(f"Deleted item-2: {deleted}")
    print(f"Final count: {await storage.count()}")

    # Cleanup
    await storage.close()


asyncio.run(main())