"""Get account by phone TUI page."""

from __future__ import annotations

from typing import Dict, Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Label, Select, TextArea

from returns.pipeline import is_successful

from rc_cli.account_pool.service import AccountService
from rc_cli.tui_common import BaseScreen
from rc_cli.account_pool.tui_components.base import AccountPoolBaseResultWidget


class GetAccountByPhoneWidget(AccountPoolBaseResultWidget):
    """Widget for getting account by phone number."""

    def compose(self) -> ComposeResult:
        with Vertical():
            with Container(id="get-by-phone-container"):
                yield Label("📱 Get Account by Phone", id="get-by-phone-title")
                yield Input(placeholder="Phone Number", id="phone-input")
                yield Select(
                    [("webaqaxmn", "webaqaxmn"), ("xmn-up", "xmn-up"), ("glpdevxmn", "glpdevxmn")],
                    id="env-select",
                    value="webaqaxmn",
                    prompt="Select environment...",
                )
                yield TextArea(id="result-area", read_only=True)
                with Horizontal(id="get-by-phone-buttons"):
                    yield Button("Get Account", id="get-btn", variant="primary")
                    yield Button("Clear", id="clear-btn")
                    yield Button("Back", id="back-btn")

    def on_mount(self) -> None:
        super().on_mount()
        self.query_one("#phone-input", Input).focus()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "get-btn":
            await self._get_account_by_phone()
        elif event.button.id == "clear-btn":
            self.query_one("#phone-input", Input).value = ""
            env_select = self.query_one("#env-select", Select)
            env_select.value = "webaqaxmn"
            self.query_one("#result-area", TextArea).text = ""
        elif event.button.id == "back-btn":
            self.app.action_back()

    async def _get_account_by_phone(self) -> None:
        phone = self.query_one("#phone-input", Input).value.strip()
        env_select = self.query_one("#env-select", Select)
        env_name = env_select.value if isinstance(env_select.value, str) and env_select.value else "webaqaxmn"

        def validate():
            if not phone:
                return False, "Please enter Phone Number"
            return True, None

        await self.query_and_display_account(
            query_func=self._get_account_by_phone_sync,
            title_label_id="get-by-phone-title",
            loading_msg="📱 Loading...",
            validation_func=validate,
            phone=phone,
            env_name=env_name,
        )

    def _get_account_by_phone_sync(self, account_service: AccountService, phone: str, env_name: str) -> Optional[Dict]:
        from rc_cli.common_lib.config import ValidationUtils

        main_number_str = ValidationUtils.normalize_phone_number(phone)
        if not main_number_str:
            return (None, "Invalid phone number format")

        result = account_service.data_manager.get_all_accounts_for_env(env_name).bind(
            lambda accounts: account_service._find_account_by_phone_in_list(accounts, main_number_str)
        )
        if is_successful(result):
            return result.unwrap()
        error = result.failure()
        return (None, error.message)


class GetAccountByPhoneScreen(BaseScreen):
    """Screen wrapper for GetAccountByPhoneWidget."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield GetAccountByPhoneWidget()
        yield Footer()


