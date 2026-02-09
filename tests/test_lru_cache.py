# tests/test_lru_cache.py
import pytest

from mlsys.data_structures.lru_cache import LRUCache


# ----------------------------
# Helpers
# ----------------------------

class WeirdKey:
    """Hashable key with controlled equality semantics."""
    def __init__(self, x):
        self.x = x

    def __hash__(self):
        # Intentionally not constant; stable but not just x
        return hash(("WeirdKey", self.x))

    def __eq__(self, other):
        return isinstance(other, WeirdKey) and self.x == other.x

    def __repr__(self):
        return f"WeirdKey({self.x!r})"


def assert_mru_to_lru(cache, expected_items):
    """
    Assert cache.items() returns MRU -> LRU ordering.
    expected_items: list[tuple[key, value]]
    """
    assert cache.items() == expected_items
    assert cache.keys() == [k for k, _ in expected_items]
    assert cache.values() == [v for _, v in expected_items]


# ----------------------------
# Construction / basic API
# ----------------------------

def test_capacity_must_be_positive():
    with pytest.raises(ValueError):
        LRUCache(0)
    with pytest.raises(ValueError):
        LRUCache(-1)


def test_empty_cache_len_contains_and_get_default():
    c = LRUCache(2)

    assert len(c) == 0
    assert ("x" in c) is False

    # missing key with default should return default (even if falsy)
    assert c.get("missing", default=0) == 0
    assert c.get("missing", default="") == ""
    assert c.get("missing", default=False) is False
    assert c.get("missing", default=None) is None


def test_get_missing_raises_keyerror_when_no_default():
    c = LRUCache(2)
    with pytest.raises(KeyError):
        c.get("missing")


def test_delete_missing_raises_keyerror():
    c = LRUCache(2)
    with pytest.raises(KeyError):
        c.delete("nope")


# ----------------------------
# put/get semantics + recency
# ----------------------------

def test_put_then_get_basic_and_recency_order():
    c = LRUCache(3)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)

    # Most recent is the last put: c, then b, then a
    assert_mru_to_lru(c, [("c", 3), ("b", 2), ("a", 1)])

    # Access 'a' -> becomes MRU
    assert c.get("a") == 1
    assert_mru_to_lru(c, [("a", 1), ("c", 3), ("b", 2)])

    # Access 'c' -> becomes MRU
    assert c.get("c") == 3
    assert_mru_to_lru(c, [("c", 3), ("a", 1), ("b", 2)])


def test_put_existing_key_overwrites_value_and_moves_to_mru_without_growing():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert len(c) == 2

    # overwrite 'a'
    c.put("a", 10)
    assert len(c) == 2
    assert c.get("a") == 10  # also makes MRU (already MRU after put)

    assert_mru_to_lru(c, [("a", 10), ("b", 2)])


def test_contains_does_not_change_recency_by_default():
    """
    This test assumes your design choice: __contains__ should NOT update recency.
    If you intentionally decided the opposite, adjust or delete this test.
    """
    c = LRUCache(3)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    assert_mru_to_lru(c, [("c", 3), ("b", 2), ("a", 1)])

    assert ("a" in c) is True
    # recency unchanged
    assert_mru_to_lru(c, [("c", 3), ("b", 2), ("a", 1)])


# ----------------------------
# Eviction behavior
# ----------------------------

def test_capacity_one_always_evicts_previous_on_new_key():
    c = LRUCache(1)
    c.put("a", 1)
    assert_mru_to_lru(c, [("a", 1)])

    c.put("b", 2)  # evict a
    assert len(c) == 1
    assert ("a" in c) is False
    assert ("b" in c) is True
    assert_mru_to_lru(c, [("b", 2)])

    with pytest.raises(KeyError):
        c.get("a")
    assert c.get("a", default=None) is None


def test_put_new_key_when_full_evicts_lru():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert_mru_to_lru(c, [("b", 2), ("a", 1)])  # b is MRU, a is LRU

    c.put("c", 3)  # should evict a
    assert len(c) == 2
    assert ("a" in c) is False
    assert ("b" in c) is True
    assert ("c" in c) is True
    assert_mru_to_lru(c, [("c", 3), ("b", 2)])


