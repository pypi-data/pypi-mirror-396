import pytest
from _pytest.config.argparsing import Parser
from _pytest.python import Metafunc

from pytest_tui_runner.config import load_config
from pytest_tui_runner.logging import logger, setup_logger
from pytest_tui_runner.paths import Paths
from pytest_tui_runner.utils.config import iter_tests
from pytest_tui_runner.utils.pytest.arguments import flag_to_test_name, format_test_flag
from pytest_tui_runner.utils.pytest.encoding import decode_variants
from pytest_tui_runner.utils.test_results import IGNORED_MARKERS
from pytest_tui_runner.utils.types.config import Test, TestConfig


def pytest_addoption(parser: Parser) -> None:
    """Add custom command-line options to pytest based on the user configuration."""
    # After running the test as a new process, it is necessary to set up the logger again.
    # This is the first function called when the test is run, so it's here
    setup_logger()
    logger.debug("---------------------------- PYTEST HOOKS ----------------------------")
    logger.debug("▶️ ADD OPTIONS hook")

    config: TestConfig = load_config(Paths.config())

    for test in iter_tests(config):
        option_name: str = format_test_flag(test["label"])

        # Special test with arguments
        if "arguments" in test:
            logger.debug(f"Adding option with arguments = '{option_name}'")
            parser.addoption(
                option_name,
                action="store",
                help=f"Run '{test['label']}' test with arguments",
            )
        else:
            logger.debug(f"Adding basic option = '{option_name}'")
            parser.addoption(
                option_name,
                action="store_true",
                default=False,
                help=f"Run '{test['label']}' test",
            )

    logger.debug("✅ ADD OPTIONS hook")
    logger.debug("-------------------------------------------------")


