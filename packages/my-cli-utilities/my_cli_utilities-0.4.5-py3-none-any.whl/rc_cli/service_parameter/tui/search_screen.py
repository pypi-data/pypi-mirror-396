# -*- coding: utf-8 -*-

"""Search screen for SP parameters."""

from textual.containers import Container, Horizontal, Vertical
from textual.binding import Binding
from textual.widgets import Button, DataTable, Footer, Header, Input, Label
from textual.widget import Widget
from ...tui_common import BaseScreen
from rc_cli.tui_clipboard import copy_selected_cell_from_table
from ..service import sp_service
from rc_cli.tui_prefill import set_prefill


class SPSearchWidget(Widget):
    """Widget for searching SP parameters."""

    BINDINGS = [
        Binding("/", "focus_search", "Focus Search", show=True),
        Binding("enter", "search", "Search", show=False),
        Binding("r", "search", "Search", show=True),
        Binding("c", "copy_cell", "Copy Cell", show=True),
        Binding("g", "go_value", "Open Value", show=True),
        Binding("e", "go_definition", "Open Def", show=True),
        Binding("l", "go_list", "List", show=True),
    ]
    
    def compose(self):
        with Vertical():
            with Container(id="search-container"):
                yield Label("🔍 Search Service Parameters", id="search-title")
                yield Input(
                    placeholder="Enter search query...",
                    id="search-input"
                )
                yield DataTable(id="search-results", cursor_type="cell")
                with Horizontal(id="search-buttons"):
                    yield Button("Search", id="search-btn", variant="primary")
                    yield Button("Clear", id="clear-btn")
                    yield Button("Back", id="back-btn")
    
    def on_mount(self) -> None:
        """Initialize the search screen."""
        table = self.query_one("#search-results", DataTable)
        table.add_columns("SP ID", "Description")
        self.query_one("#search-input", Input).focus()

    def action_focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()

    async def action_search(self) -> None:
        await self._perform_search()

    def action_copy_cell(self) -> None:
        table = self.query_one("#search-results", DataTable)
        copy_selected_cell_from_table(self.app, table, columns=["SP ID", "Description"], timeout=2)

    def action_go_list(self) -> None:
        self.app.push_screen("sp_list")

    def _get_selected_sp_id(self) -> str | None:
        table = self.query_one("#search-results", DataTable)
        if table.row_count == 0:
            return None
        cursor_row = table.cursor_row
        if cursor_row is None:
            return None
        sp_id = str(table.get_cell_at((cursor_row, 0)))
        return sp_id if sp_id and sp_id != "None" else None

    def action_go_value(self) -> None:
        sp_id = self._get_selected_sp_id()
        if not sp_id:
            self.app.notify("Select a row first", severity="warning", timeout=2)
            return
        set_prefill(self.app, "sp_get_value", {"sp_id": sp_id})
        self.app.push_screen("sp_get_value")

    def action_go_definition(self) -> None:
        sp_id = self._get_selected_sp_id()
        if not sp_id:
            self.app.notify("Select a row first", severity="warning", timeout=2)
            return
        set_prefill(self.app, "sp_definition", {"sp_id": sp_id})
        self.app.push_screen("sp_definition")
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "search-btn":
            await self._perform_search()
        elif event.button.id == "clear-btn":
            self.query_one("#search-input", Input).value = ""
            table = self.query_one("#search-results", DataTable)
            table.clear()
        elif event.button.id == "back-btn":
            self.app.action_back()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "search-input":
            await self._perform_search()
    
    async def _perform_search(self) -> None:
        """Perform SP search."""
        input_widget = self.query_one("#search-input", Input)
        query = input_widget.value.strip()
        
        if not query:
            return
        
        table = self.query_one("#search-results", DataTable)
        table.clear()
        
        # Show loading
        self.query_one("#search-title", Label).update("🔍 Searching...")
        
        try:
            result = await sp_service.search_service_parameters(query)
            
            if not result.success:
                self.query_one("#search-title", Label).update(
                    f"❌ Error: {result.error_message}"
                )
                return
            
            matching_sps = result.data
            
            if not matching_sps:
                self.query_one("#search-title", Label).update(
                    f"🔍 No results found for '{query}'"
                )
                return
            
            # Add results to table
            for sp_id, description in matching_sps.items():
                # Truncate description if too long
                display_desc = description
                if len(display_desc) > 60:
                    display_desc = display_desc[:57] + "..."
                table.add_row(sp_id, display_desc, key=sp_id)
            
            self.query_one("#search-title", Label).update(
                f"🔍 Found {len(matching_sps)} results for '{query}'"
            )
            
        except Exception as e:
            self.query_one("#search-title", Label).update(
                f"❌ Error: {str(e)}"
            )


class SPSearchScreen(BaseScreen):
    """Search screen for SP parameters."""

    BINDINGS = [
        *BaseScreen.BINDINGS,
        Binding("/", "focus_search", "Focus Search", show=True),
        Binding("enter", "search", "Search", show=False),
        Binding("r", "search", "Search", show=True),
        Binding("c", "copy_cell", "Copy Cell", show=True),
        Binding("g", "go_value", "Open Value", show=True),
        Binding("e", "go_definition", "Open Def", show=True),
        Binding("l", "go_list", "List", show=True),
    ]
    
    def compose(self):
        yield Header()
        yield SPSearchWidget()
        yield Footer()

    def action_focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()

    async def action_search(self) -> None:
        widget = self.query_one(SPSearchWidget)
        await widget._perform_search()  # noqa: SLF001

    def action_copy_cell(self) -> None:
        table = self.query_one("#search-results", DataTable)
        copy_selected_cell_from_table(self.app, table, columns=["SP ID", "Description"], timeout=2)

    def action_go_list(self) -> None:
        self.app.push_screen("sp_list")

    def _get_selected_sp_id(self) -> str | None:
        table = self.query_one("#search-results", DataTable)
        if table.row_count == 0:
            return None
        cursor_row = table.cursor_row
        if cursor_row is None:
            return None
        sp_id = str(table.get_cell_at((cursor_row, 0)))
        return sp_id if sp_id and sp_id != "None" else None

    def action_go_value(self) -> None:
        sp_id = self._get_selected_sp_id()
        if not sp_id:
            self.app.notify("Select a row first", severity="warning", timeout=2)
            return
        set_prefill(self.app, "sp_get_value", {"sp_id": sp_id})
        self.app.push_screen("sp_get_value")

    def action_go_definition(self) -> None:
        sp_id = self._get_selected_sp_id()
        if not sp_id:
            self.app.notify("Select a row first", severity="warning", timeout=2)
            return
        set_prefill(self.app, "sp_definition", {"sp_id": sp_id})
        self.app.push_screen("sp_definition")
