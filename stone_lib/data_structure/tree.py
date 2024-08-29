from __future__ import annotations
from typing import Optional, Any, Dict, AnyStr
import uuid


class TreeNode:
    def __init__(self, value: Any):
        """ Initialize a TreeNode object.

        Args:
            value (Any): The value of the node.
        """
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
        """ Add a child node to the current node.

        Args:
            child (TreeNode): The child node to be added.

        Returns:
            None
        """
        if child not in self.children:
            self._children[child.id] = child

    def remove_child(self, child: TreeNode):
        """ Remove a child node from the current node.

        Args:
            child (TreeNode): The child node to be removed.

        Returns:
            None

        """
        if child in self._children:
            self._children.pop(child.id)
            child.set_parent(None)

    def set_parent(self, parent: Optional[TreeNode]):
        """ Set the parent node of the current node.

        Args:
            parent (Optional[TreeNode]): The parent node to be set.

        Returns:
            None
        """
        if parent is not None:
            if isinstance(self.parent, TreeNode):
                self.parent.remove_child(self)
            parent.add_child(self)
        self._parent = parent

    def search(self, value: Any) -> Optional[TreeNode]:
        """ Search a node with the given value.

        Args:
            value (Any): The value to be searched.

        Returns:
            Optional[TreeNode]: The node with the given value.

        """
        if self.value == value:
            return self
        for child in self.children.values():
            node = child.search(value)
            if node is not None:
                return node
        return None
