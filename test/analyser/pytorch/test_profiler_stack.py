import copy
import xml.etree.ElementTree as ET
from unittest.mock import patch

import pytest

from stone_lib.analyser.pytorch.profiler.stack import (
    StackLeaf,
    StackNode,
)


class TestStackLeaf:
    def test_basic_properties(self, profiler_data__python_function):
        stack_node = StackNode(profiler_data__python_function)
        stack_leaf = StackLeaf(stack_node)
        assert stack_leaf.leaf == stack_node
        assert stack_leaf.is_model_layer_trace == False
        assert stack_leaf.module_name == "fspath>"

    def test_flame_string(self, profiler_data__python_function):
        profiler_data__python_function["name"] = "test_profiler_analyser.py:10"
        stack_node = StackNode(profiler_data__python_function)
        stack_leaf = StackLeaf(stack_node)
        assert stack_leaf.flame_string() == "test_profiler_analyser.py:10 1"

    def test_flame_string_with_weight(self, profiler_data__python_function):
        profiler_data__python_function["name"] = "test_profiler_analyser.py:10"
        stack_node = StackNode(profiler_data__python_function)
        stack_leaf = StackLeaf(stack_node)
        assert stack_leaf.flame_string(weight=2) == "test_profiler_analyser.py:10 2"

    @pytest.fixture(scope="function")
    def five_node_stack(self):
        root = None
        for i in range(5):
            profiler_data__python_function = {
                "name": f"test_profiler_analyser.py:{i}",
                "cat": "python_function",
                "ph": "X",
                "ts": i,
                "dur": 1,
                "tid": 1,
                "pid": 1,
                "args": {"Python id": i, "Parent python id": i - 1 if i > 0 else None},
            }
            stack_node = StackNode(profiler_data__python_function)
            if i == 0:
                root = stack_node
            else:
                root.add_child(stack_node)
                root = stack_node
        return root

    def test_long_flame_string(self, five_node_stack):
        stack_leaf = StackLeaf(five_node_stack)
        assert (
            stack_leaf.flame_string()
            == "test_profiler_analyser.py:0; test_profiler_analyser.py:1; test_profiler_analyser.py:2; test_profiler_analyser.py:3; test_profiler_analyser.py:4 1"
        )

    def test_long_flame_string_module_only(self, five_node_stack):
        stack_leaf = StackLeaf(five_node_stack)
        assert stack_leaf.flame_string(module_only=True) == None

    def test_long_flame_string_module_only_1(self, five_node_stack):
        five_node_stack.parent.parent.value["name"] = (
            "torch.nn.functional.py: _call_impl"
        )
        five_node_stack.parent.parent.parent.value["name"] = (
            "torch.nn.modules.module.py: Conv2d"
        )
        stack_leaf = StackLeaf(five_node_stack)
        assert (
            stack_leaf.flame_string(module_only=True)
            == "torch.nn.modules.module.py: Conv2d 1"
        )

    def test_is_model_layer_trace__true(self, five_node_stack):
        five_node_stack.parent.parent.value["name"] = (
            "torch.nn.functional.py: _call_impl"
        )
        five_node_stack.parent.parent.parent.value["name"] = (
            "torch.nn.modules.module.py: Conv2d"
        )
        stack_leaf = StackLeaf(five_node_stack)
        assert stack_leaf.is_model_layer_trace == True

    def test_module_name(self, five_node_stack):
        five_node_stack.parent.value["name"] = "torch.nn.functional.py: _call_impl"
        five_node_stack.parent.parent.value["name"] = (
            "torch.nn.modules.module.py: Conv2d_0"
        )
        stack_leaf = StackLeaf(five_node_stack)
        assert stack_leaf.module_name == "Conv2d_0"

    def test_module_name_1(self, five_node_stack):
        five_node_stack.parent.value["name"] = "torch.nn.functional.py: _call_impl"
        five_node_stack.parent.parent.value["name"] = (
            "torch.nn.modules.module.py: Conv2d_0"
        )
        five_node_stack.parent.parent.parent.value["name"] = (
            "torch.nn.functional.py: _call_impl"
        )
        five_node_stack.parent.parent.parent.parent.value["name"] = (
            "torch.nn.modules.module.py: Conv2d_1"
        )
        stack_leaf = StackLeaf(five_node_stack)
        assert stack_leaf.module_name == "Conv2d_1->Conv2d_0"

    def test_to_json(self, five_node_stack):
        five_node_stack.parent.parent.value["name"] = (
            "torch.nn.functional.py: _call_impl"
        )
        five_node_stack.parent.parent.parent.value["name"] = "nn.Module: Conv2d"
        stack_leaf = StackLeaf(five_node_stack)
        print(stack_leaf.to_json())
        assert stack_leaf.to_json() == {
            "layer": "Conv2d",
            "start": 4,
            "end": 5,
            "duration": 1,
            "id": stack_leaf.leaf_id,
        }


