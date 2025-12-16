"""Modal screens for Account Pool TUI."""

from __future__ import annotations

import logging
from typing import Any, Dict

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, TextArea

from rc_cli.account_pool.tui_components.base import AccountPoolBaseResultWidget
from rc_cli.account_pool.tui_components.constants import MODAL_SEPARATOR_WIDTH

logger = logging.getLogger(__name__)


class AccountQueryResultScreen(Screen):
    """Modal screen to display account query results with copy support."""

    BINDINGS = [
        Binding("escape", "back", "Back", priority=True),
        Binding("c", "copy_selected", "Copy Selected", show=True),
        Binding("a", "copy_all", "Copy All", show=True),
    ]

    def __init__(self, account: Dict[str, Any], query_info: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.account = account
        self.query_info = query_info

    def action_back(self) -> None:
        self.app.pop_screen()

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            with Container(id="account-result-modal-container"):
                yield Label(f"✅ Account Found: {self.query_info}", id="modal-title")
                yield TextArea("", read_only=True, show_line_numbers=False, id="modal-result-area")
            with Horizontal(id="modal-buttons"):
                yield Button("Copy Selected", id="copy-selected-btn", variant="success")
                yield Button("Copy All", id="copy-all-btn")
                yield Button("Back", id="back-btn", variant="primary")
        yield Footer()

    def on_mount(self) -> None:
        result_area = self.query_one("#modal-result-area", TextArea)
        formatted = AccountPoolBaseResultWidget._format_account_info(  # type: ignore[misc]
            self,
            self.account,
            separator_width=MODAL_SEPARATOR_WIDTH,
            use_na_for_missing=False,
        )
        result_area.text = formatted
        result_area.show_line_numbers = False

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "copy-selected-btn":
            self.action_copy_selected()
        elif event.button.id == "copy-all-btn":
            self.action_copy_all()
        elif event.button.id == "back-btn":
            self.action_back()

    def action_copy_selected(self) -> None:
        from rc_cli.tui_clipboard import copy_from_text_area

        result_area = self.query_one("#modal-result-area", TextArea)
        ok = copy_from_text_area(self.app, result_area, strip_phone_plus=True, timeout=2)
        if not ok:
            self.action_copy_all()

    def action_copy_all(self) -> None:
        from rc_cli.tui_clipboard import copy_to_clipboard

        result_area = self.query_one("#modal-result-area", TextArea)
        copy_to_clipboard(self.app, result_area.text or "", timeout=2)


