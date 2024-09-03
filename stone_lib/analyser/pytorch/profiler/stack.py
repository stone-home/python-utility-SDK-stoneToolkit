from typing import Any, Dict, List, Optional, Tuple
from hashlib import sha256
from stone_lib.utilis.diagram import FlameGraph
from stone_lib.analyser.pytorch.profiler.node import (
    CpuInstantNode,
    OperatorNode,
    StackNode,
)


class StackLeaf:
    def __init__(self, node: StackNode):
        assert isinstance(node, StackNode)
        self._leaf = node
        self._hierarchy = None

    @property
    def leaf(self) -> StackNode:
        return self._leaf

    @property
    def is_model_layer_trace(self) -> bool:
        self._hierarchy = self._get_model_layer_trace()
        return len(self._hierarchy) > 0

    @property
    def module_name(self) -> str:
        """
        Generate a module name for the stack leaf.
        The module name will be the function name of the leaf if the leaf is not a module layer.
        The last module lauer name will be extracted from the backward stack if the leaf is a module layer.

        Returns:

        """
        _hierarchy = self._get_model_layer_trace()
        if len(_hierarchy) == 0:
            _hierarchy = [self.leaf]
        return "->".join([node.function_name for node in _hierarchy])

    @property
    def leaf_id(self) -> str:
        return sha256(self.flame_string().encode()).hexdigest()

    def _get_model_layer_trace(self) -> List[StackNode]:
        module_hierarchy = self._hierarchy
        if module_hierarchy is None:
            module_hierarchy = [
                node.parent
                for node in self.leaf.backward_stack()
                if node.is_module_layer
            ]
            module_hierarchy.reverse()
        return module_hierarchy

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
        if module_only:
            trace_list = self._get_model_layer_trace()
        else:
            for node in self.leaf.backward_stack():
                trace_list.append(node)
            trace_list = list(reversed(trace_list))
        if len(trace_list) == 0:
            return None
        return (
            "; ".join([node.name for node in trace_list])
            + f" {weight if weight else 1}"
        )

    def to_json(self) -> Dict[str, Any]:
        """reformat the stack leaf to a json format.
        The field `id` is used to identify if the stack leaf is the same as another stack leaf
        based on the flame graph string.

        Returns:
            Dict[str, Any]: a dictionary contains the information of the stack leaf.

        """
        return {
            "layer": self.module_name,
            "start": self.leaf.start_time,
            "end": self.leaf.end_time,
            "duration": self.leaf.duration,
            "id": self.leaf_id,
        }


# class ModelCallStacks:
#     def __init__(self, data: List[Dict[str, Any]]):
#         self._leafs: List[StackLeaf] = []
#         self._nodes_in_order: Dict[int, StackNode] = {}
#         self._build_up(data)
#
#     @property
#     def leafs(self) -> List[StackLeaf]:
#         return self._leafs
#
#     @property
#     def model_layer_leafs(self) -> List[StackLeaf]:
#         return [leaf for leaf in self.leafs if leaf.is_model_layer_trace]
#
#     @property
#     def nodes_in_order(self) -> Dict[int, StackNode]:
#         return self._nodes_in_order
#
#     def _build_up(self, data: List[Dict[str, Any]]):
#         _nodes_in_order: Dict[int, StackNode] = {}
#         _leafs: List[StackLeaf] = []
#         for record in data:
#             if record["cat"] != "python_function":
#                 continue
#             node = StackNode(record)
#             _nodes_in_order[node.id] = node
#             if node.parent_id is not None:
#                 _nodes_in_order[node.parent_id].add_child(node)
#
#         for node in _nodes_in_order.values():
#             if node.is_leaf:
#                 _leafs.append(StackLeaf(node))
#         self._nodes_in_order = _nodes_in_order
#         self._leafs = _leafs
#
#     def get_node_by_id(self, leaf_id: int) -> Optional[StackNode]:
#         if leaf_id in self.nodes_in_order.keys():
#             return self.nodes_in_order[leaf_id]
#         return None
#
#     def flame_graph(self, module_only: bool = True) -> str:
#         import io
#
#         _model_leafs = sorted(
#             self.model_layer_leafs, key=lambda x: x.leaf.start_time, reverse=False
#         )
#         flame_strings = io.StringIO()
#         for leaf in _model_leafs:
#             flame_strings.write(f"{leaf.flame_string(module_only=module_only)}\n")
#         return FlameGraph().generate_flame_graph(flame_strings.getvalue())
#
#     def to_json(self) -> List[Dict[str, Any]]:
#         return sorted(
#             [leaf.to_json() for leaf in self.model_layer_leafs],
#             key=lambda x: x["start"],
#         )
