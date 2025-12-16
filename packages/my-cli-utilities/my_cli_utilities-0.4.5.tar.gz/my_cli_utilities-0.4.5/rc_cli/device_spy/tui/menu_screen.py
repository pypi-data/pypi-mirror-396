# -*- coding: utf-8 -*-

"""Main menu screen for Device Spy TUI."""

from textual.containers import Container, Vertical, VerticalScroll
from textual.widgets import Button, Footer, Header, Label
from textual.widget import Widget

from ...tui_common import BaseScreen


class DeviceSpyMenuWidget(VerticalScroll):
    """Device Spy Menu Widget."""
    
    def compose(self):
        with Vertical():
            with Container(id="menu-container"):
                yield Label("🖥️ Device Spy", id="menu-title")
                with Container(id="menu-buttons"):
                    yield Button("Host info", id="host-btn", variant="primary")
                    yield Button("Device info", id="device-btn")
                    yield Button("Quit", id="quit-btn", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle menu navigation."""
        button_id = event.button.id
        if button_id == "host-btn":
            self.app.push_screen("ds_host_info")
        elif button_id == "device-btn":
            self.app.push_screen("ds_device_info")
        elif button_id == "quit-btn":
            self.app.action_quit()


class DeviceSpyMenuScreen(BaseScreen):
    """Main menu that routes to host/device flows."""

    def compose(self):
        yield Header()
        yield DeviceSpyMenuWidget()
        yield Footer()

