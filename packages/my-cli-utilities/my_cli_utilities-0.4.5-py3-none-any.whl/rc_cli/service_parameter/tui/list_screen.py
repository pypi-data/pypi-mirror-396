# -*- coding: utf-8 -*-

"""List screen for all SP parameters."""

from textual.containers import Container, Horizontal, Vertical
from textual.binding import Binding
from textual.widgets import Button, DataTable, Footer, Header, Label
from textual.widget import Widget
from ...tui_common import BaseScreen
from rc_cli.tui_clipboard import copy_selected_cell_from_table
from ..service import sp_service
from rc_cli.tui_prefill import set_prefill


class SPListWidget(Widget):
    """Widget for listing all SP parameters."""

    BINDINGS = [
        Binding("r", "refresh", "Refresh", show=True),
        Binding("c", "copy_cell", "Copy Cell", show=True),
        Binding("s", "search", "Search", show=True),
        Binding("g", "go_value", "Open Value", show=True),
        Binding("e", "go_definition", "Open Def", show=True),
    ]
    
    def compose(self):
        with Vertical():
            with Container(id="list-container"):
                yield Label("📋 All Service Parameters", id="list-title")
                yield DataTable(id="sp-list", cursor_type="cell")
                with Horizontal(id="list-buttons"):
                    yield Button("Refresh", id="refresh-btn", variant="primary")
                    yield Button("Search", id="search-btn")
                    yield Button("Back", id="back-btn")
    
    def on_mount(self) -> None:
        """Initialize the list screen."""
        table = self.query_one("#sp-list", DataTable)
        table.add_columns("SP ID", "Description")
        table.focus()
        self.app.call_later(self._load_sp_list)

    async def action_refresh(self) -> None:
        await self._load_sp_list()

    def action_search(self) -> None:
        self.app.push_screen("sp_search")

    def action_copy_cell(self) -> None:
        table = self.query_one("#sp-list", DataTable)
        copy_selected_cell_from_table(self.app, table, columns=["SP ID", "Description"], timeout=2)

    def _get_selected_sp_id(self) -> str | None:
        table = self.query_one("#sp-list", DataTable)
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
        if event.button.id == "refresh-btn":
            await self._load_sp_list()
        elif event.button.id == "search-btn":
             # We should probably use the new navigation system for this too, 
             # calling app.push_screen("sp_search") should work as it's mapped in unified_tui
            self.app.push_screen("sp_search")
        elif event.button.id == "back-btn":
            self.app.action_back()
    
    async def _load_sp_list(self) -> None:
        """Load all SP parameters."""
        table = self.query_one("#sp-list", DataTable)
        table.clear()
        
        self.query_one("#list-title", Label).update("📋 Loading...")
        
        try:
            result = await sp_service.get_all_service_parameters()
            
            if not result.success:
                self.query_one("#list-title", Label).update(
                    f"❌ Error: {result.error_message}"
                )
                return
            
            service_parameters = result.data
            
            # Add results to table
            for sp_id, description in service_parameters.items():
                # Truncate description if too long
                display_desc = description
                if len(display_desc) > 60:
                    display_desc = display_desc[:57] + "..."
                table.add_row(sp_id, display_desc, key=sp_id)
            
            self.query_one("#list-title", Label).update(
                f"📋 {len(service_parameters)} Service Parameters"
            )
            
        except Exception as e:
            self.query_one("#list-title", Label).update(
                f"❌ Error: {str(e)}"
            )


class SPListScreen(BaseScreen):
    """List screen for all SP parameters."""

    BINDINGS = [
        *BaseScreen.BINDINGS,
        Binding("r", "refresh", "Refresh", show=True),
        Binding("c", "copy_cell", "Copy Cell", show=True),
        Binding("s", "search", "Search", show=True),
        Binding("g", "go_value", "Open Value", show=True),
        Binding("e", "go_definition", "Open Def", show=True),
    ]
    
    def compose(self):
        yield Header()
        yield SPListWidget()
        yield Footer()

    async def action_refresh(self) -> None:
        widget = self.query_one(SPListWidget)
        await widget._load_sp_list()  # noqa: SLF001

    def action_search(self) -> None:
        self.app.push_screen("sp_search")

    def action_copy_cell(self) -> None:
        table = self.query_one("#sp-list", DataTable)
        copy_selected_cell_from_table(self.app, table, columns=["SP ID", "Description"], timeout=2)

    def _get_selected_sp_id(self) -> str | None:
        table = self.query_one("#sp-list", DataTable)
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
