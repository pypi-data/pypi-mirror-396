"""Menu widget for Account Pool inside the unified TUI."""

from textual.containers import Container, Vertical
from textual.widgets import Button, Label
from textual.containers import VerticalScroll


class AccountPoolMenuWidget(VerticalScroll):
    """Account Pool Menu Widget."""

    def compose(self):
        with Vertical():
            with Container(id="menu-container"):
                yield Label("🏦 Account Pool Management", id="menu-title")
                with Vertical(id="menu-buttons"):
                    yield Button("📱 Get Account by Phone", id="get-by-phone-btn", variant="primary")
                    yield Button("🏷️  Get Account by Alias", id="get-by-alias-btn")
                    yield Button("📋 List Aliases", id="list-aliases-btn")
                    yield Button("❌ Exit", id="exit-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "get-by-phone-btn":
            self.app.push_screen("ap_get_by_phone")
        elif event.button.id == "get-by-alias-btn":
            self.app.push_screen("ap_get_by_alias")
        elif event.button.id == "list-aliases-btn":
            self.app.push_screen("ap_list_aliases")
        elif event.button.id == "exit-btn":
            self.app.exit()


