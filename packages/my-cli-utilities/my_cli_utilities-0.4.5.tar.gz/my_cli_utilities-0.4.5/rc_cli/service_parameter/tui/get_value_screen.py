# -*- coding: utf-8 -*-

"""Screen for getting SP value."""

from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Label, Select, TextArea
from ...tui_common import BaseResultScreen, BaseResultWidget
from ..service import sp_service
from ..display_manager import SPDisplayManager
from rc_cli.tui_prefill import consume_prefill


class SPGetValueWidget(BaseResultWidget):
    """Widget for getting SP value."""
    
    def compose(self):
        with Vertical():
            with Container(id="get-container"):
                yield Label("📊 Get Service Parameter Value", id="get-title")
                yield Input(placeholder="SP ID (e.g., SP-123)", id="sp-id-input")
                yield Input(placeholder="Phone Number (e.g., 16789350903)", id="phone-input")
                yield Select(
                    [
                        ("webaqaxmn", "webaqaxmn"),
                        ("xmn-up", "xmn-up"),
                        ("glpdevxmn", "glpdevxmn"),
                    ],
                    id="env-select",
                    value="webaqaxmn",
                    prompt="Select environment..."
                )
                yield TextArea(id="result-area", read_only=True)
                with Horizontal(id="get-buttons"):
                    yield Button("Get Value", id="get-btn", variant="primary")
                    yield Button("Clear", id="clear-btn")
                    yield Button("Back", id="back-btn")
    
    def on_mount(self) -> None:
        """Initialize the get value screen."""
        super().on_mount()
        prefill = consume_prefill(self.app, "sp_get_value")
        sp_id = prefill.get("sp_id")
        if sp_id:
            self.query_one("#sp-id-input", Input).value = sp_id
            self.query_one("#phone-input", Input).focus()
            return
        self.query_one("#sp-id-input", Input).focus()
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "get-btn":
            await self._get_sp_value()
        elif event.button.id == "clear-btn":
            self.query_one("#sp-id-input", Input).value = ""
            self.query_one("#phone-input", Input).value = ""
            env_select = self.query_one("#env-select", Select)
            env_select.value = "webaqaxmn"
            self.query_one("#result-area", TextArea).text = ""
        elif event.button.id == "back-btn":
            self.app.action_back()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "phone-input":
            self.query_one("#env-select", Select).focus()
        elif event.input.id == "sp-id-input":
            self.query_one("#phone-input", Input).focus()
    
    async def _get_sp_value(self) -> None:
        """Get SP value by phone number."""
        sp_id = self.query_one("#sp-id-input", Input).value.strip()
        phone = self.query_one("#phone-input", Input).value.strip()
        env_select = self.query_one("#env-select", Select)
        env_name = env_select.value if env_select.value and isinstance(env_select.value, str) else "webaqaxmn"
        
        if not sp_id or not phone:
            self.query_one("#get-title", Label).update(
                "⚠️  Please enter both SP ID and Phone Number"
            )
            return
        
        result_area = self.query_one("#result-area", TextArea)
        self.query_one("#get-title", Label).update(f"📊 Loading from {env_name}...")
        result_area.text = ""
        
        try:
            # Use the new method that resolves phone to account ID
            result = await sp_service.get_service_parameter_value_by_phone(sp_id, phone, env_name)
            
            if not result.success:
                error_msg = result.error_message
                self.query_one("#get-title", Label).update(
                    f"❌ Error: {error_msg}"
                )
                
                # Provide helpful suggestions
                suggestion = ""
                if "not found in environment" in error_msg:
                    suggestion = (
                        f"\n\n💡 Suggestions:\n"
                        f"  • Verify the phone number is correct\n"
                        f"  • Try a different environment (webaqaxmn, glpdevxmn)\n"
                        f"  • Check if the account exists in {env_name}\n"
                        f"  • Use 'rc account list {env_name}' to see available accounts"
                    )
                
                result_area.text = f"Error: {error_msg}{suggestion}"
                return
            
            sp_data = result.data
            formatted_output = SPDisplayManager.format_sp_value(sp_data)
            
            result_area.text = formatted_output
            self.query_one("#get-title", Label).update(
                f"✅ SP {sp_id} value retrieved"
            )
            
        except Exception as e:
            self.query_one("#get-title", Label).update(
                f"❌ Error: {str(e)}"
            )
            result_area.text = f"Error: {str(e)}"


class SPGetValueScreen(BaseResultScreen):
    """Screen for getting SP value."""
    
    def compose(self):
        yield Header()
        yield SPGetValueWidget()
        yield Footer()
