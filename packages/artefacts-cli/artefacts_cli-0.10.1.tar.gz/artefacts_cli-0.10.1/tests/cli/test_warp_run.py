import pytest

from http import HTTPStatus
import json

from click.exceptions import ClickException
from requests import Response

import artefacts
from artefacts.cli import Run


def test_run_with_upload_on_stop(mocker, artefacts_run):
    """
    Check that `uploads` list is registered to the API when stopping a run.
    """
    _success = mocker.Mock()
    _success.status_code = 200
    spy = mocker.patch.object(artefacts_run.job.api_conf, "sdk", return_value=_success)
    artefacts_run.job.dryrun = False

    artefacts_run.stop()

    assert spy.call_args.kwargs["body"].uploads


def test_run_without_upload_on_stop(mocker, artefacts_run):
    """
    Check that `uploads` list is not registered to the API when stopping a run
    for a job that specifies the `noupload` option.

    This is required by the API protocol.
    """
    _success = mocker.Mock()
    _success.status_code = 200
    spy = mocker.patch.object(artefacts_run.job.api_conf, "sdk", return_value=_success)
    artefacts_run.job.dryrun = False

    artefacts_run.job.noupload = True
    artefacts_run.stop()

    assert spy.call_args.kwargs["body"].uploads.to_dict() == {}


def test_run_uses_scenario_name(mocker, artefacts_job):
    """
    The API protocol stipulates run creation now needs to specify a scenario
    name, passed as a `scenario_name` entry in the payload.
    """
    expected_name = "scenario test"

    _success = Response()
    _success.status_code = 200
    spy = mocker.patch.object(artefacts_job.api_conf, "sdk", return_value=_success)
    artefacts_job.dryrun = False
    Run(job=artefacts_job, name=expected_name, params={}, run_n=0)

    assert expected_name == spy.call_args.kwargs["body"].scenario_name


def test_run_uses_common_scenario_name_for_all_parameterised_runs(
    mocker, artefacts_job
):
    """
    The code currently overwrites scenario parameters, notably their names, to guarantee unique names (1 scenario <=> 1 run). This happens only on run-remote at this time (see artefacts/cli/app.py around line 555).

    This test reproduces the conditions executed when run-remote changes the scenario name in the parameters. It checks that the params are as expected (unique names) yet the run object uses a common scenario name.
    """
    expected_name = "scenario test"

    _success = mocker.Mock()
    _success.status_code = 200
    spy = mocker.patch.object(artefacts_job.api_conf, "sdk", return_value=_success)
    artefacts_job.dryrun = False

    # The check must be on at least 2 run objects to ensure the common name.
    for idx in range(2):
        Run(
            job=artefacts_job,
            name=expected_name,
            params={"name": f"{expected_name}-{idx}"},
            run_n=idx,
        )
        assert expected_name == spy.call_args.kwargs["body"].scenario_name


def test_run_uses_scenario_name_on_stop(mocker, artefacts_run):
    """
    The API protocol stipulates run stop now needs to specify a scenario name,
    passed as a `scenario_name` entry in the payload.
    """
    expected_name = "scenario test"

    _success = mocker.Mock()
    _success.status_code = 200
    spy = mocker.patch.object(artefacts_run.job.api_conf, "sdk", return_value=_success)
    artefacts_run.job.dryrun = False
    artefacts_run.job.noupload = True
    artefacts_run.scenario_name = expected_name

    artefacts_run.stop()

    assert expected_name == spy.call_args.kwargs["body"].scenario_name


def test_run_uses_scenario_name_on_stop_for_all_parameterised_runs(
    mocker, artefacts_job
):
    """
    This test reproduces the conditions executed when run-remote changes the scenario name in the parameters, on run creation (see test `test_run_uses_common_scenario_name_for_all_parameterised_runs`) and on run stop as addressed here.

    The checks that the stop params are as expected (unique names) yet the run object uses a common scenario name.
    """
    expected_name = "scenario test"

    artefacts_job.noupload = True
    artefacts_job.dryrun = False

    _success = Response()
    _success.status_code = 200
    spy = mocker.patch.object(artefacts_job.api_conf, "sdk", return_value=_success)

    # The check must be on at least 2 run objects to ensure the common name.
    for idx in range(2):
        run = Run(
            job=artefacts_job,
            name=expected_name,
            params={"name": f"{expected_name}-{idx}"},
            run_n=idx,
        )
        run.stop()
        assert expected_name == spy.call_args.kwargs["body"].scenario_name


def test_run_creation_403(mocker, artefacts_job):
    """
    Check bad authentication is handled.
    """
    artefacts_job.dryrun = False
    error403 = mocker.Mock()
    error403.status_code = HTTPStatus.FORBIDDEN
    new_run_ep = mocker.patch.object(artefacts.cli, "create_job_run")
    new_run_ep.sync_detailed.return_value = error403

    with pytest.raises(ClickException, match=str(HTTPStatus.FORBIDDEN.value)):
        Run(job=artefacts_job, name="run", params={}, run_n=1)


def test_run_creation_non_403_error(mocker, artefacts_job):
    """
    Check non-403 errors are handled.
    """
    artefacts_job.dryrun = False
    error401 = mocker.Mock()
    error401.status_code = HTTPStatus.UNAUTHORIZED
    new_run_ep = mocker.patch.object(artefacts.cli, "create_job_run")
    new_run_ep.sync_detailed.return_value = error401

    with pytest.raises(ClickException, match=str(HTTPStatus.UNAUTHORIZED.value)):
        Run(job=artefacts_job, name="run", params={}, run_n=1)


def test_run_error_with_none_test_results(mocker, artefacts_run):
    """
    Confirm error behaviour when runs are stopped with invalid (None) `test_results`.
    """
    artefacts_run.job.dryrun = False
    artefacts_run.test_results = None
    with pytest.raises(
        ClickException,
        match=f"Test results are not available yet for job run #{artefacts_run.run_n}. The run will be empty.",
    ):
        artefacts_run.stop()


def test_run_no_error_with_empty_test_results(mocker, artefacts_run):
    """
    Confirm behaviour when runs are stopped with valid empty `test_results`.
    """
    spy = mocker.patch.object(artefacts_run.job.api_conf, "sdk")

    completion_helper = Response()
    completion_helper.status_code = 200
    completion_helper.raw = json.dumps({"upload_urls": "http://test.com"})
    mocker.patch("requests.post", return_value=completion_helper)

    artefacts_run.job.dryrun = False
    artefacts_run.test_results = []

    # No error raised
    artefacts_run.stop()

    spy.assert_called()
