from collections.abc import Iterator
from typing import TYPE_CHECKING

from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.widget import Widget
from textual.widgets import Button

from pytest_tui_runner.logging import logger
from pytest_tui_runner.paths import Paths
from pytest_tui_runner.ui.tui.handlers.button_handler import ButtonHandler

if TYPE_CHECKING:
    from pytest_tui_runner.ui.tui.pages.terminal_view import TerminalView
    from pytest_tui_runner.utils.types.config import TestConfig

from pytest_tui_runner.config import load_config
from pytest_tui_runner.utils.widgets.manager import WidgetManager


class TestsView(Vertical):
    """A page for displaying and managing tests widgets in the TUI.

    Handles loading configuration, managing widgets, and responding to button events.
    """

    def __init__(self) -> None:
        """Initialize the TestsView, loading configuration and setting up the widget manager."""
        super().__init__()
        logger.debug("▶️ Setuping widgets for tests...")

        # Load a user-defined test configuration.
        # Categories, subcategories, tests and their arguments are defined here
        self.config: TestConfig = load_config(Paths.config())

        # Create a WidgetManager class that is responsible for all work with widgets.
        # It will create widgets according to the config and then load their stored values
        self.widget_manager = WidgetManager(self.config, Paths.state_file())

        logger.debug("✅ Widgets for tests prepared")

    async def on_mount(self) -> None:
        """Set up the button handler when the view is mounted."""
        logger.debug("▶️ Mounting page for tests...")

        # Gets a handler for the terminal page, which is stored in the main application.
        # Thanks to this, we will be able to display the progress of the tests in the terminal
        terminal_view: TerminalView = self.app.terminal_view

        # ButtonHandler handles all actions associated with pressing buttons
        logger.debug("Initialize ButtonHandler")
        self.button_handler = ButtonHandler(
            self.widget_manager.widgets,
            self.buttons,
            terminal_view,
        )

        logger.debug("✅ Mounting test page finnished")

    def compose(self) -> Iterator[Widget]:
        """Compose the widgets for the tests view, including the scrollable test widgets and control buttons.

        Yields
        ------
        Widget
            The scrollable container of test widgets and the horizontal container of control buttons.

        """
        logger.debug("▶️ Composing page for tests...")

        # A container that contains all widgets associated with tests
        yield ScrollableContainer(*self.widget_manager.compose())

        self.buttons: list[Button] = [
            Button("Run tests", id="run_tests", classes="button"),
            Button("Exit", id="exit", classes="button"),
        ]

        # A container that contains all the additional buttons for controlling the test
        yield Horizontal(*self.buttons, id="button_container")

        logger.debug("✅ Composing test page finnished")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events and trigger corresponding actions.

        Parameters
        ----------
        event : Button.Pressed
            The button press event containing the button ID.

        """
        match event.button.id:
            case "run_tests":
                self.button_handler.run_tests()
            case "exit":
                self.widget_manager.save_state()
                self.app.exit()
