from functools import partial
import signal
import sys

from artefacts.cli import _sigint_handler, init_job


def test_init_job_sets_sigint_handler(valid_project_settings, valid_api_conf):
    """
    Jobs created via `init_job` get a SIGINT handler attached. This test
    checks the attachment is completed.
    """
    job = init_job(
        valid_project_settings["full_project_name"],
        valid_api_conf,
        "jobname",
        {},
        dryrun=True,
    )
    expected_handler = partial(_sigint_handler, job)
    existing_handler = signal.getsignal(signal.SIGINT)
    assert existing_handler.func == expected_handler.func
    assert existing_handler.args == expected_handler.args
    assert existing_handler.keywords == expected_handler.keywords


def test_sigint_handler_harmless(mocker):
    """
    Basic checks that calling the SIGINT handler with typical values
    is harmless (does nothing) by default.
    """
    mocker.patch("sys.exit", return_value=None)
    assert _sigint_handler(None, None, None) is None
    assert _sigint_handler(None, signal.SIG_IGN, None) is None
    assert _sigint_handler(None, None, sys._getframe()) is None
    assert _sigint_handler("not a WarpJob object", None, None) is None


def test_sigint_handler_fails_job(mocker, artefacts_job):
    """
    Check a job is marked as failed when SIGINT
    """
    mocker.patch("sys.exit", return_value=None)
    spy = mocker.spy(artefacts_job, "update")
    _sigint_handler(artefacts_job, None, None)
    spy.assert_called_with(False)
    assert spy.call_count == 1


def test_sigint_handler_stops_run(mocker, artefacts_job, artefacts_run):
    """
    Check a run is stopped when SIGINT
    """
    mocker.patch("sys.exit", return_value=None)
    spy = mocker.spy(artefacts_run, "stop")
    _sigint_handler(artefacts_job, None, None)
    assert spy.call_count == 1
