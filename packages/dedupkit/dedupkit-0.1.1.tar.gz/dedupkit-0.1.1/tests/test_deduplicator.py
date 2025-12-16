import uuid

def is_uuid(val: str) -> bool:
    try:
        uuid.UUID(val)
        return True
    except ValueError:
        return False

def test_add_returns_id(deduplicator):
    returned_id = deduplicator.add("some text", item_id="my-id")
    assert returned_id == "my-id"

def test_add_generates_id(deduplicator):
    returned_id = deduplicator.add("some text")
    assert is_uuid(returned_id) is True

def test_len(deduplicator):
    size = 3
    assert len(deduplicator) == 0
    for i in range(size):
        deduplicator.add(f"text-{i}", f"id-{i}")
    assert len(deduplicator) == size

def test_check_finds_duplicate(deduplicator):
    deduplicator.add("Login button is disabled", "id-1")
    result = deduplicator.check("Login button is disabled")
    assert result.is_duplicate is True
    assert result.matches[0].id == f"id-1"

def test_check_no_duplicate(deduplicator):
    deduplicator.add("some text", "id-1")
    assert deduplicator.check("1+2*4<20").is_duplicate is False

def test_check_respects_threshold(deduplicator):
    deduplicator.add("Login button is disabled", "id-1")
    deduplicator.add("Window has closed unexpectedly", "id-2")
    result = deduplicator.check(text="Login button issue", threshold=0.70)
    assert len(result.matches) == 1
    assert result.matches[0].id == "id-1"
    result = deduplicator.check(text="Login button issue", threshold=0.20)
    assert len(result.matches) == 2

def test_remove(deduplicator):
    deduplicator.add("Login button is disabled", "id-1")
    assert len(deduplicator) == 1
    assert deduplicator.remove(item_id="id-1") is True
    assert len(deduplicator) == 0