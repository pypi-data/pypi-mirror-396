import pytest

from pathlib import Path
import webbrowser

import json
import yaml

import artefacts
from artefacts.cli.app import (
    hello,
    run,
    run_remote,
    add,
)
from artefacts.cli.config import APIConf


@pytest.fixture(scope="function")
def mask_local_artefacts_yaml(mocker):
    def biased_path(path):
        if path == "artefacts.yaml":
            m = mocker.Mock()
            m.exists.return_value = False
            return m
        else:
            return Path(path)

    return mocker.patch("artefacts.cli.app.Path", side_effect=biased_path)


@pytest.fixture(scope="function")
def expose_local_artefacts_yaml(mocker):
    def biased_path(path):
        if path == "artefacts.yaml":
            m = mocker.Mock()
            m.exists.return_value = True
            return m
        else:
            return Path(path)

    return mocker.patch("artefacts.cli.app.Path", side_effect=biased_path)


def test_hello_with_wrong_project_name(mocker, cli_runner):
    # Hide any local Artefacts configuration file.
    mocker.patch("artefacts.cli.app.read_config_raw", side_effect=FileNotFoundError)
    project_name = "project_without_key"
    result = cli_runner.invoke(hello, [project_name])
    assert result.exit_code == 1
    assert result.output == (
        f"Error: No API KEY set. Please run `artefacts config add {project_name}`\n"
    )


def test_hello_without_project_name_with_artefacts_config(
    mocker, cli_runner, authorised_project_with_conf, valid_project_settings
):
    r = mocker.Mock()
    r.status_code = 200
    r.json.return_value = {"name": "name", "framework": "framework"}
    api_mock = mocker.patch.object(artefacts.cli.app.APIConf, "sdk", return_value=r)
    result = cli_runner.invoke(hello, ["--config", authorised_project_with_conf])
    assert result.exit_code == 0
    api_mock.assert_called_once()
    assert (
        f"Checking for {valid_project_settings['full_project_name']} found in {authorised_project_with_conf}"
        in result.output
    )


def test_hello_without_project_name_without_artefacts_config(cli_runner):
    result = cli_runner.invoke(hello, ["--config", "i/do/not/exist/for/sure"])
    assert result.exit_code == 2
    assert (
        "Missing PROJECT_NAME argument, or project key in an `artefacts.yaml` configuration file (please use --config to choose your configuration file)."
        in result.output
    )


def test_hello_with_project_name_with_artefacts_config(
    mocker, cli_runner, authorised_project_with_conf, valid_project_settings
):
    r = mocker.Mock()
    r.status_code = 200
    r.json.return_value = {"name": "name", "framework": "framework"}
    api_mock = mocker.patch.object(artefacts.cli.app.APIConf, "sdk", return_value=r)

    # Before options
    result = cli_runner.invoke(
        hello,
        [
            valid_project_settings["full_project_name"],
            "--config",
            authorised_project_with_conf,
        ],
    )
    assert result.exit_code == 0
    api_mock.assert_called_once()

    # After options
    result = cli_runner.invoke(
        hello,
        [
            "--config",
            authorised_project_with_conf,
            valid_project_settings["full_project_name"],
        ],
    )
    assert result.exit_code == 0
    assert api_mock.call_count == 2


def test_local_config_plain(
    cli_runner, mocker, api_exists, valid_project_settings, mask_local_artefacts_yaml
):
    # Do not open a browser in test mode.
    mocker.patch("webbrowser.open")
    result = cli_runner.invoke(
        add, [valid_project_settings["full_project_name"]], input="MYAPIKEY\n"
    )
    # Ensure the script has attempted to open the browser as intended
    webbrowser.open.assert_called_once()

    # Check CLI output
    assert result.output == (
        f"Opening the project settings page: https://app.artefacts.com/{valid_project_settings['org']}/{valid_project_settings['project']}/settings\n"
        f"Please enter your API KEY for {valid_project_settings['org']}/{valid_project_settings['project']}: \n"
        f"API KEY saved for {valid_project_settings['org']}/{valid_project_settings['project']}\n"
        "Would you like to download a pregenerated artefacts.yaml file? This will overwrite any existing config file in the current directory. [y/N]: \n"
    )


