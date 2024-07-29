import sys

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from stone_lib.resource.monitor.nvml import GPUMetric, nvml, HostGPUs


class TestGPUMetric:

    @patch.object(nvml, "nvmlDeviceGetHandleByIndex")
    def test_init(self, mock_get_handler):
        mock_get_handler.return_value = MagicMock()
        index = 0
        gpu = GPUMetric(index)
        assert gpu.index == index
        assert gpu.handle == mock_get_handler.return_value
        mock_get_handler.assert_called_once_with(index)

    @pytest.fixture(scope="function")
    def mock_handler(self):
        return MagicMock()

    @pytest.fixture(scope="function")
    @patch.object(nvml, "nvmlDeviceGetHandleByIndex")
    def instance(self, mock_get_handler, mock_handler) -> GPUMetric:
        mock_get_handler.return_value = mock_handler
        index = 0
        return GPUMetric(index)

    @patch.object(GPUMetric, "_call_nvml")
    def test_name(self, mock_call_nvml, instance):
        mock_call_nvml.return_value = "mock_name"
        assert instance.name == "mock_name"
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetName")

    @patch.object(GPUMetric, "_call_nvml")
    def test_uuid(self, mock_call_nvml, instance):
        mock_call_nvml.return_value = "mock_uuid"
        assert instance.uuid == "mock_uuid"
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetUUID")

    @patch.object(GPUMetric, "_call_nvml")
    def test_arch_maxwell(self, mock_call_nvml, instance):
        mock_call_nvml.return_value = nvml.NVML_DEVICE_ARCH_MAXWELL
        assert instance.arch == "MAXWELL"
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetArchitecture")

    @patch.object(GPUMetric, "_call_nvml")
    def test_arch_kepler(self, mock_call_nvml, instance):
        mock_call_nvml.return_value = nvml.NVML_DEVICE_ARCH_KEPLER
        assert instance.arch == "KEPLER"
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetArchitecture")

    @patch.object(GPUMetric, "_call_nvml")
    def test_arch_pascal(self, mock_call_nvml, instance):
        mock_call_nvml.return_value = nvml.NVML_DEVICE_ARCH_PASCAL
        assert instance.arch == "PASCAL"
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetArchitecture")

    @patch.object(GPUMetric, "_call_nvml")
    def test_arch_volta(self, mock_call_nvml, instance):
        mock_call_nvml.return_value = nvml.NVML_DEVICE_ARCH_VOLTA
        assert instance.arch == "VOLTA"
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetArchitecture")

    @patch.object(GPUMetric, "_call_nvml")
    def test_arch_turing(self, mock_call_nvml, instance):
        mock_call_nvml.return_value = nvml.NVML_DEVICE_ARCH_TURING
        assert instance.arch == "TURING"
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetArchitecture")

    @patch.object(GPUMetric, "_call_nvml")
    def test_arch_ampere(self, mock_call_nvml, instance):
        mock_call_nvml.return_value = nvml.NVML_DEVICE_ARCH_AMPERE
        assert instance.arch == "AMPERE"
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetArchitecture")

    @patch.object(GPUMetric, "_call_nvml")
    def test_arch_ada(self, mock_call_nvml, instance):
        mock_call_nvml.return_value = nvml.NVML_DEVICE_ARCH_ADA
        assert instance.arch == "ADA"
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetArchitecture")

    @patch.object(GPUMetric, "_call_nvml")
    def test_arch_hopper(self, mock_call_nvml, instance):
        mock_call_nvml.return_value = nvml.NVML_DEVICE_ARCH_HOPPER
        assert instance.arch == "HOPPER"
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetArchitecture")

    @patch.object(nvml, "nvmlDeviceGetComputeRunningProcesses_v3")
    def test_call_nvml(self, mock_get_test_method, instance):
        mock_get_test_method.return_value = "mock_result"
        assert instance._call_nvml("nvmlDeviceGetComputeRunningProcesses_v3") == "mock_result"
        mock_get_test_method.assert_called_once_with(instance.handle)

    @patch.object(nvml, "nvmlDeviceGetComputeRunningProcesses_v3")
    def test_call_nvml_with_agrs(self, mock_get_test_method, instance):
        mock_get_test_method.return_value = "mock_result"
        assert instance._call_nvml("nvmlDeviceGetComputeRunningProcesses_v3", "1", "2") == "mock_result"
        mock_get_test_method.assert_called_once_with(instance.handle, "1", "2")

    @patch.object(nvml, "nvmlDeviceGetComputeRunningProcesses_v3")
    def test_call_nvml_with_kwagrs(self, mock_get_test_method, instance):
        mock_get_test_method.return_value = "mock_result"
        _dict = {
            "mode": 1,
            "test": "test"
        }
        assert instance._call_nvml("nvmlDeviceGetComputeRunningProcesses_v3", **_dict) == "mock_result"
        mock_get_test_method.assert_called_once_with(instance.handle, **_dict)

    @patch.object(nvml, "nvmlDeviceGetComputeRunningProcesses_v3")
    @pytest.mark.skipif(True, reason="NVML raise error all the time, so we can't test it now")
    def test_call_nvml_with_unsupported_error(self, mock_get_test_method, instance):
        nvml.nvmlInit()
        mock_get_test_method.side_effect = nvml.NVMLError(nvml.NVML_ERROR_NOT_SUPPORTED)
        assert instance._call_nvml("nvmlDeviceGetComputeRunningProcesses_v3") is None
        nvml.nvmlShutdown()

    @pytest.mark.skipif(sys.platform == "darwin", reason="Not supported on MacOS")
    def test_call_nvml_with_other_nvml_error(self, instance):
        nvml.nvmlInit()
        with patch.object(nvml, "nvmlDeviceGetFanSpeed", side_effect=KeyError()):
            with pytest.raises(RuntimeError):
                instance._call_nvml("nvmlDeviceGetFanSpeed")
        nvml.nvmlShutdown()

    @patch.object(nvml, "nvmlDeviceGetComputeRunningProcesses_v3")
    def test_call_nvml_with_other_general_error(self, mock_get_test_method, instance):
        mock_get_test_method.side_effect = ValueError()
        with pytest.raises(RuntimeError):
            instance._call_nvml("nvmlDeviceGetComputeRunningProcesses_v3")

    @patch.object(GPUMetric, "_call_nvml")
    def test_get_running_processes(self, mock_call_nvml, instance):
        mock_call_nvml.return_value = "mock_result"
        assert instance.get_running_processes(0) == "mock_result"
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetComputeRunningProcesses_v3")

    @patch.object(GPUMetric, "_call_nvml")
    def test_get_running_processes_with_mode_1(self, mock_call_nvml, instance):
        mock_call_nvml.return_value = "mock_result"
        assert instance.get_running_processes(1) == "mock_result"
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetGraphicsRunningProcesses_v3")

    @patch.object(GPUMetric, "_call_nvml")
    def test_get_running_processes_with_mode_3(self, mock_call_nvml, instance):
        mock_call_nvml.return_value = "mock_result"
        assert instance.get_running_processes(3) == "mock_result"
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetMPSComputeRunningProcesses_v3")

    @patch.object(GPUMetric, "_call_nvml")
    def test_get_running_processes_with_invalid_mode(self, mock_call_nvml, instance):
        with pytest.raises(ValueError):
            instance.get_running_processes(2)

    @patch.object(GPUMetric, "_call_nvml")
    def test_get_clock_info(self, mock_call_nvml, instance):
        mock_call_nvml.return_value = "mock_result"
        assert instance._get_clock_info("test") == "mock_result"
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetClockInfo", "test")

    @patch.object(GPUMetric, "_get_clock_info")
    def test_get_graphics_clock(self, mock_get_clock_info, instance):
        mock_get_clock_info.return_value = "mock_result"
        assert instance.get_graphics_clock() == "mock_result"
        mock_get_clock_info.assert_called_once_with(nvml.NVML_CLOCK_GRAPHICS)

    @patch.object(GPUMetric, "_get_clock_info")
    def test_get_memory_clock(self, mock_get_clock_info, instance):
        mock_get_clock_info.return_value = "mock_result"
        assert instance.get_memory_clock() == "mock_result"
        mock_get_clock_info.assert_called_once_with(nvml.NVML_CLOCK_MEM)

    @patch.object(GPUMetric, "_get_clock_info")
    def test_get_sm_clock(self, mock_get_clock_info, instance):
        mock_get_clock_info.return_value = "mock_result"
        assert instance.get_sm_clock() == "mock_result"
        mock_get_clock_info.assert_called_once_with(nvml.NVML_CLOCK_SM)

    @patch.object(GPUMetric, "_call_nvml")
    def test_get_memory_info(self, mock_call_nvml, instance):
        mock_class = MagicMock()
        mock_class.total = 10
        mock_class.free = 2
        mock_class.used = 3
        mock_call_nvml.return_value = mock_class
        assert instance.get_memory_info() == {
            "total": mock_class.total,
            "free": mock_class.free,
            "used": mock_class.used,
            "utilisation": round((mock_class.used / mock_class.total) * 100, 2)
        }
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetMemoryInfo")

    @patch.object(GPUMetric, "_call_nvml")
    def test_get_temperature(self, mock_call_nvml, instance):
        mock_call_nvml.return_value = "mock_result"
        assert instance.get_temperature() == "mock_result"
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetTemperature", nvml.NVML_TEMPERATURE_GPU)

    @patch.object(GPUMetric, "_call_nvml")
    def test_get_power_usage(self, mock_call_nvml, instance):
        mock_call_nvml.return_value = "mock_result"
        assert instance.get_power_usage() == "mock_result"
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetPowerUsage")

    @patch.object(GPUMetric, "_call_nvml")
    def test_get_power_limit(self, mock_call_nvml, instance):
        mock_call_nvml.return_value = "mock_result"
        assert instance.get_power_limit() == "mock_result"
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetPowerManagementLimit")

    @patch.object(GPUMetric, "_call_nvml")
    def test_get_power_state(self, mock_call_nvml, instance):
        mock_call_nvml.return_value = "mock_result"
        assert instance.get_power_state() == "mock_result"
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetPowerState")

    @patch.object(GPUMetric, "_call_nvml")
    def test_get_fan_speed(self, mock_call_nvml, instance):
        mock_call_nvml.return_value = "mock_result"
        assert instance.get_fan_speed() == "mock_result"
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetFanSpeed")

    @patch.object(GPUMetric, "_call_nvml")
    def test_get_gpu_utilisation(self, mock_call_nvml, instance):
        mock_class = MagicMock()
        mock_class.gpu = 199
        mock_call_nvml.return_value = mock_class
        assert instance.get_gpu_utilisation() == mock_class.gpu
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetUtilizationRates")

    @patch.object(GPUMetric, "_call_nvml")
    def test_get_memory_utilisation(self, mock_call_nvml, instance):
        mock_class = MagicMock
        mock_class.memory = 199
        mock_call_nvml.return_value = mock_class
        assert instance.get_memory_utilisation() == mock_class.memory
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetUtilizationRates")

    @patch.object(GPUMetric, "get_temperature")
    @patch.object(GPUMetric, "get_fan_speed")
    @patch.object(GPUMetric, "get_gpu_utilisation")
    @patch.object(GPUMetric, "get_memory_utilisation")
    def test_get_info(self, mock_get_memory_utilisation, mock_get_gpu_utilisation,
                      mock_get_fan_speed, mock_get_temperature, instance):
        mock_get_memory_utilisation.return_value = "mock_memory_utilisation"
        mock_get_gpu_utilisation.return_value = "mock_gpu_utilisation"
        mock_get_fan_speed.return_value = "mock_fan_speed"
        mock_get_temperature.return_value = "mock_temperature"
        assert instance.get_info() == {
            "temperature": mock_get_temperature.return_value,
            "fan_speed": mock_get_fan_speed.return_value,
            "gpu_utilisation": mock_get_gpu_utilisation.return_value,
            "memory_utilisation": mock_get_memory_utilisation.return_value,
        }
        mock_get_memory_utilisation.assert_called_once()
        mock_get_gpu_utilisation.assert_called_once()
        mock_get_fan_speed.assert_called_once()
        mock_get_temperature.assert_called_once()

    @patch.object(GPUMetric, "get_graphics_clock")
    @patch.object(GPUMetric, "get_memory_clock")
    @patch.object(GPUMetric, "get_sm_clock")
    def test_get_clock_info(self, mock_get_sm_clock, mock_get_memory_clock, mock_get_graphics_clock, instance):
        mock_get_graphics_clock.return_value = "mock_graphics_clock"
        mock_get_memory_clock.return_value = "mock_memory_clock"
        mock_get_sm_clock.return_value = "mock_sm_clock"
        assert instance.get_clock_info() == {
            "graphics_clock": mock_get_graphics_clock.return_value,
            "memory_clock": mock_get_memory_clock.return_value,
            "sm_clock": mock_get_sm_clock.return_value,
        }
        mock_get_graphics_clock.assert_called_once()
        mock_get_memory_clock.assert_called_once()
        mock_get_sm_clock.assert_called_once()

    @patch.object(GPUMetric, "get_power_usage")
    @patch.object(GPUMetric, "get_power_limit")
    @patch.object(GPUMetric, "get_power_state")
    def test_get_power_info(self, mock_get_power_state, mock_get_power_limit, mock_get_power_usage, instance):
        mock_get_power_state.return_value = "mock_power_state"
        mock_get_power_limit.return_value = "mock_power_limit"
        mock_get_power_usage.return_value = "mock_power_usage"
        assert instance.get_power_info() == {
            "usage": mock_get_power_usage.return_value,
            "limit": mock_get_power_limit.return_value,
            "state": mock_get_power_state.return_value,
        }
        mock_get_power_state.assert_called_once()
        mock_get_power_limit.assert_called_once()
        mock_get_power_usage.assert_called_once()

    @patch.object(GPUMetric, "_call_nvml")
    def test_get_pci_info(self, mock_call_nvml, instance):
        mock_class = MagicMock()
        mock_class.busId = "busId"
        mock_class.domain = "domain"
        mock_class.bus = "bus"
        mock_class.device = "device"
        mock_class.pciDeviceId = "pciDeviceId"
        mock_class.pciSubSystemId = "pciSubSystemId"
        mock_class.busIdLegacy = "busIdLegacy"
        mock_call_nvml.return_value = mock_class
        assert instance.get_pci_info() == {
            "bus_id": mock_class.busId,
            "domain": mock_class.domain,
            "bus": mock_class.bus,
            "device": mock_class.device,
            "pci_id": mock_class.pciDeviceId,
            "pci_sub_id": mock_class.pciSubSystemId,
            "bus_id_legacy": mock_class.busIdLegacy,
        }
        mock_call_nvml.assert_called_once_with("nvmlDeviceGetPciInfo")

    @patch.object(GPUMetric, "get_info")
    @patch.object(GPUMetric, "get_pci_info")
    @patch.object(GPUMetric, "get_memory_info")
    @patch.object(GPUMetric, "get_power_info")
    @patch.object(GPUMetric, "get_clock_info")
    @patch.object(GPUMetric, "uuid", new_callable=PropertyMock)
    @patch.object(GPUMetric, "arch", new_callable=PropertyMock)
    @patch.object(GPUMetric, "name", new_callable=PropertyMock)
    def test_to_json(self, mock_name, mock_arch, mock_uuid, mock_get_clock_info, mock_get_power_info,
                     mock_get_memory_info, mock_get_pci_info, mock_get_info, instance):
        mock_get_info.return_value = "mock_get_info"
        mock_get_pci_info.return_value = "mock_get_pci_info"
        mock_get_memory_info.return_value = "mock_get_memory_info"
        mock_get_power_info.return_value = "mock_get_power_info"
        mock_get_clock_info.return_value = "mock_get_clock_info"
        mock_name.return_value = "mock_name"
        mock_arch.return_value = "mock_arch"
        mock_uuid.return_value = "mock_uuid"
        assert instance.to_json() == {
            "name": mock_name.return_value,
            "uuid": mock_uuid.return_value,
            "arch": mock_arch.return_value,
            "info": mock_get_info.return_value,
            "pci_info": mock_get_pci_info.return_value,
            "memory": mock_get_memory_info.return_value,
            "power": mock_get_power_info.return_value,
            "clock": mock_get_clock_info.return_value,
        }
        mock_get_info.assert_called_once()
        mock_get_pci_info.assert_called_once()
        mock_get_memory_info.assert_called_once()
        mock_get_power_info.assert_called_once()
        mock_get_clock_info.assert_called_once()
        mock_name.assert_called_once()
        mock_arch.assert_called_once()
        mock_uuid.assert_called_once()


