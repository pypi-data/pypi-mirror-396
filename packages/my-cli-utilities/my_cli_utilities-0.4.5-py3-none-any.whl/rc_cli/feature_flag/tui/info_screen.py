# -*- coding: utf-8 -*-

"""Screen for server information."""

from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Label, TextArea
from ...tui_common import BaseInfoScreen, BaseInfoWidget
from ..service import ffs_service
from ..display_manager import FFSDisplayManager


class FFSInfoWidget(BaseInfoWidget):
    """Widget for server information."""
    
    def compose(self):
        with Vertical():
            with Container(id="info-container"):
                yield Label("🔧 Server Information", id="info-title")
                yield TextArea(id="info-area", read_only=True)
                with Horizontal(id="info-buttons"):
                    yield Button("Refresh", id="refresh-btn", variant="primary")
                    yield Button("Clear Cache", id="clear-cache-btn")
                    yield Button("Back", id="back-btn")
    
    def on_mount(self) -> None:
        """Initialize the info screen."""
        super().on_mount()
        self._load_server_info()
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "refresh-btn":
            self._load_server_info()
        elif event.button.id == "clear-cache-btn":
            ffs_service.clear_cache()
            self._load_server_info()
            self.query_one("#info-title", Label).update(
                "✅ Cache cleared successfully"
            )
        elif event.button.id == "back-btn":
            self.app.action_back()
    
    def _load_server_info(self) -> None:
        """Load server information."""
        server_info = ffs_service.get_server_info()
        formatted_output = FFSDisplayManager.format_server_info(server_info)
        
        info_area = self.query_one("#info-area", TextArea)
        info_area.text = formatted_output
        self.query_one("#info-title", Label).update("🔧 Server Information")


class FFSInfoScreen(BaseInfoScreen):
    """Screen for server information."""
    
    def compose(self):
        yield Header()
        yield FFSInfoWidget()
        yield Footer()
