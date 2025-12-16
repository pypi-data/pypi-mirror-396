import asyncio
import os
from asyncio.subprocess import Process
from pathlib import Path

from textual.widgets import Button

from pytest_tui_runner.logging import logger
from pytest_tui_runner.paths import Paths
from pytest_tui_runner.ui.tui.pages.terminal_view import TerminalView
from pytest_tui_runner.utils.pytest.arguments import build_pytest_arguments
from pytest_tui_runner.utils.types.widgets import WidgetsDict
from pytest_tui_runner.utils.widgets.buttons import (
    disable_buttons_after_test_runs,
    enable_buttons_after_test_finnished,
)
from pytest_tui_runner.utils.widgets.marking import mark_widgets_from_report, reset_widgets_style


class ButtonHandler:
    """Handles button actions in the TUI, such as running tests and managing widget states.

    Attributes
    ----------
    widgets : dict
        Dictionary of widgets representing test options.
    terminal_view
        The terminal view interface for displaying output.

    Methods
    -------
    run_tests()
        Initiates running tests asynchronously.
    check_all()
        Checks all test option widgets.
    uncheck_all()
        Unchecks all test option widgets.

    """

    def __init__(
        self,
        widgets: WidgetsDict,
        buttons: list[Button],
        terminal_view: TerminalView,
    ) -> None:
        """Initialize ButtonHandler with widgets and terminal view.

        Parameters
        ----------
        widgets : dict
            Dictionary of widgets representing test options.
        terminal_view
            The terminal view interface for displaying output.

        """
        self.widgets: WidgetsDict = widgets
        self.buttons: list[Button] = buttons
        self.terminal_view: TerminalView = terminal_view

    def run_tests(self) -> None:
        """Initiate running tests asynchronously.

        This method schedules the asynchronous test runner to execute in the event loop.
        """
        logger.debug("Resetting widget styles")
        reset_widgets_style(self.widgets)
        Paths.delete_pytest_report()

        logger.debug("------------------------- COMMAND EXECUTING -------------------------")
        logger.debug("'RUN TESTS' button pressed")
        logger.info("------------- Executing the tests -------------")
        self._test_task = asyncio.create_task(self._run_tests_async())

    async def _run_tests_async(self) -> None:
        if not self._validate_test_path(Paths.user_root()):
            return

        logger.debug("▶️ Building command to run tests...")
        args: list[str] = self._build_test_command()
        logger.debug("✅ Command built")

        logger.debug("Executing command")
        logger.debug("------------------------- COMMAND EXECUTING -------------------------")
        await self._execute_test_process(args, cwd=Paths.user_root())

    def _validate_test_path(self, path: Path) -> bool:
        """Check if test path exists."""
        if not path.exists():
            logger.error(f"Test path {path} does not exist.")
            self.terminal_view.write_line(f"Error: Test path {path} not found.\n")
            return False
        return True

    def _build_test_command(self) -> list[str]:
        """Build the pytest command arguments."""
        return build_pytest_arguments(self.widgets)

    async def _execute_test_process(self, args: list[str], cwd: Path) -> None:
        """Run a subprocess for tests and stream output to terminal."""
        self.terminal_view.write_line("\n")
        self.terminal_view.write_line(
            "==============================================================================\n",
            style="#F39D2D",
        )
        self.terminal_view.write_line(
            "                                 Running tests                                 \n",
            style="#F39D2D",
        )
        self.terminal_view.write_line(
            "==============================================================================\n",
            style="#F39D2D",
        )

        logger.debug("Disabling buttons during test run")
        await disable_buttons_after_test_runs(self.buttons)

        process: Process = await asyncio.create_subprocess_exec(
            *args,
            env={**os.environ, "PYTEST_TUI_RUNNER_ROOT": str(Paths.user_root())},
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=cwd,
        )

        if not process.stdout:
            raise RuntimeError("Process stdout is not available.")

        logger.debug("Starting to write output to terminal")
        await self._stream_process_output(process)

        await process.wait()
        logger.info("✅ Tests finished")

        logger.debug("Enabling buttons after test run")
        await enable_buttons_after_test_finnished(self.buttons)

        logger.debug("------------------------- RESULTS EVALUATION -------------------------")
        logger.debug("▶️ Marking widgets according to the result...")
        mark_widgets_from_report(self.widgets, Paths.pytest_report())
        logger.debug("✅ Widgets marked")
        logger.info("Results evaluated")
        logger.debug("------------------------- RESULTS EVALUATION -------------------------")

    async def _stream_process_output(self, process: Process) -> None:
        """Stream process stdout to terminal line by line."""
        if process.stdout is None:
            raise RuntimeError("Process stdout is not available.")
        async for line in process.stdout:
            self.terminal_view.write_line(line.decode(errors="replace").rstrip())
