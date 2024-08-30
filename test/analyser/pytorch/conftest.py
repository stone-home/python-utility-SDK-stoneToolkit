import os

import pytest


@pytest.fixture(scope="function")
def profiler_data__cpu_op():
    return {
        "ph": "X",
        "cat": "cpu_op",
        "name": "aten::to",
        "pid": 6632,
        "tid": 6632,
        "ts": 1724696154697016,
        "dur": 26,
        "args": {
            "External id": 2,
            "Sequence number": 15,
            "Fwd thread id": 0,
            "Concrete Inputs": ["", "6", "0", "", "", "False", "False", ""],
            "Input type": ["float", "Scalar", "Scalar", "", "", "Scalar", "Scalar", ""],
            "Input Dims": [[200, 3, 86, 86], [], [], [], [], [], [], []],
            "Ev Idx": 1,
        },
    }


@pytest.fixture(scope="function")
def profiler_data__python_function():
    return {
        "ph": "X",
        "cat": "python_function",
        "name": "<built-in function fspath>",
        "pid": 6632,
        "tid": 6632,
        "ts": 1724696155107983,
        "dur": 0,
        "args": {"Python parent id": 39550, "Python id": 39551, "Ev Idx": 39974},
    }


@pytest.fixture(scope="function")
def profiler_data__other_type_data():
    return {
        "name": "process_name",
        "ph": "M",
        "ts": 1724696154696880,
        "pid": 6632,
        "tid": 0,
        "args": {"name": "python"},
    }


@pytest.fixture(scope="function")
def profiler_data__cpu_instant_event():
    return {
        "ph": "i",
        "cat": "cpu_instant_event",
        "s": "t",
        "name": "[memory]",
        "pid": 6504,
        "tid": 6569,
        "ts": 1724696104648464,
        "args": {
            "Total Reserved": 1910505472,
            "Total Allocated": 795438592,
            "Bytes": 102400,
            "Addr": 137224702615552,
            "Device Id": 0,
            "Device Type": 1,
            "Ev Idx": 126,
        },
    }


@pytest.fixture(scope="function")
def profiler_data_sample():
    return {
        "schemaVersion": 1,
        "deviceProperties": [
            {
                "id": 0,
                "name": "NVIDIA GeForce RTX 4060",
                "totalGlobalMem": 8223916032,
                "computeMajor": 8,
                "computeMinor": 9,
                "maxThreadsPerBlock": 1024,
                "maxThreadsPerMultiprocessor": 1536,
                "regsPerBlock": 65536,
                "regsPerMultiprocessor": 65536,
                "warpSize": 32,
                "sharedMemPerBlock": 49152,
                "sharedMemPerMultiprocessor": 102400,
                "numSms": 24,
                "sharedMemPerBlockOptin": 101376,
            }
        ],
        "record_shapes": 1,
        "with_stack": 1,
        "profile_memory": 1,
        "traceEvents": [
            {
                "ph": "X",
                "cat": "user_annotation",
                "name": "ProfilerStep#2",
                "pid": 6632,
                "tid": 6632,
                "ts": 1724696154696971,
                "dur": 310239,
                "args": {"External id": 1, "Ev Idx": 0},
            },
            {
                "ph": "X",
                "cat": "cpu_op",
                "name": "aten::to",
                "pid": 6632,
                "tid": 6632,
                "ts": 1724696154697016,
                "dur": 26,
                "args": {
                    "External id": 2,
                    "Sequence number": 15,
                    "Fwd thread id": 0,
                    "Concrete Inputs": ["", "6", "0", "", "", "False", "False", ""],
                    "Input type": [
                        "float",
                        "Scalar",
                        "Scalar",
                        "",
                        "",
                        "Scalar",
                        "Scalar",
                        "",
                    ],
                    "Input Dims": [[200, 3, 86, 86], [], [], [], [], [], [], []],
                    "Ev Idx": 1,
                },
            },
            {
                "ph": "X",
                "cat": "cpu_op",
                "name": "aten::to",
                "pid": 6632,
                "tid": 6632,
                "ts": 1724696154697149,
                "dur": 18,
                "args": {
                    "External id": 3,
                    "Sequence number": 15,
                    "Fwd thread id": 0,
                    "Concrete Inputs": ["", "4", "0", "", "", "False", "False", ""],
                    "Input type": [
                        "long int",
                        "Scalar",
                        "Scalar",
                        "",
                        "",
                        "Scalar",
                        "Scalar",
                        "",
                    ],
                    "Input Dims": [[200], [], [], [], [], [], [], []],
                    "Ev Idx": 2,
                },
            },
            {
                "ph": "X",
                "cat": "user_annotation",
                "name": "Optimizer.zero_grad#SGD.zero_grad",
                "pid": 6632,
                "tid": 6632,
                "ts": 1724696154697312,
                "dur": 32,
                "args": {"External id": 4, "Ev Idx": 3},
            },
            {
                "ph": "X",
                "cat": "python_function",
                "name": "posixpath.py(41): _get_sep",
                "pid": 6632,
                "tid": 6632,
                "ts": 1724696155103538,
                "dur": 0,
                "args": {
                    "Python parent id": 26569,
                    "Python id": 26571,
                    "Ev Idx": 26994,
                },
            },
            {
                "ph": "X",
                "cat": "python_function",
                "name": "<built-in function isinstance>",
                "pid": 6632,
                "tid": 6632,
                "ts": 1724696155103538,
                "dur": 0,
                "args": {
                    "Python parent id": 26571,
                    "Python id": 26572,
                    "Ev Idx": 26995,
                },
            },
            {
                "ph": "X",
                "cat": "python_function",
                "name": "<built-in method startswith of str object at 0x7a51b3f696c0>",
                "pid": 6632,
                "tid": 6632,
                "ts": 1724696155103538,
                "dur": 0,
                "args": {
                    "Python parent id": 26569,
                    "Python id": 26573,
                    "Ev Idx": 26996,
                },
            },
            {
                "ph": "X",
                "cat": "python_function",
                "name": "<built-in method endswith of str object at 0x7a51b3f696c0>",
                "pid": 6632,
                "tid": 6632,
                "ts": 1724696155103538,
                "dur": 0,
                "args": {
                    "Python parent id": 26569,
                    "Python id": 26574,
                    "Ev Idx": 26997,
                },
            },
            {
                "name": "process_sort_index",
                "ph": "M",
                "ts": 1724696154696807,
                "pid": "Spans",
                "tid": 0,
                "args": {"sort_index": 536870912},
            },
            {
                "name": "Iteration Start: PyTorch Profiler",
                "ph": "i",
                "s": "g",
                "pid": "Traces",
                "tid": "Trace PyTorch Profiler",
                "ts": 1724696154696807,
            },
            {
                "name": "Record Window End",
                "ph": "i",
                "s": "g",
                "pid": "",
                "tid": "",
                "ts": 1724696155143440,
            },
        ],
        "traceName": "./log/stone-System-Product-Name_6632.1724696155242817250.pt.trace.json",
    }


@pytest.fixture(scope="class")
def profiler_data_original(root_dir) -> dict:
    import json

    file_name = "test_profiler_cpu_only.json"
    data_file = os.path.join(root_dir, "analyser/pytorch/testdata", file_name)
    with open(data_file, "r") as f:
        return json.load(f)
