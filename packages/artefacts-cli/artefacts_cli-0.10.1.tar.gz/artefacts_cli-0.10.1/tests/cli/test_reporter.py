import pytest

from datetime import datetime, timedelta
import errno
import os
from pathlib import Path
import tempfile
from uuid import uuid4

from artefacts.cli.constants import CONFIG_DIR
from artefacts.cli.reporter import _report_dir, fail_safe_report, _cleanup


def test_report_dir_plain():
    assert (
        _report_dir("org/project")
        == Path(CONFIG_DIR) / "projects" / "org" / "project" / "logs"
    )


def test_report_dir_exception_on_bad_project(mocker):
    """
    Checks on typical errors and edge cases
    """
    # Forgot the /
    with pytest.raises(Exception, match="Invalid project name: orgproject"):
        _report_dir("orgproject")

    # Somehow the implicit CONFIG_DIR is invalid (user can override)
    def to_none(path):
        if path == CONFIG_DIR:
            raise TypeError("fake")
        else:
            return Path(path)

    with mocker.patch("artefacts.cli.reporter.Path", side_effect=to_none):
        # Ideally we want to test the value of CONFIG_DIR in the match, but
        # still difficulties with unittest::mock to change a simple constant.
        with pytest.raises(
            Exception,
            match="Invalid value found, either: project=org/project, or .artefacts path=",
        ):
            _report_dir("org/project")


def test_fail_safe_report_is_fail_safe(mocker):
    """
    Reasonable exploration of code paths that can raise and should be passed on.
    """
    spy = mocker.Mock()
    mocker.patch("artefacts.cli.reporter.open", spy)
    for org_proj in ["org/project", "orgproject", None, 123, {}, []]:
        for value in ["", "a", None, {}, []]:
            fail_safe_report(org_proj, value)
    spy.assert_called()


def test_fail_safe_report_plain(mocker):
    """
    Check the reporter attempts to write to the report file.

    We expect at this point a full stack trace and the error message.
    """
    spy = mocker.mock_open()
    mocker.patch("artefacts.cli.reporter.open", spy)

    fail_safe_report("org/project", "fake report")

    handle = spy()
    calls = [
        mocker.call("Stacktrace\n"),
        mocker.call("\n"),
        mocker.call("Message\n"),
        mocker.call("\tfake report\n"),
        mocker.call("\n"),
        mocker.call("Top Error\n"),
        mocker.call("\tNo object\n"),
        mocker.call("\n"),
        mocker.call("Local Error\n"),
        mocker.call("\tNo object\n"),
        mocker.call("\n"),
        mocker.call("Locals\n"),
        mocker.call("\tNo data\n"),
    ]
    handle.write.assert_has_calls(calls, any_order=False)


def test_fail_safe_report_with_top_error(mocker):
    """
    Check the reporter attempts to write to the report file.

    We expect a full stack trace, error message and serialised top error object.

    Top error is understood as the origin of the exception handling procedure.
    """
    spy = mocker.mock_open()
    mocker.patch("artefacts.cli.reporter.open", spy)

    error_object = Exception("me test")
    fail_safe_report("org/project", "fake report", top_error=error_object)

    handle = spy()
    calls = [
        mocker.call("Stacktrace\n"),
        mocker.call("\n"),
        mocker.call("Message\n"),
        mocker.call("\tfake report\n"),
        mocker.call("\n"),
        mocker.call("Top Error\n"),
        mocker.call("\t<class 'Exception'>: me test\n"),
        mocker.call("\n"),
        mocker.call("Local Error\n"),
        mocker.call("\tNo object\n"),
        mocker.call("\n"),
        mocker.call("Locals\n"),
        mocker.call("\tNo data\n"),
    ]
    handle.write.assert_has_calls(calls, any_order=False)


