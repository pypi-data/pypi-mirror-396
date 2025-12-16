# -*- coding: utf-8 -*-

"""Screen for getting SP definition."""

from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Label, TextArea
from ...tui_common import BaseResultScreen, BaseResultWidget
from ..service import sp_service
from ..display_manager import SPDisplayManager
from rc_cli.tui_prefill import consume_prefill


class SPDefinitionWidget(BaseResultWidget):
    """Widget for getting SP definition."""
    
    def compose(self):
        with Vertical():
            with Container(id="definition-container"):
                yield Label("📖 Get Service Parameter Definition", id="definition-title")
                yield Input(placeholder="SP ID (e.g., SP-123)", id="sp-id-input")
                yield TextArea(id="result-area", read_only=True)
                with Horizontal(id="definition-buttons"):
                    yield Button("Get Definition", id="get-btn", variant="primary")
                    yield Button("Clear", id="clear-btn")
                    yield Button("Back", id="back-btn")
    
    def on_mount(self) -> None:
        """Initialize the definition screen."""
        super().on_mount()
        prefill = consume_prefill(self.app, "sp_definition")
        sp_id = prefill.get("sp_id")
        if sp_id:
            self.query_one("#sp-id-input", Input).value = sp_id
        self.query_one("#sp-id-input", Input).focus()
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "get-btn":
            await self._get_sp_definition()
        elif event.button.id == "clear-btn":
            self.query_one("#sp-id-input", Input).value = ""
            self.query_one("#result-area", TextArea).text = ""
        elif event.button.id == "back-btn":
            self.app.action_back()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "sp-id-input":
            await self._get_sp_definition()
    
    async def _get_sp_definition(self) -> None:
        """Get SP definition."""
        sp_id = self.query_one("#sp-id-input", Input).value.strip()
        
        if not sp_id:
            self.query_one("#definition-title", Label).update(
                "⚠️  Please enter SP ID"
            )
            return
        
        result_area = self.query_one("#result-area", TextArea)
        self.query_one("#definition-title", Label).update("📖 Loading...")
        result_area.text = ""
        
        try:
            result = await sp_service.get_service_parameter_definition(sp_id)
            
            if not result.success:
                self.query_one("#definition-title", Label).update(
                    f"❌ Error: {result.error_message}"
                )
                result_area.text = f"Error: {result.error_message}"
                return
            
            sp_definition = result.data
            formatted_output = SPDisplayManager.format_sp_definition(sp_definition)
            
            result_area.text = formatted_output
            self.query_one("#definition-title", Label).update(
                f"✅ SP {sp_id} definition retrieved"
            )
            
        except Exception as e:
            self.query_one("#definition-title", Label).update(
                f"❌ Error: {str(e)}"
            )
            result_area.text = f"Error: {str(e)}"


class SPDefinitionScreen(BaseResultScreen):
    """Screen for getting SP definition."""
    
    def compose(self):
        yield Header()
        yield SPDefinitionWidget()
        yield Footer()
