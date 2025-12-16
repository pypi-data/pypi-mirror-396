# -*- coding: utf-8 -*-

"""Main menu screen."""

from textual.containers import Container, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label
from textual.binding import Binding
from textual import events
from textual.widget import Widget


class FFSMenuWidget(VerticalScroll):
    """Feature Flag Service Menu Widget."""

    def compose(self):
        with Vertical():
            with Container(id="menu-container"):
                yield Label("🚩 Feature Flag Service (FFS) Management", id="menu-title")
                with Vertical(id="menu-buttons"):
                    yield Button("🔍 Search Flags", id="search-btn", variant="primary")
                    yield Button("📖 Get Flag", id="get-btn")
                    yield Button("📊 Evaluate Flag", id="evaluate-btn")
                    yield Button("✅ Check Enabled", id="check-btn")
                    yield Button("🔧 Server Info", id="info-btn")
                    yield Button("❌ Exit", id="exit-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "search-btn":
            self.app.push_screen("ffs_search")
        elif event.button.id == "get-btn":
            self.app.push_screen("ffs_get")
        elif event.button.id == "evaluate-btn":
            self.app.push_screen("ffs_evaluate")
        elif event.button.id == "check-btn":
            self.app.push_screen("ffs_check")
        elif event.button.id == "info-btn":
            self.app.push_screen("ffs_info")
        elif event.button.id == "exit-btn":
            self.app.exit()


class MainMenuScreen(Screen):
    """Main menu screen."""
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("escape", "quit", "Quit", priority=True),
        Binding("up", "move_up", "Move Up", priority=True),
        Binding("down", "move_down", "Move Down", priority=True),
        Binding("enter", "select", "Select", priority=True),
    ]
    
    def __init__(self):
        super().__init__()
        self.selected_index = 0
        self.button_ids = [
            "search-btn",
            "get-btn",
            "evaluate-btn",
            "check-btn",
            "info-btn",
            "exit-btn",
        ]
    
    def compose(self):
        yield Header()
        yield FFSMenuWidget()
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize menu with first button focused."""
        self._update_selection()
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
    
    def on_key(self, event: events.Key) -> None:
        """Handle key events explicitly."""
        if event.key == "escape":
            # On main screen, Esc key exits the application
            self.app.exit()
            event.prevent_default()
        else:
            # Other keys handled by default processing
            super().on_key(event)
    
    def action_move_up(self) -> None:
        """Move selection up."""
        if self.selected_index > 0:
            self.selected_index -= 1
            self._update_selection()
    
    def action_move_down(self) -> None:
        """Move selection down."""
        if self.selected_index < len(self.button_ids) - 1:
            self.selected_index += 1
            self._update_selection()
    
    def action_select(self) -> None:
        """Select the current menu item."""
        button_id = self.button_ids[self.selected_index]
        button = self.query_one(f"#{button_id}", Button)
        button.press()
    
    def _update_selection(self) -> None:
        """Update button selection state."""
        for i, button_id in enumerate(self.button_ids):
            button = self.query_one(f"#{button_id}", Button)
            if i == self.selected_index:
                button.variant = "primary"
                button.focus()
            else:
                button.variant = "default"

