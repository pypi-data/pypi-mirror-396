"""Get account by alias TUI page."""

from __future__ import annotations

import asyncio
from typing import Dict, List, Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Label, Select, TextArea
from textual.widget import Widget

from rc_cli.account_pool.service import AccountService
from rc_cli.account_pool.tui_components.base import AccountPoolBaseResultWidget
from rc_cli.common.service_factory import ServiceFactory
from rc_cli.tui_common import BaseScreen


class GetAccountByAliasWidget(AccountPoolBaseResultWidget):
    """Widget for getting account by alias with fuzzy matching."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._all_mappings: List = []

    def compose(self) -> ComposeResult:
        with Vertical():
            with Container(id="get-by-alias-container"):
                yield Label("🏷️  Get Account by Alias", id="get-by-alias-title")
                yield Select([], id="alias-select", prompt="Select alias...")
                yield Input(placeholder="Alias (e.g., webAqaXmn) - Type to search...", id="alias-input")
                yield Select(
                    [("webaqaxmn", "webaqaxmn"), ("xmn-up", "xmn-up"), ("glpdevxmn", "glpdevxmn")],
                    id="env-select",
                    value="webaqaxmn",
                    prompt="Select environment...",
                )
                yield TextArea(id="result-area", read_only=True)
                with Horizontal(id="get-by-alias-buttons"):
                    yield Button("Get Account", id="get-btn", variant="primary")
                    yield Button("Copy Selected", id="copy-btn", variant="success")
                    yield Button("Clear", id="clear-btn")
                    yield Button("Back", id="back-btn")

    def on_mount(self) -> None:
        super().on_mount()
        alias_select = self.query_one("#alias-select", Select)
        alias_select.styles.display = "none"
        self.query_one("#alias-input", Input).focus()

        title_label = self.query_one("#get-by-alias-title", Label)
        title_label.update("🏷️  Get Account by Alias (Initializing...)")

        asyncio.create_task(self._load_aliases())

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "get-btn":
            await self._get_account_by_alias()
        elif event.button.id == "copy-btn":
            self.action_copy_selected()
        elif event.button.id == "clear-btn":
            self.query_one("#alias-input", Input).value = ""
            env_select = self.query_one("#env-select", Select)
            env_select.value = "webaqaxmn"
            self.query_one("#result-area", TextArea).text = ""
            self._hide_suggestions()
        elif event.button.id == "back-btn":
            self.app.action_back()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "alias-input":
            self._filter_aliases(event.value)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "alias-input":
            alias_select = self.query_one("#alias-select", Select)
            if alias_select.styles.display != "none":
                alias_select.focus()
            else:
                self.query_one("#env-select", Select).focus()

    def action_focus_input(self) -> None:
        self.query_one("#alias-input", Input).focus()

    def action_copy_selected(self) -> None:
        from rc_cli.tui_clipboard import copy_from_text_area

        result_area = self.query_one("#result-area", TextArea)
        copy_from_text_area(self.app, result_area, strip_phone_plus=True, timeout=2)

    async def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "alias-select":
            selected_alias = event.value
            if selected_alias and isinstance(selected_alias, str):
                self.query_one("#alias-input", Input).value = selected_alias
                event.select.styles.display = "none"
                self.query_one("#env-select", Select).focus()

    def _hide_suggestions(self) -> None:
        try:
            alias_select = self.query_one("#alias-select", Select)
            alias_select.styles.display = "none"
            self.query_one("#get-by-alias-title", Label).update("🏷️  Get Account by Alias")
        except Exception:
            return

    async def _load_aliases(self) -> None:
        title_label = self.query_one("#get-by-alias-title", Label)
        try:
            title_label.update("🏷️  Get Account by Alias (Loading...)")
            account_service = ServiceFactory.get_account_service()
            loop = asyncio.get_event_loop()
            mappings = await loop.run_in_executor(None, lambda: list(account_service.alias_service.get_mappings(False).values()))
            self._all_mappings = mappings or []
            title_label.update(f"🏷️  Get Account by Alias (Loaded {len(self._all_mappings)} aliases)")
        except Exception:
            self._all_mappings = []
            title_label.update("🏷️  Get Account by Alias (Load error)")

    def _filter_aliases(self, search_term: str) -> None:
        try:
            alias_select = self.query_one("#alias-select", Select)
            title_label = self.query_one("#get-by-alias-title", Label)
            if not self._all_mappings:
                title_label.update("🏷️  Get Account by Alias (Waiting for aliases...)")
                alias_select.styles.display = "none"
                return

            search_term = search_term.strip()
            if not search_term:
                title_label.update("🏷️  Get Account by Alias")
                alias_select.styles.display = "none"
                return

            search_term_lower = search_term.lower()
            filtered = [
                m
                for m in self._all_mappings
                if search_term_lower in m.alias.lower()
                or search_term_lower in m.brand.lower()
                or search_term_lower in m.kamino_key.lower()
            ][:10]

            if filtered:
                title_label.update(f"🏷️  Get Account by Alias (Found {len(filtered)} matches)")
                options = [(f"{m.alias} ({m.brand})", m.alias) for m in filtered]
                alias_select.set_options(options)
                alias_select.styles.display = "block"
            else:
                title_label.update(f"🏷️  Get Account by Alias (No matches for '{search_term}')")
                alias_select.styles.display = "none"
        except Exception:
            return

    async def _get_account_by_alias(self) -> None:
        alias = self.query_one("#alias-input", Input).value.strip()
        env_select = self.query_one("#env-select", Select)
        env_name = env_select.value if isinstance(env_select.value, str) and env_select.value else "webaqaxmn"

        self._hide_suggestions()

        def validate():
            if not alias:
                return False, "Please enter Alias"
            return True, None

        await self.query_and_display_account(
            query_func=self._get_account_by_alias_sync,
            title_label_id="get-by-alias-title",
            loading_msg="🏷️  Loading...",
            validation_func=validate,
            alias=alias,
            env_name=env_name,
            account_type=None,
        )

    def _get_account_by_alias_sync(
        self,
        account_service: AccountService,
        alias: str,
        env_name: str,
        account_type: Optional[str],
    ) -> Optional[Dict]:
        from returns.pipeline import is_successful

        mapping = account_service.alias_service.get_mapping_by_alias(alias)
        if not mapping:
            return (None, f"Alias '{alias}' not found in GitLab configuration")

        kamino_key = mapping.kamino_key
        result = account_service.data_manager.get_account_by_kamino_key(kamino_key, env_name, account_type)
        if is_successful(result):
            return result.unwrap()
        error = result.failure()
        return (None, error.message)


class GetAccountByAliasScreen(BaseScreen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield GetAccountByAliasWidget()
        yield Footer()


