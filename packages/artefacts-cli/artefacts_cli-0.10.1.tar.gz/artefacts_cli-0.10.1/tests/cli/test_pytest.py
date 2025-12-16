import tempfile
import os
from pathlib import Path
from unittest.mock import patch

from artefacts.cli.run_pytest import run_pytest_tests, generate_parameter_output
from artefacts.cli.parameters import TMP_SCENARIO_PARAMS_YAML, TMP_SCENARIO_PARAMS_JSON


def test_correct_parameter_generation():
    params = {"gravity": 9.807, "seed": 42, "target": "goal"}

    try:
        generate_parameter_output(params)

        # YAML file created?
        assert os.path.exists(TMP_SCENARIO_PARAMS_YAML)
        with open(TMP_SCENARIO_PARAMS_YAML) as f:
            import yaml

            yaml_params = yaml.load(f, Loader=yaml.Loader)
        assert yaml_params == params

        # JSON file created?
        assert os.path.exists(TMP_SCENARIO_PARAMS_JSON)
        with open(TMP_SCENARIO_PARAMS_JSON) as f:
            import json

            json_params = json.load(f)
        assert json_params == params

    finally:
        for file_path in [TMP_SCENARIO_PARAMS_YAML, TMP_SCENARIO_PARAMS_JSON]:
            if os.path.exists(file_path):
                os.remove(file_path)


@patch("artefacts.cli.run_pytest.run_and_save_logs")
@patch("artefacts.cli.run_pytest.parse_xml_tests_results")
def test_missing_pytest_file(mock_parse_xml, mock_run_save, artefacts_run, mocker):
    artefacts_run.params = {
        "name": "test_scenario",
        "pytest_file": "nonexistent_test_file.py",
    }
    artefacts_run.output_path = "/tmp/test_output"
    artefacts_run.log_tests_results = mocker.Mock()

    results, success = run_pytest_tests(artefacts_run, framework=None)

    assert success is False
    assert len(results) == 1
    assert results[0]["tests"] == 1
    assert results[0]["failures"] == 0
    assert results[0]["errors"] == 1
    assert "pytest_file not found" in results[0]["details"][0]["name"]

    mock_run_save.assert_not_called()
    mock_parse_xml.assert_not_called()
    artefacts_run.log_tests_results.assert_called_once_with(results, success=False)


@patch("artefacts.cli.run_pytest.run_and_save_logs")
@patch("artefacts.cli.run_pytest.parse_xml_tests_results")
@patch("artefacts.cli.run_pytest.check_and_prepare_rosbags_for_upload")
@patch("artefacts.cli.run_pytest.glob")
def test_pytest_with_ros2_checks_rosbags(
    mock_glob, mock_rosbag_check, mock_parse_xml, mock_run_save, artefacts_run, mocker
):
    """A ROS2 test (using pytest) should check for any new rosbags"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_file = os.path.join(tmp_dir, "test_ros2.py")
        with open(test_file, "w") as f:
            f.write("def test_ros2(): assert True")

        rosbag_dir = os.path.join(tmp_dir, "rosbags")
        os.makedirs(rosbag_dir)

        artefacts_run.params = {
            "name": "test_ros2_scenario",
            "pytest_file": test_file,
        }
        artefacts_run.output_path = tmp_dir
        artefacts_run.log_artifacts = mocker.Mock()
        artefacts_run.log_tests_results = mocker.Mock()

        # Mock glob for rosbag detection
        mock_glob.return_value = [rosbag_dir]

        # Mock XML parser (minimal return)
        mock_parse_xml.return_value = ([], True)

        # Test ROS2 framework
        run_pytest_tests(artefacts_run, framework="ros2:humble")

        mock_glob.assert_called_once_with("**/rosbag2*", recursive=True)
        mock_rosbag_check.assert_called_once_with(artefacts_run, [rosbag_dir])


@patch("artefacts.cli.run_pytest.run_and_save_logs")
def test_non_ros_frameworks_with_pytest_skip_rosbag_handling(
    mock_run_save, artefacts_run, mocker
):
    """Non ROS frameworks skip rosbag handling."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_file = os.path.join(tmp_dir, "test_no_ros2.py")
        with open(test_file, "w") as f:
            f.write("def test_no_ros2(): assert True")

        artefacts_run.params = {
            "name": "test_no_ros2_scenario",
            "pytest_file": test_file,
        }
        artefacts_run.output_path = tmp_dir
        artefacts_run.log_artifacts = mocker.Mock()
        artefacts_run.log_tests_results = mocker.Mock()

        with patch("artefacts.cli.run_pytest.parse_xml_tests_results") as mock_parse:
            with patch(
                "artefacts.cli.run_pytest.check_and_prepare_rosbags_for_upload"
            ) as mock_rosbag_check:
                with patch("artefacts.cli.run_pytest.glob") as mock_glob:
                    mock_parse.return_value = ([], True)

                    run_pytest_tests(artefacts_run, framework=None)

                    mock_glob.assert_not_called()
                    mock_rosbag_check.assert_not_called()


def test_run_pytest_integration_test(artefacts_run, mocker):
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_file = "tests/fixtures/sample_pytest_file.py"

        output_dir = os.path.join(tmp_dir, "test_outputs")
        os.makedirs(output_dir)

        artefacts_run.params = {
            "name": "real_integration_scenario",
            "pytest_file": test_file,
            "params": {"gravity": 9.807, "seed": 42},
            "output_dirs": [output_dir],
        }
        artefacts_run.output_path = tmp_dir
        artefacts_run.log_artifacts = mocker.Mock()
        artefacts_run.log_tests_results = mocker.Mock()

        results, success = run_pytest_tests(artefacts_run, framework=None)

        assert success is False
        assert len(results) == 1

        suite = results[0]
        assert suite["suite"] == "pytest"  # pytest uses "pytest" as default suite name
        assert suite["tests"] == 3
        assert suite["failures"] == 1
        assert suite["errors"] == 0

        details = suite["details"]
        assert len(details) == 3

        results_by_name = {detail["name"]: detail for detail in details}
        assert results_by_name["test_basic_math"]["result"] == "success"
        assert results_by_name["test_string_operations"]["result"] == "success"
        assert results_by_name["test_intentional_failure"]["result"] == "failure"

        failure_detail = results_by_name["test_intentional_failure"]
        assert "failure_message" in failure_detail
        assert "2 + 2 should not equal 5" in failure_detail["failure_message"]

        # Junit created in correct dir?
        junit_xml_path = os.path.join(tmp_dir, "tests_junit.xml")
        assert os.path.exists(junit_xml_path)

        user_upload_dir = Path(tmp_dir) / "user"
        assert user_upload_dir.exists()
        assert user_upload_dir.is_dir()

        artefacts_run.log_artifacts.assert_any_call(tmp_dir)  # Main output path
        artefacts_run.log_artifacts.assert_any_call(output_dir)  # Output directory
        artefacts_run.log_tests_results.assert_called_once_with(results, False)
