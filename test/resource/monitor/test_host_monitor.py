from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

from stone_lib.resource.monitor.host_monitor import (
    HostMetrics,
    HostMonitor,
    MonitorThreading,
    _Template,
    threading,
)
from stone_lib.resource.monitor.nvml import HostGPUs


class TestHostMetrics:
    @patch(f"stone_lib.resource.monitor.nvml.HostGPUs")
    @patch(f"stone_lib.resource.monitor.host_monitor.EthernetMonitor")
    @patch(f"stone_lib.resource.monitor.host_monitor.CGroupMonitor")
    def test_init(self, mock_cg, mock_eth, mock_gpu):
        interval = 10
        gpu_enable = False
        uuid = "test"
        host_metrics = HostMetrics(interval=interval, gpu_enable=gpu_enable, uuid=uuid)
        assert host_metrics._id == uuid
        assert host_metrics.gpu == None
        assert host_metrics._interval == interval / 1000
        assert host_metrics._count == 0
        assert host_metrics._records == []
        assert host_metrics.net == mock_eth.return_value
        assert host_metrics.cgroup == mock_cg.return_value
        mock_cg.assert_called_once()
        mock_eth.assert_called_once()
        mock_gpu.assert_not_called()

    @patch("stone_lib.resource.monitor.nvml.HostGPUs")
    @patch("stone_lib.resource.monitor.host_monitor.EthernetMonitor")
    @patch("stone_lib.resource.monitor.host_monitor.CGroupMonitor")
    def test_init_with_gpu(self, mock_cg, mock_eth, mock_gpu):
        interval = 10
        gpu_enable = True
        uuid = "test"
        host_metrics = HostMetrics(interval=interval, gpu_enable=gpu_enable, uuid=uuid)
        assert host_metrics._id == uuid
        assert host_metrics._interval == interval / 1000
        assert host_metrics._count == 0
        assert host_metrics._records == []
        assert host_metrics.net == mock_eth.return_value
        assert host_metrics.cgroup == mock_cg.return_value
        assert host_metrics.gpu == mock_gpu.return_value
        mock_cg.assert_called_once()
        mock_eth.assert_called_once()
        mock_gpu.assert_called_once()

    @pytest.fixture(scope="function")
    def mock_cg(self):
        return MagicMock()

    @pytest.fixture(scope="function")
    def mock_eth(self):
        return MagicMock()

    @pytest.fixture(scope="function")
    def mock_gpu(self):
        return MagicMock()

    @pytest.fixture(scope="function")
    def instance(self, mock_gpu, mock_eth, mock_cg):
        interval = 10
        gpu_enable = True
        uuid = "test"
        with patch(
            "stone_lib.resource.monitor.host_monitor.CGroupMonitor",
            return_value=mock_cg,
        ) as mock_cg, patch(
            "stone_lib.resource.monitor.host_monitor.EthernetMonitor",
            return_value=mock_eth,
        ) as mock_eth, patch(
            "stone_lib.resource.monitor.nvml.HostGPUs", return_value=mock_gpu
        ) as mock_gpu:
            return HostMetrics(interval=interval, gpu_enable=gpu_enable, uuid=uuid)

    def test_property_interval(self, instance):
        assert instance.interval == 10 / 1000

    def test_setter_interval(self, instance):
        instance.interval = 20
        assert instance.interval == 20 / 1000

    def test_get_records(self, instance):
        assert instance.get_records() == []

    @patch("stone_lib.resource.monitor.host_monitor.time")
    def test_record(self, mock_time, instance):
        instance.cgroup.cpu_usage.side_effect = [100000, 200000]

        mock_eth_1 = MagicMock()
        mock_eth_1.r_bytes = 100
        mock_eth_1.t_bytes = 100
        mock_eth_2 = MagicMock()
        mock_eth_2.r_bytes = 200
        mock_eth_2.t_bytes = 200

        instance.net.interfaces = ["eth0"]
        instance.net.get_all_interfaces_data.side_effect = [
            {"eth0": mock_eth_1},
            {"eth0": mock_eth_2},
        ]

        instance.cgroup.memory_max.return_value = -1
        instance.cgroup.memory_usage.return_value = 1024 * 1024

        instance.gpu.to_json.return_value = {"gpu": "test"}

        mock_time.time_ns.return_value = 100
        instance.record()
        assert instance._count == 1
        assert len(instance._records) == 1
        assert instance._records[0] == {
            "timestamp": round(mock_time.time_ns.return_value / 1000000, 2),
            "cpu": {
                "utilisation": 1000,
            },
            "memory": {"max": -1, "usage": 1.0},
            "network": {"eth0": {"rx": 0, "tx": 0}},
            "gpu": {"gpu": "test"},
        }

    @patch("stone_lib.resource.monitor.host_monitor.time")
    def test_record_withnot_gpu(self, mock_time, instance):
        instance.gpu = None
        instance.cgroup.cpu_usage.side_effect = [100000, 200000]

        mock_eth_1 = MagicMock()
        mock_eth_1.r_bytes = 100
        mock_eth_1.t_bytes = 100
        mock_eth_2 = MagicMock()
        mock_eth_2.r_bytes = 200
        mock_eth_2.t_bytes = 200

        instance.net.interfaces = ["eth0"]
        instance.net.get_all_interfaces_data.side_effect = [
            {"eth0": mock_eth_1},
            {"eth0": mock_eth_2},
        ]

        instance.cgroup.memory_max.return_value = -1
        instance.cgroup.memory_usage.return_value = 1024 * 1024

        mock_time.time_ns.return_value = 100
        instance.record()
        assert instance._count == 1
        assert len(instance._records) == 1
        assert instance._records[0] == {
            "timestamp": round(mock_time.time_ns.return_value / 1000000, 2),
            "cpu": {
                "utilisation": 1000,
            },
            "memory": {"max": -1, "usage": 1.0},
            "network": {"eth0": {"rx": 0, "tx": 0}},
            "gpu": {},
        }

    @patch("stone_lib.resource.monitor.host_monitor.time")
    def test_record_with_max_memory(self, mock_time, instance):
        instance.gpu = None
        instance.cgroup.cpu_usage.side_effect = [100000, 200000]

        mock_eth_1 = MagicMock()
        mock_eth_1.r_bytes = 100
        mock_eth_1.t_bytes = 100
        mock_eth_2 = MagicMock()
        mock_eth_2.r_bytes = 200
        mock_eth_2.t_bytes = 200

        instance.net.interfaces = ["eth0"]
        instance.net.get_all_interfaces_data.side_effect = [
            {"eth0": mock_eth_1},
            {"eth0": mock_eth_2},
        ]

        instance.cgroup.memory_max.return_value = 1024 * 1024
        instance.cgroup.memory_usage.return_value = 1024 * 1024

        mock_time.time_ns.return_value = 100
        instance.record()
        assert instance._count == 1
        assert len(instance._records) == 1
        assert instance._records[0] == {
            "timestamp": round(mock_time.time_ns.return_value / 1000000, 2),
            "cpu": {
                "utilisation": 1000,
            },
            "memory": {"max": 1.0, "usage": 1.0},
            "network": {"eth0": {"rx": 0, "tx": 0}},
            "gpu": {},
        }

    def test_to_json(self, instance):
        instance._records = [{"timestamp": 100}, {"timestamp": 200}]
        assert instance.to_json() == {
            "interval": 10,
            "records": [{"timestamp": 100}, {"timestamp": 200}],
            "num": 0,
            "makespan": 100,
        }

    @patch.object(HostMetrics, "to_json", return_value={"test": "test"})
    @patch("builtins.open", new_callable=mock_open)
    def test_save(self, mock_file, mock_to_json, instance):
        instance.save("test")
        mock_to_json.assert_called_once()
        mock_file.assert_called_once_with("test", "w")


