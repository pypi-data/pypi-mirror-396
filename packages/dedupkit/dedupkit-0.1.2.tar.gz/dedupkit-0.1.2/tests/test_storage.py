def test_store_and_count(memory_storage):
    size = 3
    assert memory_storage.count() == 0
    for i in range(size):
        memory_storage.store(f"item-{i}", [], None)
    assert memory_storage.count() == size

def test_search_empty(memory_storage):
    assert memory_storage.search([1.0, 2.0, 3.0], 3) == []

def test_search_finds_similar(memory_storage):
    memory_storage.store(f"item-0", [0.1, 0.2, 0.3], None)
    memory_storage.store(f"item-1", [0.2, 0.3, 0.4], None)
    memory_storage.store(f"item-2", [0.1, 0.3, 0.3], None)

    first_found = memory_storage.search([1.0, 2.0, 3.0], 3)[0]
    assert first_found.id == "item-0"


def test_delete_existing(memory_storage):
    memory_storage.store(f"item-0", [0.1, 0.2, 0.3], None)
    memory_storage.store(f"item-1", [0.2, 0.3, 0.4], None)
    memory_storage.store(f"item-2", [0.1, 0.3, 0.3], None)
    assert memory_storage.count() == 3
    assert memory_storage.delete(f"item-1") is True
    assert memory_storage.count() == 2

def test_delete_nonexistent(memory_storage):
    memory_storage.store(f"item-0", [0.1, 0.2, 0.3], None)
    assert memory_storage.count() == 1
    assert memory_storage.delete(f"item-1") is False
    assert memory_storage.count() == 1
