from typing import Any, Dict, List
from bisect import bisect_left, bisect_right
from .node import CpuInstantNode
from .ops import StackLeaf


class MemoryActivity:
    def __init__(self, data: List[Dict[str, Any]]):
        self._data: Dict[int, CpuInstantNode] = self._build_up(data)

    @property
    def activities(self) -> Dict[int, CpuInstantNode]:
        return self._data

    def _build_up(self, data: List[Dict[str, Any]]) -> Dict[int, CpuInstantNode]:
        _activities: Dict[int, CpuInstantNode] = {}
        for trace in data:
            if trace.get("cat", None) not in ["cpu_instant_event"]:
                continue
            _node = CpuInstantNode(trace)
            if _node.start_time in _activities.keys():
                _duplicate_node = _activities[_node.start_time]
                raise ValueError(
                    f"Duplicated Events"
                    f"Event 1: start time: {_node.start_time}, Event index: {_node.value['args']['Ev Idx']},"
                    f"Event 2: start time: {_duplicate_node.start_time}, Event index: {_duplicate_node.value['args']['Ev Idx']}"
                )
            _activities[_node.start_time] = _node
        return _activities

    def search_activities_in_time_range(
        self, start: int, end: int
    ) -> List[CpuInstantNode]:
        """The function is built upon the binary search algorithm to find all the operator nodes within a specified time range.

        Args:
            start (int): the start time of the time range.
            end (int): the end time of the time range.

        Returns:
            List[OperatorNode]: a list of operator nodes within the specified time range.
        """
        sorted_timestamps = sorted(self.activities.keys())

        # To find the start and end positions of the time using binary search
        start_idx = bisect_left(sorted_timestamps, start)
        end_idx = bisect_right(sorted_timestamps, end)

        # To collect all values within a specified time range
        result = []
        for i in range(start_idx, end_idx):
            result.append(self._data[sorted_timestamps[i]])

        result.sort(key=lambda x: x.start_time)
        return result
