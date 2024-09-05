import copy
from typing import Any, Dict, List, Tuple, Union, Optional
from bisect import bisect_left, bisect_right
from .node import OperatorNode
from .stack import StackLeaf


class ForwardBackward:
    def __init__(self):
        self._forward: List[OperatorNode] = []
        self._backward: List[OperatorNode] = []

    @property
    def forward(self) -> List[OperatorNode]:
        return self._forward

    @property
    def backward(self) -> List[OperatorNode]:
        return self._backward

    @property
    def forward_timestamp(self) -> Tuple[Optional[int], Optional[int]]:
        if len(self.forward) == 0:
            return None, None
        _element = self._get_node_in_first_order_and_max_duration(
            copy.deepcopy(self.forward)
        )
        return _element.start_time, _element.end_time

    @property
    def backward_timestamp(self) -> Tuple[Optional[int], Optional[int]]:
        if len(self.backward) == 0:
            return None, None
        _element = self._get_node_in_first_order_and_max_duration(
            copy.deepcopy(self.backward)
        )
        return _element.start_time, _element.end_time

    def _get_node_in_first_order_and_max_duration(
        self, nodes: List[OperatorNode]
    ) -> OperatorNode:
        nodes.sort(key=lambda x: (x.start_time, -x.end_time))
        return nodes[0]

    def add_op(self, op: OperatorNode):
        if "Backward" in op.name:
            self._add_op(op, "_backward")
        else:
            self._add_op(op, "_forward")

    def _add_op(self, op: OperatorNode, attr_name: str):
        _attr_value: List[OperatorNode] = getattr(self, attr_name)
        if op not in _attr_value:
            return _attr_value.append(op)


class Operators:
    def __init__(self, data: List[Dict[str, Any]]):
        self._data: Dict[int, List[OperatorNode]] = {}
        self._sequences: Dict[int, Union[ForwardBackward]] = {}
        self._data, self._sequences = self._build_up(data)

    @property
    def ops(self) -> Dict[int, List[OperatorNode]]:
        return self._data

    @property
    def sequences(self) -> Dict[int, Union[ForwardBackward]]:
        return self._sequences

    def _build_up(
        self, data: List[Dict[str, Any]]
    ) -> Tuple[Dict[int, List[OperatorNode]], Dict[int, Union[ForwardBackward]]]:
        """Build up a time-based dictionary data structure to store all the operator nodes.

        Args:
            data (List[Dict[str, Any]]): a list of operator events. only support cpu_op events.

        Returns:
            Dict[int, OperatorNode]: a dictionary contains all the operator nodes.
        """
        _ops_nodes: Dict[int, List[OperatorNode]] = {}
        _sequences: Dict[int, Union[ForwardBackward]] = {}
        for trace in data:
            if trace.get("cat", None) not in ["cpu_op"]:
                # Only specified type of events will be imported to the class
                # currently, only support cpu_op
                continue
            _node = OperatorNode(trace)
            if _node.start_time in _ops_nodes:
                if _node not in _ops_nodes[_node.start_time]:
                    _ops_nodes[_node.start_time].append(_node)
            else:
                _ops_nodes[_node.start_time] = [_node]
            # to build up the sequence of the operator nodes
            if _node.seq_number is not None:
                if _node.seq_number not in _sequences.keys():
                    _sequences[_node.seq_number] = ForwardBackward()
                _sequences[_node.seq_number].add_op(_node)

        return _ops_nodes, _sequences

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
            for item in self._data[sorted_timestamps[i]]:
                result.append(item)

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