class TestMonitorThreading:
    def test_init(self):
        monitor = MonitorThreading()
        assert monitor.name == "monitor"
        assert isinstance(monitor.stop_flat, threading.Event)
        assert monitor.func == _Template.monitor
        assert monitor.thread is None

    def test_init_with_name(self):
        monitor = MonitorThreading(name="test")
        assert monitor.name == "test"
        assert isinstance(monitor.stop_flat, threading.Event)
        assert monitor.func == _Template.monitor
        assert monitor.thread is None

    def test_is_alive(self):
        monitor = MonitorThreading()
        assert monitor.is_alive is False

    @patch(
        "stone_lib.resource.monitor.host_monitor.threading.Thread",
        return_value=MagicMock(),
    )
    def test_run(self, mock_thread):
        monitor = MonitorThreading()
        monitor.run()
        kwargs = {
            "signal": monitor.stop_flat,
            "uuid": monitor.name,
        }
        mock_thread.assert_called_once_with(target=monitor.func, kwargs=kwargs)
        mock_thread.start.called_once()

    @patch(
        "stone_lib.resource.monitor.host_monitor.threading.Thread",
        return_value=MagicMock(),
    )
    def test_run_with_kwargs(self, mock_thread):
        monitor = MonitorThreading()
        monitor.run(temp="test")
        kwargs = {
            "temp": "test",
            "signal": monitor.stop_flat,
            "uuid": monitor.name,
        }
        mock_thread.assert_called_once_with(target=monitor.func, kwargs=kwargs)
        monitor.thread.start.assert_called_once()

    @patch("stone_lib.resource.monitor.host_monitor.threading.Event")
    def test_stop(self, mock_event):
        monitor = MonitorThreading()
        monitor.thread = MagicMock()
        monitor.stop()
        assert monitor.stop_flat is mock_event.return_value
        monitor.stop_flat.set.assert_called_once()

    @patch("stone_lib.resource.monitor.host_monitor.threading.Event")
    def test_stop_thread_not_exist(self, mock_event):
        monitor = MonitorThreading()
        monitor.stop()
        assert monitor.stop_flat is mock_event.return_value
        monitor.stop_flat.set.assert_not_called()


