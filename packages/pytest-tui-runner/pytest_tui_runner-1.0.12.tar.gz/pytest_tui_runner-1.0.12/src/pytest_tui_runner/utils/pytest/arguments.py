import sys

from textual.widget import Widget
from textual.widgets import Checkbox

from pytest_tui_runner.logging import logger
from pytest_tui_runner.paths import Paths
from pytest_tui_runner.utils.pytest.encoding import encode_variants
from pytest_tui_runner.utils.types.widgets import TestArguments, WidgetsDict
from pytest_tui_runner.utils.widgets.marking import mark_widget_running


def build_pytest_arguments(widgets: dict) -> list[str]:
    """Build a list of arguments for running pytest based on provided widgetsand an optional pytest.ini path.

    Parameters
    ----------
    widgets : dict
        Dictionary containing widget objects organized by categories and subcategories.
    pytest_init_path : str, optional
        Path to a custom pytest.ini file (default is "")

    Returns
    -------
    list[str]
        List of command-line arguments for pytest.

    """
    # Default arguments to run pytest
    args: list[str] = [sys.executable, "-m", "pytest"]

    # Add flag to ignore unknows pytest markings in the user project
    args += ["-W", "ignore::pytest.PytestUnknownMarkWarning"]

    # Additional arguments for pytest
    args += ["-s"]  # -s for capturing output
    args += ["-v"]  # -v for verbose output

    # Additional arguments for saving the pytest result to a json file
    args += [
        "--json-report",  # Plugin activation
        f"--json-report-file={Paths.pytest_report()}",  # Path where the results are saved
    ]

    logger.debug(f"Arguments to run pytest = {args}")

    # Add widget-derived arguments
    pytest_arguments = extract_widget_arguments(widgets)
    logger.debug(f"Pytest arguments = {pytest_arguments}")
    args.extend(pytest_arguments)

    logger.info(f"Command to start the tests = {args}")
    return args


def extract_widget_arguments(widgets: WidgetsDict) -> list[str]:
    """Extract pytest CLI arguments from widget states."""
    args: list[str] = []
    for subcats in widgets.values():
        for tests in subcats.values():
            for test_name, widget_list in tests.items():
                # Check if widget_list contains arguments for the test
                if isinstance(widget_list[0], list):
                    arg: str | None = widget_to_argument(test_name, widget_list)
                    if arg:
                        logger.debug(f"Converted special test '{test_name}' to '{arg}'")
                        args.append(arg)
                    else:
                        logger.debug(f"Test '{test_name}' has no set arguments")
                else:
                    for widget in widget_list:
                        arg: str | None = widget_to_argument(test_name, widget)
                        if arg:
                            logger.debug(f"Converted basic test '{test_name}' to '{arg}'")
                            args.append(arg)

                            logger.debug(f"Marking widget as running: {widget}")
                            mark_widget_running(widget)
                        else:
                            logger.debug(f"Test '{test_name}' not selected")
    return args


def widget_to_argument(test_name: str, widgets: Widget | list[TestArguments]) -> str | None:
    """Convert a widget into a pytest CLI argument, if applicable."""
    # Basic Checkbox type test
    if isinstance(widgets, Checkbox) and widgets.value:
        return format_test_flag(str(widgets.label))

    if isinstance(widgets, list) and widgets:
        logger.debug("▶️ Encoding special test...")
        variant_strings: str = encode_variants(test_name, widgets)
        if variant_strings is not None:
            logger.debug("✅ Special test encoded")
            return f"{format_test_flag(test_name)}=" + variant_strings

    return None


def format_test_flag(test_name: str) -> str:
    """Format test name into a pytest CLI flag."""
    # Example: "My Test" → "--run-my-test"
    return f"--run-{test_name.lower().replace(' ', '-')}"


def flag_to_test_name(flag: str) -> str:
    """Convert a pytest CLI flag back to the original test name."""
    # Example: "--run-my-test" → "My Test"
    if flag.startswith("--run-"):
        test_name = flag[len("--run-") :]
        return test_name.replace("-", " ").title()
    return flag
