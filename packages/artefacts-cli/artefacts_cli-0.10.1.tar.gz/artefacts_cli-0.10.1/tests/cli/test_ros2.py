import os
import yaml
from unittest.mock import patch, MagicMock, Mock
import pytest

from artefacts.cli import Job, Run
from artefacts.cli.config import APIConf
from artefacts.cli.parameters import TMP_SCENARIO_PARAMS_YAML
from artefacts.cli.run_launch_test import (
    generate_scenario_parameter_output,
    run_ros2_tests,
    ros2_run_and_save_logs,
)
from artefacts.cli.run_launch_test import (
    LaunchTestFileNotFoundError,
    BadLaunchTestFileError,
)


def test_generate_parameter_output(tmp_path):
    params = {
        "turtle/speed": 5,
        "turtle/color.rgb.r": 255,
        "controller_server/FollowPath.critics": ["RotateToGoal", "Oscillation"],
    }
    file_path = tmp_path / "params.yaml"
    generate_scenario_parameter_output(params, file_path)
    with open(file_path) as f:
        ros2_params = yaml.load(f, Loader=yaml.Loader)
    assert ros2_params == {
        "turtle": {
            "ros__parameters": {
                "speed": 5,
                "color": {"rgb": {"r": 255}},
            }
        },
        "controller_server": {
            "ros__parameters": {
                "FollowPath": {"critics": ["RotateToGoal", "Oscillation"]}
            }
        },
    }


@patch("os.path.exists", return_value=False)
@patch("artefacts.cli.run_launch_test.ros2_run_and_save_logs")
@pytest.mark.ros2
def test_passing_launch_arguments(
    mock_ros2_run_and_save_logs, _mock_exists, valid_project_settings_with_env
):
    job = Job(
        "test_project_id",
        APIConf(valid_project_settings_with_env["full_project_name"], "test_version"),
        "test_jobname",
        {},
        dryrun=True,
    )
    scenario = {
        "name": "test scenario",
        "launch_test_file": "test.launch.py",
        "launch_arguments": {"arg1": "val1", "arg2": "val2"},
    }
    run = Run(job, "scenario name", scenario, 0)

    run_ros2_tests(run)

    mock_ros2_run_and_save_logs.assert_called_once()
    assert (
        " test.launch.py arg1:=val1 arg2:=val2"
        in mock_ros2_run_and_save_logs.call_args[0][0]
    ), (
        "Launch arguments should be passed to the test command after the launch file path"
    )


@pytest.mark.ros2
def test_run_and_save_logs_missing_ros2_launchtest():
    filename = "missing_launchtest.test.py"
    command = [
        "launch_test",
        filename,
    ]
    with pytest.raises(LaunchTestFileNotFoundError):
        ros2_run_and_save_logs(
            " ".join(command),
            shell=True,
            executable="/bin/bash",
            env=os.environ,
            output_path="/tmp/test_log.txt",
        )


@pytest.mark.ros2
def test_run_and_save_logs_bad_ros2_launchtest():
    filename = "bad_launch_test.py"
    command = [
        "launch_test",
        f"tests/fixtures/{filename}",
    ]
    with pytest.raises(BadLaunchTestFileError):
        ros2_run_and_save_logs(
            " ".join(command),
            shell=True,
            executable="/bin/bash",
            env=os.environ,
            output_path="/tmp/test_log.txt",
        )


