from typing import Any
from collections import OrderedDict
_MISSING = object()
class LRUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError
        self._capacity = capacity
        self._size = 0
        self._cache = OrderedDict() 

    def get(self, key, default=_MISSING) -> Any:
        if self.__contains__(key):
            self._cache.move_to_end(key)
            value = self._cache[key]
            return value
        if default != _MISSING:
            return default
        raise KeyError
    

    

    def put(self, key, value) -> None:
        if self.__contains__(key):
            self._cache.move_to_end(key)
            self._cache[key] = value
            return 
        if self._size >= self._capacity:
            self._cache.popitem(last = False)
        self._cache[key] = value
        self._size  = self.__len__()


    def delete(self, key) -> None:
        self._cache.pop(key)
        self._size  = self.__len__()

    def __contains__(self, key) -> bool:
        if key in self._cache:
            return True
        return False

    def __len__(self) -> int:
        return len(self._cache)

    def keys(self) -> list:
        return list(self._cache.keys())

    def values(self) -> list:
        return list(self._cache.values())
    
    def items(self) -> list:
        return list(self._cache.items())

nil  = LRUCache(3)
nil.put(3, 61)
nil.put(8, 10)
nil.put(4, 6)
nil.get(8)
nil.put(53, 9)
nil.put(63, 7)
print(nil.keys())
# print(nil.get(3))