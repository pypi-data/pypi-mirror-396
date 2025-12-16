# -*- coding: utf-8 -*-

"""Main menu screen."""

from textual.containers import Container, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label
from textual.binding import Binding
from textual import events
from textual.widget import Widget


class SPMenuWidget(VerticalScroll):
    """Service Parameter Menu Widget."""
    
    def compose(self):
        with Vertical():
            with Container(id="menu-container"):
                yield Label("🔧 Service Parameter (SP) Management", id="menu-title")
                with Vertical(id="menu-buttons"):
                    yield Button("📋 List All SPs", id="list-btn", variant="primary")
                    yield Button("🔍 Search SPs", id="search-btn")
                    yield Button("📊 Get SP Value", id="get-value-btn")
                    yield Button("📖 Get SP Definition", id="get-definition-btn")
                    yield Button("🔧 Server Info", id="info-btn")
                    yield Button("❌ Exit", id="exit-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "list-btn":
            self.app.push_screen("sp_list")
        elif event.button.id == "search-btn":
            self.app.push_screen("sp_search")
        elif event.button.id == "get-value-btn":
            self.app.push_screen("sp_get_value")
        elif event.button.id == "get-definition-btn":
            self.app.push_screen("sp_definition")
        elif event.button.id == "info-btn":
            self.app.push_screen("sp_info")
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
            "list-btn",
            "search-btn",
            "get-value-btn",
            "get-definition-btn",
            "info-btn",
            "exit-btn",
        ]
    
    def compose(self):
        yield Header()
        yield SPMenuWidget()
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

