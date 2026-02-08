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
        bucket_idx = hash(key)%self._capacity
        for idx, item in enumerate(self._buckets[bucket_idx]):
            existing_key, existing_value = item
            if existing_key == key:
                self._buckets[bucket_idx][idx] = (key, value)
                existed = True
        if not existed:
            self._buckets[bucket_idx].append((key, value))
            self._size += 1
            if self._size/self._capacity >= self._load_factor:
                self._buckets.extend([] for _ in range(self._capacity))
                self._capacity = self._capacity * 2

    def get(self, key, default= _MISSING) -> Any:
        for existing_key, value in self._buckets[hash(key)%self._capacity]:
            if existing_key == key:
                return value
        return default

    def delete(self, key) -> None:
        deleted = False
        for existing_key, value in self._buckets[hash(key)%self._capacity]:
            if existing_key == key:
                self._buckets[hash(key)%self._capacity].remove((existing_key, value))
                deleted = True
        if deleted:
            self._size -= 1
        else:
            raise KeyError

    def __contains__(self, key) -> bool:
        for existing_key, value in self._buckets[hash(key)%self._capacity]:
            if existing_key == key:
                return True
        return False

    # __len__(self) -> int

    def keys(self) -> list:
        return [tuple[0] for bucket in self._buckets for tuple in bucket]

        # return self._buckets[:][0]

    def values(self) -> list: 
        return [tuple[1] for bucket in self._buckets for tuple in bucket]

    def items(self) -> list[tuple]:
        return [tuple for bucket in self._buckets for tuple in bucket]

    def __repr__(self) -> str:
        return f"HashMap(capacity={self._capacity}, buckets={self._buckets})"

    # Optional but recommended:
    # 10. clear(self) -> None
    # 11. __repr__(self) -> str

nil = HashMap(initial_capacity = 8)
print(nil.keys())
nil.set(key=10, value=11)
nil.set(key=67, value=15)
print(nil.keys())
print(nil.items())
print(nil.get(67))
nil.delete(67)
nil.set(key=10, value=100)
nil.set(key=12, value=100)
nil.set(key=103, value=100)
nil.set(key=140, value=100)
nil.set(key=0, value=100)
nil.set(key=106, value=100)
nil.set(key=180, value=100)
print(nil.items())
