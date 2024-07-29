import pytest
from unittest.mock import patch, mock_open, MagicMock
from src.monitor.cgroup import _CGroupAbc, CGroupV1, CGroupV2, CGroupMonitor


class TestCGroupAbc:
    def test_cgroup_abc_init(self):
        with pytest.raises(TypeError):
            _CGroupAbc("/sys/fs/cgroup")

    # Test _get_cgroup_data method logic and parsing
    @patch("os.path.join", return_value="mocked_path")
    @patch("builtins.open", new_callable=mock_open, read_data="key1 value1\nkey2 value2")
    def test_get_cgroup_data(self, mock_file, mock_path_join):
        cgroup = CGroupV1("/sys/fs/cgroup/v1")
        result = cgroup._get_cgroup_data("mock_file", "key1")
        assert result == "value1"

    @patch("os.path.join", return_value="mocked_path")
    @patch("builtins.open", new_callable=mock_open, read_data="key1 value1_1 value1_2\nkey2 value2_1 value_2_2")
    def test_get_cgroup_data_with_index(self, mock_file, mock_path_join):
        cgroup = CGroupV1("/sys/fs/cgroup/v1")
        result = cgroup._get_cgroup_data("mock_file", "key1", 2)
        assert result == "value1_2"

    @patch("os.path.join", return_value="mocked_path")
    @patch("builtins.open", new_callable=mock_open, read_data="key1 value1_1 value1_2\nkey2 value2_1 value_2_2")
    def test_get_cgroup_data_with_keyerror(self, mock_file, mock_path_join):
        cgroup = CGroupV1("/sys/fs/cgroup/v1")
        with pytest.raises(KeyError):
            result = cgroup._get_cgroup_data("mock_file", "key3")

    @patch("os.path.join", return_value="mocked_path")
    @patch("builtins.open", new_callable=mock_open, read_data="1")
    def test_get_cgroup_data_with_keyerror(self, mock_file, mock_path_join):
        cgroup = CGroupV1("/sys/fs/cgroup/v1")
        result = cgroup._get_cgroup_data("mock_file")
        assert result == "1"


class TestCGroupV1:
    def test_cpu_usage(self):
        cgroup = CGroupV1("/sys/fs/cgroup/v1")
        with patch.object(cgroup, "_get_cgroup_data", return_value=100) as mock_method:
            result = cgroup.cpu_usage()
            assert result == 100
            mock_method.assert_called_once_with("cpuacct/cpuacct.usage")

    def test_cpu_system(self):
        cgroup = CGroupV1("/sys/fs/cgroup/v1")
        with patch.object(cgroup, "_get_cgroup_data", return_value=100) as mock_method:
            result = cgroup.cpu_system()
            assert result == 100
            mock_method.assert_called_once_with("cpuacct/cpuacct.stat", "system")

    def test_cpu_user(self):
        cgroup = CGroupV1("/sys/fs/cgroup/v1")
        with patch.object(cgroup, "_get_cgroup_data", return_value=100) as mock_method:
            result = cgroup.cpu_user()
            assert result == 100
            mock_method.assert_called_once_with("cpuacct/cpuacct.stat", "user")

    def test_memory_usage(self):
        cgroup = CGroupV1("/sys/fs/cgroup/v1")
        with patch.object(cgroup, "_get_cgroup_data", return_value=100) as mock_method:
            result = cgroup.memory_usage()
            assert result == 100
            mock_method.assert_called_once_with("memory/memory.usage_in_bytes")

    def test_memory_max(self):
        cgroup = CGroupV1("/sys/fs/cgroup/v1")
        with patch.object(cgroup, "_get_cgroup_data", return_value=100) as mock_method:
            result = cgroup.memory_max()
            assert result == 100 * 100
            mock_method.assert_called_once_with("memory/memory.limit_in_bytes")

    def test_memory_max_no_limited(self):
        cgroup = CGroupV1("/sys/fs/cgroup/v1")
        with patch.object(cgroup, "_get_cgroup_data", return_value="max") as mock_method:
            result = cgroup.memory_max()
            assert result == -1
            mock_method.assert_called_once_with("memory/memory.limit_in_bytes")



class TestCGroupV2:
    def test_cpu_usage(self):
        cgroup = CGroupV2("/sys/fs/cgroup/v2")
        with patch.object(cgroup, "_get_cgroup_data", return_value=100) as mock_method:
            result = cgroup.cpu_usage()
            assert result == 100
            mock_method.assert_called_once_with("cpu.stat", "usage_usec")

    def test_cpu_system(self):
        cgroup = CGroupV2("/sys/fs/cgroup/v2")
        with patch.object(cgroup, "_get_cgroup_data", return_value=100) as mock_method:
            result = cgroup.cpu_system()
            assert result == 100
            mock_method.assert_called_once_with("cpu.stat", "system_usec")

    def test_cpu_user(self):
        cgroup = CGroupV2("/sys/fs/cgroup/v2")
        with patch.object(cgroup, "_get_cgroup_data", return_value=100) as mock_method:
            result = cgroup.cpu_user()
            assert result == 100
            mock_method.assert_called_once_with("cpu.stat", "user_usec")

    def test_memory_usage(self):
        cgroup = CGroupV2("/sys/fs/cgroup/v2")
        with patch.object(cgroup, "_get_cgroup_data", return_value=100) as mock_method:
            result = cgroup.memory_usage()
            assert result == 100
            mock_method.assert_called_once_with("memory.current")

    def test_memory_max(self):
        cgroup = CGroupV2("/sys/fs/cgroup/v2")
        with patch.object(cgroup, "_get_cgroup_data", return_value=0.01) as mock_method:
            result = cgroup.memory_max()
            assert result == 1
            mock_method.assert_called_once_with("memory.max")

    def test_memory_max_no_limited(self):
        cgroup = CGroupV2("/sys/fs/cgroup/v2")
        with patch.object(cgroup, "_get_cgroup_data", return_value="max") as mock_method:
            result = cgroup.memory_max()
            assert result == -1
            mock_method.assert_called_once_with("memory.max")


