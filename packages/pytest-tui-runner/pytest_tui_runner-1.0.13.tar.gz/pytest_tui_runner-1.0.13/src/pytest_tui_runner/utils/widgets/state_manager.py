import json
from pathlib import Path

from textual.widgets import Checkbox, Select

from pytest_tui_runner.logging import logger
from pytest_tui_runner.utils.types.saved_state import SavedState, TestState, TestValue
from pytest_tui_runner.utils.types.widgets import TestWidgets, WidgetsDict


def load_widget_state(widgets: WidgetsDict, filename: Path) -> None:
    """Retrieve the state of the widgets from the JSON fileand set the values for the existing widgets."""
    logger.debug(f"Loading saved states from '{filename}' file")
    saved: SavedState = read_json_state_file(filename)

    for cat, subcats in widgets.items():
        for subcat, tests in subcats.items():
            for test_name, test_widgets in tests.items():
                saved_value: TestValue = _get_saved_value(saved, cat, subcat, test_name)
                logger.debug(f"Saved value for test '{test_name}' = {saved_value}")
                _set_widgets_values(test_widgets, saved_value)

    logger.debug(f"Loaded widgets = {widgets}")


def save_widget_state(widgets: WidgetsDict, filename: Path) -> None:
    """Save the state of the widgets from the JSON file."""
    logger.debug(f"Saving widgets states to '{filename}' file")
    saved: SavedState = {}

    for cat, subcats in widgets.items():
        saved[cat] = {}
        for subcat, tests in subcats.items():
            saved[cat][subcat] = {}
            for test_name, test_widgets in tests.items():
                value_to_save: TestValue = _serialize_test_widgets(test_widgets)
                logger.debug(f"Value to save for test '{test_name}' = {value_to_save}")
                saved[cat][subcat][test_name] = value_to_save

    logger.debug(f"Saved widgets = {saved}")
    write_json_state_file(filename, saved)


def read_json_state_file(filename: Path) -> SavedState:
    """Load saved widget states from file and return as a dictionary."""
    if not filename or not filename.is_file():
        logger.debug(f"WARNING: Configuration file '{filename}' not found")
        return {}
    try:
        with Path.open(filename, encoding="utf-8") as f:
            data: SavedState = json.load(f)
            if not data:
                logger.warning("No saved state found.")
            return data
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.error(f"Invalid JSON format in saved state file '{filename}': {e}", exc_info=True)
        return {}


def write_json_state_file(filename: Path, data: SavedState) -> None:
    """Write widget states data to a JSON file."""
    try:
        with Path.open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except (OSError, TypeError) as e:
        logger.error(f"An error occurred while saving data: {e}", exc_info=True)


def _get_saved_value(saved: SavedState, cat: str, subcat: str, test: str) -> TestValue:
    """Safely returns the saved list of values for the given test."""
    return saved.get(cat, {}).get(subcat, {}).get(test, [])


def _set_widgets_values(test_widgets: TestWidgets, saved_values: TestValue) -> None:
    """Retrieve widget values from stored data."""
    # Simple checkbox
    if _test_value_is_checkbox(test_widgets):
        _set_checkbox_value(test_widgets, saved_values)
        return

    if not _test_value_is_test_arguments(test_widgets):
        logger.error(f"Saved values for widgets have invalid format = {test_widgets}")
        return

    logger.debug(
        f"Number of instances the arguments found in state file: '{len(saved_values)}'",
    )
    for i, arguments_widgets in enumerate(test_widgets):
        if i >= len(saved_values):
            logger.debug("WARNING: Number of widgets is greater than the number of stored values")
            continue

        saved_entry = saved_values[i]
        if not isinstance(saved_entry, dict):
            logger.warning(f"Invalid saved entry format at index {i} (expected dict).")
            continue

        try:
            for widget in arguments_widgets:
                value = saved_entry.get(widget.name)
                if value:
                    logger.debug(f"Setting value for widget {widget} = '{value}'")
                    widget.value = value
                else:
                    logger.debug(f"WARNING: No value saved for this widget = {widget}")

        except (TypeError, AttributeError) as e:
            logger.error(
                f"Error setting widget '{getattr(widget, 'name', '?')}': {e}",
                exc_info=True,
            )


def _set_checkbox_value(test_widgets: TestWidgets, saved_values: TestValue) -> None:
    """Set the value for a simple checkbox widget."""
    if not saved_values:
        return
    try:
        test_widgets[0].value = saved_values[0]
    except (TypeError, AttributeError) as e:
        logger.error(f"Invalid checkbox value type: {e}", exc_info=True)


def _serialize_test_widgets(widget_group: TestWidgets) -> TestValue:
    """Convert widgets to a suitable structure for saving to a file."""
    if _test_value_is_checkbox(widget_group):
        return [widget_group[0].value]

    result: TestValue = []
    for widgets in widget_group:
        widget_data: TestState = {}
        for instance in widgets:
            widget_data[instance.name] = "" if instance.value == Select.BLANK else instance.value
        result.append(widget_data)
    return result


def _test_value_is_checkbox(test_widgets: TestWidgets) -> bool:
    """Check if they are widgets for checkbox type test or not."""
    # Widgets for the checkbox type test have only one element in the list, the checkbox widget
    return len(test_widgets) == 1 and isinstance(test_widgets[0], Checkbox)


def _test_value_is_test_arguments(test_widgets: TestWidgets) -> bool:
    """Check if they are widgets for special type test or not."""
    return len(test_widgets) >= 1 and isinstance(test_widgets[0], list)
