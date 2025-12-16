import pytest

from docker.types import DeviceRequest

from artefacts.cli.containers import docker_utils


def test_identity_helper():
    # Simple data type
    assert docker_utils._identity(1) == 1

    # Structured data type
    d = dict()
    result = docker_utils._identity(d)
    assert result == d
    assert id(result) == id(d)

    # Class-y type
    class Klass:
        pass

    obj = Klass()
    result = docker_utils._identity(obj)
    assert result == obj
    assert id(result) == id(obj)


def test_making_all_gpus_device_request():
    assert docker_utils._make_gpu_device_request("all") == [
        DeviceRequest(device_ids=["all"], capabilities=[["gpu"]])
    ]


def test_making_first_gpu_device_request():
    assert docker_utils._make_gpu_device_request("device=0") == [
        DeviceRequest(device_ids=["0"], capabilities=[["gpu"]])
    ]


def test_making_second_gpu_device_request():
    assert docker_utils._make_gpu_device_request("device=1") == [
        DeviceRequest(device_ids=["1"], capabilities=[["gpu"]])
    ]


def test_making_specific_gpu_device_request():
    assert docker_utils._make_gpu_device_request(
        "device=GPU-3a23c669-1f69-c64e-cf85-44e9b07e7a2a"
    ) == [
        DeviceRequest(
            device_ids=["GPU-3a23c669-1f69-c64e-cf85-44e9b07e7a2a"],
            capabilities=[["gpu"]],
        )
    ]


def test_making_gpu_list_device_request():
    assert docker_utils._make_gpu_device_request('"device=1,0"') == [
        DeviceRequest(device_ids=["0", "1"], capabilities=[["gpu"]])
    ]


def test_invalid_docker_gpu_in_making_device_request():
    with pytest.raises(Exception, match="Invalid GPU device for Docker: 0"):
        docker_utils._make_gpu_device_request("0")


def test_missing_quotes_in_making_device_request_from_list():
    with pytest.raises(Exception):
        docker_utils._make_gpu_device_request("device=1,2,3")
    with pytest.raises(Exception):
        docker_utils._make_gpu_device_request('device=1,2,3"')


def test_wrongly_quoted_in_making_device_request_from_list():
    with pytest.raises(Exception):
        docker_utils._make_gpu_device_request('""device=1,2,3""')
    with pytest.raises(Exception):
        docker_utils._make_gpu_device_request('"device=1,2,3""')


def test_cli2sdk_network_mode():
    result_sdk_host_config = {}
    result_sdk_container_config = {}
    docker_utils.cli2sdk(
        result_sdk_host_config, result_sdk_container_config, "net", "host"
    )
    assert result_sdk_host_config["network_mode"] == "host"
    assert len(result_sdk_container_config) == 0


def test_cli2sdk_gpus():
    result_sdk_container_config = {}

    # All GPUs
    result_sdk_host_config = {}
    docker_utils.cli2sdk(
        result_sdk_host_config, result_sdk_container_config, "gpus", "all"
    )
    assert result_sdk_host_config["device_requests"] == [
        DeviceRequest(device_ids=["all"], capabilities=[["gpu"]])
    ]
    assert len(result_sdk_container_config) == 0

    # Specific GPU
    result_sdk_host_config = {}
    docker_utils.cli2sdk(
        result_sdk_host_config, result_sdk_container_config, "gpus", "device=test"
    )
    assert result_sdk_host_config["device_requests"] == [
        DeviceRequest(device_ids=["test"], capabilities=[["gpu"]])
    ]
    assert len(result_sdk_container_config) == 0

    # GPU list
    result_sdk_host_config = {}
    docker_utils.cli2sdk(
        result_sdk_host_config,
        result_sdk_container_config,
        "gpus",
        '"device=test,test2,test3"',
    )
    assert result_sdk_host_config["device_requests"] == [
        DeviceRequest(device_ids=["test", "test2", "test3"], capabilities=[["gpu"]])
    ]
    assert len(result_sdk_container_config) == 0


def test_cli2sdk_tshort_flag():
    result_sdk_host_config = {}
    result_sdk_container_config = {}
    docker_utils.cli2sdk(result_sdk_host_config, result_sdk_container_config, "t", True)
    assert result_sdk_container_config["tty"] is True
    assert len(result_sdk_host_config) == 0


def test_cli2sdk_tplain_flag():
    result_sdk_host_config = {}
    result_sdk_container_config = {}
    docker_utils.cli2sdk(
        result_sdk_host_config, result_sdk_container_config, "tty", True
    )
    assert result_sdk_container_config["tty"] is True
    assert len(result_sdk_host_config) == 0


def test_cli2sdk_ishort_flag():
    result_sdk_host_config = {}
    result_sdk_container_config = {}
    docker_utils.cli2sdk(result_sdk_host_config, result_sdk_container_config, "i", True)
    assert result_sdk_container_config["stdin_open"] is True
    assert len(result_sdk_host_config) == 0


def test_cli2sdk_iplain_flag():
    result_sdk_host_config = {}
    result_sdk_container_config = {}
    docker_utils.cli2sdk(
        result_sdk_host_config, result_sdk_container_config, "interactive", True
    )
    assert result_sdk_container_config["stdin_open"] is True
    assert len(result_sdk_host_config) == 0
