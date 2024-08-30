from typing import List, Optional, Tuple, Dict, Any
from stone_lib.utilis.diagram import FlameGraph
from .profiler_node import StackNode, OperatorNode, CpuInstantNode


class StackLeaf:
    def __init__(self, node: StackNode):
        assert isinstance(node, StackNode)
        self._leaf = node
        self._operators: List[OperatorNode] = []
        self._cpu_instants: List[CpuInstantNode] = []

    @property
    def leaf(self) -> StackNode:
        return self._leaf

    @property
    def ops(self) -> List[OperatorNode]:
        return self._operators

    @property
    def cpu_instants(self) -> List[CpuInstantNode]:
        return self._cpu_instants

    @property
    def is_model_layer_trace(self) -> bool:
        return any([node.is_module_layer for node in self.leaf.backward_stack()])

    @property
    def max_memory_usage_in_cpu(self) -> int:
        return max(
            [_memory_record[1] for _memory_record in self.memory_change_history()]
        )

    def flame_string(
        self, weight: Optional[int] = None, module_only: bool = False
    ) -> Optional[str]:
        """Generate a flame graph string for the stack leaf.

        Args:
            weight (int, optional): weight is used to calculate the width of the flame graph. Defaults to None.
                                    it can be memory, time, or any other metric.
            module_only (bool): if True, only module layers are included in the flame graph.

        Returns:
            str: flame graph string, the string is in the format of "trace1;trace2;trace3;...;traceN <weight>"
        """
        trace_list = []
        for node in self.leaf.backward_stack():
            if module_only:
                if node.is_module_layer:
                    trace_list.append(node.parent.function_name)
            else:
                trace_list.append(node.name)
        if len(trace_list) == 0:
            return None
        return "; ".join(reversed(trace_list)) + f" {weight if weight else 1}"

    def memory_change_history(self) -> List[Tuple[int, int]]:
        """Get the memory change history of the stack leaf.

        Returns:
            List[Tuple[int, int]]: a list of memory change history, each tuple is (timestamp, max_memory),
                                   if there is no memory change, the list will contain only one record (0, 0).
        """
        memory_history = []
        ordered_cpu_instants = sorted(self.cpu_instants, key=lambda x: x.start_time)
        max_memory = 0
        for instant in ordered_cpu_instants:
            max_memory += instant.bytes
            memory_history.append((instant.start_time, max_memory))
        if len(memory_history) == 0:
            memory_history.append((0, 0))
        return memory_history

    def add_operator(self, operator: OperatorNode):
        assert isinstance(operator, OperatorNode)
        if operator not in self._operators:
            self._operators.append(operator)

    def remove_operator(self, operator: OperatorNode):
        if operator in self._operators:
            self._operators.remove(operator)

    def add_cpu_instant(self, cpu_instant: CpuInstantNode):
        assert isinstance(cpu_instant, CpuInstantNode)
        if cpu_instant not in self._cpu_instants:
            self._cpu_instants.append(cpu_instant)

    def remove_cpu_instant(self, cpu_instant: CpuInstantNode):
        if cpu_instant in self._cpu_instants:
            self._cpu_instants.remove(cpu_instant)


class ModelCallStacks:
    def __init__(self, data: List[Dict[str, Any]]):
        self._leafs: List[StackLeaf] = []
        self._nodes_in_order: Dict[int, StackNode] = {}
        self._build_call_stack(data)

    @property
    def leafs(self) -> List[StackLeaf]:
        return self._leafs

    @property
    def model_layer_leafs(self) -> List[StackLeaf]:
        return [leaf for leaf in self.leafs if leaf.is_model_layer_trace]

    @property
    def nodes_in_order(self) -> Dict[int, StackNode]:
        return self._nodes_in_order

    def _build_call_stack(self, data: List[Dict[str, Any]]):
        _nodes_in_order: Dict[int, StackNode] = {}
        _leafs: List[StackLeaf] = []
        for record in data:
            if record["cat"] != "python_function":
                continue
            node = StackNode(record)
            _nodes_in_order[node.id] = node
            if node.parent_id is not None:
                _nodes_in_order[node.parent_id].add_child(node)

        for node in _nodes_in_order.values():
            if node.is_leaf:
                _leafs.append(StackLeaf(node))
        self._nodes_in_order = _nodes_in_order
        self._leafs = _leafs

    def get_node_by_id(self, leaf_id: int) -> Optional[StackNode]:
        if leaf_id in self.nodes_in_order.keys():
            return self.nodes_in_order[leaf_id]
        return None

    def flame_graph(self, module_only: bool = True) -> str:
        import io

        _model_leafs = sorted(
            self.model_layer_leafs, key=lambda x: x.leaf.start_time, reverse=False
        )
        flame_strings = io.StringIO()
        for leaf in _model_leafs:
            flame_strings.write(f"{leaf.flame_string(module_only=module_only)}\n")
        return FlameGraph().generate_flame_graph(flame_strings.getvalue())