def test_get_changes_lru_target_for_future_eviction():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert_mru_to_lru(c, [("b", 2), ("a", 1)])  # a is LRU

    # access a -> now b becomes LRU
    assert c.get("a") == 1
    assert_mru_to_lru(c, [("a", 1), ("b", 2)])

    # insert c -> should evict b (current LRU)
    c.put("c", 3)
    assert ("b" in c) is False
    assert_mru_to_lru(c, [("c", 3), ("a", 1)])


def test_put_existing_key_when_full_does_not_evict_anything():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert len(c) == 2

    # Overwriting existing key should not evict
    c.put("a", 100)
    assert len(c) == 2
    assert ("a" in c) is True and ("b" in c) is True
    assert_mru_to_lru(c, [("a", 100), ("b", 2)])


# ----------------------------
# delete behavior
# ----------------------------

def test_delete_removes_key_and_updates_order_and_size():
    c = LRUCache(3)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    assert_mru_to_lru(c, [("c", 3), ("b", 2), ("a", 1)])

    c.delete("b")
    assert len(c) == 2
    assert ("b" in c) is False
    assert_mru_to_lru(c, [("c", 3), ("a", 1)])

    # deleting remaining ends should also work
    c.delete("c")
    assert_mru_to_lru(c, [("a", 1)])
    c.delete("a")
    assert len(c) == 0
    assert c.items() == []
    assert c.keys() == []
    assert c.values() == []


def test_delete_then_put_reuses_capacity_correctly():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.delete("a")
    assert len(c) == 1

    c.put("c", 3)  # should not evict b, because size<capacity
    assert len(c) == 2
    assert ("b" in c) is True
    assert ("c" in c) is True
    assert_mru_to_lru(c, [("c", 3), ("b", 2)])


# ----------------------------
# keys/values/items ordering + content
# ----------------------------

def test_keys_values_items_consistent_after_mixed_ops():
    c = LRUCache(3)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    assert_mru_to_lru(c, [("c", 3), ("b", 2), ("a", 1)])

    c.get("a")       # a becomes MRU
    c.put("d", 4)    # evict LRU (should be b)
    assert ("b" in c) is False
    assert_mru_to_lru(c, [("d", 4), ("a", 1), ("c", 3)])


# ----------------------------
# Custom / tricky keys
# ----------------------------

def test_supports_none_key_and_tuple_key():
    c = LRUCache(2)
    c.put(None, "nil")
    c.put(("x", 1), "tup")
    assert c.get(None) == "nil"
    assert c.get(("x", 1)) == "tup"

    # Ordering after get(None): None becomes MRU
    assert_mru_to_lru(c, [(None, "nil"), (("x", 1), "tup")])


def test_supports_custom_objects_as_keys():
    c = LRUCache(2)
    k1a = WeirdKey(1)
    k1b = WeirdKey(1)  # equal to k1a
    k2 = WeirdKey(2)

    c.put(k1a, "one")
    c.put(k2, "two")

    # get using equal-but-not-same instance should work
    assert c.get(k1b) == "one"
    assert ("missing" in c) is False

    # After accessing key 1, it becomes MRU
    assert c.items()[0][0] == k1a  # stored key object may be original; value should match
    assert c.items()[0][1] == "one"


def test_equal_keys_overwrite_same_entry_not_duplicate():
    c = LRUCache(3)
    k1a = WeirdKey(1)
    k1b = WeirdKey(1)

    c.put(k1a, "v1")
    assert len(c) == 1

    c.put(k1b, "v2")  # should overwrite, not add new
    assert len(c) == 1
    assert c.get(k1a) == "v2"
    assert c.get(k1b) == "v2"


# ----------------------------
# clear / repr (optional features)
# ----------------------------

def test_clear_optional_if_implemented():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)

    if hasattr(c, "clear"):
        c.clear()
        assert len(c) == 0
        assert c.items() == []
        assert ("a" in c) is False
        assert ("b" in c) is False


def test_repr_optional_smoke_if_implemented():
    c = LRUCache(2)
    c.put("a", 1)

    if hasattr(c, "__repr__"):
        s = repr(c)
        assert isinstance(s, str)
        # don't require a specific format, just that it contains the class name or key
        assert ("LRU" in s) or ("a" in s)
