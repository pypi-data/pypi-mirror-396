# -*- coding: utf-8 -*-

"""Screen for evaluating feature flag."""

import json
from typing import Dict, Any
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Label, TextArea
from ...tui_common import BaseResultScreen, BaseResultWidget
from ..service import ffs_service
from ..display_manager import FFSDisplayManager


class FFSEvaluateWidget(BaseResultWidget):
    """Widget for evaluating feature flag."""
    
    def compose(self):
        with Vertical():
            with Container(id="evaluate-container"):
                yield Label("📊 Evaluate Feature Flag", id="evaluate-title")
                yield Input(placeholder="Flag ID", id="flag-id-input")
                yield Input(placeholder="Account ID (optional)", id="account-id-input")
                yield Input(placeholder="Extension ID (optional)", id="extension-id-input")
                yield Input(placeholder="Email Domain (optional)", id="email-domain-input")
                yield TextArea(id="result-area", read_only=True)
                with Horizontal(id="evaluate-buttons"):
                    yield Button("Evaluate", id="evaluate-btn", variant="primary")
                    yield Button("Clear", id="clear-btn")
                    yield Button("Back", id="back-btn")
    
    def on_mount(self) -> None:
        """Initialize the evaluate screen."""
        super().on_mount()
        self.query_one("#flag-id-input", Input).focus()
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "evaluate-btn":
            await self._evaluate_flag()
        elif event.button.id == "clear-btn":
            self.query_one("#flag-id-input", Input).value = ""
            self.query_one("#account-id-input", Input).value = ""
            self.query_one("#extension-id-input", Input).value = ""
            self.query_one("#email-domain-input", Input).value = ""
            self.query_one("#result-area", TextArea).text = ""
        elif event.button.id == "back-btn":
            self.app.action_back()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "email-domain-input":
            await self._evaluate_flag()
        elif event.input.id == "flag-id-input":
            self.query_one("#account-id-input", Input).focus()
        elif event.input.id == "account-id-input":
            self.query_one("#extension-id-input", Input).focus()
        elif event.input.id == "extension-id-input":
            self.query_one("#email-domain-input", Input).focus()
    
    async def _evaluate_flag(self) -> None:
        """Evaluate feature flag."""
        flag_id = self.query_one("#flag-id-input", Input).value.strip()
        account_id = self.query_one("#account-id-input", Input).value.strip()
        extension_id = self.query_one("#extension-id-input", Input).value.strip()
        email_domain = self.query_one("#email-domain-input", Input).value.strip()
        
        if not flag_id:
            self.query_one("#evaluate-title", Label).update(
                "⚠️  Please enter Flag ID"
            )
            return
        
        # Build context
        context: Dict[str, Any] = {}
        if account_id:
            context["accountId"] = account_id
        if extension_id:
            context["extensionId"] = extension_id
        if email_domain:
            context["emailDomain"] = email_domain
        
        result_area = self.query_one("#result-area", TextArea)
        self.query_one("#evaluate-title", Label).update("📊 Evaluating...")
        result_area.text = ""
        
        try:
            result = await ffs_service.evaluate_feature_flag(flag_id, context)
            
            if not result.success:
                self.query_one("#evaluate-title", Label).update(
                    f"❌ Error: {result.error_message}"
                )
                result_area.text = f"Error: {result.error_message}"
                return
            
            eval_data = result.data
            formatted_output = FFSDisplayManager.format_evaluation(eval_data)
            
            result_area.text = formatted_output
            self.query_one("#evaluate-title", Label).update(
                f"✅ Flag {flag_id} evaluated"
            )
            
        except Exception as e:
            self.query_one("#evaluate-title", Label).update(
                f"❌ Error: {str(e)}"
            )
            result_area.text = f"Error: {str(e)}"


class FFSEvaluateScreen(BaseResultScreen):
    """Screen for evaluating feature flag."""
    
    def compose(self):
        yield Header()
        yield FFSEvaluateWidget()
        yield Footer()
