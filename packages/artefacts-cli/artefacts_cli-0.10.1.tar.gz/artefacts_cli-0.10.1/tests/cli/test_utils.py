import pytest

from datetime import datetime, timedelta
from pathlib import Path
import tempfile

import click

from artefacts.cli.utils import (
    _background_version_check,
    add_output_from_default,
    is_first_run_today,
    new_version_available,
    project_info_from,
    run_and_save_logs,
)


@pytest.fixture
def deactivate_daily_run_check(mocker):
    return mocker.patch("artefacts.cli.utils.is_first_run_today", return_value=True)


@pytest.fixture
def spy_on_version_memo(mocker, deactivate_daily_run_check):
    versions = ["1.2.3", "2.3.4"]

    # PyPi will return a new version
    pypi_index = mocker.Mock()
    pypi_index.status_code = 200
    pypi_index.json.return_value = {"versions": versions}
    mocker.patch("requests.get", return_value=pypi_index)

    # Spy on memo file
    spy = mocker.mock_open()
    mocker.patch("artefacts.cli.utils.open", spy)

    return spy(), versions


def test_adds_nothing_on_missing_default_output(
    artefacts_run, mocker, valid_project_settings
):
    path = mocker.patch("artefacts.cli.utils.ARTEFACTS_DEFAULT_OUTPUT_DIR")
    mocked = {
        "exists.return_value": False,
        "is_dir.return_value": True,
    }
    path.configure_mock(**mocked)
    add_output_from_default(artefacts_run)
    assert len(artefacts_run.uploads) == 0


@pytest.mark.ros2
def test_run_and_save_logs_missing_launch_test_command():
    filename = "launchtest.test.py"
    command = [
        "launch_test",
        filename,
    ]
    # launch_test won't be in the path, and an error will be raised
    with pytest.raises(FileNotFoundError):
        run_and_save_logs(" ".join(command), output_path="/tmp/test_log.txt")


def test_background_version_check_with_new_version(spy_on_version_memo):
    """
    Check that if PyPi reports a new version, the version is written
    in a memo file for later use (later use is to inform the user
    in a next run).
    """
    spy, versions = spy_on_version_memo
    # Claim current version (first argument) is the oldest (index 0)
    result = _background_version_check(versions[0], "memofile")

    assert result is None
    # Check the memo-ed version is the newest (last index)
    spy.write.assert_called_with(versions[-1])


def test_background_version_check_with_no_new_version(spy_on_version_memo):
    """
    Check that if PyPi reports no new version, no memo file is written.
    """
    spy, versions = spy_on_version_memo
    # Claim current version (first argument) is the latest (last index)
    result = _background_version_check(versions[-1], "memofile")

    assert result is None
    spy.write.assert_not_called()


def test_new_version_available_with_new_version_memo(
    mocker, deactivate_daily_run_check
):
    """
    Check a new version detection gets found from memo.
    """
    spy = mocker.mock_open(read_data="2.3.4")
    mocker.patch("artefacts.cli.utils.open", spy)

    unlink_spy = mocker.patch("artefacts.cli.utils.Path.unlink")

    with tempfile.NamedTemporaryFile("r") as memo:
        result = new_version_available("1.2.3", Path(memo.name))

        # Check the fake temp memo file was written with the expected new version
        assert result == "2.3.4"
        spy().read.assert_called()
        unlink_spy.assert_called()


def test_new_version_available_witout_new_version_memo_and_new_version(
    mocker, deactivate_daily_run_check, spy_on_version_memo
):
    """
    Check a new version detection gets found and written to a memo.
    """
    memo_spy, versions = spy_on_version_memo

    # Force detection of no memo
    exists_spy = mocker.patch("artefacts.cli.utils.Path.exists", return_value=False)

    with tempfile.NamedTemporaryFile("w+") as memo:
        result = new_version_available(versions[0], Path(memo.name))

        # Sanity check
        exists_spy.assert_called()

        # Check the fake temp memo file was written with the expected new version
        assert result is None
        memo_spy.write.assert_called_with(versions[-1])


def test_new_version_available_witout_new_version_memo_without_new_version(
    spy_on_version_memo, mocker
):
    """
    Check a new version detection gets found and written to a memo.
    """
    memo_spy, versions = spy_on_version_memo

    # Force detection of no memo
    exists_spy = mocker.patch("artefacts.cli.utils.Path.exists", return_value=False)

    with tempfile.NamedTemporaryFile("w+") as memo:
        result = new_version_available(versions[-1], Path(memo.name))

        # Sanity check
        exists_spy.assert_called()

        # Check the fake temp memo file was not written to.
        assert result is None
        memo_spy.write.assert_not_called()


