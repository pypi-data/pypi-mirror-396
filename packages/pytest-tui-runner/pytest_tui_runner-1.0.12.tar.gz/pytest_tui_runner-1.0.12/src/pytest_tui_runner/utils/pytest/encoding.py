from urllib.parse import quote, unquote

from textual.widgets import Select

from pytest_tui_runner.logging import logger
from pytest_tui_runner.utils.types.widgets import TestArguments
from pytest_tui_runner.utils.widgets.marking import mark_widget_list_running

VARIANT_SEP = ";"
PAIR_SEP = ","
KV_SEP = ":"


def encode_variants(test_name: str, variants: list[TestArguments]) -> str | None:
    """
    Encode list of variant dicts into a single string.

    Example:
      [{'action': 'Delete', 'image': '123'}, {'action': 'Copy', 'image': '456'}]
    → "action:Delete,image:123;action:Copy,image:456"
    """
    encoded_variants: list[str] = []
    had_any_value = False

    for i, widget_list in enumerate(variants):
        logger.debug(f"Processing '{i}' variant of the arguments")
        parts: list[str] = []
        for widget in widget_list:
            if hasattr(widget, "name") and hasattr(widget, "value"):
                if widget.value in (None, "", Select.BLANK):
                    logger.debug(f"Missing value for widget = {widget}")
                    continue
                had_any_value = True
                name: str = quote(str(widget.name), safe="")
                value: str = quote(str(widget.value), safe="")
                parts.append(f"{name}{KV_SEP}{value}")

        logger.debug(f"Processed variant of the arguments = {parts}")
        if parts and len(parts) == len(widget_list):
            encoded_variants.append(PAIR_SEP.join(parts))
            logger.debug("Marking this variant as running")
            mark_widget_list_running(widget_list)
        else:
            logger.debug("WARNING: This variant will be skipped because some argument is missing")

    if not had_any_value:
        logger.debug(f"Test '{test_name}' has no arguments set, so it will be skipped")
        return None

    # This part checks if the user has not entered duplicate arguments for the test,
    # which would cause the pytest result to be incorrectly processed for coloring the widgets.
    # But now there is no way to tell the user what is wrong (pop-up window),
    # so that's why the program continues.

    if has_duplicates(encoded_variants):
        logger.warning(f"Duplicate argument variants found for test '{test_name}'")
        # return None

    logger.debug(f"Final variants of the arguments = {encoded_variants}")
    return VARIANT_SEP.join(encoded_variants)


def decode_variants(raw_value: str) -> list[TestArguments]:
    """
    Decode CLI argument string back into list of dicts.

    Example:
      "action:Delete,image:123;action:Copy,image:456"
    → [{'action': 'Delete', 'image': '123'}, {'action': 'Copy', 'image': '456'}]
    """
    variants: list[TestArguments] = []
    for part in raw_value.split(VARIANT_SEP):
        if not part.strip():
            continue
        variant = {}
        for arg in part.split(PAIR_SEP):
            if not arg.strip():
                continue
            key, value = arg.split(KV_SEP, 1)
            variant[unquote(key.strip())] = unquote(value.strip())
        variants.append(variant)
    return variants


def has_duplicates(items: list[str]) -> bool:
    """Check if the given list has duplicate items."""
    return len(items) != len(set(items))
