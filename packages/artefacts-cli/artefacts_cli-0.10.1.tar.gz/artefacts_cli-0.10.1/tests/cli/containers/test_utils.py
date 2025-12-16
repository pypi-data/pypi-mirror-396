import pytest

from artefacts.cli import errors
from artefacts.cli.containers.utils import ContainerMgr


def test_exit_when_no_container_engine(mocker):
    # Make believe there is no engine
    mocker.patch.object(ContainerMgr, "_configure", lambda _: None)
    with pytest.raises(SystemExit) as e:
        ContainerMgr()
    assert e.type is SystemExit
    assert e.value.code == errors.CONTAINER_ENGINE_NOT_FOUND
