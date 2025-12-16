"""Register `rc sp list` command."""

from __future__ import annotations

from typing import Optional

import typer

from rc_cli.common_lib.config import DisplayUtils
from rc_cli.service_parameter.service import sp_service
from rc_cli.common import async_command


def register(app: typer.Typer) -> None:
    @app.command("list")
    @async_command
    async def list_service_parameters(
        limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Limit the number of results to display"),
    ) -> None:
        """📋 List all service parameters."""
        DisplayUtils.format_search_info("All Service Parameters")

        result = await sp_service.get_all_service_parameters()
        if not result.success:
            DisplayUtils.format_error(result.error_message)
            raise typer.Exit(1)

        service_parameters = result.data
        total_count = result.count

        typer.echo(f"\n📊 Found {total_count} service parameters")
        typer.echo("-" * 60)

        items_to_show = service_parameters
        if limit and limit > 0:
            items_to_show = dict(list(service_parameters.items())[:limit])
            if limit < total_count:
                typer.echo(f"📌 Showing first {limit} results")

        for sp_id, description in items_to_show.items():
            typer.echo(f"  {sp_id:<20} {description}")


