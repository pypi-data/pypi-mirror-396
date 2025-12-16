import json
from pathlib import Path

from textual.widget import Widget
from textual.widgets import Select

from pytest_tui_runner.logging import logger
from pytest_tui_runner.utils.config import get_test_result
from pytest_tui_runner.utils.test_results import TestResult, extract_tests_results
from pytest_tui_runner.utils.types.widgets import WidgetsDict


def reset_widgets_style(widgets: WidgetsDict) -> None:
    """Remove marks from widgets."""
    for category in widgets.values():
        for subcategory in category.values():
            for widget_list in subcategory.values():
                if (
                    isinstance(widget_list, list)
                    and widget_list
                    and isinstance(widget_list[0], list)
                ):
                    for inner_list in widget_list:
                        reset_widget_list(inner_list)
                else:
                    reset_widget_list(widget_list)


def mark_widgets_from_report(widgets: WidgetsDict, report_path: Path) -> None:
    """Update widget styles based on pytest JSON report outcomes."""
    logger.debug(f"Loading report to mark widgets from path: {report_path}")
    if not report_path.exists():
        logger.error(f"Report file not found: {report_path}")
        raise FileNotFoundError(f"Report file not found: {report_path}")

    with Path.open(report_path, encoding="utf-8") as f:
        report: dict = json.load(f)

    logger.debug("▶️ Extracting test results from report...")
    test_results: list[TestResult] = extract_tests_results(report)
    logger.debug("✅ Test results extracted")

    for category in widgets.values():
        for subcategory in category.values():
            for widget_list in subcategory.values():
                for test in widget_list:
                    logger.debug(f"▶️ Getting result for test {test}...")
                    test_result = get_test_result(test, test_results)
                    logger.debug(f"✅ Result = {test_result}")

                    if not test_result:
                        logger.debug("Widget does not have test result")
                    else:
                        process_widgets(test, test_result)


def process_widgets(widgets: Widget | list[Widget], test_result: TestResult) -> None:
    """Update widget styles based on test result."""
    if isinstance(widgets, list):
        for widget in widgets:
            process_widget(widget, test_result)
    else:
        process_widget(widgets, test_result)


def process_widget(widget: Widget, test_result: TestResult) -> None:
    """Update widget style based on test result."""
    outcome = test_result.outcome
    if outcome == "passed":
        add_class(widget, "passed")
    elif outcome in {"failed", "xpassed"}:
        add_class(widget, "failed")
    elif outcome == "skipped":
        add_class(widget, "skipped")
    elif outcome == "xfailed":
        add_class(widget, "xfailed")
    elif outcome == "error":
        logger.warning(f"Test resulted in error: {test_result}")
        add_class(widget, "error")
    else:
        logger.error(f"Unknown test outcome '{outcome}' for widget {widget}")


def parse_result_arg_values(args: str) -> list[str]:
    """Parse argument values from test result args string."""
    if not args:
        logger.error("No args to parse.")
        return []

    return [arg.strip() for arg in args.split("-")]


def args_match_widget_values(args: list[str], widgets: list[Widget]) -> bool:
    """Check if argument values match the values of the given widgets."""
    return all(i < len(args) and args[i] == widget.value for i, widget in enumerate(widgets))


def mark_widget_running(widget: Widget) -> None:
    """Mark widget as running."""
    add_class(widget, "running")


def mark_widget_list_running(widget_list: list[Widget]) -> None:
    """Mark all widgets as running."""
    for widget in widget_list:
        mark_widget_running(widget)


def reset_widget_list(widgets: list[Widget]) -> None:
    """Remove all marks from widgets."""
    logger.debug(f"Resetting widget styles {widgets}")
    for widget in widgets:
        reset_widget(widget)


def reset_widget(widget: Widget) -> None:
    """Remove all marks from widget."""
    remove_classes(widget, ["running", "passed", "failed", "skipped", "xfailed", "error"])


def add_class(widget: Widget, style: str) -> None:
    """Add class to widget."""
    if isinstance(widget, Select):
        select_current = widget.query_one("SelectCurrent")
        select_current.add_class(style)
    else:
        widget.add_class(style)


def add_classes(widget: Widget, styles: list[str]) -> None:
    """Add multiple classes to widget."""
    for style in styles:
        add_class(widget, style)


def remove_class(widget: Widget, style: str) -> None:
    """Remove class from widget."""
    if isinstance(widget, Select):
        select_current = widget.query_one("SelectCurrent")
        select_current.remove_class(style)
    else:
        widget.remove_class(style)


def remove_classes(widget: Widget, styles: list[str]) -> None:
    """Remove multiple classes from widget."""
    for style in styles:
        remove_class(widget, style)