def test_fail_safe_report_with_local_error(mocker):
    """
    Check the reporter attempts to write to the report file.

    We expect a full stack trace, error message and serialised local error object.

    Local error is understood as a consequence or wrapping of a "top error" (when
    available). The top error is the root event of the exception handling procedure.
    """
    spy = mocker.mock_open()
    mocker.patch("artefacts.cli.reporter.open", spy)

    error_object = Exception("me test")
    fail_safe_report("org/project", "fake report", local_error=error_object)

    handle = spy()
    calls = [
        mocker.call("Stacktrace\n"),
        mocker.call("\n"),
        mocker.call("Message\n"),
        mocker.call("\tfake report\n"),
        mocker.call("\n"),
        mocker.call("Top Error\n"),
        mocker.call("\tNo object\n"),
        mocker.call("\n"),
        mocker.call("Local Error\n"),
        mocker.call("\t<class 'Exception'>: me test\n"),
        mocker.call("\n"),
        mocker.call("Locals\n"),
        mocker.call("\tNo data\n"),
    ]
    handle.write.assert_has_calls(calls, any_order=False)


def test_fail_safe_report_with_top_and_localerror(mocker):
    """
    Check the reporter attempts to write to the report file.

    We expect a full stack trace, error message and serialised top and local
    error object.
    """
    spy = mocker.mock_open()
    mocker.patch("artefacts.cli.reporter.open", spy)

    error_object = Exception("me test")
    fail_safe_report(
        "org/project", "fake report", top_error=error_object, local_error=error_object
    )

    handle = spy()
    calls = [
        mocker.call("Stacktrace\n"),
        mocker.call("\n"),
        mocker.call("Message\n"),
        mocker.call("\tfake report\n"),
        mocker.call("\n"),
        mocker.call("Top Error\n"),
        mocker.call("\t<class 'Exception'>: me test\n"),
        mocker.call("\n"),
        mocker.call("Local Error\n"),
        mocker.call("\t<class 'Exception'>: me test\n"),
        mocker.call("\n"),
        mocker.call("Locals\n"),
        mocker.call("\tNo data\n"),
    ]
    handle.write.assert_has_calls(calls, any_order=False)


def test_fail_safe_report_with_locals(mocker):
    """
    Check the reporter attempts to write to the report file.

    We expect a full stack trace, error message and serialised error object.
    """
    spy = mocker.mock_open()
    mocker.patch("artefacts.cli.reporter.open", spy)

    fail_safe_report("org/project", "fake report", locals_dict=locals())

    handle = spy()
    calls = [
        mocker.call("Stacktrace\n"),
        mocker.call("\n"),
        mocker.call("Message\n"),
        mocker.call("\tfake report\n"),
        mocker.call("\n"),
        mocker.call("Top Error\n"),
        mocker.call("\tNo object\n"),
        mocker.call("\n"),
        mocker.call("Local Error\n"),
        mocker.call("\tNo object\n"),
        mocker.call("\n"),
        mocker.call("Locals\n"),
        mocker.call(
            f"\t- {next(iter(locals().keys()))}={next(iter(locals().values()))}\n"
        ),
    ]
    handle.write.assert_has_calls(calls, any_order=False)


def test_fail_safe_report_no_space_on_device(mocker):
    """
    Check the reporter fails safe and logs warning on ENOSPC
    """
    mopen = mocker.mock_open()
    mocker.patch("artefacts.cli.reporter.open", mopen)
    handle = mopen()
    err = OSError()
    err.errno = errno.ENOSPC
    handle.write.side_effect = err

    spy = mocker.patch("artefacts.cli.reporter.logger")
    spy.warning = mocker.Mock()

    fail_safe_report("org/project", "fake report")

    spy.warning.assert_called_with(
        "No space available on device. Detailed error log not storable."
    )


