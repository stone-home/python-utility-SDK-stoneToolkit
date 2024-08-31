from platform import machine
from typing import Any, Dict, List
from bisect import bisect_left, bisect_right
from .node import OperatorNode
from .stack import StackLeaf


class Operators:
    def __init__(self, data: List[Dict[str, Any]]):
        self._data: Dict[int, OperatorNode] = self._build_up(data)

    @property
    def ops(self) -> Dict[int, OperatorNode]:
        return self._data

    def _build_up(self, data: List[Dict[str, Any]]):
        """Build up a time-based dictionary data structure to store all the operator nodes.
        todo: a large scale of data may occurs duplicated timestamp issue. The nested structure should be considered.
                such as Dict[int, List[OperatorNode]].

        Args:
            data (List[Dict[str, Any]]): a list of operator events. only support cpu_op events.

        Returns:
            Dict[int, OperatorNode]: a dictionary contains all the operator nodes.
        """
        _ops_nodes: Dict[int, OperatorNode] = {}
        for trace in data:
            if trace.get("cat", None) not in ["cpu_op"]:
                # Only specified type of events will be imported to the class
                # currently, only support cpu_op
                continue
            _node = OperatorNode(trace)
            if _node.start_time in _ops_nodes.keys():
                # To avoid the duplicated timestamp issue
                # the nested structure should be considered.
                # such as Dict[int, List[OperatorNode]].
                _duplicate_node = _ops_nodes[_node.start_time]
                raise ValueError(
                    f"Duplicated Events"
                    f"Event 1: start time: {_node.start_time}, OP name: {_node.name}, Event index: {_node.value['args']['Ev Idx']},"
                    f"Event 2: start time: {_duplicate_node.start_time}, OP name: {_duplicate_node.name}, Event index: {_duplicate_node.value['args']['Ev Idx']}"
                )
            _ops_nodes[_node.start_time] = _node
        return _ops_nodes

    def search_ops_by_stackleaf(self, leaf: StackLeaf):
        """The function is built upon the binary search algorithm to find all the operator nodes within a specified stack leaf.

        Args:
            leaf (StackLeaf): the stack leaf.

        Returns:
            List[OperatorNode]: a list of operator nodes within the specified stack leaf.
        """
        ops = self.search_ops_in_time_range(leaf.leaf.start_time, leaf.leaf.end_time)
        for op in ops:
            leaf.add_operator(op)

    def search_ops_in_time_range(self, start: int, end: int) -> List[OperatorNode]:
        """The function is built upon the binary search algorithm to find all the operator nodes within a specified time range.

        Args:
            start (int): the start time of the time range.
            end (int): the end time of the time range.

        Returns:
            List[OperatorNode]: a list of operator nodes within the specified time range.
        """
        sorted_timestamps = sorted(self.ops.keys())

        # To find the start and end positions of the time using binary search
        start_idx = bisect_left(sorted_timestamps, start)
        end_idx = bisect_right(sorted_timestamps, end)

        # To collect all values within a specified time range
        result = []
        for i in range(start_idx, end_idx):
            result.append(self._data[sorted_timestamps[i]])

        return self._stack_op_up(result)

    def _stack_op_up(self, op_list: List[OperatorNode]) -> List[OperatorNode]:
        """Stack up the operator nodes based on timestampe

        Args:
            op_list (List[OperatorNode]): a list of operator nodes.

        See Also:
            The algorithm leverage the power of sorting and filtering to stack up the operator nodes.
            the key operation .sort(start_time, -end_time) is used to sort the operator and ensure
            the operator which has the smallest interval will be list in the last position of the matched_result.

        Returns:
            List[OperatorNode]: a list of root operator nodes.
        """
        root_stacks: List[OperatorNode] = []
        for op in op_list:
            matched_result = list(
                filter(
                    lambda x: x.start_time <= op.start_time
                    and x.end_time >= op.end_time,
                    op_list,
                )
            )
            matched_result.remove(op)
            if len(matched_result) == 0:
                root_stacks.append(op)
            else:
                matched_result.sort(key=lambda x: (x.start_time, -x.end_time))
                matched_result[-1].add_child(op)
        return root_stacks
