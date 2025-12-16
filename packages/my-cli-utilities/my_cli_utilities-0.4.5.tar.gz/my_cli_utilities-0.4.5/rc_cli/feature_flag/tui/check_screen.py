# -*- coding: utf-8 -*-

"""Screen for checking if feature is enabled."""

import json
from typing import Dict, Any
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Label, TextArea
from ...tui_common import BaseResultScreen, BaseResultWidget
from ..service import ffs_service


class FFSCheckWidget(BaseResultWidget):
    """Widget for checking if feature is enabled."""
    
    def compose(self):
        with Vertical():
            with Container(id="check-container"):
                yield Label("✅ Check Feature Enabled", id="check-title")
                yield Input(placeholder="Flag ID", id="flag-id-input")
                yield Input(placeholder="Account ID (optional)", id="account-id-input")
                yield Input(placeholder="Extension ID (optional)", id="extension-id-input")
                yield TextArea(id="result-area", read_only=True)
                with Horizontal(id="check-buttons"):
                    yield Button("Check", id="check-btn", variant="primary")
                    yield Button("Clear", id="clear-btn")
                    yield Button("Back", id="back-btn")
    
    def on_mount(self) -> None:
        """Initialize the check screen."""
        super().on_mount()
        self.query_one("#flag-id-input", Input).focus()
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "check-btn":
            await self._check_enabled()
        elif event.button.id == "clear-btn":
            self.query_one("#flag-id-input", Input).value = ""
            self.query_one("#account-id-input", Input).value = ""
            self.query_one("#extension-id-input", Input).value = ""
            self.query_one("#result-area", TextArea).text = ""
        elif event.button.id == "back-btn":
            self.app.action_back()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "extension-id-input":
            await self._check_enabled()
        elif event.input.id == "flag-id-input":
            self.query_one("#account-id-input", Input).focus()
        elif event.input.id == "account-id-input":
            self.query_one("#extension-id-input", Input).focus()
    
    async def _check_enabled(self) -> None:
        """Check if feature is enabled."""
        flag_id = self.query_one("#flag-id-input", Input).value.strip()
        account_id = self.query_one("#account-id-input", Input).value.strip()
        extension_id = self.query_one("#extension-id-input", Input).value.strip()
        
        if not flag_id:
            self.query_one("#check-title", Label).update(
                "⚠️  Please enter Flag ID"
            )
            return
        
        # Build context
        context: Dict[str, Any] = {}
        if account_id:
            context["accountId"] = account_id
        if extension_id:
            context["extensionId"] = extension_id
        
        result_area = self.query_one("#result-area", TextArea)
        self.query_one("#check-title", Label).update("✅ Checking...")
        result_area.text = ""
        
        try:
            result = await ffs_service.check_feature_enabled(flag_id, context)
            
            if not result.success:
                self.query_one("#check-title", Label).update(
                    f"❌ Error: {result.error_message}"
                )
                result_area.text = f"Error: {result.error_message}"
                return
            
            check_data = result.data
            enabled = check_data.get("enabled", False)
            
            status_text = "ENABLED ✅" if enabled else "DISABLED ❌"
            result_text = f"Flag ID: {check_data.get('flagId', 'N/A')}\n"
            result_text += f"Status: {status_text}\n"
            result_text += f"Matched Rule ID: {check_data.get('matchedRuleId', 'N/A')}\n"
            if context:
                result_text += f"Context: {json.dumps(context, indent=2)}"
            
            result_area.text = result_text
            self.query_one("#check-title", Label).update(
                f"✅ Feature {status_text}"
            )
            
        except Exception as e:
            self.query_one("#check-title", Label).update(
                f"❌ Error: {str(e)}"
            )
            result_area.text = f"Error: {str(e)}"


class FFSCheckScreen(BaseResultScreen):
    """Screen for checking if feature is enabled."""
    
    def compose(self):
        yield Header()
        yield FFSCheckWidget()
        yield Footer()
