import pytest

from click.exceptions import ClickException
from requests.exceptions import HTTPError, JSONDecodeError

from artefacts.cli.config import APIConf


@pytest.fixture(scope="function")
def httperror_json_settings(mocker):
    """
    Code settings to trigger an HTTPError that returns valid
    JSON error report.
    """
    # Detail we expect to get reported
    detail = {
        "error": {"msg": "blah", "job": 123},
        1: [],
        2: {},
    }
    # Fake response that fits our error scenario
    response = mocker.Mock()
    response.json.return_value = detail
    # Fake HTTPError, for example a possible 500 Internal Server Error
    error = mocker.Mock()
    error.status_code = 500
    error.raise_for_status.side_effect = HTTPError(response=response)

    expected = "Unable to complete the operation: Error interacting with Artefacts.\n"
    "All we know:\n{error}".format(error=detail["error"])

    return error, expected


@pytest.fixture(scope="function")
def httperror_plain_text_settings(mocker):
    """
    Code settings to trigger an HTTPError that returns plain
    text error report.
    """
    # Detail we expect to get reported
    detail = "this is not JSON"
    # Fake response that fits our error scenario
    response = mocker.Mock()
    response.json.side_effect = JSONDecodeError(detail, detail, 0)
    # Fake HTTPError, for example an 500 Internal Server Error
    error = mocker.Mock()
    error.status_code = 500
    error.raise_for_status.side_effect = HTTPError(response=response)

    expected = "Unable to complete the operation: Error interacting with Artefacts.\n"
    "All we know:\n{error}".format(error=detail)

    return error, expected


@pytest.fixture(scope="function")
def httperror_no_error_in_json_settings(mocker):
    """
    Code settings to trigger an HTTPError that returns non-compliant
    JSON error report. Compliance requires JSON with an `error` key.
    """
    # Fake response that fits our error scenario
    response = mocker.Mock()
    response.json.side_effect = KeyError("error")
    # Fake HTTPError, for example an 500 Internal Server Error
    error = mocker.Mock()
    error.status_code = 500
    error.raise_for_status.side_effect = HTTPError(response=response)

    expected = "Unable to complete the operation: Error interacting with Artefacts.\n"
    "All we know:\nNo error detail from Artefacts"

    return error, expected


def test_post_json_error_converted_to_click_error(
    httperror_json_settings, valid_project_settings, test_session
):
    """
    Check that an HTTPError while creating a resource gets JSON detail reported.
    """
    error, expected = httperror_json_settings
    test_session.post.return_value = error
    sut = APIConf(
        valid_project_settings["full_project_name"],
        "test_version",
        session=test_session,
    )
    with pytest.raises(ClickException, match=expected):
        sut.create("url", None)


def test_post_text_error_converted_to_click_error(
    httperror_plain_text_settings, valid_project_settings, test_session
):
    """
    Check that an HTTPError while creating a resource gets any text (non-JSON) reported.
    """
    error, expected = httperror_plain_text_settings
    test_session.post.return_value = error
    sut = APIConf(
        valid_project_settings["full_project_name"],
        "test_version",
        session=test_session,
    )
    with pytest.raises(ClickException, match=expected):
        sut.create("url", None)


def test_post_invalid_json_error_converted_to_click_error(
    httperror_no_error_in_json_settings, valid_project_settings, test_session
):
    """
    Check that an HTTPError without `error` entry in a valid JSON payload is
    reported well.
    """
    error, expected = httperror_no_error_in_json_settings
    test_session.post.return_value = error
    sut = APIConf(
        valid_project_settings["full_project_name"],
        "test_version",
        session=test_session,
    )
    with pytest.raises(ClickException, match=expected):
        sut.create("url", None)


def test_get_json_error_converted_to_click_error(
    httperror_json_settings, valid_project_settings, test_session
):
    """
    Check that an HTTPError while reading a resource gets JSON detail reported.
    """
    error, expected = httperror_json_settings
    test_session.get.return_value = error
    sut = APIConf(
        valid_project_settings["full_project_name"],
        "test_version",
        session=test_session,
    )
    with pytest.raises(ClickException, match=expected):
        sut.read("url", None)


def test_get_text_error_converted_to_click_error(
    httperror_plain_text_settings, valid_project_settings, test_session
):
    """
    Check that an HTTPError while reading a resource gets any text (non-JSON) reported.
    """
    error, expected = httperror_plain_text_settings
    test_session.get.return_value = error
    sut = APIConf(
        valid_project_settings["full_project_name"],
        "test_version",
        session=test_session,
    )
    with pytest.raises(ClickException, match=expected):
        sut.read("url", None)


def test_get_invalid_json_error_converted_to_click_error(
    httperror_no_error_in_json_settings, valid_project_settings, test_session
):
    """
    Check that an HTTPError without `error` entry in a valid JSON payload is
    reported well.
    """
    error, expected = httperror_no_error_in_json_settings
    test_session.get.return_value = error
    sut = APIConf(
        valid_project_settings["full_project_name"],
        "test_version",
        session=test_session,
    )
    with pytest.raises(ClickException, match=expected):
        sut.read("url", None)


def test_put_json_error_converted_to_click_error(
    httperror_json_settings, valid_project_settings, test_session
):
    """
    Check that an HTTPError while updating a resource gets JSON detail reported.
    """
    error, expected = httperror_json_settings
    test_session.put.return_value = error
    sut = APIConf(
        valid_project_settings["full_project_name"],
        "test_version",
        session=test_session,
    )
    with pytest.raises(ClickException, match=expected):
        sut.update("url", "id", None)


def test_put_text_error_converted_to_click_error(
    httperror_plain_text_settings, valid_project_settings, test_session
):
    """
    Check that an HTTPError while updating a resource gets any text (non-JSON) reported.
    """
    error, expected = httperror_plain_text_settings
    test_session.put.return_value = error
    sut = APIConf(
        valid_project_settings["full_project_name"],
        "test_version",
        session=test_session,
    )
    with pytest.raises(ClickException, match=expected):
        sut.update("url", "id", None)


def test_put_invalid_json_error_converted_to_click_error(
    httperror_no_error_in_json_settings, valid_project_settings, test_session
):
    """
    Check that an HTTPError without `error` entry in a valid JSON payload is
    reported well.
    """
    error, expected = httperror_no_error_in_json_settings
    test_session.put.return_value = error
    sut = APIConf(
        valid_project_settings["full_project_name"],
        "test_version",
        session=test_session,
    )
    with pytest.raises(ClickException, match=expected):
        sut.update("url", "id", None)
