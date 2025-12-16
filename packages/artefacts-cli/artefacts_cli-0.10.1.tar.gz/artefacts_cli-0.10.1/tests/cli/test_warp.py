import pytest

from datetime import datetime, timezone
from http import HTTPStatus
from uuid import uuid4

import click

import artefacts
from artefacts.cli import (
    generate_scenarios,
    APIConf,
    Job,
)
from artefacts.cli.app import run


def test_generate_scenarios(loaded_valid_conf):
    """
    Ensure scenarios (vague, runs too) get generated as expected when
    the configuration includes parameterised settings.
    """
    jobs = loaded_valid_conf["jobs"]
    scenarios, first = generate_scenarios(jobs["simple_job"])
    assert len(scenarios) == 2
    scenarios, first = generate_scenarios(jobs["tests"])
    assert first == 0
    assert len(scenarios) == 5
    jobs["simple_job"]["scenarios"]["defaults"] = {"params": {}}
    scenarios, first = generate_scenarios(jobs["simple_job"])
    assert len(scenarios) == 2
    scenarios, first = generate_scenarios(jobs["simple_job"], 0)
    assert len(scenarios) == 1
    scenarios, first = generate_scenarios(jobs["simple_job"], 1)
    assert len(scenarios) == 1
    scenarios, first = generate_scenarios(jobs["tests"], 1)
    assert len(scenarios) == 3
    scenarios, first = generate_scenarios(jobs["tests"], 0)
    assert len(scenarios) == 2
    # assert 1 == 2


def test_default_params_only(loaded_valid_conf):
    """
    Testing scenarios inherit default params.
    """
    jobs = loaded_valid_conf["jobs"]
    # testing with just default params
    scenarios, first = generate_scenarios(jobs["default_params_only"])
    assert len(scenarios) == 2
    assert [s["params"] for s in scenarios] == [
        {"seed": 42},
        {"seed": 43},
    ]


def test_settings_params_only(loaded_valid_conf):
    """
    Testing scenarios are well set with their direct params (not inherited
    from defaults).
    """
    jobs = loaded_valid_conf["jobs"]
    # testing with just default params
    scenarios, first = generate_scenarios(jobs["settings_params_only"])
    assert len(scenarios) == 2
    assert [s["params"] for s in scenarios] == [
        {"seed": 42},
        {"seed": 43},
    ]


def test_settings_and_default_params(loaded_valid_conf):
    """
    Testing scenarios are well configured with defaults and own params.
    """
    jobs = loaded_valid_conf["jobs"]
    # testing with both settings and default params
    scenarios, first = generate_scenarios(jobs["settings_and_default_params"])
    assert len(scenarios) == 4
    assert [s["params"] for s in scenarios] == [
        {"gravity": 1.62, "seed": 42},
        {"gravity": 1.62, "seed": 43},
        {"gravity": 0, "seed": 42},
        {"gravity": 0, "seed": 43},
    ]


def test_default_params_overwritten_by_settings(loaded_valid_conf):
    """
    Testing with settings that overwrite default params
    """
    jobs = loaded_valid_conf["jobs"]
    scenarios, first = generate_scenarios(jobs["settings_overwrite_default_params"])
    assert len(scenarios) == 2
    assert [s["params"] for s in scenarios] == [
        {"gravity": 1.62, "seed": 42},
        {"gravity": 0, "seed": 42},
    ]


def test_default_params_overwritten_by_settings2(loaded_valid_conf):
    """
    Testing with settings that overwrite default params on two scenarios
    """
    jobs = loaded_valid_conf["jobs"]
    scenarios, first = generate_scenarios(jobs["settings_overwrite_full"])
    assert len(scenarios) == 5
    assert [s["params"] for s in scenarios] == [
        {"gravity": 9.807, "seed": 42},
        {"gravity": 1.62, "seed": 42},
        {"gravity": 0, "seed": 42},
        {"gravity": 1.62, "seed": 42},
        {"gravity": 0, "seed": 42},
    ]


def test_default_params_overwritten_by_launch_argument(loaded_valid_conf):
    """
    Testing explicit launch arguments override default params.
    """
    jobs = loaded_valid_conf["jobs"]
    scenarios, _ = generate_scenarios(jobs["handles_launch_arguments"])
    assert len(scenarios) == 1
    assert scenarios[0]["launch_arguments"] == {
        "gravity": "9.807",
        "seed": "42",
        "target": "goal",
    }