@patch("artefacts.cli.run_launch_test.glob")
@patch("artefacts.cli.result_utils.glob")
@patch("os.path.isdir", return_value=True)
@patch("artefacts.cli.bagparser.BagFileParser")
@patch("artefacts.cli.run_launch_test.parse_xml_tests_results", return_value=([], True))
@patch("artefacts.cli.run_launch_test.run_and_save_logs", return_value=(0, "", ""))
@pytest.mark.ros2
def test_rosbag_discovered_and_metric_logged(
    mock_run_logs,
    mock_parse,
    mock_bag_parser,
    mock_isdir,
    mock_result_utils_glob,
    mock_ros2_glob,
    valid_project_settings_with_env,
):
    job = Job(
        "test_project_id",
        APIConf(valid_project_settings_with_env["full_project_name"], "test_version"),
        "test_jobname",
        {},
        dryrun=True,
    )
    scenario = {
        "name": "test scenario",
        "launch_test_file": "test_launch.py",
        "metrics": ["topic1"],
    }
    run = Run(job, "scenario name", scenario, 0)

    # Patch the methods to verify
    run.log_artifacts = MagicMock()
    run.log_metric = MagicMock()

    # mock returns
    preexisting_rosbags = [
        "src/my_test_folder/rosbag2_existing",
        "src/venv/some_rosbag_package/rosbag2_existing",
    ]

    mock_ros2_glob.return_value = preexisting_rosbags

    all_rosbags = [
        "src/my_test_folder/rosbag2_existing",
        "src/venv/some_rosbag_package/rosbag2_existing",
        "src/my_test_folder/rosbag2_new",
    ]
    bag_files = ["src/my_test_folder/rosbag2_new/test.mcap"]
    mock_result_utils_glob.side_effect = [all_rosbags, bag_files]

    # BagFileParser mock
    mock_bag = MagicMock()
    mock_bag.get_last_message.return_value = (None, MagicMock(data=42.0))
    mock_bag_parser.return_value = mock_bag

    run_ros2_tests(run)

    # Assert the right new rosbag directory was found
    run.log_artifacts.assert_any_call("src/my_test_folder/rosbag2_new", "rosbag")

    # Assert the right metric was logged
    run.log_metric.assert_called_with("topic1", 42.0)


@patch("artefacts.cli.run_launch_test.ros2_run_and_save_logs")
@patch("artefacts.cli.run_launch_test.parse_xml_tests_results", return_value=([], True))
@patch("os.path.exists", return_value=True)
@patch("shutil.make_archive")
@patch("shutil.rmtree")
@pytest.mark.ros2
def test_ros2_setting_env_vars(
    mock_rmtree, mock_archive, mock_exists, mock_parse, mock_run_save_logs
):
    """
    Test that run_other_tests sets the environment variables correctly.
    """
    # Create a mock Run instance
    mock_run = Mock(spec=Run)

    # Set required attributes
    mock_run.output_path = "/tmp/fake_output_path"
    mock_run.logger = Mock()
    mock_run.params = {
        "ros_testfile": "test_launch_file.py",
        "params": {"turtle/speed": 5},
        "launch_arguments": {"arg1": "val1"},
        "output_dirs": ["/tmp/test_output"],
    }

    # Call the function under test
    run_ros2_tests(mock_run)

    # Verify that artifacts are logged
    mock_run.log_artifacts.assert_any_call(mock_run.output_path)
    mock_run.log_artifacts.assert_any_call("/tmp/test_output")
    mock_run.log_tests_results.assert_called_once()

    # Check that ros2_run_and_save_logs was called with correct env variables
    args, kwargs = mock_run_save_logs.call_args
    passed_env = kwargs.get("env", {})

    # Check ROS2-specific environment variables
    assert "ROS_LOG_DIR" in passed_env
    assert passed_env["ROS_LOG_DIR"] == "/tmp/fake_output_path/ros_logs"

    # Check parameter file environment variable
    assert "ARTEFACTS_SCENARIO_PARAMS_FILE" in passed_env
    assert passed_env["ARTEFACTS_SCENARIO_PARAMS_FILE"] == TMP_SCENARIO_PARAMS_YAML

    # Check upload directory environment variable
    assert "ARTEFACTS_SCENARIO_UPLOAD_DIR" in passed_env
    assert passed_env["ARTEFACTS_SCENARIO_UPLOAD_DIR"] == "/tmp/fake_output_path/user"

    # Verify the command includes launch arguments
    command = args[0]
    assert "test_launch_file.py arg1:=val1" in command
