"""Register `rc sp get` and `rc sp get-by-phone` commands."""

from __future__ import annotations

from typing import Any, Dict, Optional

import typer

from rc_cli.common_lib.config import DisplayUtils
from rc_cli.service_parameter.cli.helpers import display_sp_value
from rc_cli.service_parameter.service import sp_service
from rc_cli.common import async_command


async def _get_sp_value_with_description(
    sp_id: str,
    account_id: str,
    env_name: str = "webaqaxmn",
) -> tuple[Dict[str, Any], Optional[str]]:
    result = await sp_service.get_service_parameter_value(sp_id, account_id, env_name)
    if not result.success:
        DisplayUtils.format_error(result.error_message)
        raise typer.Exit(1)

    sp_data = result.data
    sp_def_result = await sp_service.get_service_parameter_definition(sp_id)
    sp_description = sp_def_result.data.get("description") if sp_def_result.success else None
    return sp_data, sp_description


def register(app: typer.Typer) -> None:
    @app.command("get")
    @async_command
    async def get_sp_value(
        sp_id: str = typer.Argument(..., help="Service parameter ID (e.g., SP-123)"),
        account_id: str = typer.Argument(..., help="Account ID"),
        env_name: str = typer.Option("webaqaxmn", "--env", "-e", help="Environment name"),
    ) -> None:
        """📊 Get service parameter value for an account ID."""
        sp_data, sp_desc = await _get_sp_value_with_description(sp_id, account_id, env_name)
        display_sp_value(sp_data, sp_desc)

    @app.command("get-by-phone")
    @async_command
    async def get_sp_value_by_phone(
        sp_id: str = typer.Argument(..., help="Service parameter ID (e.g., SP-123)"),
        phone_number: str = typer.Argument(..., help="Phone number (with or without + prefix)"),
        env_name: str = typer.Option("webaqaxmn", "--env", "-e", help="Environment name"),
    ) -> None:
        """📞 Get service parameter value by phone number."""
        result = await sp_service.get_service_parameter_value_by_phone(sp_id, phone_number, env_name)
        if not result.success:
            DisplayUtils.format_error(result.error_message)
            raise typer.Exit(1)

        sp_def_result = await sp_service.get_service_parameter_definition(sp_id)
        sp_description = sp_def_result.data.get("description") if sp_def_result.success else None
        display_sp_value(result.data, sp_description)


