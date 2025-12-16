"""Standalone Account Pool TUI app (rc ap tui)."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from rc_cli.account_pool.tui_components.get_by_alias import GetAccountByAliasScreen
from rc_cli.account_pool.tui_components.get_by_phone import GetAccountByPhoneScreen
from rc_cli.account_pool.tui_components.list_aliases import ListAliasesScreen
from rc_cli.account_pool.tui_components.menu import AccountPoolMenuWidget
from rc_cli.tui_common import BaseScreen
from textual.binding import Binding
from textual import events
from textual.containers import Container, Vertical
from textual.widgets import Button, Label


class MainMenuScreen(BaseScreen):
    """Main menu screen."""

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("escape", "quit", "Quit", priority=True),
        Binding("up", "move_up", "Move Up", priority=True),
        Binding("down", "move_down", "Move Down", priority=True),
        Binding("enter", "select", "Select", priority=True),
    ]

    button_ids = ["get-by-phone-btn", "get-by-alias-btn", "list-aliases-btn", "exit-btn"]
    selected_index = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield AccountPoolMenuWidget()
        yield Footer()

    def on_mount(self) -> None:
        self._update_selection()

    def action_quit(self) -> None:
        self.app.exit()

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.app.exit()
            event.prevent_default()

    def action_move_up(self) -> None:
        if self.selected_index > 0:
            self.selected_index -= 1
            self._update_selection()

    def action_move_down(self) -> None:
        if self.selected_index < len(self.button_ids) - 1:
            self.selected_index += 1
            self._update_selection()

    def action_select(self) -> None:
        button_id = self.button_ids[self.selected_index]
        button = self.query_one(f"#{button_id}", Button)
        button.press()

    def _update_selection(self) -> None:
        for i, button_id in enumerate(self.button_ids):
            button = self.query_one(f"#{button_id}", Button)
            if i == self.selected_index:
                button.variant = "primary"
                button.focus()
            else:
                button.variant = "default"


class AccountPoolTUIApp(App):
    """Main TUI application for Account Pool management."""

    def on_mount(self) -> None:
        self.push_screen("main")

    def action_quit(self) -> None:
        self.exit()

    def action_back(self) -> None:
        if len(self.screen_stack) > 1:
            self.pop_screen()

    def push_screen(self, screen_name_or_instance) -> None:  # type: ignore[override]
        from textual.screen import Screen as TextualScreen

        if isinstance(screen_name_or_instance, TextualScreen):
            super().push_screen(screen_name_or_instance)
            return

        screens = {
            "main": MainMenuScreen(),
            "ap_get_by_phone": GetAccountByPhoneScreen(),
            "ap_get_by_alias": GetAccountByAliasScreen(),
            "ap_list_aliases": ListAliasesScreen(),
        }
        if screen_name_or_instance in screens:
            super().push_screen(screens[screen_name_or_instance])


def run_tui() -> None:
    """Run the TUI application."""
    app = AccountPoolTUIApp()
    app.run()