def test_job_empty_init_dryrun():
    """
    Plain basic test the Job object initialises as expected on dryrun.
    """
    job = Job("org/project", {}, "jobname", {}, dryrun=True)
    assert job.success is False
    assert job.start < datetime.now(timezone.utc).timestamp()


def test_job_empty_init(mocker, valid_project_settings):
    """
    Plain basic test the Job object initialises as expected.
    """
    success = mocker.Mock()
    success.status_code = 200
    success.json.return_value = {"job_id": str(uuid4())}
    api_mock = mocker.patch.object(APIConf, "sdk", return_value=success)
    job = Job(
        valid_project_settings["full_project_name"],
        api_mock,
        "jobname",
        {},
    )
    assert job.success is False
    assert job.start < datetime.now(timezone.utc).timestamp()


def test_job_update(mocker, valid_project_settings):
    """
    Test on the update function of Job objects.
    """
    success = mocker.Mock()
    success.status_code = 200
    api_mock = mocker.patch("artefacts.cli.config.APIConf")
    api_mock.sdk.return_value = success
    job = Job(
        valid_project_settings["full_project_name"],
        api_mock,
        "jobname",
        {},
    )
    assert job.update(True)


def test_job_valid_context(mocker, valid_project_settings):
    """
    Check that a custom context param is processed as expected.

    A job creation currently invokes the API at init time,
    which is supposed to send any optional `context` data.
    """
    now = datetime.now()
    time_mock = mocker.patch("datetime.datetime")
    time_mock.now.return_value = now

    success = mocker.Mock()
    success.status_code = 200
    success.json.return_value = {"job_id": str(uuid4())}
    api_conf = mocker.patch("artefacts.cli.config.APIConf")
    api_conf.sdk.return_value = success

    Job(
        valid_project_settings["full_project_name"],
        api_conf,
        "jobname",
        {},
        context={
            "description": "test",
            "commit": "testcommithash",
            "ref": "testref",
        },
    )

    api_conf.sdk.assert_called_with(
        artefacts.api.api.job.api_project_new_job,
        organization_slug=valid_project_settings["org"],
        project_name=valid_project_settings["project"],
        body=artefacts.api.models.CreateNewJob.from_dict(
            dict(
                project_id=valid_project_settings["full_project_name"],
                start=round(now.timestamp()),
                status="in progress",
                params="{}",
                project=valid_project_settings["full_project_name"],
                jobname="jobname",
                timeout=300,
                n_subjobs=1,
                message="test",
                commit="testcommithash",
                ref="testref",
            )
        ),
    )


def test_job_creation_403(mocker, valid_api_conf):
    """
    Check bad authentication is handled.
    """
    error403 = mocker.Mock()
    error403.status_code = HTTPStatus.FORBIDDEN
    new_job_ep = mocker.patch.object(artefacts.cli, "api_project_new_job")
    new_job_ep.sync_detailed.return_value = error403
    with pytest.raises(click.ClickException, match=str(HTTPStatus.FORBIDDEN.value)):
        Job(
            "org/project",
            valid_api_conf,
            "jobname",
            {},
        )


def test_job_creation_non_403_error(mocker, valid_api_conf):
    """
    Check non-403 errors are handled.
    """
    error401 = mocker.Mock()
    error401.status_code = HTTPStatus.UNAUTHORIZED
    new_job_ep = mocker.patch.object(artefacts.cli, "api_project_new_job")
    new_job_ep.sync_detailed.return_value = error401
    with pytest.raises(click.ClickException, match=str(HTTPStatus.UNAUTHORIZED.value)):
        Job(
            "org/project",
            valid_api_conf,
            "jobname",
            {},
        )


@pytest.mark.ros2
def test_job_update_called_after_every_run(
    cli_runner, authorised_project_with_conf, mocker
):
    """
    Test to confirm Dashboard API is updated after each run in a job
    """
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    api_mock = mocker.patch("artefacts.cli.APIConf")
    api_mock.sdk.return_value = mock_response
    api_run_mock = mocker.patch("artefacts.cli.app.APIConf")
    api_run_mock.sdk.return_value = mock_response

    # Count calls to Job.update
    update_spy = mocker.spy(Job, "update")

    cli_runner.invoke(run, ["tests", "--config", authorised_project_with_conf])

    # We expect 5 runs total accross 2 scenarios:
    # 2 from "basic-tests" and 3 from "param-grid"
    expected_update_calls = 5

    assert update_spy.call_count == expected_update_calls
