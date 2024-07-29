import threading
import time
import os
import json
import logging
import uuid
from typing import List, Optional, Dict
from .cgroup import CGroupMonitor
from .ethernet import EthernetMonitor

logger = logging.getLogger(__name__)


class HostMetrics:
    def __init__(self, interval: int = 10, gpu_enable: bool = True, uuid: Optional[str] = None):
        """A host metrics class to monitor the host system

        Args:
            interval (int): The interval to monitor the system. Defaults to 10 ms
        """
        self._id = uuid or str(uuid.uuid4())[:8]
        self.cgroup = CGroupMonitor()
        self.net = EthernetMonitor()
        if gpu_enable:
            from .nvml import HostGPUs
            self.gpu = HostGPUs()
            logger.info(f"[{self._id}]GPU monitoring is enabled.")
        else:
            self.gpu = None
        logger.info(f"[{self._id}]GPU monitoring is disabled.")
        # convert to seconds
        self._interval = interval/1000
        self._count = 0
        self._records = []
        logger.info(f"[{self._id}]Set the interval to monitor the system: {interval} ms")

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, value):
        """Change the interval to monitor the system, in ms

        Args:
            value (int): The interval to monitor the system, in ms

        """
        logger.warning(f"[{self._id}]Change the interval to monitor the system: {value} ms")
        self._interval = value / 1000

    def get_records(self) -> List[dict]:
        return self._records

    def record(self):
        if self._count % (1/self.interval) == 0:
            logger.info(f"[{self._id}]Record the system metrics at {time.time_ns()}")
        _cpu_time_p = self.cgroup.cpu_usage()
        _ethernet_p = self.net.get_all_interfaces_data()
        time.sleep(self.interval)
        _cpu_time_c = self.cgroup.cpu_usage()
        _ethernet_c = self.net.get_all_interfaces_data()
        _cpu_time_ms = (_cpu_time_c - _cpu_time_p) / 1000000  # convert to ms
        _net_utils = {}
        interval_in_sec = self.interval * 1000
        for interface in self.net.interfaces:
            _net_p = _ethernet_p[interface]
            _net_c = _ethernet_c[interface]
            _utils = {
                "rx": round(((_net_c.r_bytes - _net_p.r_bytes)/1024/1024) / interval_in_sec, 2),
                "tx": round(((_net_c.t_bytes - _net_p.t_bytes)/1024/1024) / interval_in_sec, 2)
            }
            _net_utils[interface] = _utils

        _max_mem = self.cgroup.memory_max()
        if _max_mem > 0:
            _max_mem = round(_max_mem/1024/1024, 2)  # convert to MB

        _metric = {
            "timestamp": round(time.time_ns()/1000000, 2),  # convert to ms
            "cpu": {
                "utilisation":  round((_cpu_time_ms / self.interval) * 100, 2), # convert to percentage
            },
            "memory": {
                "usage": self.cgroup.memory_usage()/1024/1024,  # convert to MB,
                "max": _max_mem,
            },
            "network": _net_utils,
        }
        if self.gpu is not None:
            _metric["gpu"] = self.gpu.to_json()
        else:
            _metric["gpu"] = {}
        self._records.append(_metric)
        # this protected variable 'count' is used to save the memory for calculating the length of records
        # length of records will be called every time when the record method is called and the logger will
        # record a message when mod (length of record)%(1/interval) is 0
        self._count += 1

    def to_json(self):
        """Get the data in JSON format

        Returns:
            dict: The data in JSON format

        Examples:
            {
                "interval": "10",  # unit: s
                "num": 2,
                "makespan": 10, # unit: ms
                "records": [
                    {
                        "timestamp": 1630627340000, # unit: ms
                        "cpu": {
                            "utilisation": 0.0  # unit: percentage
                        },
                        "memory": {
                            "usage": 0.0,  # unit: MB
                            "max": 0.0 # unit: MB
                        },
                        "network": {
                            "eth0": {
                                "rx": 0.0,  # unit: MB/s
                                "tx": 0.0   # unit: MB/s
                            }
                        },
                        "gpu": {}
                    }
                ]
            }

        """
        _records = self.get_records()
        _data = {
            "interval": self.interval * 1000,  # unit: ms
            "num": self._count,
            "makespan": round((_records[-1]["timestamp"] - _records[0]["timestamp"]), 2),  # unit: ms
            "records": _records
        }
        return _data

    def save(self, file_path: str):
        """Save the data to a file

        Args:
            file_path (str): The file path to save the data

        """
        with open(file_path, "w") as f:
            json.dump(self.to_json(), f, indent=4)
        logger.info(f"[{self._id}]Save the monitoring data to {file_path}")


