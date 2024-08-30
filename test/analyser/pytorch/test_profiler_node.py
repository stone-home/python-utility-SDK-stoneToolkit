from operator import index

import pytest
from unittest.mock import patch, PropertyMock
from stone_lib.analyser.pytorch.profiler_node import (
    ProfilerNode,
    StackNode,
    OperatorNode,
    CpuInstantNode,
)
from stone_lib.data_structure import TreeNode


class ProfilerNodeStub(ProfilerNode):
    def _parse_name(self) -> list:
        return ["namespace", "function_name"]


class TestProfilerNode:
    @pytest.fixture(scope="function")
    def instant(self, profiler_data__cpu_op):
        return ProfilerNodeStub(profiler_data__cpu_op)

    def test_ph(self, instant, profiler_data__cpu_op):
        assert instant.ph == profiler_data__cpu_op["ph"]

    def test_category(self, instant, profiler_data__cpu_op):
        assert instant.category == profiler_data__cpu_op.get("cat")

    def test_name(self, instant, profiler_data__cpu_op):
        assert instant.name == profiler_data__cpu_op["name"]

    def test_namespace_name(self, instant):
        assert instant.namespace_name == "namespace"

    def test_function_name(self, instant):
        assert instant.function_name == "function_name"

    def test_start_time(self, instant, profiler_data__cpu_op):
        assert instant.start_time == profiler_data__cpu_op["ts"]

    def test_duration(self, instant, profiler_data__cpu_op):
        assert instant.duration == profiler_data__cpu_op.get("dur", 0)

    def test_end_time(self, instant, profiler_data__cpu_op):
        assert instant.end_time == profiler_data__cpu_op[
            "ts"
        ] + profiler_data__cpu_op.get("dur", 0)

    def test_tid(self, instant, profiler_data__cpu_op):
        assert instant.tid == profiler_data__cpu_op["tid"]

    def test_pid(self, instant, profiler_data__cpu_op):
        assert instant.pid == profiler_data__cpu_op["pid"]

    def test_parse_name(self, instant):
        assert instant._parse_name() == ["namespace", "function_name"]


class TestStackNode:
    @pytest.fixture(scope="function")
    def instant(self, profiler_data__python_function):
        return StackNode(profiler_data__python_function)

    def test_raise_assert_error(self, profiler_data__cpu_op):
        with pytest.raises(AssertionError):
            StackNode(profiler_data__cpu_op)

    def test_id(self, instant, profiler_data__python_function):
        assert instant.id == profiler_data__python_function["args"]["Python id"]

    def test_parent_id(self, instant, profiler_data__python_function):
        assert (
            instant.parent_id
            == profiler_data__python_function["args"]["Python parent id"]
        )

    @patch.object(StackNode, "function_name", new_callable=PropertyMock)
    def test_is_module_layer(
        self, mock_function_name, instant, profiler_data__python_function
    ):
        mock_function_name.return_value = "_call_impl"
        assert instant.is_module_layer is True

    @patch.object(StackNode, "function_name", new_callable=PropertyMock)
    def test_is_module_layer__false(
        self, mock_function_name, instant, profiler_data__python_function
    ):
        mock_function_name.return_value = "something else"
        assert instant.is_module_layer is False

    @patch.object(StackNode, "function_name", new_callable=PropertyMock)
    def test_is_getattr(
        self, mock_function_name, instant, profiler_data__python_function
    ):
        mock_function_name.return_value = "__getattr__"
        assert instant.is_getattr is True

    @patch.object(StackNode, "function_name", new_callable=PropertyMock)
    def test_is_getattr__false(
        self, mock_function_name, instant, profiler_data__python_function
    ):
        mock_function_name.return_value = "something else"
        assert instant.is_getattr is False

    @patch.object(StackNode, "name", new_callable=PropertyMock)
    def test_parse_name(self, mock_name, instant):
        mock_name.return_value = (
            "<built-in method __getattr__ of type object at 0x7f7f7f7f7f7f>"
        )
        print(instant._parse_name())
        assert instant._parse_name() == [
            "built-in method",
            " __getattr__ of type object at 0x7f7f7f7f7f7f>",
        ]

    @patch.object(StackNode, "name", new_callable=PropertyMock)
    def test_parse_name__no_match(self, mock_name, instant):
        mock_name.return_value = "resnet.py (41): _get_sep"
        assert instant._parse_name() == ["resnet.py (41)", " _get_sep"]

    @patch.object(StackNode, "name", new_callable=PropertyMock)
    def test_parse_name__no_match_2(self, mock_name, instant):
        mock_name.return_value = "resnet.py (41)"
        assert instant._parse_name() == ["resnet.py (41)", "unknown"]


