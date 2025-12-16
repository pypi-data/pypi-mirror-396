import json
import yaml
import os
from glob import glob
from pathlib import Path

from artefacts.cli import Run

from .utils import run_and_save_logs
from .parameters import TMP_SCENARIO_PARAMS_YAML, TMP_SCENARIO_PARAMS_JSON
from .result_utils import (
    parse_xml_tests_results,
    check_and_prepare_rosbags_for_upload,
    get_TestSuite_error_result,
)


def generate_parameter_output(params: dict):
    """Store `params` in both json and yaml temporary files
    Note: fixed filenames will lead concurent executions to overwrite each other
    """
    with open(TMP_SCENARIO_PARAMS_JSON, "w") as f:
        json.dump(params, f)
    with open(TMP_SCENARIO_PARAMS_YAML, "w") as f:
        yaml.dump(params, f)


def run_pytest_tests(run: Run, framework):
    """Note: parameter names will be set as environment variables
    (must be letters, numbers and underscores), and saved into yaml and json files
    """
    scenario = run.params
    test_file = scenario.get("pytest_file")

    if not os.path.exists(test_file):
        result = get_TestSuite_error_result(
            test_file,
            "pytest_file not found",
            f"pytest file {test_file} not found. Please check the file path.",
        )
        results = [result]
        run.log_tests_results(results, success=False)
        return results, False

    if "params" in scenario:
        generate_parameter_output(scenario["params"])

    full_env = {**os.environ, **scenario.get("params", {})}
    full_env["ARTEFACTS_SCENARIO_PARAMS_FILE"] = TMP_SCENARIO_PARAMS_YAML
    # Create a separate directory for user-uploaded files and set it in the environment
    user_upload_dir = Path(run.output_path) / "user"
    user_upload_dir.mkdir(parents=True, exist_ok=True)
    full_env["ARTEFACTS_SCENARIO_UPLOAD_DIR"] = str(user_upload_dir)

    is_ros2_framework = framework is not None and framework.startswith("ros2:")
    preexisting_rosbags = []
    if is_ros2_framework:
        preexisting_rosbags = [
            path for path in glob("**/rosbag2*", recursive=True) if os.path.isdir(path)
        ]

    test_result_file = f"{run.output_path}/tests_junit.xml"
    command = f"python3 -m pytest {test_file} -s --junit-xml {test_result_file}"
    run_and_save_logs(
        command,
        shell=True,
        env={k: str(v) for k, v in full_env.items()},
        output_path=os.path.join(run.output_path, "test_process_log.txt"),
    )

    results, success = parse_xml_tests_results(test_result_file)

    run.log_artifacts(run.output_path)

    for output in scenario.get("output_dirs", []):
        run.log_artifacts(output)

    if is_ros2_framework:
        check_and_prepare_rosbags_for_upload(run, preexisting_rosbags)

    run.log_tests_results(results, success)
    return results, success