def test_is_first_run_today_with_empty_marker_file(mocker):
    test_now = datetime(2025, 8, 6, 15, 55)
    replace_spy = mocker.patch("artefacts.cli.utils.Path.replace")
    with tempfile.NamedTemporaryFile("r") as marker_file:
        # Empty marker file: Invalid marker
        assert is_first_run_today(test_now, Path(marker_file.name)) is True
        replace_spy.assert_called_with(
            f"{marker_file.name}.offending.{int(test_now.timestamp())}"
        )


def test_is_first_run_today_with_invalid_marker_file(mocker):
    test_now = datetime(2025, 8, 6, 15, 55)
    replace_spy = mocker.patch("artefacts.cli.utils.Path.replace")
    with tempfile.NamedTemporaryFile("w+") as marker_file:
        with open(marker_file.name, "w") as f:
            f.write("not an integer")
        # Invalid marker file content: Invalid marker
        assert is_first_run_today(test_now, Path(marker_file.name)) is True
        replace_spy.assert_called_with(
            f"{marker_file.name}.offending.{int(test_now.timestamp())}"
        )


def test_is_first_run_today_with_valid_marker_file_same_day(mocker):
    test_now = datetime(2025, 8, 6, 15, 55)
    replace_spy = mocker.patch("artefacts.cli.utils.Path.replace")
    with tempfile.NamedTemporaryFile("w+") as marker_file:
        with open(marker_file.name, "w") as f:
            f.write(str(int((test_now - timedelta(hours=1)).timestamp())))
        assert is_first_run_today(test_now, Path(marker_file.name)) is True

        # Sanity check
        replace_spy.assert_not_called()


def test_is_first_run_today_with_valid_marker_file_next_day(mocker):
    """
    Unlikely scenario, but for sanity: If the marker file is set the next day
    (that would be a manual hack), then we consider a run happened today.

    This may help as an insider trick, and makes for simpler logic.
    """
    test_now = datetime(2025, 8, 6, 15, 55)
    replace_spy = mocker.patch("artefacts.cli.utils.Path.replace")
    with tempfile.NamedTemporaryFile("w+") as marker_file:
        with open(marker_file.name, "w") as f:
            f.write(str(int((test_now + timedelta(days=1)).timestamp())))

        assert is_first_run_today(test_now, Path(marker_file.name)) is False

        # Sanity check
        replace_spy.assert_not_called()


def test_is_first_run_today_with_valid_marker_file_previous_day(mocker):
    """ """
    test_now = datetime(2025, 8, 6, 15, 55)
    replace_spy = mocker.patch("artefacts.cli.utils.Path.replace")
    with tempfile.NamedTemporaryFile("w+") as marker_file:
        with open(marker_file.name, "w") as f:
            f.write(str(int((test_now - timedelta(days=1)).timestamp())))

        assert is_first_run_today(test_now, Path(marker_file.name)) is True

        # Sanity check
        replace_spy.assert_not_called()


def test_is_first_run_today_without_marker_file(mocker):
    test_now = datetime(2025, 8, 6, 15, 55)
    marker_path = Path("marker_test")
    try:
        assert is_first_run_today(test_now, marker_path) is True
        assert marker_path.exists()
        with open(marker_path) as f:
            marker = int(f.read().strip())
            assert marker == int(
                datetime(
                    test_now.year, test_now.month, test_now.day, 23, 59, 59
                ).timestamp()
            )
    finally:
        if marker_path.exists():
            marker_path.unlink()


def test_is_first_run_today_with_errors(mocker):
    test_now = datetime(2025, 8, 6, 15, 55)

    mocker.patch("artefacts.cli.utils.open", side_effect=OSError())
    assert is_first_run_today(test_now) is None

    mocker.patch("artefacts.cli.utils.open", side_effect=IOError())
    assert is_first_run_today(test_now) is None


def test_project_info_from_valid_project_id():
    org, proj = project_info_from("org/project")
    assert org == "org"
    assert proj == "project"


def test_project_info_from_invalid_project_ids():
    # Missing separator
    with pytest.raises(click.ClickException):
        project_info_from("orgproject")

    # None input
    with pytest.raises(click.ClickException):
        project_info_from(None)

    # Empty input
    with pytest.raises(click.ClickException):
        project_info_from("")