#
#
# class TestModelCallStacks:
#     @pytest.fixture(scope="class")
#     def python_function_events(self, profiler_data_original):
#         return [
#             event
#             for event in profiler_data_original["traceEvents"]
#             if event.get("cat", None) == "python_function"
#         ]
#
#     @pytest.fixture(scope="function")
#     def instant(self, python_function_events):
#         return ModelCallStacks(python_function_events)
#
#     @patch.object(ModelCallStacks, "_build_up")
#     def test_preprocessing(self, mock_build_up, python_function_events):
#         instant = ModelCallStacks(python_function_events)
#         mock_build_up.assert_called_once()
#         assert instant._leafs == []
#         assert instant._nodes_in_order == {}
#
#     def test_check_properties_leafs(self, instant):
#         assert len(instant.leafs) == 41019
#         assert all(isinstance(leaf, StackLeaf) for leaf in instant.leafs)
#
#     def test_check_properties_model_layer_leafs(self, instant):
#         assert len(instant.model_layer_leafs) == 565
#         assert all(isinstance(node, StackLeaf) for node in instant.model_layer_leafs)
#         assert all(leaf.is_model_layer_trace for leaf in instant.model_layer_leafs)
#
#     def test_check_nodes_in_order(self, instant):
#         assert len(instant.nodes_in_order) == 52589
#         assert all(
#             isinstance(node, StackNode) for node in instant.nodes_in_order.values()
#         )
#         for node_id, node in instant.nodes_in_order.items():
#             assert node_id == node.id
#             if node.parent_id is None:
#                 assert node.parent is None
#             else:
#                 assert instant.nodes_in_order[node.parent_id] == node.parent
#                 assert node in instant.nodes_in_order[node.parent_id].children.values()
#
#     def test_get_node_by_id(self, instant):
#         assert instant.get_node_by_id(1) == instant.nodes_in_order[1]
#         assert instant.get_node_by_id(0) is None
#
#     def test_flame_graph(self, instant):
#         svg_code = instant.flame_graph(False)
#         assert isinstance(ET.fromstring(svg_code), ET.Element)
#         svg_code_1 = instant.flame_graph(True)
#         assert isinstance(ET.fromstring(svg_code_1), ET.Element)
#         assert len(svg_code) > len(svg_code_1)
#
#     def test_to_json(self, instant):
#         result = instant.to_json()
#         assert isinstance(result, list)
#         for element in result:
#             assert isinstance(element, dict)
#             assert "layer" in element.keys() and isinstance(element["layer"], str)
#             assert "start" in element.keys() and isinstance(element["start"], int)
#             assert "end" in element.keys() and isinstance(element["end"], int)
#             assert "duration" in element.keys() and isinstance(element["duration"], int)
#             assert "memory_history" in element.keys() and isinstance(
#                 element["memory_history"], list
#             )
#             assert "id" in element.keys() and isinstance(element["id"], str)
