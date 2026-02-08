# tests/test_hashmap.py
import pytest

from mlsys.data_structures.hashmap import HashMap


class ConstantHashKey:
    """Forces collisions: all instances share the same hash value."""
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return 12345

    def __eq__(self, other):
        return isinstance(other, ConstantHashKey) and self.value == other.value

    def __repr__(self):
        return f"ConstantHashKey({self.value!r})"


def test_empty_map_len_contains_get_default():
    hm = HashMap(initial_capacity=4)

    assert len(hm) == 0
    assert ("x" in hm) is False

    # missing key with default should return default (even if falsy)
    assert hm.get("missing", default=0) == 0
    assert hm.get("missing", default="") == ""
    assert hm.get("missing", default=False) is False
    assert hm.get("missing", default=None) is None


def test_get_missing_raises_keyerror_when_no_default():
    hm = HashMap(initial_capacity=4)

    with pytest.raises(KeyError):
        hm.get("missing")


def test_set_and_get_basic():
    hm = HashMap(initial_capacity=4)
    hm.set("a", 1)
    hm.set("b", 2)

    assert hm.get("a") == 1
    assert hm.get("b") == 2
    assert len(hm) == 2
    assert "a" in hm
    assert "b" in hm
    assert "c" not in hm


def test_set_overwrites_existing_key_without_growing_size():
    hm = HashMap(initial_capacity=4)
    hm.set("a", 1)
    assert len(hm) == 1

    hm.set("a", 999)
    assert len(hm) == 1
    assert hm.get("a") == 999


def test_delete_existing_key():
    hm = HashMap(initial_capacity=4)
    hm.set("a", 1)
    hm.set("b", 2)

    hm.delete("a")

    assert len(hm) == 1
    assert "a" not in hm
    assert "b" in hm

    with pytest.raises(KeyError):
        hm.get("a")


def test_delete_missing_raises_keyerror():
    hm = HashMap(initial_capacity=4)

    with pytest.raises(KeyError):
        hm.delete("missing")


def test_none_key_supported():
    hm = HashMap(initial_capacity=4)
    hm.set(None, "nil")

    assert hm.get(None) == "nil"
    assert None in hm
    assert len(hm) == 1

    hm.delete(None)
    assert None not in hm
    assert len(hm) == 0


def test_collision_handling_separate_chaining_get_set_delete():
    hm = HashMap(initial_capacity=4)

    k1 = ConstantHashKey("k1")
    k2 = ConstantHashKey("k2")
    k3 = ConstantHashKey("k3")

    hm.set(k1, 10)
    hm.set(k2, 20)
    hm.set(k3, 30)

    assert len(hm) == 3
    assert hm.get(k1) == 10
    assert hm.get(k2) == 20
    assert hm.get(k3) == 30

    # overwrite inside a collision bucket
    hm.set(k2, 200)
    assert len(hm) == 3
    assert hm.get(k2) == 200

    # delete inside collision bucket
    hm.delete(k1)
    assert len(hm) == 2
    assert k1 not in hm
    assert hm.get(k2) == 200
    assert hm.get(k3) == 30


def test_keys_values_items_basic_contents():
    hm = HashMap(initial_capacity=4)
    hm.set("a", 1)
    hm.set("b", 2)
    hm.set("c", 3)

    ks = hm.keys()
    vs = hm.values()
    it = hm.items()

    # Order is not required, so compare as sets
    assert set(ks) == {"a", "b", "c"}
    assert set(vs) == {1, 2, 3}
    assert set(it) == {("a", 1), ("b", 2), ("c", 3)}


def test_keys_values_items_after_overwrite_and_delete():
    hm = HashMap(initial_capacity=4)
    hm.set("a", 1)
    hm.set("b", 2)
    hm.set("c", 3)

    hm.set("b", 200)  # overwrite
    hm.delete("a")    # delete

    assert set(hm.keys()) == {"b", "c"}
    assert set(hm.values()) == {200, 3}
    assert set(hm.items()) == {("b", 200), ("c", 3)}


