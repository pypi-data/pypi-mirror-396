from collections.abc import Iterator

from rich.text import Text
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import RichLog


class TerminalView(Vertical):
    """A page for displaying terminal output using RichLog in a vertical container."""

    def compose(self) -> Iterator[Widget]:
        """Compose the widgets for the tests view, including the scrollable test widgets and control buttons.

        Yields
        ------
        Widget
            The scrollable container of test widgets and the horizontal container of control buttons.

        """
        yield RichLog(id="pytest_log", highlight=True, wrap=True)

    def write_line(self, line: str, style: str | None = None) -> None:
        """Write a line to the RichLog widget.

        Parameters
        ----------
        line : str
            The line of text to write to the terminal log.

        """
        log: RichLog = self.query_one("#pytest_log", RichLog)

        # I want to be able to enter my own style, but if I don't enter any,
        # I want to leave the basic styling (even entering an empty style would cancel it)
        if style:
            line_with_style = Text(line, style=style)
            log.write(line_with_style)
        else:
            log.write(line)
