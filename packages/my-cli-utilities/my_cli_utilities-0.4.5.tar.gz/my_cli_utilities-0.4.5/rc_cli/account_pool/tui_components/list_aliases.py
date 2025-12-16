"""List aliases TUI pages."""

from __future__ import annotations

import asyncio
from typing import List, Optional, Dict, Any, Tuple

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Button, DataTable, Footer, Header, Input, Label
from textual.binding import Binding

from rc_cli.common.service_factory import ServiceFactory
from rc_cli.tui_common import BaseScreen
from rc_cli.account_pool.service import AccountService
from rc_cli.account_pool.tui_components.modal import AccountQueryResultScreen


class ListAliasesWidget(Widget):
    """
    Lightweight widget-style list for embedding in unified TUI.

    Kept compatible with existing UnifiedTUIApp usage (mounted inside ContentSwitcher).
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            with Container(id="list-aliases-container"):
                yield Label("📋 List Aliases", id="list-aliases-title")
                yield Input(placeholder="Filter aliases...", id="filter-input")
                yield DataTable(id="aliases-table")
                with Horizontal(id="list-aliases-buttons"):
                    yield Button("Refresh", id="refresh-btn", variant="primary")
                    yield Button("Back", id="back-btn")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Alias", "Brand", "Kamino Key")
        self._load_aliases()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "refresh-btn":
            self._load_aliases()
        elif event.button.id == "back-btn":
            self.app.action_back()

    def on_input_changed(self, event: Input.Changed) -> None:
        self._filter_table(event.value)

    def _load_aliases(self) -> None:
        try:
            account_service = ServiceFactory.get_account_service()
            mappings = account_service.alias_service.get_mappings(False)
            self._all_mappings = list(mappings.values())
            self._update_table(self._all_mappings)
        except Exception as e:
            self.app.notify(f"Error loading aliases: {e}", severity="error")

    def _filter_table(self, query: str) -> None:
        if not hasattr(self, "_all_mappings"):
            return
        if not query:
            self._update_table(self._all_mappings)
            return
        q = query.lower()
        filtered = [
            m for m in self._all_mappings if q in m.alias.lower() or q in m.brand.lower() or q in m.kamino_key.lower()
        ]
        self._update_table(filtered)

    def _update_table(self, mappings: List) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for m in mappings:
            table.add_row(m.alias, m.brand, m.kamino_key)


class ListAliasesScreen(BaseScreen):
    """Full-feature list aliases screen for standalone AccountPoolTUIApp."""

    BINDINGS = [
        Binding("escape", "back", "Back", priority=True),
        Binding("c", "copy_selected", "Copy", show=True),
        Binding("/", "focus_search", "Search", show=True),
        Binding("enter", "query_account", "Query", show=True),
        Binding("r", "query_account", "Query", show=True),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._all_mappings: list = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            with Container(id="list-aliases-container"):
                yield Label("🏷️  List Aliases", id="list-aliases-title")
                yield Input(placeholder="🔍 Search aliases (fuzzy match)...", id="search-input")
                yield DataTable(id="aliases-table", cursor_type="cell")
                with Horizontal(id="list-aliases-buttons"):
                    yield Button("Load Aliases", id="load-btn", variant="primary")
                    yield Button("Refresh", id="refresh-btn")
                    yield Button("Copy Cell", id="copy-btn")
                    yield Button("Query Account", id="query-account-btn", variant="success")
                    yield Button("Clear Search", id="clear-search-btn")
                    yield Button("Back", id="back-btn")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#aliases-table", DataTable)
        table.add_column("#", width=5)
        table.add_column("Alias", width=32)
        table.add_column("Brand", width=10)
        table.add_column("Kamino Key")
        self.app.call_later(self._load_aliases, False)

    def action_focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "load-btn":
            await self._load_aliases(False)
        elif event.button.id == "refresh-btn":
            await self._load_aliases(True)
        elif event.button.id == "copy-btn":
            self.action_copy_selected()
        elif event.button.id == "query-account-btn":
            await self.action_query_account()
        elif event.button.id == "clear-search-btn":
            search_input = self.query_one("#search-input", Input)
            search_input.value = ""
            self._filter_aliases("")
        elif event.button.id == "back-btn":
            self.action_back()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-input":
            self._filter_aliases(event.value)

    async def _load_aliases(self, force_refresh: bool) -> None:
        try:
            self.query_one("#list-aliases-title", Label).update("🏷️  Loading aliases...")
            account_service = ServiceFactory.get_account_service()
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: list(account_service.alias_service.get_mappings(force_refresh).values()))
            self._all_mappings = result or []
            self._render_table(self._all_mappings, "")
        except Exception as e:
            self.app.notify(f"Error loading aliases: {e}", severity="error", timeout=5)
            self.query_one("#list-aliases-title", Label).update("🏷️  List Aliases (Load error)")

    def _filter_aliases(self, search_term: str) -> None:
        term = (search_term or "").strip().lower()
        if not term:
            self._render_table(self._all_mappings, "")
            return
        filtered = [
            m
            for m in self._all_mappings
            if term in m.alias.lower() or term in m.brand.lower() or term in m.kamino_key.lower()
        ]
        self._render_table(filtered, term)

    def _render_table(self, mappings: list, search_term: str) -> None:
        table = self.query_one("#aliases-table", DataTable)
        table.clear()
        for i, mapping in enumerate(mappings, 1):
            table.add_row(str(i), mapping.alias, mapping.brand, mapping.kamino_key, key=str(i))

        title = (
            f"🔍 {len(mappings)} / {len(self._all_mappings)} Alias(es) (filtered)"
            if search_term
            else f"🏷️  {len(mappings)} Alias(es) Found"
        )
        self.query_one("#list-aliases-title", Label).update(title)

    def action_copy_selected(self) -> None:
        from rc_cli.tui_clipboard import copy_selected_cell_from_table

        table = self.query_one("#aliases-table", DataTable)
        copy_selected_cell_from_table(
            self.app,
            table,
            columns=["#", "Alias", "Brand", "Kamino Key"],
            timeout=2,
        )

    async def action_query_account(self) -> None:
        """Query account using the selected row's alias or kamino key."""
        table = self.query_one("#aliases-table", DataTable)
        if table.row_count == 0:
            self.app.notify("No data available", severity="warning", timeout=2)
            return

        cursor_row = table.cursor_row
        cursor_col = table.cursor_column
        if cursor_row is None or cursor_row < 0:
            self.app.notify("Please select a row first", severity="warning", timeout=2)
            return

        alias = str(table.get_cell_at((cursor_row, 1)))
        kamino_key = str(table.get_cell_at((cursor_row, 3)))
        use_alias = cursor_col == 1

        if use_alias and alias:
            self.app.notify(f"🔍 Querying account by Alias: {alias}", timeout=2)
            query_param: Tuple[str, str] = ("alias", alias)
        elif kamino_key:
            self.app.notify(f"🔍 Querying account by Kamino Key from: {alias}", timeout=2)
            query_param = ("kamino_key", kamino_key)
        else:
            self.app.notify("No valid query parameter found", severity="warning", timeout=2)
            return

        account_service: AccountService = ServiceFactory.get_account_service()
        loop = asyncio.get_event_loop()

        result = await loop.run_in_executor(None, lambda: self._query_account_sync(account_service, query_param))
        if result is None or (isinstance(result, tuple) and result[0] is None):
            error_msg = result[1] if isinstance(result, tuple) else "Failed to query account"
            self.app.notify(f"❌ {error_msg}", severity="error", timeout=5)
            return

        account = result if not isinstance(result, tuple) else result[0]
        self._show_account_result_popup(account, alias, query_param[1])

    def _query_account_sync(
        self,
        account_service: AccountService,
        query_param: Tuple[str, str],
    ) -> Optional[Dict[str, Any] | tuple[None, str]]:
        """Sync query helper for executor thread."""
        try:
            from returns.pipeline import is_successful

            query_type, query_value = query_param

            if query_type == "alias":
                mapping = account_service.alias_service.get_mapping_by_alias(query_value)
                if not mapping:
                    return (None, f"Alias '{query_value}' not found")
                result = account_service.data_manager.get_account_by_kamino_key(mapping.kamino_key, "webaqaxmn", None)
            else:
                result = account_service.data_manager.get_account_by_kamino_key(query_value, "webaqaxmn", None)

            if is_successful(result):
                return result.unwrap()
            error = result.failure()
            return (None, error.message)
        except Exception as e:
            return (None, str(e))

    def _show_account_result_popup(self, account: Dict[str, Any], alias: str, query_value: str) -> None:
        query_info = f"{alias} [{query_value}]"
        self.app.push_screen(AccountQueryResultScreen(account=account, query_info=query_info))