class TestHostGPUs:
    @patch.object(HostGPUs, "init")
    def test_class_init(self, moke_init):
        instance = HostGPUs()
        moke_init.assert_called_once()
        assert instance._gpus == {}
        assert instance._num_gpus == 0

    @patch.object(nvml, "nvmlDeviceGetCount")
    @patch.object(nvml, "nvmlInit")
    def test_init(self, mock_nvmlInit, mock_nvmlDeviceGetCount):
        num_device = 10
        mock_nvmlDeviceGetCount.return_value = num_device
        mock_instance = []
        for i in range(num_device):
            mock_instance = MagicMock()
            mock_instance.index = i
            mock_instance.append(mock_instance)
        with patch("stone_lib.resource.monitor.nvml.GPUMetric", side_effect=mock_instance) as mock_gpumetric:
            instance = HostGPUs()
            mock_nvmlInit.assert_called_once()
            mock_nvmlDeviceGetCount.assert_called_once()
            assert instance._num_gpus == num_device
            assert len(instance._gpus) == num_device
            mock_gpumetric.call_count == num_device
            for i in range(num_device):
                assert i in instance._gpus

    @patch.object(nvml, "nvmlShutdown")
    @patch.object(HostGPUs, "init")
    def test_shutdown(self, mock_init, mock_nvmlShutdown):
        instance = HostGPUs()
        instance.shutdown()

        mock_nvmlShutdown.assert_called_once()

    @patch.object(HostGPUs, "init")
    def test_to_json(self, mock_init):
        _data = {
            0: MagicMock(to_json=MagicMock(return_value="mock_result_0")),
            1: MagicMock(to_json=MagicMock(return_value="mock_result_1"))
        }
        instance = HostGPUs()
        with patch.object(instance, "_gpus", new_callable=PropertyMock(return_value=_data)) as mock_p_gpus:
            assert instance.to_json() == {
                0: "mock_result_0",
                1: "mock_result_1"
            }
