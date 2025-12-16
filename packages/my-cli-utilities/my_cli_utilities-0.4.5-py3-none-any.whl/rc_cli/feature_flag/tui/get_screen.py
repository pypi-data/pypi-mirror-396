# -*- coding: utf-8 -*-

"""Screen for getting feature flag."""

from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Label, TextArea
from ...tui_common import BaseResultScreen, BaseResultWidget
from ..service import ffs_service
from ..display_manager import FFSDisplayManager
from rc_cli.tui_prefill import consume_prefill


class FFSGetWidget(BaseResultWidget):
    """Widget for getting feature flag."""
    
    def compose(self):
        with Vertical():
            with Container(id="get-container"):
                yield Label("📖 Get Feature Flag", id="get-title")
                yield Input(placeholder="Flag ID (e.g., rc-app-mobile.user.sms_translate_sms)", id="flag-id-input")
                yield TextArea(id="result-area", read_only=True)
                with Horizontal(id="get-buttons"):
                    yield Button("Get Flag", id="get-btn", variant="primary")
                    yield Button("Clear", id="clear-btn")
                    yield Button("Back", id="back-btn")
    
    def on_mount(self) -> None:
        """Initialize the get screen."""
        super().on_mount()
        prefill = consume_prefill(self.app, "ffs_get")
        flag_id = prefill.get("flag_id")
        if flag_id:
            self.query_one("#flag-id-input", Input).value = flag_id
        self.query_one("#flag-id-input", Input).focus()
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "get-btn":
            await self._get_flag()
        elif event.button.id == "clear-btn":
            self.query_one("#flag-id-input", Input).value = ""
            self.query_one("#result-area", TextArea).text = ""
        elif event.button.id == "back-btn":
            self.app.action_back()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "flag-id-input":
            await self._get_flag()
    
    async def _get_flag(self) -> None:
        """Get feature flag."""
        flag_id = self.query_one("#flag-id-input", Input).value.strip()
        
        if not flag_id:
            self.query_one("#get-title", Label).update(
                "⚠️  Please enter Flag ID"
            )
            return
        
        result_area = self.query_one("#result-area", TextArea)
        self.query_one("#get-title", Label).update("📖 Loading...")
        result_area.text = ""
        
        try:
            result = await ffs_service.get_feature_flag(flag_id)
            
            if not result.success:
                self.query_one("#get-title", Label).update(
                    f"❌ Error: {result.error_message}"
                )
                result_area.text = f"Error: {result.error_message}"
                return
            
            flag_data = result.data
            formatted_output = FFSDisplayManager.format_flag(flag_data)
            
            result_area.text = formatted_output
            self.query_one("#get-title", Label).update(
                f"✅ Flag {flag_id} retrieved"
            )
            
        except Exception as e:
            self.query_one("#get-title", Label).update(
                f"❌ Error: {str(e)}"
            )
            result_area.text = f"Error: {str(e)}"


class FFSGetScreen(BaseResultScreen):
    """Screen for getting feature flag."""
    
    def compose(self):
        yield Header()
        yield FFSGetWidget()
        yield Footer()
