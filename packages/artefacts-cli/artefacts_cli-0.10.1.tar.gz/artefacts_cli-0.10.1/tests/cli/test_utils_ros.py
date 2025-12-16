from artefacts.cli.result_utils import parse_xml_tests_results


def test_parse_xml_tests_results_handles_full_results():
    """Test that the parser correctly handles real JUnit XML test results."""
    test_file = "tests/fixtures/test_junit.xml"
    results, success = parse_xml_tests_results(test_file)

    assert success is False  # Should be False due to failures and errors
    assert len(results) == 1

    # The suite level lists are integers and determine the summary bar
    # in the dashboard
    suite = results[0]
    assert suite["tests"] == 5
    assert suite["failures"] == 1
    assert suite["errors"] == 3

    details = suite["details"]
    assert len(details) == 5

    # The actual results determine the displayed final state of individual tests
    success_cases = [case for case in details if case["result"] == "success"]
    failure_cases = [case for case in details if case["result"] == "failure"]
    error_cases = [case for case in details if case["result"] == "error"]

    # Verify counts
    assert len(success_cases) == 1
    assert len(failure_cases) == 1
    assert len(error_cases) == 3

    # Correct message type tags
    for case in success_cases:
        assert "failure_message" not in case
        assert "error_message" not in case

    for case in failure_cases:
        assert "failure_message" in case
        assert "error_message" not in case

    for case in error_cases:
        assert "error_message" in case
        assert "failure_message" not in case
