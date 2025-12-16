from artefacts.cli.other import generate_parameter_output, run_other_tests
from artefacts.cli.parameters import TMP_SCENARIO_PARAMS_YAML, TMP_SCENARIO_PARAMS_JSON
import yaml
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock

from artefacts.cli import Run


def test_generate_parameter_output(tmp_path):
    params = {"turtle/speed": 5}
    generate_parameter_output(params)
    file_path = TMP_SCENARIO_PARAMS_YAML
    with open(file_path) as f:
        out_params = yaml.load(f, Loader=yaml.Loader)
    os.remove(file_path)
    assert out_params == params

    generate_parameter_output(params)
    file_path = TMP_SCENARIO_PARAMS_JSON
    with open(file_path) as f:
        ros2_params = json.load(f)
    os.remove(file_path)
    assert ros2_params == params


@patch("artefacts.cli.other.run_and_save_logs")
@patch("pathlib.Path.mkdir")  # Mock directory creation
def test_run_other_tests_sets_env_var(_mock_mkdir, mock_run_save):
    """
    Test that run_other_tests sets the environment variables correctly.
    """
    # Create a mock Run instance
    mock_run = Mock(spec=Run)

    # Set required attributes and methods
    mock_run.output_path = "/tmp/fake_output_path"
    mock_run.params = {
        "run": "echo test",
        "params": {"TEST_PARAM": "value"},
        "output_dirs": ["/tmp/test_output"],
    }
    framework = "other"
    # Call the function under test
    run_other_tests(mock_run, framework)

    # Verify the mock object was used correctly
    mock_run.log_artifacts.assert_any_call(mock_run.output_path)
    mock_run.log_artifacts.assert_any_call("/tmp/test_output")
    mock_run.log_tests_results.assert_called_once()

    # Check that run_and_save_logs was called with correct env variables
    args, kwargs = mock_run_save.call_args
    passed_env = kwargs.get("env", {})
    assert "ARTEFACTS_SCENARIO_PARAMS_FILE" in passed_env
    assert passed_env["ARTEFACTS_SCENARIO_PARAMS_FILE"] == TMP_SCENARIO_PARAMS_YAML
    assert "ARTEFACTS_SCENARIO_UPLOAD_DIR" in passed_env
    assert passed_env["ARTEFACTS_SCENARIO_UPLOAD_DIR"] == "/tmp/fake_output_path/user"
    assert "TEST_PARAM" in passed_env
    assert passed_env["TEST_PARAM"] == "value"


@patch("artefacts.cli.other.run_and_save_logs")
def test_run_other_tests_parses_junit_xml(mock_run_save, artefacts_run: MagicMock):
    """Test that run_other_tests correctly parses JUnit XML if the 'run' command produces one."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Setup mock run object
        artefacts_run.params = {
            "name": "test_scenario",
            "run": "pytest --junit-xml=tests_junit.xml",
        }
        artefacts_run.output_path = tmp_dir
        artefacts_run.log_artifacts = MagicMock()
        artefacts_run.log_tests_results = MagicMock()

        # JUnit XML file
        junit_xml_content = """<?xml version="1.0" encoding="utf-8"?>
<testsuites name="pytest" tests="3" failures="1" errors="1" time="2.345">
    <testsuite name="test_example" tests="3" failures="1" errors="1" time="2.345">
        <testcase classname="test_example" name="test_success" time="0.001"/>
        <testcase classname="test_example" name="test_failure" time="0.002">
            <failure message="AssertionError: 2 != 3">assert 2 == 3</failure>
        </testcase>
        <testcase classname="test_example" name="test_error" time="0.003">
            <error message="ValueError: invalid literal">ValueError: invalid literal for int()</error>
        </testcase>
    </testsuite>
</testsuites>"""

        junit_xml_path = Path(tmp_dir) / "tests_junit.xml"
        junit_xml_path.write_text(junit_xml_content)
        framework = "other"
        results, success = run_other_tests(artefacts_run, framework)

        # Overall assertions
        assert success is False  # Should be False due to failures/errors
        assert len(results) == 1
        assert results[0]["suite"] == "test_example"
        assert results[0]["tests"] == 3
        assert results[0]["failures"] == 1
        assert results[0]["errors"] == 1
        assert len(results[0]["details"]) == 3

        # Individual test assertions
        test_details = results[0]["details"]
        assert test_details[0]["name"] == "test_success"
        assert test_details[0]["result"] == "success"

        assert test_details[1]["name"] == "test_failure"
        assert test_details[1]["result"] == "failure"
        assert "AssertionError: 2 != 3" in test_details[1]["failure_message"]

        assert test_details[2]["name"] == "test_error"
        assert test_details[2]["result"] == "error"
        assert "ValueError: invalid literal" in test_details[2]["error_message"]

        # Assert run_and_save_logs was called
        mock_run_save.assert_called_once()


@patch("artefacts.cli.other.run_and_save_logs")
def test_run_other_tests_no_junit_xml_defaults_success(
    mock_run_save, artefacts_run: MagicMock, mocker
):
    """Test that run_other_tests defaults to success when no JUnit XML file is produced."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Setup mock run object
        artefacts_run.params = {
            "name": "test_scenario",
            "run": "echo 'no xml output'",
        }
        artefacts_run.output_path = tmp_dir
        artefacts_run.log_artifacts = MagicMock()
        artefacts_run.log_tests_results = MagicMock()

        xml_parser_spy = mocker.patch("artefacts.cli.other.parse_xml_tests_results")

        framework = "other"
        results, success = run_other_tests(artefacts_run, framework)

        assert success is True
        assert results == []

        # Assert run_and_save_logs was called
        mock_run_save.assert_called_once()

        # Assert XML parser was not called since no XML file exists
        xml_parser_spy.assert_not_called()