def test_local_config_with_override_local_artefacts_yaml(
    cli_runner, mocker, api_exists, valid_project_settings, expose_local_artefacts_yaml
):
    """
    Check adding a project while the current directory specifies a different project name
    in artefacts.yaml leads to a confirmation prompt. Accepting to continue resumes
    normal operation.
    """
    # Do not open a browser in test mode.
    mocker.patch("webbrowser.open")

    # Make sure the local artefacts.yaml pretends a different project name than the one passed to CLI
    mocker.patch(
        "artefacts.cli.app.read_config",
        return_value={
            "project": valid_project_settings["full_project_name"] + "something"
        },
    )

    # Accept continuing
    spy = mocker.patch("click.confirm", return_value=True)

    cli_runner.invoke(
        add, [valid_project_settings["full_project_name"]], input="MYAPIKEY\n"
    )

    # Ensure the script has attempted to open the browser as intended
    webbrowser.open.assert_called_once()
    # Ensure confirm happened twice (ignore artefacts.yaml, and accept new artefacts.yaml DL)
    assert spy.call_count == 2


def test_local_config_with_cancel_on_local_artefacts_yaml(
    cli_runner, mocker, api_exists, valid_project_settings, expose_local_artefacts_yaml
):
    """
    Check adding a project while the current directory specifies a different project name
    in artefacts.yaml leads to a confirmation prompt. Declining to continue aborts the
    operation.
    """
    # Detect attempts
    mocker.patch("webbrowser.open")

    # Make sure the local artefacts.yaml pretends a different project name than the one passed to CLI
    mocker.patch(
        "artefacts.cli.app.read_config",
        return_value={
            "project": valid_project_settings["full_project_name"] + "something"
        },
    )

    # Accept continuing
    spy = mocker.patch("click.confirm", return_value=False)

    cli_runner.invoke(
        add, [valid_project_settings["full_project_name"]], input="MYAPIKEY\n"
    )

    # Ensure the script has not attempted to open the browser, as operation cancelled
    webbrowser.open.assert_not_called()
    # Ensure confirm happened only once, leading to cancel the operation
    assert spy.call_count == 1


def test_local_config_download_config(
    cli_runner, mocker, api_exists, valid_project_settings
):
    # Do not open a browser in test mode.
    mocker.patch("webbrowser.open")
    # Accept ignoring the local artefacts.yaml and downloading the generated artefacts.yaml
    mocker.patch("click.confirm", return_value=True)
    # Controlled artefacts.yaml content
    valid_config = {
        "version": "0.1.0",
        "project": valid_project_settings["full_project_name"],
    }

    class ValidResponse:
        def __init__(self):
            self.content = bytes(yaml.dump(valid_config).encode("ascii"))
            self.status_code = 200

    mocker.patch("artefacts.cli.config.APIConf.sdk", return_value=ValidResponse())

    with cli_runner.isolated_filesystem():
        cli_runner.invoke(
            add, [valid_project_settings["full_project_name"]], input="MYAPIKEY\n"
        )
        artefacts_yaml = Path("artefacts.yaml")

        assert artefacts_yaml.exists(), (
            f"expected {artefacts_yaml.absolute()} file is missing"
        )

        # Parse the downloaded file to check basic content
        with open(artefacts_yaml) as f:
            config = yaml.load(f, Loader=yaml.Loader)

        assert config["version"] == valid_config["version"]
        assert config["project"] == valid_config["project"]


def test_local_config_failed_api_access(
    cli_runner, mocker, api_doesnt_exist, valid_project_settings
):
    # Ensure we don't collide with any existing file
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(
            add, [valid_project_settings["full_project_name"]], input="MYAPIKEY\n"
        )

        artefacts_yaml = Path("artefacts.yaml")

        assert not artefacts_yaml.exists(), (
            f"{artefacts_yaml.absolute()} file should not exit"
        )
        assert (
            f"Our apologies: The project page does not seem available at the moment. If `{valid_project_settings['org']}/{valid_project_settings['project']}` is correct, please try again later.\nIf you are using an alternative server, please also consider checking the value of ARTEFACTS_API_URL in your environment."
            in result.output
        )


