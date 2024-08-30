from __future__ import annotations

import uuid
from typing import Any, AnyStr, Dict, Optional


class BiDirection:
    def __init__(self, value: Any):
        """Create a bi-directional link node.

        Args:
            value (Any): The value of the node.
        """
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
        """Insert a node after the current node.

        Args:
            node (BiDirection): The node to be inserted.

        Returns:
            None

        """
        node._prev = self
        node._next = self._next
        self._next._prev = node
        self._next = node

    def insert_before(self, node: BiDirection):
        """Insert a node before the current node.

        Args:
            node (BiDirection): The node to be inserted.

        Returns:
            None

        """
        node._prev = self._prev
        node._next = self
        self._prev._next = node
        self._prev = node

    def remove(self):
        """Remove the current node.

        Returns:
            None
        """
        self._prev._next = self._next
        self._next._prev = self._prev
        self._prev = self
        self._next = self

    def search(self, value: Any) -> Optional[BiDirection]:
        """Search a node by value.

        Args:
            value (Any): The value to be searched.

        Returns:
            Optional[BiDirection]: The node with the value.
        """
        node = self
        while node.value != value and node.next != self:
            node = node.next
        return node if node.value == value else None

    def __eq__(self, other: BiDirection) -> bool:
        """Check if two nodes are equal."""
        return self.id == other.id

    def __str__(self):
        """Return the string representation of the node."""
        return str(self.value)

    def __repr__(self):
        """Return the string representation of the node."""
        return f"BiDirection({self.value})"
