from typing import Any
from collections import OrderedDict
_MISSING = object()

class Node:
    def __init__(self, key, value, prev, next):
        self._prev = prev
        self._next = next
        self._key = key
        self._value = value
class LRUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError
        self._capacity = capacity
        self._size = 0
        # self._cache = OrderedDict() 
        head = Node(key = None, value = None, prev = None, next = None)
        self.head = head

    def get(self, key, default=_MISSING) -> Any:
        self._move_to_end(key)
        value = self._get_node(key)._value
        if value:
            return value
        # if self.__contains__(key):
        #     self._cache.move_to_end(key)
        #     value = self._cache[key]
        #     return value
        if default != _MISSING:
            return default
        raise KeyError
    

    

    def put(self, key, value) -> None:
        if self.__contains__(key):
            self._move_to_end(key)
            self.get_tail(key)._value = value
            return 
        if self._size >= self._capacity:
            self.head._next = self.head._next._next
            self.head._next._prev = self.head
            # self._cache.popitem(last = False)
        new_node = Node(key=key, value=value, prev=self.get_tail(), next= None)
        self.get_tail()._next = new_node
        self._size  = self.__len__()


    def delete(self, key) -> None:
        node = self.head._next
        while (node):
            if node._key == key:
                node._prev._next = node._next
                node._next._prev = node._prev
            node = node._next

        self._size  = self.__len__()

        if not node:
            raise KeyError

        # self._cache.pop(key)
        

    def __contains__(self, key) -> bool:
        node = self.head._next
        while node:
            if key == node._key:
                return True
            node = node._next
        return False

    def __len__(self) -> int:
        n = 0
        node = self.head._next
        while node:
            n += 1
            node = node._next
        return n

    def keys(self) -> list:
        keys = []
        node = self.head._next
        while node:
            keys.append(node._key)
            node = node._next
        return keys

    def values(self) -> list:
        values = []
        node = self.head._next
        while node:
            values.append(node._value)
            node = node._next
        return values
    
    def items(self) -> list:
        items = []
        node = self.head._next
        while node:
            items.append((node._key, node._value))
            node = node._next
        return items
    
    def get_tail(self) -> Node:
        head = self.head
        while head._next:
            head = head._next
        return head
    
    def _move_to_end(self, key):
        node = self.head._next
        while node:
            if node._key == key:
                break
            node = node._next
        node._prev._next = node._next
        node._next._prev = node._prev
        self.get_tail()._next = node
        node._next = None
    
    def _get_node(self, key) -> Node:
        node = self.head._next
        while node:
            if node._key == key:
                return node
            node = node._next
        return None

nil  = LRUCache(3)
nil.put(3, 61)
nil.put(8, 10)
nil.put(4, 6)
print(nil.items())
print(nil.get(8))
nil.put(53, 9)
nil.put(63, 7)
print(nil.keys())
# print(nil.get(3))