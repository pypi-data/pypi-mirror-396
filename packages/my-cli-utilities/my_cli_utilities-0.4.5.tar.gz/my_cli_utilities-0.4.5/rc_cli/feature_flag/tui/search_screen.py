# -*- coding: utf-8 -*-

"""Search screen for feature flags."""

from textual.containers import Container, Horizontal, Vertical
from textual.binding import Binding
from textual.widgets import Button, DataTable, Footer, Header, Input, Label
from textual.widget import Widget
from ...tui_common import BaseScreen
from rc_cli.tui_clipboard import copy_selected_cell_from_table
from ..service import ffs_service
from rc_cli.tui_prefill import set_prefill


class FFSSearchWidget(Widget):
    """Widget for searching feature flags."""

    BINDINGS = [
        Binding("/", "focus_search", "Focus Search", show=True),
        Binding("enter", "search", "Search", show=False),
        Binding("r", "search", "Search", show=True),
        Binding("c", "copy_cell", "Copy Cell", show=True),
        Binding("g", "go_get", "Open", show=True),
        Binding("m", "go_menu", "Menu", show=True),
    ]
    
    def compose(self):
        with Vertical():
            with Container(id="search-container"):
                yield Label("🔍 Search Feature Flags", id="search-title")
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
        table.add_columns("Flag ID", "Status", "Description")
        self.query_one("#search-input", Input).focus()

    def action_focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()

    async def action_search(self) -> None:
        await self._perform_search()

    def action_copy_cell(self) -> None:
        table = self.query_one("#search-results", DataTable)
        copy_selected_cell_from_table(
            self.app,
            table,
            columns=["Flag ID", "Status", "Description"],
            timeout=2,
        )

    def action_go_menu(self) -> None:
        self.app.push_screen("main")

    def action_go_get(self) -> None:
        """Open Get screen with selected flag id prefilled."""
        table = self.query_one("#search-results", DataTable)
        if table.row_count == 0:
            self.app.notify("No results to open", severity="warning", timeout=2)
            return
        cursor_row = table.cursor_row
        if cursor_row is None:
            self.app.notify("Select a row first", severity="warning", timeout=2)
            return
        flag_id = str(table.get_cell_at((cursor_row, 0)))
        if not flag_id or flag_id == "None":
            self.app.notify("Invalid flag id", severity="warning", timeout=2)
            return

        set_prefill(self.app, "ffs_get", {"flag_id": flag_id})
        self.app.push_screen("ffs_get")
    
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
        """Perform feature flag search."""
        input_widget = self.query_one("#search-input", Input)
        query = input_widget.value.strip()
        
        if not query:
            return
        
        table = self.query_one("#search-results", DataTable)
        table.clear()
        
        # Show loading
        self.query_one("#search-title", Label).update("🔍 Searching...")
        
        try:
            result = await ffs_service.search_feature_flags(query)
            
            if not result.success:
                self.query_one("#search-title", Label).update(
                    f"❌ Error: {result.error_message}"
                )
                return
            
            flags = result.data
            
            if not flags:
                self.query_one("#search-title", Label).update(
                    f"🔍 No results found for '{query}'"
                )
                return
            
            # Add results to table
            for flag in flags:
                flag_id = flag.get("id", "N/A")
                status = flag.get("status", "N/A")
                description = flag.get("description", "N/A")
                
                # Truncate description if too long
                if len(description) > 50:
                    description = description[:47] + "..."
                
                table.add_row(flag_id, status, description, key=flag_id)
            
            self.query_one("#search-title", Label).update(
                f"🔍 Found {len(flags)} results for '{query}'"
            )
            
        except Exception as e:
            self.query_one("#search-title", Label).update(
                f"❌ Error: {str(e)}"
            )


class FFSSearchScreen(BaseScreen):
    """Search screen for feature flags."""

    BINDINGS = [
        *BaseScreen.BINDINGS,
        Binding("/", "focus_search", "Focus Search", show=True),
        Binding("enter", "search", "Search", show=False),
        Binding("r", "search", "Search", show=True),
        Binding("c", "copy_cell", "Copy Cell", show=True),
        Binding("g", "go_get", "Open", show=True),
        Binding("m", "go_menu", "Menu", show=True),
    ]
    
    def compose(self):
        yield Header()
        yield FFSSearchWidget()
        yield Footer()

    def action_focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()

    async def action_search(self) -> None:
        widget = self.query_one(FFSSearchWidget)
        await widget._perform_search()  # noqa: SLF001

    def action_copy_cell(self) -> None:
        table = self.query_one("#search-results", DataTable)
        copy_selected_cell_from_table(
            self.app,
            table,
            columns=["Flag ID", "Status", "Description"],
            timeout=2,
        )

    def action_go_menu(self) -> None:
        self.app.push_screen("main")

    def action_go_get(self) -> None:
        """Open Get screen with selected flag id prefilled."""
        table = self.query_one("#search-results", DataTable)
        if table.row_count == 0:
            self.app.notify("No results to open", severity="warning", timeout=2)
            return
        cursor_row = table.cursor_row
        if cursor_row is None:
            self.app.notify("Select a row first", severity="warning", timeout=2)
            return
        flag_id = str(table.get_cell_at((cursor_row, 0)))
        if not flag_id or flag_id == "None":
            self.app.notify("Invalid flag id", severity="warning", timeout=2)
            return

        set_prefill(self.app, "ffs_get", {"flag_id": flag_id})
        self.app.push_screen("ffs_get")
