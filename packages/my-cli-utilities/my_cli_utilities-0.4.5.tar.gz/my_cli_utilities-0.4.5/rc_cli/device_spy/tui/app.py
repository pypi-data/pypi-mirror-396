# -*- coding: utf-8 -*-

"""Device Spy TUI application."""

from textual.app import App
from textual.binding import Binding

from ..data_manager import DataManager
from .menu_screen import DeviceSpyMenuScreen
from .host_screen import HostInfoScreen
from .device_screen import DeviceInfoScreen
from rc_cli.tui_css_common import COMMON_TUI_CSS


class DeviceSpyTUIApp(App):
    """Main TUI application for Device Spy."""

    CSS = COMMON_TUI_CSS + """

    #menu-container {
        width: 60;
        height: auto;
        border: solid $primary;
        padding: 1;
    }

    #menu-title {
        text-align: center;
        width: 100%;
        margin: 1;
    }

    #menu-buttons > Button {
        width: 100%;
        margin: 1;
    }

    #host-container, #device-container {
        width: 110;
        height: auto;
        border: solid $primary;
        padding: 1;
    }

    #host-title, #device-title {
        text-align: center;
        width: 100%;
        margin: 1;
    }

    #host-query, #device-udid, #platform-select {
        width: 100%;
        margin: 1;
    }

    #host-buttons, #device-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }

    #host-buttons > Button, #device-buttons > Button {
        margin: 1;
    }

    #result-area, #info-area {
        height: 28;
        width: 100%;
        scrollbar-size: 1 1;
    }
    """

    TITLE = "Device Spy TUI"
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
    ]

    def on_mount(self) -> None:
        """Set up the initial screen."""
        self.data_manager = DataManager()
        self.push_screen("menu")

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def action_back(self) -> None:
        """Go back to previous screen."""
        if len(self.screen_stack) > 1:
            self.pop_screen()

    def push_screen(self, screen_name: str) -> None:
        """Push a screen by name."""
        screens = {
            "menu": DeviceSpyMenuScreen(),
            "ds_host_info": HostInfoScreen(),
            "ds_device_info": DeviceInfoScreen(),
        }

        screen = screens.get(screen_name)
        if screen:
            super().push_screen(screen)


def run_tui() -> None:
    """Run the Device Spy TUI application."""
    try:
        app = DeviceSpyTUIApp()
        app.run()
    except Exception as exc:
        import sys

        print(f"Error running TUI: {exc}", file=sys.stderr)
        raise

