import os
from junitparser import JUnitXml, Attr, Element
from glob import glob

from artefacts.cli.i18n import localise


class FailureElement(Element):
    _tag = "failure"
    message = Attr()


class ErrorElement(Element):
    _tag = "error"
    message = Attr()


def get_TestSuite_error_result(test_suite_name, name, error_msg):
    return {
        "suite": test_suite_name,
        "errors": 1,
        "failures": 0,
        "tests": 1,
        "details": [
            {
                "name": name,
                "error_message": error_msg,
                "result": "error",
            }
        ],
    }


def parse_xml_tests_results(file):
    def parse_suite(suite):
        nonlocal success, results
        suite_results = {
            "suite": suite.name,
            "errors": suite.errors,
            "failures": suite.failures,
            "tests": suite.tests,
        }
        details = []
        for case in suite:
            case_details = {
                "name": case.name,
            }

            test_result_found = False

            # We look for failures or errors first
            for element_class, result_status, message in [
                (FailureElement, "failure", "failure_message"),
                (ErrorElement, "error", "error_message"),
            ]:
                try:
                    element = case.child(element_class)
                    case_details[message] = element.message
                    case_details["result"] = result_status
                    success = False
                    test_result_found = True
                    break
                except AttributeError:
                    pass

            # No Fail or Error = success
            if not test_result_found:
                case_details["result"] = "success"

            details.append(case_details)

        suite_results["details"] = details
        results.append(suite_results)

    try:
        xml = JUnitXml.fromfile(file)

        results = []
        success = True
        # some xml files do not have the <testsuites> tag, just a single <tessuite>
        if xml._tag == "testsuite":
            # handle single suite
            suite = xml
            parse_suite(suite)
        elif xml._tag == "testsuites":
            # handle suites
            for suite in xml:
                parse_suite(suite)
        # else: TODO
        return results, success

    except Exception as e:
        print(
            localise(
                "[Exception in parse_xml_tests_results] {message}".format(message=e)
            )
        )
        print(localise("Test result xml could not be loaded, marking success as False"))
        result = get_TestSuite_error_result(
            "unittest.suite.TestSuite",
            "Error parsing XML test results",
            f"The test may have timed out. Exception: {e}",
        )
        return [result], None


def check_and_prepare_rosbags_for_upload(run, preexisting_rosbags):
    # Checks for a new rosbag after test completions. We look for the directory
    # as drilling down will find both the directory as well as the rosbag itself.
    rosbags = [
        path for path in glob("**/rosbag2*", recursive=True) if os.path.isdir(path)
    ]
    new_rosbags = set(rosbags).difference(set(preexisting_rosbags))
    from artefacts.cli.bagparser import BagFileParser

    if len(new_rosbags) > 0:
        run.logger.info(f"Found new rosbags: {new_rosbags}")
        rosbag_dir = new_rosbags.pop()
        run.log_artifacts(rosbag_dir, "rosbag")
        if "metrics" in run.params:
            # Search for database files in the directory
            # TODO: should go inside BagFileParser?
            db_files = glob(f"{rosbag_dir}/*.mcap")  # Ros2 Default
            if not db_files:
                db_files = glob(f"{rosbag_dir}/*.db3")  # Legacy
            if not db_files:
                raise FileNotFoundError(
                    "No .mcap or .db3 files found in the specified path. Attempted to find in "
                    f"{rosbag_dir}/*.mcap and {rosbag_dir}/*.db3"
                )
            db_file = db_files[0]

            bag = BagFileParser(db_file)
            for metric in run.params["metrics"]:
                try:
                    last_value = bag.get_last_message(metric)[1].data
                    run.log_metric(metric, last_value)
                except KeyError:
                    run.logger.error(f"Metric {metric} not found in rosbag, skipping.")
                except TypeError or IndexError:
                    run.logger.error(
                        f"Metric {metric} not found. Is it being published?. Skipping."
                    )
