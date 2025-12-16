"""Shared helpers for Account Pool TUI."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Dict, Optional

from textual.widgets import Label, TextArea
from textual.widget import Widget

from rc_cli.account_pool.service import AccountService
from rc_cli.common.service_factory import ServiceFactory
from rc_cli.tui_common import BaseResultWidget as CommonBaseResultWidget

from rc_cli.account_pool.tui_components.constants import DEFAULT_SEPARATOR_WIDTH

logger = logging.getLogger(__name__)


class AccountPoolBaseResultWidget(CommonBaseResultWidget):
    """Base widget for Account Pool result pages."""

    def _format_account_info(
        self,
        account: Dict,
        separator_width: int = DEFAULT_SEPARATOR_WIDTH,
        use_na_for_missing: bool = False,
    ) -> str:
        lines: list[str] = []
        separator = "=" * separator_width
        lines.append(separator)
        lines.append("Account Information")
        lines.append(separator)

        def add_field(emoji: str, label: str, value: Any, show_if_none: bool = False) -> None:
            if value is not None or show_if_none:
                display_value = value if value is not None else "N/A"
                lines.append(f"{emoji} {label}: {display_value}")

        if use_na_for_missing:
            add_field("📱", "Phone", account.get("mainNumber"), show_if_none=True)
            add_field("🆔", "Account ID", account.get("accountId"), show_if_none=True)
            add_field("🏷️ ", "Type", account.get("accountType"), show_if_none=True)
            add_field("🌐", "Environment", account.get("envName"), show_if_none=True)
            add_field("📧", "Email Domain", account.get("companyEmailDomain"), show_if_none=True)
            add_field("📅", "Created", account.get("createdAt"), show_if_none=True)
            add_field("🔗", "MongoDB ID", account.get("_id"), show_if_none=True)
        else:
            if account.get("mainNumber"):
                lines.append(f"📱 Phone: {account['mainNumber']}")
            if account.get("accountId"):
                lines.append(f"🆔 Account ID: {account['accountId']}")
            if account.get("accountType"):
                lines.append(f"🏷️  Type: {account['accountType']}")
            if account.get("envName"):
                lines.append(f"🌐 Environment: {account['envName']}")
            if account.get("companyEmailDomain"):
                lines.append(f"📧 Email Domain: {account['companyEmailDomain']}")
            if account.get("createdAt"):
                lines.append(f"📅 Created: {account['createdAt']}")
            if account.get("loginTimes") is not None:
                lines.append(f"🔢 Login Times: {account['loginTimes']}")
            if account.get("_id"):
                lines.append(f"🔗 MongoDB ID: {account['_id']}")

        locked = account.get("locked", [])
        status = "🔒 Locked" if locked else "✅ Available"
        lines.append(f"🔐 Status: {status}")

        if locked:
            lines.append("🛑 Lock Details:")
            for item in locked:
                if isinstance(item, dict):
                    lines.append(f"  • Type: {item.get('accountType', 'N/A')}")

        lines.append(separator)
        return "\n".join(lines)

    async def query_and_display_account(
        self,
        query_func: Callable[..., Any],
        title_label_id: str,
        loading_msg: str,
        success_msg: str = "✅ Account retrieved",
        validation_func: Optional[Callable[[], tuple[bool, str | None]]] = None,
        validation_error_msg: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Run a blocking account query in executor and render the output into #result-area."""
        if validation_func:
            is_valid, error_msg = validation_func()
            if not is_valid:
                self.query_one(f"#{title_label_id}", Label).update(
                    f"⚠️  {error_msg or validation_error_msg or 'Invalid input'}"
                )
                return

        result_area = self.query_one("#result-area", TextArea)
        self.query_one(f"#{title_label_id}", Label).update(loading_msg)
        result_area.text = ""

        account_service: AccountService = ServiceFactory.get_account_service()
        loop = asyncio.get_event_loop()

        def execute_query():
            return query_func(account_service, **kwargs)

        try:
            result = await loop.run_in_executor(None, execute_query)
        except Exception as e:
            logger.exception("Account query failed")
            self.query_one(f"#{title_label_id}", Label).update(f"❌ Error: {str(e)}")
            result_area.text = f"Error: {str(e)}"
            return

        if result is None or (isinstance(result, tuple) and result[0] is None):
            error_msg = result[1] if isinstance(result, tuple) else "Failed to get account"
            self.query_one(f"#{title_label_id}", Label).update(f"❌ {error_msg}")
            result_area.text = f"Error: {error_msg}"
            return

        account = result if not isinstance(result, tuple) else result[0]
        result_area.text = self._format_account_info(account)
        self.query_one(f"#{title_label_id}", Label).update(success_msg)


