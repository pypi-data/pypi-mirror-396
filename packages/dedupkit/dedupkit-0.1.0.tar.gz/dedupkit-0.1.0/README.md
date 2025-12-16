# DedupKit

Semantic deduplication using embeddings.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

DedupKit detects duplicate or similar text using semantic embeddings. Unlike keyword matching, it understands **meaning** — so "Login button is broken" matches "Can't sign in".

## Installation
```bash
# Core with local embeddings
pip install dedupkit[local]

# With OpenAI embeddings
pip install dedupkit[openai]

# With PostgreSQL storage
pip install dedupkit[postgres]

# Everything
pip install dedupkit[all]
```

## Quick Start
```python
from dedupkit import Deduplicator
from dedupkit.providers import LocalEmbeddingProvider
from dedupkit.storage import MemoryStorage

dedup = Deduplicator(
    embedding=LocalEmbeddingProvider(),
    storage=MemoryStorage(),
    threshold=0.85
)

# Add items
dedup.add("Login button is broken", item_id="BUG-001")
dedup.add("Payment form crashes", item_id="BUG-002")

# Check for duplicates
result = dedup.check("Login button not working")
print(result.is_duplicate)           # True
print(result.matches[0].id)          # BUG-001
print(result.matches[0].similarity)  # 0.92
```

## Providers

**Local (no API key needed):**
```python
from dedupkit.providers import LocalEmbeddingProvider

provider = LocalEmbeddingProvider()
```

**OpenAI:**
```python
from dedupkit.providers import OpenAIProvider

provider = OpenAIProvider(api_key="sk-...")
```

## Storage Backends

**In-Memory (development):**
```python
from dedupkit.storage import MemoryStorage

storage = MemoryStorage()
```

**PostgreSQL + pgvector (production):**
```python
from dedupkit.storage import PostgresStorage

storage = await PostgresStorage.create(
    connection_string="postgresql://user:pass@localhost:5432/db",
    dimensions=384  # Must match embedding provider
)
```

## Async Support

For production applications, use `AsyncDeduplicator` with PostgreSQL:
```python
import asyncio
from dedupkit import AsyncDeduplicator
from dedupkit.providers import LocalEmbeddingProvider
from dedupkit.storage import PostgresStorage

async def main():
    storage = await PostgresStorage.create(
        connection_string="postgresql://user:pass@localhost:5432/db",
        dimensions=384
    )
    
    dedup = AsyncDeduplicator(
        embedding=LocalEmbeddingProvider(),
        storage=storage,
        threshold=0.85
    )
    
    await dedup.add("Login button is broken", item_id="BUG-001")
    
    result = await dedup.check("Can't sign in")
    print(result.is_duplicate)  # True
    
    await storage.close()

asyncio.run(main())
```

## API Reference

### Deduplicator / AsyncDeduplicator

| Method | Description | Returns |
|--------|-------------|---------|
| `add(text, item_id?, metadata?)` | Add item to index | `str` |
| `check(text, threshold?)` | Check for duplicates | `DedupResult` |
| `remove(item_id)` | Remove item | `bool` |
| `len()` / `count()` | Number of items | `int` |

### DedupResult
```python
DedupResult(
    is_duplicate: bool,        # True if matches found above threshold
    matches: list[SearchHit]   # Similar items, sorted by similarity
)
```

### SearchHit
```python
SearchHit(
    id: str,              # Item ID
    similarity: float,    # Similarity score (0.0 - 1.0)
    metadata: dict | None # Optional metadata
)
```

## Error Handling
```python
from dedupkit.exceptions import ValidationError, StorageError

try:
    dedup.add("")  # Empty text
except ValidationError as e:
    print(f"Invalid input: {e}")
```

## License

MIT