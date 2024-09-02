from importlib import import_module

import pytest
from unittest.mock import patch
from typing import List
from stone_lib.analyser.pytorch.profiler.node import OperatorNode, StackNode
from stone_lib.analyser.pytorch.profiler.ops import Operators, StackLeaf


class TestOperator:
    @pytest.fixture(scope="class")
    def cpu_op_events(self, profiler_data_original):
        return [
            event
            for event in profiler_data_original["traceEvents"]
            if event.get("cat", None) == "cpu_op"
        ]

    @pytest.fixture(scope="function")
    def instant(self, cpu_op_events):
        return Operators(cpu_op_events)

    @patch.object(Operators, "_build_up")
    def test_init(self, mock_build_up, cpu_op_events):
        mock_build_up.return_value = ({}, {})
        _op = Operators(cpu_op_events)
        mock_build_up.assert_called_once_with(cpu_op_events)
        assert _op.ops == {}

    def test_properties(self, instant):
        assert isinstance(instant.ops, dict)
        assert len(instant.ops.keys()) == 284
        for ops in instant.ops.values():
            assert isinstance(ops, list)
            for op in ops:
                assert isinstance(op, OperatorNode)

    def test_search_ops_in_time_range(self, instant):
        ops = list(instant.ops.values())
        start_time = ops[0][0].start_time
        end_time = ops[100][0].start_time
        ops = instant.search_ops_in_time_range(start_time, end_time)
        assert isinstance(ops, list)
        assert all(op.parent is None for op in ops)

    # def test_search_ops_by_stackleaf(
    #     self, instant, profiler_data__python_function__module_call
    # ):
    #     stack_leaf = StackLeaf(StackNode(profiler_data__python_function__module_call))
    #     instant.search_ops_by_stackleaf(stack_leaf)
    #     assert len(stack_leaf.ops) == 10
    #     assert all(isinstance(op, OperatorNode) for op in stack_leaf.ops)
