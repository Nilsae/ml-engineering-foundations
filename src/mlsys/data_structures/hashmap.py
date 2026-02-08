# import numpy as np
from typing import Any
_MISSING = object()
class HashMap:
    def __init__(self, initial_capacity: int = 8, load_factor: float = 0.75):
        self._buckets = [ [] for _ in range(initial_capacity) ]
        self._capacity = initial_capacity
        self._size = 0
        self._load_factor = load_factor

    def set(self, key, value) -> None:
        bucket_idx = self._bucket_index(key)
        for idx, item in enumerate(self._buckets[bucket_idx]):
            existing_key, existing_value = item
            if existing_key == key:
                self._buckets[bucket_idx][idx] = (key, value)
                return
        self._buckets[bucket_idx].append((key, value))
        self._size += 1
        if self._size/self._capacity > self._load_factor:
            self._resize()


    def get(self, key, default= _MISSING) -> Any:
        bucket_idx = self._bucket_index(key)
        for existing_key, value in self._buckets[bucket_idx]:
            if existing_key == key:
                return value
        if default == _MISSING:
            raise KeyError
        return default

    def delete(self, key) -> None:
        bucket_idx = self._bucket_index(key)
        deleted = False
        for idx, item in enumerate(self._buckets[bucket_idx]):
            existing_key, value = item
            if existing_key == key:
                self._buckets[bucket_idx].pop(idx)
                self._size -= 1
                deleted = True
                break
        if not deleted:
            raise KeyError

    def __contains__(self, key) -> bool:
        bucket_idx = self._bucket_index(key)
        for existing_key, value in self._buckets[bucket_idx]:
            if existing_key == key:
                return True
        return False

    def __len__(self): return self._size

    def keys(self) -> list:
        return [pair[0] for bucket in self._buckets for pair in bucket]

    def values(self) -> list: 
        return [pair[1] for bucket in self._buckets for pair in bucket]

    def items(self) -> list[tuple]:
        return [pair for bucket in self._buckets for pair in bucket]

    def __repr__(self) -> str:
        return f"HashMap(capacity={self._capacity}, buckets={self._buckets})"

    # clear(self) -> None

    def _bucket_index(self, key):
        return hash(key)%self._capacity

    def _resize(self):
        self._capacity = self._capacity * 2
        extended_buckets = [ [] for _ in range(self._capacity) ]
        for lst in self._buckets:
            for idx, item in enumerate(lst):
                key, value = item
                extended_buckets[self._bucket_index(key)].append((key, value))
        self._buckets = extended_buckets