# import numpy as np
from typing import Any # If not already imported

# Define the sentinel object
_MISSING = object()
class HashMap:
    def __init__(self, initial_capacity: int = 4, load_factor: float = 0.75):
        self._buckets = [ [] for _ in range(initial_capacity) ]
        self._capacity = initial_capacity
        self._size = 0
        self._load_factor = load_factor

    def set(self, key, value) -> None:
        existed = False
        for idx, item in enumerate(self._buckets[self._bucket_index(key)]):
            existing_key, existing_value = item
            if existing_key == key:
                self._buckets[self._bucket_index(key)][idx] = (key, value)
                existed = True
                break
        if not existed:
            self._buckets[self._bucket_index(key)].append((key, value))
            self._size += 1
            if self._size/self._capacity >= self._load_factor:
                self._resize()


    def get(self, key, default= _MISSING) -> Any:
        for existing_key, value in self._buckets[self._bucket_index(key)]:
            if existing_key == key:
                return value
        if default:
            return default
        raise KeyError

    def delete(self, key) -> None:
        to_be_deleted = -1
        for idx, item in enumerate(self._buckets[self._bucket_index(key)]):
            existing_key, value = item
            if existing_key == key:
                to_be_deleted = idx
        if to_be_deleted != -1:
            self._buckets[self._bucket_index(key)].pop(to_be_deleted)
            self._size -= 1
        else:
            raise KeyError

    def __contains__(self, key) -> bool:
        for existing_key, value in self._buckets[self._bucket_index(key)]:
            if existing_key == key:
                return True
        return False

    def __len__(self): return self._size

    def keys(self) -> list:
        return [pair[0] for bucket in self._buckets for pair in bucket]

        # return self._buckets[:][0]

    def values(self) -> list: 
        return [pair[1] for bucket in self._buckets for pair in bucket]

    def items(self) -> list[tuple]:
        return [pair for bucket in self._buckets for pair in bucket]

    def __repr__(self) -> str:
        return f"HashMap(capacity={self._capacity}, buckets={self._buckets})"

    # Optional but recommended:
    # 10. clear(self) -> None
    # 11. __repr__(self) -> str

    def _bucket_index(self, key):
        return hash(key)%self._capacity

    def _resize(self):
        self._capacity = self._capacity * 2
        extended_buckets = [ [] for _ in range(self._capacity) ]
        for list in self._buckets:
            for idx, item in enumerate(list):
                key, value = item
                extended_buckets[self._bucket_index(key)].append((key, value))
        self._buckets = extended_buckets