def test_resize_preserves_all_items_and_behavior():
    # Use a low capacity to force resizing quickly
    hm = HashMap(initial_capacity=4, load_factor=0.75)

    # Insert enough items to trigger resize (>= 0.75 * 4 => 3 items triggers with >=)
    # We will insert more to ensure multiple buckets are used.
    items = [(f"k{i}", i) for i in range(20)]
    for k, v in items:
        hm.set(k, v)

    assert len(hm) == 20

    # All items must still be retrievable
    for k, v in items:
        assert hm.get(k) == v
        assert k in hm

    # Deletions still work after resizing
    hm.delete("k0")
    hm.delete("k10")
    assert len(hm) == 18
    assert "k0" not in hm
    assert "k10" not in hm
    with pytest.raises(KeyError):
        hm.get("k0")
    with pytest.raises(KeyError):
        hm.get("k10")


def test_resize_with_collisions_preserves_all_items():
    hm = HashMap(initial_capacity=4, load_factor=0.75)

    keys = [ConstantHashKey(i) for i in range(30)]
    for i, k in enumerate(keys):
        hm.set(k, i)

    assert len(hm) == 30
    for i, k in enumerate(keys):
        assert hm.get(k) == i

    # overwrite a few after resize
    hm.set(keys[5], 999)
    hm.set(keys[25], 888)
    assert hm.get(keys[5]) == 999
    assert hm.get(keys[25]) == 888
    assert len(hm) == 30


def test_repr_contains_capacity_and_does_not_crash():
    hm = HashMap(initial_capacity=4)
    hm.set("a", 1)

    s = repr(hm)
    assert "HashMap" in s
    assert "capacity" in s
def test_equal_keys_overwrite_even_if_different_objects():
    hm = HashMap(initial_capacity=4)
    k1 = ConstantHashKey("same")
    k2 = ConstantHashKey("same")  # equal to k1

    hm.set(k1, 1)
    hm.set(k2, 2)

    assert len(hm) == 1
    assert hm.get(k1) == 2
    assert hm.get(k2) == 2


def test_delete_middle_and_tail_in_collision_chain():
    hm = HashMap(initial_capacity=4)
    k1, k2, k3 = ConstantHashKey("k1"), ConstantHashKey("k2"), ConstantHashKey("k3")
    hm.set(k1, 10); hm.set(k2, 20); hm.set(k3, 30)

    hm.delete(k2)  # middle
    assert len(hm) == 2
    assert hm.get(k1) == 10
    assert hm.get(k3) == 30
    assert k2 not in hm

    hm.delete(k3)  # tail
    assert len(hm) == 1
    assert hm.get(k1) == 10
    assert k3 not in hm


def test_store_falsy_values_not_treated_as_missing():
    hm = HashMap(initial_capacity=4)
    hm.set("a", 0)
    hm.set("b", "")
    hm.set("c", None)
    hm.set("d", False)

    assert hm.get("a") == 0
    assert hm.get("b") == ""
    assert hm.get("c") is None
    assert hm.get("d") is False


def test_items_after_resize_and_deletes_have_no_stale_entries():
    hm = HashMap(initial_capacity=4, load_factor=0.75)
    keys = [ConstantHashKey(i) for i in range(30)]
    for i, k in enumerate(keys):
        hm.set(k, i)

    hm.delete(keys[10])
    hm.delete(keys[20])
    hm.set(keys[5], 999)

    items = dict(hm.items())
    assert len(items) == len(hm)
    assert keys[10] not in items
    assert keys[20] not in items
    assert items[keys[5]] == 999


def test_random_operations_match_dict():
    import random
    random.seed(0)

    hm = HashMap(initial_capacity=4, load_factor=0.75)
    d = {}

    keys = [ConstantHashKey(i) for i in range(50)]

    for _ in range(2000):
        k = random.choice(keys)
        op = random.choice(["set", "delete", "get"])

        if op == "set":
            v = random.randint(-1000, 1000)
            hm.set(k, v)
            d[k] = v

        elif op == "delete":
            if k in d:
                hm.delete(k)
                del d[k]
            else:
                with pytest.raises(KeyError):
                    hm.delete(k)

        else:  # get
            if k in d:
                assert hm.get(k) == d[k]
            else:
                with pytest.raises(KeyError):
                    hm.get(k)

        assert len(hm) == len(d)
