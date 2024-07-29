import pytest
from unittest.mock import patch, mock_open, Mock, MagicMock, PropertyMock
from stone_lib.resource.monitor.ethernet import EthernetMonitor, EthernetMetrics


mock_data ="""Inter-|   Receive                                                |  Transmit
face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
lo:  446088     4890    0    0    0     0          0         0   446088     4890    0    0    0     0       0          0
eth0: 20714750   15080    0    0    0     0          0         0  1420561    10239    0    0    0     0       0          0
"""

class TestEthernetMetric:
    @pytest.fixture
    def input_data(self):
        return "eth0: 123 456 789 101112 131415 161718 192021 222324 252627 282930 313233 343536 373839 404142 76782 12837731"

    @pytest.fixture
    def instance(self, input_data) -> EthernetMetrics:
        return EthernetMetrics(input_data)

    def test_init_with_valueerror_greater_17(self):
        _data = "eth0: 123 456 789 101112 131415 161718 192021 222324 252627 282930 313233 343536 373839 404142 76782 12837731 668221"
        with pytest.raises(ValueError):
            EthernetMetrics(_data)

    def test_init_with_valueerror_less_17(self):
        _data = "eth0: 123 456 789 101112 131415 161718 192021 222324 252627 282930 313233 343536"
        with pytest.raises(ValueError):
            EthernetMetrics(_data)

    def test_init_data(self, input_data, instance):
        assert instance.data == input_data.split()

    def test_interface(self, input_data, instance):
        assert instance.interface == input_data.split(":")[0].strip()

    def test_receive_bytes(self, input_data, instance):
        assert instance.r_bytes == int(input_data.split()[1])

    def test_receive_packets(self, input_data, instance):
        assert instance.r_packets == int(input_data.split()[2])

    def test_receive_errors(self, input_data, instance):
        assert instance.r_errs == int(input_data.split()[3])

    def test_receive_drop(self, input_data, instance):
        assert instance.r_drop == int(input_data.split()[4])

    def test_receive_fifo(self, input_data, instance):
        assert instance.r_fifo == int(input_data.split()[5])

    def test_receive_frame(self, input_data, instance):
        assert instance.r_frame == int(input_data.split()[6])

    def test_receive_compressed(self, input_data, instance):
        assert instance.r_compressed == int(input_data.split()[7])

    def test_receive_multicast(self, input_data, instance):
        assert instance.r_multicast == int(input_data.split()[8])

    def test_transmit_bytes(self, input_data, instance):
        assert instance.t_bytes == int(input_data.split()[9])

    def test_transmit_packets(self, input_data, instance):
        assert instance.t_packets == int(input_data.split()[10])

    def test_transmit_errors(self, input_data, instance):
        assert instance.t_errs == int(input_data.split()[11])

    def test_transmit_drop(self, input_data, instance):
        assert instance.t_drop == int(input_data.split()[12])

    def test_transmit_fifo(self, input_data, instance):
        assert instance.t_fifo == int(input_data.split()[13])

    def test_trainsmit_colls(self, input_data, instance):
        assert instance.t_colls == int(input_data.split()[14])

    def test_transmit_carrier(self, input_data, instance):
        assert instance.t_carrier == int(input_data.split()[15])

    def test_comppressed(self, input_data, instance):
        assert instance.t_compressed == int(input_data.split()[16])

    def test_to_json(self, instance):
        expected = {
            "interface": instance.interface,
            "receive": {
                "bytes": instance.r_bytes,
                "packets": instance.r_packets,
                "errs": instance.r_errs,
                "drop": instance.r_drop,
                "fifo": instance.r_fifo,
                "frame": instance.r_frame,
                "compressed": instance.r_compressed,
                "multicast": instance.r_multicast,
            },
            "transmit": {
                "bytes": instance.t_bytes,
                "packets": instance.t_packets,
                "errs": instance.t_errs,
                "drop": instance.t_drop,
                "fifo": instance.t_fifo,
                "colls": instance.t_colls,
                "carrier": instance.t_carrier,
                "compressed": instance.t_compressed,
            }
        }
        assert instance.to_json() == expected


class TestEthernetMonitor:
    @pytest.fixture
    def input_data(self):
        return mock_data

    @pytest.fixture
    def instance(self):
        return EthernetMonitor()

    def test_init(self, instance):
        assert instance.net_dir == instance.NetDir

    @patch('builtins.open', new_callable=mock_open, read_data=mock_data)
    def test_get_raw_data(self, mock_file):
        monitor = EthernetMonitor()
        raw_data = monitor._get_raw_data()
        with open(mock_file) as f:
            assert raw_data == f.readlines()

    @patch('builtins.open', new_callable=mock_open, read_data=mock_data)
    def test_get_structured_data(self, mock_file, instance, input_data):
        with open(mock_file) as f:
            _data = f.readlines()
            with patch.object(EthernetMonitor, "_get_raw_data", return_value=_data):
                mock_class_1 = Mock()
                mock_class_1.interface = "lo"
                mock_class_2 = Mock()
                mock_class_2.interface = "eth0"
                with patch(f"stone_lib.resource.monitor.ethernet.EthernetMetrics", side_effect=[mock_class_1, mock_class_2]) as mock_class:
                    result = instance._get_structured_data()
                    assert result == {
                        "lo": mock_class_1,
                        "eth0": mock_class_2
                    }
                    for line in _data[2:]:
                        if line.strip() == "":
                            continue
                        mock_class.assert_any_call(line)

    @patch.object(EthernetMonitor, "_get_structured_data", return_value={"lo": MagicMock(), "eth0": MagicMock()})
    def test_interfaces(self, mock_get_structured_data, instance):
        assert instance.interfaces == list(mock_get_structured_data.return_value.keys())

    @patch.object(EthernetMonitor, "_get_structured_data", return_value={"lo": MagicMock(), "eth0": MagicMock()})
    def test_get_all_interfaces(self, mock_get_structured_data, instance):
        assert instance.get_all_interfaces_data() == mock_get_structured_data.return_value

    @patch.object(EthernetMonitor, "_get_structured_data", return_value={"lo": MagicMock(), "eth0": MagicMock()})
    def test_get_specific_interface_data(self, mock_get_structured_data, instance):
        assert instance.get_specific_interface_data("lo") == mock_get_structured_data.return_value["lo"]
        assert instance.get_specific_interface_data("eth0") == mock_get_structured_data.return_value["eth0"]

    @patch.object(EthernetMonitor, "_get_structured_data", return_value={"lo": MagicMock(), "eth0": MagicMock()})
    def test_to_json(self, mock_get_structured_data, instance):
        assert instance.to_json() == {interface: mock_get_structured_data.return_value[interface].to_json() for interface in instance.interfaces}
        mock_get_structured_data.return_value["lo"].to_json.assert_called()
        mock_get_structured_data.return_value["eth0"].to_json.assert_called()

