from pathlib import Path

from textual.widget import Widget
from textual.widgets import Checkbox, Input, Select

from pytest_tui_runner.logging import logger
from pytest_tui_runner.utils.types.config import Argument, ArgumentType, Test, TestConfig
from pytest_tui_runner.utils.types.saved_state import SavedState, SavedSubcat, TestValue
from pytest_tui_runner.utils.types.widgets import WidgetsDict
from pytest_tui_runner.utils.widgets.state_manager import read_json_state_file


def generate_widgets_from_config(config: TestConfig, state_path: Path | None = None) -> WidgetsDict:
    """
    Generate a nested dictionary of widgets from the given test configuration.

    Args:
        config: Test configuration loaded from YAML/JSON.
        state_path: Optional path to saved widget state.

    Returns
    -------
        Nested dict in the form:
        {
            category: {
                subcategory: {
                    test_name: widget | list[widget]
                }
            }
        }
    """
    logger.debug(f"Loading saved states from '{state_path}' file")
    saved_state: SavedState = read_json_state_file(state_path)
    widgets: WidgetsDict = {}

    for category in config["categories"]:
        cat_name: str = category["label"]
        widgets[cat_name] = {}

        for subcat in category.get("subcategories", []):
            subcat_name: str = subcat["label"]
            widgets[cat_name][subcat_name] = {}

            for test in subcat.get("tests", []):
                widgets[cat_name][subcat_name][test["label"]] = _create_test_widgets(
                    test,
                    saved_state.get(cat_name, {}).get(subcat_name, {}),
                )

    logger.debug(f"Generated widgets: {widgets}")
    return widgets


def _create_test_widgets(test: Test, saved_subcat: SavedSubcat) -> list[Widget]:
    """Create a list of widgets by test type."""
    test_type = "special" if is_test_special(test) else "normal"

    logger.debug(f"Creating widgets for test = '{test.get('name')}', type = '{test_type}'")

    if test_type == "normal":
        return [Checkbox(test["label"])]

    if test_type == "special":
        # Get the number of saved states of the test argument
        saved_group: TestValue = saved_subcat.get(test["label"], [])
        num_groups: int = max(1, len(saved_group))
        logger.debug(f"Number of instances of the arguments found in state file: '{num_groups}'")

        return [_create_widgets_from_arguments(test["arguments"]) for _ in range(num_groups)]

    return []


def _create_widgets_from_arguments(arguments: list[Argument]) -> list[Widget]:
    """Create a list of widgets from a test's argument definitions."""
    result: list[Widget] = []
    for arg in arguments:
        widget: Widget | None = _widget_from_argument(arg)
        if widget is not None:
            result.append(widget)
    logger.debug(f"Adding one instance of arguments widgets: {result}")
    return result


def _widget_from_argument(arg: Argument) -> Widget | None:
    """Create a single widget based on argument definition."""
    arg_type: ArgumentType = arg.get("arg_type")
    if arg_type == "select":
        if "options" not in arg:
            raise ValueError(
                f"❌ Missing required 'options' in argument definition for '{arg.get('name', '<unknown>')}'. "
                f"Please add an 'options' key to your config.",
            )

        return Select(
            [(opt, opt) for opt in arg["options"]],
            allow_blank=True,
            name=arg["arg_name"],
        )
    if arg_type == "text_input":
        if "placeholder" not in arg:
            raise ValueError(
                f"❌ Missing required 'placeholder' in argument definition for '{arg.get('name', '<unknown>')}'. "
                f"Please add a 'placeholder' key to your config.",
            )

        return Input(
            placeholder=arg.get("placeholder", ""),
            name=arg["arg_name"],
        )
    logger.error(f"Unexpected argument type: '{arg_type}'")
    return None


def is_test_special(test: Test) -> bool:
    """Check if the test is of special type."""
    return "arguments" in test