class TestOperatorNode:
    @pytest.fixture(scope="function")
    def instant(self, profiler_data__cpu_op):
        return OperatorNode(profiler_data__cpu_op)

    def test_raise_assert_error(self, profiler_data__python_function):
        with pytest.raises(AssertionError):
            OperatorNode(profiler_data__python_function)

    def test_args_num(self, instant, profiler_data__cpu_op):
        assert instant.args_number == len(profiler_data__cpu_op["args"]["Input type"])

    def test_input_type(self, instant, profiler_data__cpu_op):
        assert instant.input_types == profiler_data__cpu_op["args"]["Input type"]

    def test_input_args(self, instant, profiler_data__cpu_op):
        assert instant.input_args == [
            {
                "type": profiler_data__cpu_op["args"]["Input type"][0],
                "dims": profiler_data__cpu_op["args"]["Input Dims"][0],
                "index": 0,
            }
        ]

    def test_concrete_inputs(self, instant, profiler_data__cpu_op):
        assert instant.concrete_inputs == [
            {
                "concrete_input": profiler_data__cpu_op["args"]["Concrete Inputs"][1],
                "type": profiler_data__cpu_op["args"]["Input type"][1],
                "index": 1,
            },
            {
                "concrete_input": profiler_data__cpu_op["args"]["Concrete Inputs"][2],
                "type": profiler_data__cpu_op["args"]["Input type"][2],
                "index": 2,
            },
            {
                "concrete_input": profiler_data__cpu_op["args"]["Concrete Inputs"][5],
                "type": profiler_data__cpu_op["args"]["Input type"][5],
                "index": 5,
            },
            {
                "concrete_input": profiler_data__cpu_op["args"]["Concrete Inputs"][6],
                "type": profiler_data__cpu_op["args"]["Input type"][6],
                "index": 6,
            },
        ]

    def test_seq_number(self, instant, profiler_data__cpu_op):
        assert instant.seq_number == profiler_data__cpu_op["args"].get(
            "Sequence number", None
        )

    def test_forward_thread_id(self, instant, profiler_data__cpu_op):
        assert instant.forward_thread_id == profiler_data__cpu_op["args"].get(
            "Fwd thread id", None
        )

    def test_is_autograd_enabled(self, instant, profiler_data__cpu_op):
        assert instant.is_autograd_enabled == (
            profiler_data__cpu_op["args"].get("Sequence number", None) is not None
        )

    @patch.object(OperatorNode, "name", new_callable=PropertyMock)
    def test_is_aten_op(self, mock_name, instant):
        mock_name.return_value = "aten::to"
        assert instant.is_aten_op is True

    @patch.object(OperatorNode, "name", new_callable=PropertyMock)
    def test_is_aten_op__false(self, mock_name, instant):
        mock_name.return_value = "something"
        assert instant.is_aten_op is False

    @patch.object(OperatorNode, "name", new_callable=PropertyMock)
    def test__parse_name_1(self, mock_name, instant):
        mock_name.return_value = "something: to"
        assert instant._parse_name() == ["something", "to"]

    @patch.object(OperatorNode, "name", new_callable=PropertyMock)
    def test__parse_name_2(self, mock_name, instant):
        mock_name.return_value = "something::to"
        assert instant._parse_name() == ["something", "to"]

    @patch.object(OperatorNode, "name", new_callable=PropertyMock)
    def test__parse_name__no_match(self, mock_name, instant):
        mock_name.return_value = "something"
        assert instant._parse_name() == ["op", "something"]


class TestCpuInstantNode:
    @pytest.fixture(scope="function")
    def instant(self, profiler_data__cpu_instant_event):
        return CpuInstantNode(profiler_data__cpu_instant_event)

    def test_raise_assert_error(self, profiler_data__cpu_op):
        with pytest.raises(AssertionError):
            CpuInstantNode(profiler_data__cpu_op)

    def test_name(self, instant, profiler_data__cpu_instant_event):
        assert instant.name == profiler_data__cpu_instant_event["name"]

    def test_total_reserved(self, instant, profiler_data__cpu_instant_event):
        assert (
            instant.total_reserved
            == profiler_data__cpu_instant_event["args"]["Total Reserved"]
        )

    def test_total_allocated(self, instant, profiler_data__cpu_instant_event):
        assert (
            instant.total_allocated
            == profiler_data__cpu_instant_event["args"]["Total Allocated"]
        )

    def test_bytes(self, instant, profiler_data__cpu_instant_event):
        assert instant.bytes == profiler_data__cpu_instant_event["args"]["Bytes"]

    def test_address(self, instant, profiler_data__cpu_instant_event):
        assert instant.address == profiler_data__cpu_instant_event["args"]["Addr"]

    def test_device_id(self, instant, profiler_data__cpu_instant_event):
        assert (
            instant.device_id == profiler_data__cpu_instant_event["args"]["Device Id"]
        )

    def test_device_type(self, instant, profiler_data__cpu_instant_event):
        assert (
            instant.device_type
            == profiler_data__cpu_instant_event["args"]["Device Type"]
        )

    def test_parse_name(self, instant):
        assert instant._parse_name() == ["cpu", "memory"]
        assert instant.namespace_name == "cpu"
        assert instant.function_name == "memory"
        assert instant.name == "[memory]"