class _Template:
    @staticmethod
    def monitor(interval: int, gpu_enable: bool, uuid: Optional[str] = None, **kwargs):
        monitor = HostMetrics(interval=interval, gpu_enable=gpu_enable, uuid=uuid)
        while not kwargs.get("signal").is_set():
            monitor.record()
        data_dir = kwargs.get("dir")
        file_name = kwargs.get("file_name")
        file_path = os.path.join(data_dir, file_name)
        monitor.save(file_path)


class MonitorThreading:
    def __init__(self, temp="monitor", name: str = "monitor"):
        self.name = name
        self.stop_flat = threading.Event()
        self.func = getattr(_Template, temp)
        self.thread = None

    @property
    def is_alive(self):
        if self.thread is not None:
            return self.thread.is_alive()
        return False

    def run(self, **kwargs):
        kwargs["signal"] = self.stop_flat
        kwargs["uuid"] = self.name
        self.thread = threading.Thread(target=self.func, kwargs=kwargs)
        self.thread.start()
        logger.info(f"Start monitoring thread: {self.name}, thread id: {self.thread.ident}")

    def stop(self):
        if self.thread is not None:
            logger.info(f"Stop monitoring thread: {self.name}, thread id: {self.thread.ident}")
            self.stop_flat.set()


class HostMonitor:
    def __init__(
            self,
            interval: int = 10,
            gpu_enable: bool = True,
            default_data_dir: Optional[str] = None,
            default_file_name: Optional[str] = None
    ):
        self._interval: int = interval
        self._gpu_enable: bool = gpu_enable
        self._thread: Dict[str, MonitorThreading] = {}
        self._stopping_thread: Dict[str, MonitorThreading] = {}
        self._default_data_dir = default_data_dir or "/tmp"
        self._default_file_name = default_file_name or f"host_monitor_{str(uuid.uuid4())[:10]}"

    def __enter__(self):
        self.start_new_monitor("default")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_monitor("default")
        time.sleep(0.5)
        self.cleanup()

    def start_new_monitor(self, monitor_name: str, data_dir: Optional[str] = None, file_name: Optional[str] = None):
        kwargs = {
            "dir": data_dir or self._default_data_dir,
            "file_name": file_name or self._default_file_name,
            "interval": self._interval,
            "gpu_enable": self._gpu_enable
        }
        _thread = MonitorThreading(temp="monitor", name=monitor_name)
        _thread.run(**kwargs)
        self._thread[monitor_name] = _thread

    def stop_monitor(self, monitor_name: str):
        _thread = self._thread.get(monitor_name)
        del self._thread[monitor_name]
        self._stopping_thread[monitor_name] = _thread
        logger.info(f"Stop monitoring thread: {monitor_name}, thread id: {_thread.thread.ident}. Add to stopping list.")
        logger.info(f"Current running threads: {list(self._thread.keys())}")
        logger.info(f"Current stopping threads: {list(self._stopping_thread.keys())}")
        _thread.stop()

    def cleanup(self):
        if len(self._thread) > 0:
            logger.warning("There are still running threads. Stop them first.")
            _keys = list(self._thread.keys())
            for monitor_name in _keys:
                logger.warning(f"Stop running thread: {monitor_name} in Cleanup.")
                self.stop_monitor(monitor_name)
        time.sleep(0.5)
        if len(self._stopping_thread) > 0:
            logger.warning("There are still stopping threads. Wait for them to stop.")
            for monitor_name in self._stopping_thread.keys():
                _thread = self._stopping_thread[monitor_name]
                if _thread.is_alive:
                    logger.warning(f"Wait for stopping thread: {monitor_name}, thread id: {_thread.thread.ident}")
                    _thread.stop()
                    _thread.thread.join()


def monitor(
        interval: int = 100,
        gpu_enable: bool = False,
        monitor_name: str = "host_monitor",
        data_dir: str = "/tmp",
        file_name: str = None
):
    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor_params = {
                "dir": data_dir,
                "file_name": file_name or f"host_monitor_{str(uuid.uuid4())[:10]}",
                "interval": interval,
                "gpu_enable": gpu_enable
            }
            _thread = MonitorThreading(temp="monitor", name=monitor_name)
            _thread.run(**monitor_params)
            result = func(*args, **kwargs)
            _thread.stop()
            _thread.thread.join()
            return result
        return wrapper
    return decorator
