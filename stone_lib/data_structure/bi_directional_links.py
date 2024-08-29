from __future__ import annotations
from typing import Optional, Any, Dict, AnyStr
import uuid


class BiDirection:
    def __init__(self, value: Any):
        self._prev: Optional[BiDirection] = self
        self._next: Optional[BiDirection] = self
        self._value: Any = value
        self._id = uuid.uuid4().hex

    @property
    def prev(self) -> BiDirection:
        return self._prev

    @property
    def next(self) -> BiDirection:
        return self._next

    @property
    def value(self) -> Any:
        return self._value

    @property
    def id(self) -> str:
        return self._id

    def insert_after(self, node: BiDirection):
        node._prev = self
        node._next = self._next
        self._next._prev = node
        self._next = node

    def insert_before(self, node: BiDirection):
        node._prev = self._prev
        node._next = self
        self._prev._next = node
        self._prev = node

    def remove(self):
        self._prev._next = self._next
        self._next._prev = self._prev
        self._prev = self
        self._next = self

    def search(self, value: Any) -> Optional[BiDirection]:
        node = self
        while node.value != value and node.next != self:
            node = node.next
        return node if node.value == value else None

    def __eq__(self, other: BiDirection) -> bool:
        return self.id == other.id

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f'BiDirection({self.value})'

