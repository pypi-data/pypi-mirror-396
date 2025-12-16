from textual.app import App, ComposeResult
from textual.widgets import TabbedContent, TabPane

from pytest_tui_runner.logging import logger
from pytest_tui_runner.ui.tui.pages.terminal_view import TerminalView
from pytest_tui_runner.ui.tui.pages.tests_view import TestsView


class TestRunnerApp(App):
    """Main application class for the pytest-tui-runner TUI.

    Handles the layout and navigation between Tests and Terminal views.
    """

    CSS_PATH = "styles/tests_view.css"

    def compose(self) -> ComposeResult:
        """Compose the main layout with tabbed views for Tests and Terminal."""
        # Uncomment this if you want to have Header on the page
        # yield Header()

        with TabbedContent():
            with TabPane("Tests"):
                yield TestsView()
            with TabPane("Terminal"):
                self.terminal_view = TerminalView()
                yield self.terminal_view

        # Uncomment this if you want to have Footer on the page
        # yield Footer()

    async def on_ready(self) -> None:
        """Application is completely up and running."""
        logger.info("✅ Application successfully started")
        logger.debug("---------------------- APPLICATION PREPARATION ----------------------")