def test_local_config_failed_download_config(
    cli_runner, mocker, api_exists, valid_project_settings
):
    # Do not open a browser in test mode.
    mocker.patch("webbrowser.open")
    # Accept downloading the generated artefacts.yaml
    mocker.patch("click.confirm", return_value=True)

    response_mock = mocker.Mock()
    response_mock.status_code = 500  # Anything but 200
    api_mock = mocker.patch("artefacts.cli.app.APIConf")
    api_mock.sdk.return_value = response_mock

    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(
            add, [valid_project_settings["full_project_name"]], input="MYAPIKEY\n"
        )

        # artefacts_yaml = Path("artefacts.yaml")

        # assert not artefacts_yaml.exists()
        assert (
            f"We encountered a problem in getting the generated configuration file. Please consider downloading it from the project page on the dashboard at https://app.artefacts.com/{valid_project_settings['org']}/{valid_project_settings['project']}/settings. Sorry for the inconvenience."
            in result.output
        )


def test_config_add_project_name_format(cli_runner):
    project_name = "project-without-org"
    result = cli_runner.invoke(add, [project_name])
    assert result.exit_code == 1
    assert result.output == (
        f'Error: The project field must include the organization name in the format "org/project". Got: "{project_name}"\n'
    )


def test_run(cli_runner):
    result = cli_runner.invoke(run, ["tests", "--config", "myconf.yaml"])
    assert result.exit_code == 1
    assert result.output == ("Error: Project config file myconf.yaml not found.\n")


def test_run_with_conf_invalid_jobname(cli_runner, authorised_project_with_conf):
    job_name = "invalid_job_name"
    result = cli_runner.invoke(
        run, [job_name, "--config", authorised_project_with_conf]
    )
    assert result.exit_code == 1
    assert result.output == (
        f"[{job_name}] Connecting to https://app.artefacts.com/api using ApiKey\n"
        f"[{job_name}] Starting tests\n"
        f"[{job_name}] Error: Job name not defined\n"
        "Aborted!\n"
    )


def test_run_with_conf(cli_runner, authorised_project_with_conf):
    result = cli_runner.invoke(
        run, ["simple_job", "--config", authorised_project_with_conf, "--dryrun"]
    )
    assert result.exit_code == 0
    assert result.output == (
        "[simple_job] Connecting to https://app.artefacts.com/api using ApiKey\n"
        "[simple_job] Starting tests\n"
        "[simple_job] Starting scenario 1/2: basic-tests\n"
        "[simple_job] Performing dry run\n"
        "[simple_job] Starting scenario 2/2: other-tests\n"
        "[simple_job] Performing dry run\n"
        "[simple_job] Done\n"
    )


def test_deprecated_ros_testfile_with_conf(cli_runner, authorised_project_with_conf):
    result = cli_runner.invoke(
        run,
        [
            "deprecated_ros_testfile",
            "--config",
            authorised_project_with_conf,
            "--dryrun",
        ],
    )
    assert result.exit_code == 0
    assert (
        "WARNING: 'ros_testfile' is deprecated and will be removed in a future release. Please use 'launch_test_file' instead."
        in result.output
    )


@pytest.mark.skip(
    reason="Non-ROS unsupported in CoPaVa at this time. Non-ROS like Sapien, etc, become unrunnable then."
)
def test_run_with_mode_other(cli_runner, valid_project_settings):
    result = cli_runner.invoke(
        run,
        [
            "simple_job",
            "--config",
            "tests/fixtures/artefacts-env-param.yaml",
            "--dryrun",
        ],
    )
    assert result.exit_code == 0
    assert result.output == (
        "Connecting to https://app.artefacts.com/api using ApiKey\n"
        f"Starting tests for {valid_project_settings['org']}/{valid_project_settings['project']}\n"
        "Starting scenario 1/2: basic-tests\n"
        "performing dry run\n"
        "Starting scenario 2/2: other-tests\n"
        "performing dry run\n"
        "Done\n"
    )


def test_run_remote(cli_runner):
    result = cli_runner.invoke(run_remote, ["tests", "--config", "conf.yaml"])
    assert result.exit_code == 1
    assert result.output == "Error: Project config file conf.yaml not found.\n"


