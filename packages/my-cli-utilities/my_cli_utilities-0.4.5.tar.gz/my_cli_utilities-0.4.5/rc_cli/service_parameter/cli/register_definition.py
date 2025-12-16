"""Register `rc sp definition` command."""

from __future__ import annotations

import typer

from rc_cli.common_lib.config import DisplayUtils
from rc_cli.common import async_command
from rc_cli.service_parameter.service import sp_service


def register(app: typer.Typer) -> None:
    @app.command("definition")
    @async_command
    async def get_definition(
        sp_id: str = typer.Argument(..., help="Service parameter ID (e.g., SP-123)"),
    ) -> None:
        """📖 Get service parameter definition by ID."""
        result = await sp_service.get_service_parameter_definition(sp_id)
        if not result.success:
            DisplayUtils.format_error(result.error_message)
            raise typer.Exit(1)

        sp_def = result.data
        typer.echo(f"\n📖 SP Definition")
        typer.echo("-" * 60)
        typer.echo(f"  SP ID: {sp_def.get('id')}")
        typer.echo(f"  Description: {sp_def.get('description')}")


