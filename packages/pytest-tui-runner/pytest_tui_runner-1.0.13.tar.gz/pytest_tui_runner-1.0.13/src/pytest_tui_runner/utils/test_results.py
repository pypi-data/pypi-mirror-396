from dataclasses import dataclass

from pytest_tui_runner.logging import logger

IGNORED_MARKERS = {"skip", "xfail"}


@dataclass
class TestResult:
    """Represents the result of a test with its markers and outcome."""

    markers: list[str]
    outcome: str
    args: dict[str, str] | None = None
    test_name: str | None = None


def extract_tests_results(report: dict) -> list[TestResult]:
    """Extract test results and their markers from a pytest JSON report."""
    tests_results: list[TestResult] = []

    tests = report.get("tests", [])
    for test in tests:
        logger.debug(f"▶️ PROCESSING test result = {test} ...")
        test_result = test.get("outcome", "")
        keywords = test.get("keywords", [])

        if not keywords:
            logger.error("Test has no keywords.")
            continue
        test_name = keywords[0]

        logger.debug(f"Keywords: {keywords}")
        logger.debug(f"Test name: '{test_name}'")
        logger.debug(f"Test result: '{test_result}'")

        # Extract test marks
        marks = []
        for kw in keywords[1:]:
            if kw == "pytestmark":
                break
            if kw in IGNORED_MARKERS:
                continue
            marks.append(kw)

        logger.debug(f"Extracted marks: {marks}")

        # Check if test (first keyword) is test with arguments (has format test_name[args])
        if "[" in test_name and test_name.endswith("]"):
            name_without_args, test_args = test_name.split("[", 1)
            test_args = test_args[:-1]  # Remove the closing ']'

            logger.debug(f"Test WITH arguments saved: '{name_without_args}'")
            tests_results.append(
                TestResult(
                    test_name=name_without_args,
                    markers=marks,
                    outcome=test_result,
                    args=test_args,
                ),
            )
        else:
            logger.debug(f"Test WITHOUT arguments saved: '{test_name}'")
            tests_results.append(
                TestResult(test_name=test_name, markers=marks, outcome=test_result),
            )
        logger.debug("✅ Test result processed")

    if not tests_results:
        logger.debug("WARNING: No test results found in the report.")

    logger.debug(f"ALL Test results extracted: {tests_results}")

    return tests_results