def test_run_remote_with_conf_invalid_jobname(cli_runner, authorised_project_with_conf):
    result = cli_runner.invoke(
        run_remote, ["invalid_job_name", "--config", authorised_project_with_conf]
    )
    assert result.exit_code == 1
    assert result.output == (
        "Connecting to https://app.artefacts.com/api using ApiKey\n"
        f"Error: Can't find a job named 'invalid_job_name' in config '{authorised_project_with_conf}'\n"
    )


def test_APIConf(valid_project_settings):
    conf = APIConf(valid_project_settings["full_project_name"], "test_version")
    assert conf.headers["Authorization"] == "ApiKey MYAPIKEY"


def test_upload_default_dir(cli_runner, authorised_project_with_conf, mocker):
    # Note the patch applies to the object loaded in app, rather than the original in utils.
    # https://docs.python.org/3/library/unittest.mock.html#where-to-patch
    sut = mocker.patch("artefacts.cli.app.add_output_from_default")
    result = cli_runner.invoke(
        run, ["simple_job", "--config", authorised_project_with_conf, "--dryrun"]
    )
    assert result.exit_code == 0
    # Called twice in this config.
    assert sut.call_count == 2


@pytest.mark.skip(reason="Deprecated")
def test_local_run_git_context_in_repo(
    mocker, cli_runner, authorised_project_with_conf
):
    """
    Check a job gets the current Git context on local run.
    """
    mocker.patch.object(artefacts.cli.app.getpass, "getuser", return_value="test_user")
    mocker.patch.object(artefacts.cli.app.platform, "node", return_value="test_node")
    mocker.patch.object(
        artefacts.cli.app,
        "get_git_revision_branch",
        return_value="test_get_git_revision_branch",
    )
    mocker.patch.object(
        artefacts.cli.app,
        "get_git_revision_hash",
        return_value="test_get_git_revision_hash",
    )

    spy = mocker.patch.object(artefacts.cli.app, "init_job")

    result = cli_runner.invoke(
        run,
        ["simple_job", "--config", authorised_project_with_conf, "--dryrun"],
    )
    assert result.exit_code == 0
    context_arg = spy.call_args.args[8]
    assert context_arg["ref"] == "test_get_git_revision_branch~test_user@test_node"
    assert context_arg["commit"] == "test_get_git_revision_hash"[:8] + "~"


@pytest.mark.skip(reason="Not working: The 'spy' here and in the patched code differ")
def test_remote_run_git_context_in_repo(
    mocker,
    cli_runner,
    authorised_project_with_conf,
):
    """
    Check a job gets the current Git context on remote run.
    """
    mocker.patch.object(
        artefacts.cli.os, "walk", return_value=[(".", [], ["artefacts.yaml"])]
    )
    mocker.patch.object(artefacts.cli.app.getpass, "getuser", return_value="test_user")
    mocker.patch.object(artefacts.cli.app.platform, "node", return_value="test_node")
    mocker.patch.object(
        artefacts.cli.app,
        "get_git_revision_branch",
        return_value="test_get_git_revision_branch",
    )
    mocker.patch.object(
        artefacts.cli.app,
        "get_git_revision_hash",
        return_value="test_get_git_revision_hash",
    )

    direct_success = mocker.Mock()
    direct_success.ok.return_value = True
    direct_success.json.return_value = {
        "upload_urls": {
            "archive.tgz": {"url": "http://url", "fields": []},
            "artefacts.yaml": {"url": "http://url", "fields": []},
            "integration_payload.json": {"url": "http://url", "fields": []},
        }
    }
    upload_success = mocker.Mock()
    upload_success.ok.return_value = True

    methods = {
        "direct.return_value": lambda _: direct_success,
        "upload.return_value": upload_success,
    }
    spy = mocker.Mock(
        api_url="https://test.com",
        **methods,
    )
    mocker.patch(
        "artefacts.cli.app.APIConf",
        new=spy,
    )

    cli_runner.invoke(
        run_remote,
        ["simple_job", "--config", authorised_project_with_conf],
    )
    spy.upload.assert_called()
    relevant_arg = spy.upload.call_args.args[2]
    content = json.loads(relevant_arg["file"])
    assert content["ref"] == "test_get_git_revision_branch~test_user@test_node"
    assert content["after"] == "test_get_git_revision_hash"[:8] + "~"
