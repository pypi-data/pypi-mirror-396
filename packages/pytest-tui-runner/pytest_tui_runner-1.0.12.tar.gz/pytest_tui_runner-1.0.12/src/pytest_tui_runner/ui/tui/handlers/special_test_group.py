from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Button, Input, Select

from pytest_tui_runner.logging import logger


class SpecialTestGroup(Vertical):
    """A container widget for managing a dynamic group of test input rows.

    Each row consists of Input and Select widgets, with add/remove buttons.
    Allows cloning, adding, and removing rows, and keeps track of the initial input state.
    """

    def __init__(self, initial_rows: list[list[Widget]], test_name: str) -> None:
        """Initialize the SpecialTestGroup with a list of initial widget rows.

        Args:
            initial_rows (list[list[Widget]]): The initial rows of widgets to populate the group.

        """
        super().__init__(classes="special_test_class")
        logger.debug(f"Widgets len before clonning = '{len(initial_rows)}'")

        self.test_name = test_name
        self.row_template: list[Widget] = (
            self._clone_widgets(initial_rows[0]) if initial_rows else []
        )
        self.original_input = initial_rows
        self.rows: list[Horizontal] = []

        logger.debug(f"Widgets len after clonning = '{len(initial_rows)}'")
        logger.debug(f"Pointer to widgets = {self.original_input}")
        logger.debug(f"Row template = {self.row_template}")

    async def on_mount(self) -> None:
        """Mounts the initial rows and refreshes the control buttons when the widget is added to the app."""
        logger.debug("▶️ Mounting specialTestGroup...")
        logger.debug(f"Widgets len before generating rows = '{len(self.original_input)}'")
        debug_counter = len(self.original_input)

        for widget_row in self.original_input:
            logger.debug("Adding one row")
            await self._add_row(widget_row, update_initial=False)
            debug_counter -= 1
        self._update_initial_rows()
        await self._refresh_buttons()

        if debug_counter != 0:
            logger.error("The original widget list was modified when adding rows")

        logger.debug(f"Generated rows = {self.rows}")
        logger.debug(f"Widgets len after generating rows = '{len(self.original_input)}'")
        logger.debug("✅ SpecialTestGroup mounted")

    async def _add_row(
        self,
        to_clone: list[Widget] | None = None,
        *,
        update_initial: bool = True,
        include_value: bool = True,
    ) -> None:
        widgets = self._clone_widgets(to_clone, include_value=include_value)

        row = Horizontal(classes="special_test_row")
        self.rows.append(row)
        await self.mount(row)

        for widget in widgets:
            await row.mount(widget)

        if update_initial:
            self._update_initial_rows()

    def _clone_widgets(self, widgets: list[Widget], include_value: bool = True) -> list[Widget]:
        cloned = []
        for widget in widgets:
            if isinstance(widget, Input):
                cloned.append(
                    Input(
                        value=widget.value if include_value else "",
                        name=widget.name,
                        placeholder=widget.placeholder,
                    ),
                )
            elif isinstance(widget, Select):
                widget_values = {item for item in widget._legal_values if item != Select.BLANK}

                cloned.append(
                    Select.from_values(
                        values=sorted(widget_values),
                        name=widget.name,
                        allow_blank=widget._allow_blank,
                        value=widget.value,
                    ),
                )
        return cloned

    async def _refresh_buttons(self) -> None:
        logger.debug("Refreshing buttons (delete and set new)")
        for row in self.rows:
            if row.children and isinstance(row.children[0], Button):
                await row.children[0].remove()

        for i, row in enumerate(self.rows):
            button_id = f"{i}_{self.test_name.replace(' ', '_')}"
            if i == len(self.rows) - 1:
                button = Button(
                    "+",
                    id=f"add_{button_id}",
                    classes="special_button success_button",
                )
            else:
                button = Button(
                    "-",
                    id=f"remove_{button_id}",
                    classes="special_button error_button",
                )

            await row.mount(button, before=row.children[0] if row.children else None)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events for adding or removing rows.

        Args:
            event (Button.Pressed): The button press event containing the button information.

        """
        btn_id = event.button.id
        if not btn_id:
            return

        if btn_id.startswith("add_"):
            logger.debug("'ADD' button pressed")
            await self._add_row(self.row_template, include_value=False)
            await self._refresh_buttons()

        elif btn_id.startswith("remove_"):
            logger.debug("'REMOVE' button pressed")
            index = int(btn_id.removeprefix("remove_").split("_", 1)[0])
            if 0 <= index < len(self.rows):
                await self._remove_row(self.rows[index])

    async def _remove_row(self, row: Horizontal) -> None:
        if row in self.rows:
            self.rows.remove(row)
            await row.remove()
            self._update_initial_rows()
            await self._refresh_buttons()

    def _update_initial_rows(self) -> None:
        logger.debug("Updating initial widgets (clear and set new)")
        logger.debug(f"Widgets len before = {len(self.original_input)}")
        self.original_input.clear()

        for row in self.rows:
            widgets: list[Input | Select] = [
                widget for widget in row.children if isinstance(widget, Input | Select)
            ]
            self.original_input.append(widgets)
        logger.debug(f"Widgets len after = {len(self.original_input)}")