class TestCGroupMonitor:
    def test_init(self):
        with patch("os.path.exists", return_value=True):
            cgroup = CGroupMonitor()
            assert cgroup._is_v2 is True
            assert cgroup._cgroup == "/sys/fs/cgroup"

    def test_init_with_pid(self):
        with patch("os.path.exists", return_value=False):
            _id = 123
            cgroup = CGroupMonitor(_id)
            assert cgroup._is_v2 is False
            assert cgroup._cgroup == f"/proc/{_id}/cgroup"

    def test_get_cgroup_v1(self):
        with patch("os.path.exists", return_value=False):
            cgroup = CGroupMonitor()
            result = cgroup._get_cgroup()
            assert isinstance(result, CGroupV1)

    def test_get_cgroup_v2(self):
        with patch("os.path.exists", return_value=True):
            cgroup = CGroupMonitor()
            result = cgroup._get_cgroup()
            assert isinstance(result, CGroupV2)

    def test_cpu_usage(self):
        with patch("os.path.exists", return_value=True):
            cgroup = CGroupMonitor()
            with patch.object(cgroup, "_get_cgroup", return_value=MagicMock(cpu_usage=MagicMock(return_value=100))) as mock_method:
                result = cgroup.cpu_usage()
                assert result == 100
                mock_method.assert_called_once()

    def test_cpu_usage_v1(self):
        with patch("os.path.exists", return_value=False):
            cgroup = CGroupMonitor()
            with patch.object(cgroup, "_get_cgroup", return_value=MagicMock(cpu_usage=MagicMock(return_value=100))) as mock_method:
                result = cgroup.cpu_usage()
                assert result == 100
                mock_method.assert_called_once()

    def test_cpu_system(self):
        with patch("os.path.exists", return_value=True):
            cgroup = CGroupMonitor()
            with patch.object(cgroup, "_get_cgroup", return_value=MagicMock(cpu_system=MagicMock(return_value=100))) as mock_method:
                result = cgroup.cpu_system()
                assert result == 100
                mock_method.assert_called_once()

    def test_cpu_system_v1(self):
        with patch("os.path.exists", return_value=False):
            cgroup = CGroupMonitor()
            with patch.object(cgroup, "_get_cgroup", return_value=MagicMock(cpu_system=MagicMock(return_value=100))) as mock_method:
                result = cgroup.cpu_system()
                assert result == 100
                mock_method.assert_called_once()

    def test_cpu_user(self):
        with patch("os.path.exists", return_value=True):
            cgroup = CGroupMonitor()
            with patch.object(cgroup, "_get_cgroup", return_value=MagicMock(cpu_user=MagicMock(return_value=100))) as mock_method:
                result = cgroup.cpu_user()
                assert result == 100
                mock_method.assert_called_once()

    def test_cpu_user_v1(self):
        with patch("os.path.exists", return_value=False):
            cgroup = CGroupMonitor()
            with patch.object(cgroup, "_get_cgroup", return_value=MagicMock(cpu_user=MagicMock(return_value=100))) as mock_method:
                result = cgroup.cpu_user()
                assert result == 100
                mock_method.assert_called_once()

    def test_memory_usage(self):
        with patch("os.path.exists", return_value=True):
            cgroup = CGroupMonitor()
            with patch.object(cgroup, "_get_cgroup", return_value=MagicMock(memory_usage=MagicMock(return_value=100))) as mock_method:
                result = cgroup.memory_usage()
                assert result == 100
                mock_method.assert_called_once()

    def test_memory_usage_v1(self):
        with patch("os.path.exists", return_value=False):
            cgroup = CGroupMonitor()
            with patch.object(cgroup, "_get_cgroup", return_value=MagicMock(memory_usage=MagicMock(return_value=100))) as mock_method:
                result = cgroup.memory_usage()
                assert result == 100
                mock_method.assert_called_once()

    def test_memory_max(self):
        with patch("os.path.exists", return_value=True):
            cgroup = CGroupMonitor()
            with patch.object(cgroup, "_get_cgroup", return_value=MagicMock(memory_max=MagicMock(return_value=100))) as mock_method:
                result = cgroup.memory_max()
                assert result == 100
                mock_method.assert_called_once()

    def test_memory_max_v1(self):
        with patch("os.path.exists", return_value=False):
            cgroup = CGroupMonitor()
            with patch.object(cgroup, "_get_cgroup", return_value=MagicMock(memory_max=MagicMock(return_value=100))) as mock_method:
                result = cgroup.memory_max()
                assert result == 100
                mock_method.assert_called_once()