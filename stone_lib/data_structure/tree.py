from __future__ import annotations
from typing import Optional, Any, Dict, AnyStr
import uuid


class TreeNode:
    def __init__(self, value: Any):
        self._parent: Optional[TreeNode] = None
        self._children: Dict[AnyStr, TreeNode] = {}
        self._value: Any = value
        self._id = uuid.uuid4().hex

    @property
    def parent(self) -> Optional[TreeNode]:
        return self._parent

    @property
    def children(self) -> Dict[AnyStr, TreeNode]:
        return self._children

    @property
    def is_leaf(self) -> bool:
        return len(self.children) == 0

    @property
    def value(self) -> Any:
        return self._value

    @property
    def id(self) -> str:
        return self._id

    def add_child(self, child: TreeNode):
        if child not in self.children:
            self._children[child.id] = child
            child.set_parent(self)

    def remove_child(self, child: TreeNode):
        if child in self._children:
            self._children.pop(child.id)
            child.set_parent(None)

    def set_parent(self, parent: Optional[TreeNode]):
        if parent is not None:
            if isinstance(self.parent, TreeNode):
                self.parent.remove_child(self)
            parent.add_child(self)
        self._parent = parent

    def search(self, value: Any) -> Optional[TreeNode]:
        if self.value == value:
            return self
        for child in self.children.values():
            node = child.search(value)
            if node is not None:
                return node
        return None