def pytest_generate_tests(metafunc: Metafunc) -> None:
    """Dynamically parametrize tests based on the user configuration and command-line options."""
    test_name = metafunc.function.__name__
    logger.debug(f"▶️ GENERATE TESTS hook for '{(test_name)}' test")

    config_data: TestConfig = load_config(Paths.config())

    for test_def in iter_tests(config_data):
        if "arguments" not in test_def:
            continue

        if not compare_test(metafunc, test_def):
            continue

        logger.debug("❗ FOUND TEST TO PARAMETRIZE")

        parametrize_test(metafunc, test_def)
        return

    logger.debug("❌ TEST NOT PARAMETRIZED")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Modify the collected test items to run only those selected by the user."""
    logger.debug("-------------------------------------------------")
    logger.debug("▶️ COLLECTION MODIFYITEMS hook")
    logger.debug(f"Test count before filtering = {len(items)}")

    config_data: TestConfig = load_config(Paths.config())

    # Go through the options given by pytest so we know which tests to run
    enabled_marker_sets: list = []
    enabled_tests_names: list = []
    used_options = {}

    for test_def in iter_tests(config_data):
        logger.debug(f"Checking test '{test_def['label']}' if it has been selected")

        option_name: str = format_test_flag(test_def["label"])
        opt_value = config.getoption(option_name)
        if opt_value:
            logger.debug(f"Pytest argument found = '{opt_value}'")

            if "markers" in test_def:
                marks = frozenset(test_def["markers"])
                logger.debug(f"Adding marks to the list = {marks}")
                enabled_marker_sets.append(marks)
                used_options[marks] = option_name
            elif "test_name" in test_def:
                enabled_tests_names.append(test_def["test_name"])
                used_options[test_def["test_name"]] = option_name
            else:
                logger.error("Test definition has neither 'markers' nor 'test_name' field")
        else:
            logger.debug("No pytest argument was specified for this test.")
            logger.debug("'Skipping'")

    logger.debug(f"List of wanted marks = {enabled_marker_sets}")
    logger.debug(f"List of wanted tests names = {enabled_tests_names}")

    # Keep only selected tests
    logger.debug("▶️ Filtering tests...")
    filtered_items = []
    for item in items:
        test_name = item.name.split("[")[0]
        item_marks = frozenset(m.name for m in item.iter_markers() if m.name not in IGNORED_MARKERS)

        if item_marks in enabled_marker_sets:
            logger.debug(f"Required marks found ({item_marks}), leaving the test '{test_name}'")
            filtered_items.append(item)
            used_options.pop(item_marks, None)
        elif test_name in enabled_tests_names:
            logger.debug(f"Test name found ({test_name}), leaving the test '{test_name}'")
            filtered_items.append(item)
            used_options.pop(test_name, None)
        else:
            logger.debug("TEST SKIPPED")
            logger.debug(f"Expected marks = {sorted(map(list, enabled_marker_sets))}")
            logger.debug(f"Have = {sorted(item_marks)}")
            logger.debug(f"Expected test name = {enabled_tests_names}")
            logger.debug(f"Have = {test_name}")

    log_unused_options(used_options)

    items[:] = filtered_items
    logger.debug("✅ Tests filtered")

    logger.debug(f"Test count after filtering = {len(items)}")
    logger.debug("✅ COLLECTION MODIFYITEMS hook")

    # This is the last function to run when preparing the test, hence this log
    logger.debug("---------------------------- PYTEST HOOKS ----------------------------")


def compare_test(metafunc: Metafunc, test: Test) -> bool:
    """Compare the given test definition with the current metafunc."""
    if "markers" in test:
        metafunc_markers: set[str] = {
            marker.name
            for marker in metafunc.definition.iter_markers()
            if marker.name not in IGNORED_MARKERS
        }

        test_markers = set(test.get("markers", []))

        if test_markers != metafunc_markers:
            logger.debug(
                f"WRONG 'marks' for test: {test['label']} ({metafunc_markers} != {test_markers})",
            )
            return False

        logger.debug(f"'EXPECTED MARKS FOUND' = {metafunc_markers}")
        return True

    if "test_name" in test:
        metafunc_test_name = metafunc.function.__name__
        test_name = test["test_name"]

        if metafunc_test_name != test_name:
            logger.debug(f"WRONG 'test name' ({metafunc_test_name} != {test_name})")
            return False

        logger.debug(f"'EXPECTED TEST NAME FOUND' = {metafunc_test_name}")
        return True

    logger.error("Test definition has neither 'markers' nor 'test_name' field")
    return False


def parametrize_test(metafunc: Metafunc, test: Test) -> None:
    """Parametrize the given metafunc based on the test definition."""
    option_name = format_test_flag(test["label"])
    option_value = metafunc.config.getoption(option_name)

    if not option_value:
        logger.debug("❌ NO ARGUMENTS PROVIDED")
        return

    variants: list[dict[str, str]] = decode_variants(option_value)
    if not variants:
        logger.error("Argument decoding returned nothing")
        return

    param_names = list(variants[0].keys())
    param_values = [tuple(v[k] for k in param_names) for v in variants]

    logger.debug(f"Parameters names = {param_names}")
    logger.debug(f"Parameters values = {param_values}")

    logger.debug("Executing parametrize function")
    metafunc.parametrize(param_names, param_values)
    logger.debug("✅ TEST SUCCESSFULLY PARAMETRIZED")
    return


def log_unused_options(used_options: dict) -> None:
    """Log any unused options that were specified but did not match any tests."""
    if not used_options:
        logger.debug("All specified options were used.")
        return

    for key, option in used_options.items():
        test_label = flag_to_test_name(option)
        if isinstance(key, frozenset):
            key_str = "[" + ", ".join(sorted(key)) + "]"
            key_type = "Markers"
            after_key = "are"
        else:
            key_str = key
            key_type = "Test_name"
            after_key = "is"
        logger.warning(
            f"No actual test found for test label '{test_label}'. {key_type} '{key_str}' {after_key} probably incorrect.",
        )
