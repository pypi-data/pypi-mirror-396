import pytest

import os
from pathlib import Path
import shutil
from tempfile import NamedTemporaryFile
from uuid import uuid4

from click.testing import CliRunner
import yaml


# Normalise locale to ensure tests match. Locale tests would need to set/reset accordingly
# Note: Needs to be done before package initialisation.
os.environ["LANG"] = "en_US.UTF-8"


from tests.utils import docker_mock

from artefacts.cli import Job
from artefacts.cli.app import add_key_to_conf, delete
from artefacts.cli.config import APIConf
from artefacts.cli.constants import CONFIG_DIR
from artefacts.cli.utils import read_config


class TempConfigMaker(object):
    """
    Facility to make config files from a base, valid config file.

    Notably to make *invalid* config files.

    Usage examples down this file.
    """

    def __init__(self, overrides: dict = {}):
        """
        Valid overrides:
        - key -> value to add or replace
        - key -> None to delete
        """
        base_config = (
            Path(__file__).parent / Path("fixtures") / Path("artefacts.yaml.template")
        )
        with base_config.open() as bc:
            self.config = yaml.load(bc, Loader=yaml.Loader)
        if overrides:
            self.update(overrides)

    def update(self, overrides: dict):
        for key, value in overrides.items():
            if value:
                self.config[key] = value
            else:
                del self.config[key]

    def __enter__(self):
        self.fp = NamedTemporaryFile(mode="w")
        self.fp.write(yaml.dump(self.config))
        self.fp.flush()
        return self.fp.name

    def __exit__(self, *args):
        self.fp.close()


def dockerfile_presence(mocker, value: bool):
    original = os.path.exists

    def exists(path):
        if "dockerfile" in path.lower():
            return value
        else:
            return original(path)

    return mocker.patch("os.path.exists", side_effect=exists, autospec=True)


@pytest.fixture(scope="function")
def dockerfile_available(mocker):
    return dockerfile_presence(mocker, True)


@pytest.fixture(scope="function")
def dockerfile_not_available(mocker):
    return dockerfile_presence(mocker, False)


@pytest.fixture(scope="module")
def docker_mocker(module_mocker):
    test_client = docker_mock.make_fake_api_client()
    module_mocker.patch("docker.APIClient", return_value=test_client)
    yield test_client
    test_client.reset()


@pytest.fixture(scope="module")
def cli_runner():
    """
    Ensure default, normalised environment

    Note: Not using monkeypatch as it is a function fixture.
    """
    userenv = os.environ
    try:
        if os.environ.get("ARTEFACTS_API_URL"):
            del os.environ["ARTEFACTS_API_URL"]
        yield CliRunner()
    finally:
        os.environ = userenv


@pytest.fixture(scope="function")
def org():
    yield str(uuid4())


@pytest.fixture(scope="function")
def valid_project_settings(cli_runner, org):
    try:
        project = str(uuid4())
        full_project_name = f"{org}/{project}"
        key = "MYAPIKEY"
        add_key_to_conf(full_project_name, key)
        yield {
            "org": org,
            "project": project,
            "full_project_name": full_project_name,
            "key": key,
        }
    finally:
        cli_runner.invoke(delete, [full_project_name])
        proj_dir = Path(CONFIG_DIR) / "projects" / org
        if proj_dir.exists():
            shutil.rmtree(proj_dir)


@pytest.fixture(scope="function")
def valid_project_settings_with_env(cli_runner, org):
    try:
        userenv = os.environ
        project = str(uuid4())
        full_project_name = f"{org}/{project}"
        key = "MYAPIKEY"
        os.environ["ARTEFACTS_API_URL"] = key
        add_key_to_conf(full_project_name, key)
        yield {
            "org": org,
            "project": project,
            "full_project_name": full_project_name,
            "key": key,
        }
    finally:
        os.environ = userenv
        cli_runner.invoke(delete, [full_project_name])
        proj_dir = Path(CONFIG_DIR) / "projects" / org
        if proj_dir.exists():
            shutil.rmtree(proj_dir)


@pytest.fixture(scope="function")
def authorised_project_with_conf(valid_project_settings):
    with TempConfigMaker(
        {"project": valid_project_settings["full_project_name"]}
    ) as config_file:
        yield config_file


@pytest.fixture(scope="function")
def authorised_project_with_editable_conf(valid_project_settings):
    return TempConfigMaker({"project": valid_project_settings["full_project_name"]})


@pytest.fixture(scope="function")
def loaded_valid_conf(authorised_project_with_editable_conf):
    return authorised_project_with_editable_conf.config.copy()


@pytest.fixture(scope="session")
def sample_artefacts_config():
    return read_config(os.path.join(os.path.dirname(__file__), "..", "artefacts.yaml"))


@pytest.fixture(scope="function")
def test_session(mocker):
    return mocker.Mock()


@pytest.fixture(scope="function")
def valid_api_conf(valid_project_settings, test_session):
    return APIConf(
        valid_project_settings["full_project_name"],
        "test_version",
        session=test_session,
    )


@pytest.fixture(scope="function")
def artefacts_job(valid_project_settings, valid_api_conf):
    return Job(
        valid_project_settings["full_project_name"],
        valid_api_conf,
        "jobname",
        {},
        dryrun=True,
    )


@pytest.fixture(scope="function")
def artefacts_run(artefacts_job):
    return artefacts_job.new_run({"name": "test scenario"})


@pytest.fixture(scope="function")
def api_exists(mocker):
    """
    Pretend the target Artefacts API exists.
    """
    # Patch the function imported by app, not the original, as already
    #     loaded at the beginning of this conftest. Yeah, I know.
    return mocker.patch("artefacts.cli.app.endpoint_exists", return_value=True)


@pytest.fixture(scope="function")
def api_doesnt_exist(mocker):
    # Patch the function imported by app, not the original, as already
    #     loaded at the beginning of this conftest. Yeah, I know.
    return mocker.patch("artefacts.cli.app.endpoint_exists", return_value=False)
