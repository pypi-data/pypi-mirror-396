from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest_tui_runner.utils.types.widgets import WidgetsDict

from pathlib import Path

from pytest_tui_runner.logging import logger
from pytest_tui_runner.utils.types.config import TestConfig
from pytest_tui_runner.utils.widgets.composer import compose_widgets
from pytest_tui_runner.utils.widgets.state_manager import load_widget_state, save_widget_state
from pytest_tui_runner.utils.widgets.widget_generator import generate_widgets_from_config


class WidgetManager:
    """Manages the creation, state, and composition of widgets.

    Attributes
    ----------
    config : TestConfig
        The configuration dictionary for widgets.
    state_path : str
        The path to the widget state file.
    widgets : dict
        Dictionary holding the generated widgets.

    Methods
    -------
    generate()
        Generates widgets from the configuration.
    load_state()
        Loads the state of widgets from a file.
    save_state()
        Saves the current state of widgets to a file.
    compose()
        Composes widgets for display or use.

    """

    def __init__(self, config: TestConfig, state_path: Path) -> None:
        """Initialize the WidgetManager with a configuration and optional state path.

        Parameters
        ----------
        config : dict
            The configuration dictionary for widgets.
        state_path : str, optional
            The path to the widget state file (default is STATE_PATH).

        """
        self.config: TestConfig = config
        self.state_path: Path = state_path
        self.widgets: WidgetsDict = {}

        logger.debug("Initializing WidgetManager...")
        self.generate()
        self.load_state()
        logger.debug("WidgetManager initialized")

    def generate(self) -> None:
        """Generate widgets from the provided configuration.

        It will generate widgets based on the user configuration
        and also according to the saved state of the widgets.
        """
        logger.debug("▶️ Starting to generate widgets...")
        try:
            self.widgets = generate_widgets_from_config(self.config, self.state_path)
            if not self.widgets:
                logger.warning("No widgets generated from the configuration.")
        except Exception as e:
            logger.error(f"Error generating widgets: {e}", exc_info=True)
            raise
        logger.debug("✅ Widgets generated")

    def load_state(self) -> None:
        """Load the state of widgets from the state file.

        Raises
        ------
        FileNotFoundError
            If the state file is not found.
        Exception
            For any other errors during loading.

        """
        logger.debug("▶️ Starting to load widgets state...")
        try:
            load_widget_state(self.widgets, self.state_path)
        except Exception as e:
            logger.error(f"Error loading widget state: {e}", exc_info=True)
            raise
        logger.debug("✅ Widgets state loaded")

    def save_state(self) -> None:
        """Save the current state of widgets to a file.

        Raises
        ------
        Exception
            If an error occurs during saving.

        """
        try:
            save_widget_state(self.widgets, self.state_path)
        except Exception as e:
            logger.error(f"Error saving widget state: {e}", exc_info=True)
            raise

    def compose(self) -> object:
        """Compose widgets for display or use.

        Returns
        -------
        object
            The composed widgets, ready for display or further use.

        """
        return compose_widgets(self.widgets)