def test_fail_safe_report_silent_generic_oserror(mocker):
    """
    Check the reporter fails safe on generic OSError
    """
    mopen = mocker.mock_open()
    mocker.patch("artefacts.cli.reporter.open", mopen)
    handle = mopen()
    handle.write.side_effect = OSError()

    spy = mocker.patch("artefacts.cli.reporter.logger")
    spy.warning = mocker.Mock()

    fail_safe_report("org/project", "fake report")

    spy.warning.assert_not_called()


def test_internal_log_cleanup_old_files(mocker):
    """
    Check typical log cleanup situation, in an isolated FS environment.

    Target: Cleanup "old files" defined by log_retention_max_days.

    1. Create `created_files` log files in each 2 projects of 2 orgs (4 log dirs).
    2. Apply _cleanup
    3. Count and check the number of remaining files.
    """
    # 0. Preliminary settings: Test invariants
    now = datetime.now()
    orgs = [str(uuid4()) for _ in range(2)]
    projects = {org: [str(uuid4()) for _ in range(2)] for org in orgs}
    created_files = 3
    expected_files_per_project = 1
    assert created_files > expected_files_per_project, "Test requirement unfulfilled"

    # Isolated FS environment
    with tempfile.TemporaryDirectory() as config_dir:
        # 1. Create the scenario files
        for org in orgs:
            for pname in projects[org]:
                logs = Path(config_dir) / "projects" / org / pname / "logs"
                logs.mkdir(parents=True)
                for idx in range(created_files):
                    f = logs / str(uuid4())
                    f.touch()
                    # Set file modification time to past values, -1 day at a time
                    dt = (now - timedelta(days=idx)).timestamp()
                    os.utime(f, (dt, dt))
                assert len(list(os.listdir(logs))) == created_files, (
                    f"Invalid state: Number of files created for the test differs from expected: {len(list(os.listdir(logs)))} != {created_files}"
                )

        # 2. Apply SUT
        _cleanup(
            config_dir,
            log_retention_max_days=expected_files_per_project,
            # Set max files one more than expected to ensure no interaction.
            log_retention_max_files=expected_files_per_project + 1,
        )

        # 3. Check
        for org in orgs:
            for pname in projects[org]:
                logs = Path(config_dir) / "projects" / org / pname / "logs"
                assert len(list(os.listdir(logs))) == expected_files_per_project


def test_internal_log_cleanup_many_files(mocker):
    """
    Check typical log cleanup situation, in an isolated FS environment.

    Target: Cleanup "many files" defined by log_retention_max_files.

    1. Create `created_files` log files in each 2 projects of 2 orgs (4 log dirs).
    2. Apply _cleanup
    3. Count and check the number of remaining files.
    """
    # 0. Preliminary settings: Test invariants
    orgs = [str(uuid4()) for _ in range(2)]
    projects = {org: [str(uuid4()) for _ in range(2)] for org in orgs}
    created_files = 3
    expected_files_per_project = 1
    assert created_files > expected_files_per_project, "Test requirement unfulfilled"

    # Isolated FS environment
    with tempfile.TemporaryDirectory() as config_dir:
        # 1. Create the scenario files
        for org in orgs:
            for pname in projects[org]:
                logs = Path(config_dir) / "projects" / org / pname / "logs"
                logs.mkdir(parents=True)
                for idx in range(created_files):
                    f = logs / str(uuid4())
                    f.touch()
                assert len(list(os.listdir(logs))) == created_files, (
                    f"Invalid state: Number of files created for the test differs from expected: {len(list(os.listdir(logs)))} != {created_files}"
                )

        # 2. Apply SUT
        _cleanup(
            config_dir,
            # Set past date, noting all files here are creating for today
            #     to ensure no interaction with the other condition.
            log_retention_max_days=expected_files_per_project + 1,
            log_retention_max_files=expected_files_per_project,
        )

        # 3. Check
        for org in orgs:
            for pname in projects[org]:
                logs = Path(config_dir) / "projects" / org / pname / "logs"
                assert len(list(os.listdir(logs))) == expected_files_per_project