class TestHostMonitor:
    def test_init(self):
        monitor = HostMonitor()
        assert monitor._interval == 10
        assert monitor._gpu_enable is True
        assert monitor._thread == {}
        assert monitor._stopping_thread == {}

    @patch("stone_lib.resource.monitor.host_monitor.MonitorThreading")
    def test_start_new_monitor(self, mock_monitor_thread):
        monitor = HostMonitor()
        kwargs = {
            "dir": "test",
            "file_name": "test",
            "interval": monitor._interval,
            "gpu_enable": True,
        }
        monitor.start_new_monitor("test", "test", "test")
        mock_monitor_thread.assert_called_once_with(temp="monitor", name="test")
        mock_monitor_thread.return_value.run.assert_called_once_with(**kwargs)
        assert monitor._thread == {"test": mock_monitor_thread.return_value}

    def test_stop_monitor(self):
        monitor = HostMonitor()
        mock_class = MagicMock()
        monitor._thread = {"test": mock_class}
        monitor.stop_monitor("test")
        mock_class.stop.assert_called_once()
        assert len(monitor._stopping_thread) == 1
        assert len(monitor._thread) == 0
        assert monitor._stopping_thread["test"] == mock_class

    def test_stop_monitor_thread_not_exist(self):
        monitor = HostMonitor()
        mock_class = MagicMock
        monitor._thread = {}
        with pytest.raises(KeyError):
            monitor.stop_monitor("test")

    @patch.object(HostMonitor, "stop_monitor")
    def test_cleanup(self, mock_stop_monitor):
        monitor = HostMonitor()
        mock_class = MagicMock()
        monitor._thread = {"test": mock_class, "test2": mock_class}
        monitor.cleanup()
        mock_stop_monitor.assert_any_call("test")
        mock_stop_monitor.assert_any_call("test2")

    def test_cleanup_stopping_thread_stage(self):
        monitor = HostMonitor()
        mock_class = Mock()
        mock_class.is_alive.return_value = Mock()
        monitor._thread = {}
        monitor._stopping_thread = {"test": mock_class, "test2": mock_class}
        monitor.cleanup()
        assert mock_class.stop.call_count == 2
        assert mock_class.thread.join.call_count == 2
