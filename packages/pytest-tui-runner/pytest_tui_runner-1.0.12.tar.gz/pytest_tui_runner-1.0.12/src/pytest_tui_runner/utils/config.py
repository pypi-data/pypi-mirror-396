from collections.abc import Iterator

from textual.widget import Widget
from textual.widgets import Label

from pytest_tui_runner.config import load_config
from pytest_tui_runner.logging import logger
from pytest_tui_runner.paths import Paths
from pytest_tui_runner.utils.test_results import TestResult
from pytest_tui_runner.utils.types.config import Test, TestConfig
from pytest_tui_runner.utils.types.widgets import TestArguments


def iter_tests(config_data: TestConfig) -> Iterator[Test]:
    """Yield all test definitions from config."""
    for category in config_data.get("categories", []):
        for subcat in category.get("subcategories", []):
            yield from subcat.get("tests", [])


def get_test_result(
    test: Widget | TestArguments,
    test_results: list[TestResult],
) -> TestResult | None:
    """Get the test result corresponding to the given widget or test arguments."""
    config_data: TestConfig = load_config(Paths.config())

    markers = None
    test_name = None
    if isinstance(test, list):
        widgets_sample = test[0]
        label = get_label_of_special_test_widget(widgets_sample)
        logger.debug(f"Label of special test widget: {label}")
        if label is None:
            logger.error("Could not get label of special test widget.")
            return None

        markers, test_name = get_test_markers_and_test_name(label, config_data)
    else:
        markers, test_name = get_test_markers_and_test_name(test.label, config_data)

    if markers is None and test_name is None:
        logger.error("Could not get markers or test name for the given test.")
        return None

    last_result = None
    for result in test_results:
        if not test_result_mach(result, markers, test_name):
            continue

        if result.args and isinstance(test, list):
            args = parse_result_arg_values(result.args)
            if not args_match_widget_values(args, test):
                logger.debug("Found test result, but args values dont match")
                continue

        if result.outcome != "passed":
            return result

        last_result = result

    return last_result


def parse_result_arg_values(args: str) -> list[str]:
    """Parse argument values from test result args string."""
    if not args:
        logger.error("No args to parse.")
        return []

    return [arg.strip() for arg in args.split("-")]


def args_match_widget_values(args: list[str], widgets: list[Widget]) -> bool:
    """Check if argument values match the values of the given widgets."""
    return all(i < len(args) and args[i] == widget.value for i, widget in enumerate(widgets))


def get_test_markers_and_test_name(
    test_label: str,
    config_data: TestConfig,
) -> tuple[list[str] | None, str | None]:
    """Get markers or test name for a given test label from config."""
    logger.debug(f"Getting markers or test name for test label '{test_label}'")
    for test_def in iter_tests(config_data):
        if test_def["label"] == test_label:
            if "markers" in test_def:
                logger.debug(f"MARKERS for widget: {test_def['markers']}")
                logger.debug(f"TEST NAME for widget: {None}")
                return test_def["markers"], None
            if "test_name" in test_def:
                logger.debug(f"MARKERS for widget: {None}")
                logger.debug(f"TEST NAME for widget: {test_def['test_name']}")
                return None, test_def["test_name"]

    logger.error(f"Test '{test_label}' has neither markers nor test name in config.")
    raise ValueError("Test lacks both markers and test name in config.")


def get_label_of_special_test_widget(widget: Widget) -> str | None:
    """Get the label text of a special test widget."""
    logger.debug("Getting label for special test")

    try:
        subcategory_content = widget.parent.parent.parent
    except AttributeError as e:
        logger.error(f"Error accessing parent widgets: {e}")
        return None

    for w in subcategory_content.children:
        if not isinstance(w, Label):
            continue

        # Stav widgetu
        is_mounted = getattr(w, "is_mounted", True)
        is_ready = getattr(w, "is_ready", True)

        if not is_mounted:
            logger.warning(f"Label {w!r} is not yet mounted — text may be unavailable.")
        if not is_ready:
            logger.warning(f"Label {w!r} is not yet ready — text may be unavailable.")

        # Pokus o získání textu z různých zdrojů
        text = getattr(w, "text", None)
        if text is None:
            text = getattr(w, "renderable", None)
        if text is None:
            text = getattr(w, "_text", None)  # fallback pro starší Textual verze

        if not text:
            logger.error(f"Label widget {w!r} has no 'text', 'renderable', or '_text' attribute.")
            continue

        logger.debug(f"Found label text for {widget!r}: {text!r}")
        return str(text)

    # for w in subcategory_content.children:
    #     if isinstance(w, Label):
    #         if not hasattr(w, "renderable"):
    #             logger.error(f"Label widget {w} has no 'renderable' attribute.")
    #             return None

    #         logger.debug(f"Found label widget: {w.renderable}")
    #         return w.renderable

    logger.error(f"Label not found for special test widget {widget}.")
    return None


def test_result_mach(result: TestResult, markers: list[str] | None, test_name: str | None) -> bool:
    """Check if the test result matches the given markers or test name."""
    if markers and frozenset(result.markers) == frozenset(markers):
        logger.debug(f"Found test result based on 'markers' ({markers})")
        return True

    if test_name and result.test_name == test_name:
        logger.debug(f"Found test result based on 'test_name' ({test_name})")
        return True

    return False
