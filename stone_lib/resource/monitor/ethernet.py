import os
import logging
from typing import List, Dict

logger = logging.getLogger()


class EthernetMetrics:
    def __init__(self, data: str):
        logger.debug(f"EthernetMetrics input data: {data}")
        self.data: List[str] = data.split()
        if len(self.data) != 17:
            raise ValueError("Invalid data, the data should have 17 fields")

    @property
    def interface(self) -> str:
        return self.data[0].replace(":", "")

    @property
    def r_bytes(self) -> int:
        return int(self.data[1])

    @property
    def r_packets(self) -> int:
        return int(self.data[2])

    @property
    def r_errs(self) -> int:
        return int(self.data[3])

    @property
    def r_drop(self) -> int:
        return int(self.data[4])

    @property
    def r_fifo(self) -> int:
        return int(self.data[5])

    @property
    def r_frame(self) -> int:
        return int(self.data[6])

    @property
    def r_compressed(self) -> int:
        return int(self.data[7])

    @property
    def r_multicast(self) -> int:
        return int(self.data[8])

    @property
    def t_bytes(self) -> int:
        return int(self.data[9])

    @property
    def t_packets(self) -> int:
        return int(self.data[10])

    @property
    def t_errs(self) -> int:
        return int(self.data[11])

    @property
    def t_drop(self) -> int:
        return int(self.data[12])

    @property
    def t_fifo(self) -> int:
        return int(self.data[13])

    @property
    def t_colls(self) -> int:
        return int(self.data[14])

    @property
    def t_carrier(self) -> int:
        return int(self.data[15])

    @property
    def t_compressed(self) -> int:
        return int(self.data[16])

    def to_json(self) -> dict:
        return {
            "interface": self.interface,
            "receive": {
                "bytes": self.r_bytes,
                "packets": self.r_packets,
                "errs": self.r_errs,
                "drop": self.r_drop,
                "fifo": self.r_fifo,
                "frame": self.r_frame,
                "compressed": self.r_compressed,
                "multicast": self.r_multicast
            },
            "transmit": {
                "bytes": self.t_bytes,
                "packets": self.t_packets,
                "errs": self.t_errs,
                "drop": self.t_drop,
                "fifo": self.t_fifo,
                "colls": self.t_colls,
                "carrier": self.t_carrier,
                "compressed": self.t_compressed
            }
        }


class EthernetMonitor:
    NetDir = "/proc/net"
    CheckList = ["dev"]

    def __init__(self):
        self.net_dir = self.NetDir

    def _get_raw_data(self) -> List[str]:
        """Get the raw data from the dev file

        Returns:
            list[str]: The raw data from the dev file
        """
        with open(os.path.join(self.net_dir, "dev"), "r") as f:
            lines = f.readlines()
        logger.debug(f"Raw data from /proc/net/dev: {lines}")
        return lines

    def _get_structured_data(self) -> Dict[str, EthernetMetrics]:
        """Get the structured data from the raw data

        Returns:
            dict: The structured data from the raw data

        Examples:
            {
                "eth0": EthernetMetrics,
            }

        """
        _raw_data = self._get_raw_data()
        _interface = {}
        for line in _raw_data[2:]:
            if line.strip() == "":
                continue
            logger.debug(f"create EthernetMetrics from {line}")
            _ethernet = EthernetMetrics(line)
            _interface[_ethernet.interface] = _ethernet
        return _interface

    @property
    def interfaces(self) -> List[str]:
        """Get the list of interfaces

        Returns:
            List[str]: The list of interfaces

        Examples:
            [
                "eth0",
                "eth1"
            ]
        """
        return list(self._get_structured_data().keys())

    def get_all_interfaces_data(self) -> Dict[str, EthernetMetrics]:
        """Get the data of all interfaces

        Returns:
            List[EthernetMetrics]: The data of all interfaces

        Examples:
            {
                "eth0": EthernetMetrics,
                "eth1": EthernetMetrics
            }

        """
        return self._get_structured_data()

    def get_specific_interface_data(self, interface: str) -> EthernetMetrics:
        """Get the data of a specific interface

        Args:
            interface (str): The interface name

        Returns:
            EthernetMetrics: The data of the specific interface

        """
        _data = self._get_structured_data()
        if interface in self.interfaces:
            return _data[interface]
        else:
            raise KeyError(f"Interface {interface} not found, only {self.interfaces} are available")

    def to_json(self) -> Dict[str, Dict]:
        """Convert the data to json

        Returns:
            Dict[str, Dict]: The data in json format

        """
        _data = self._get_structured_data()
        return {interface: _data[interface].to_json() for interface in self.interfaces}


if __name__ == "__main__":
    em = EthernetMonitor()
    print(em.get_all_interfaces_data())
    print(em.get_specific_interface_data("eth0").to_json())
