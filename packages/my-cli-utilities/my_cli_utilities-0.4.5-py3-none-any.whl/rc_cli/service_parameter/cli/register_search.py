"""Register `rc sp search` command."""

from __future__ import annotations

from typing import Optional

import typer

from rc_cli.common_lib.config import DisplayUtils
from rc_cli.service_parameter.service import sp_service
from rc_cli.common import async_command


def register(app: typer.Typer) -> None:
    @app.command("search")
    @async_command
    async def search_service_parameters(
        query: str = typer.Argument(..., help="Search query for service parameter descriptions"),
        limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Limit number of results"),
    ) -> None:
        """🔍 Search service parameters by description."""
        query = (query or "").strip()
        if not query:
            raise typer.Exit(1)

        DisplayUtils.format_search_info(query)

        result = await sp_service.search_service_parameters(query)
        if not result.success:
            DisplayUtils.format_error(result.error_message)
            raise typer.Exit(1)

        matches = result.data
        items = list(matches.items())
        if limit and limit > 0:
            items = items[:limit]

        typer.echo(f"\n📊 Found {len(matches)} matching service parameters")
        typer.echo("-" * 60)
        for sp_id, description in items:
            typer.echo(f"  {sp_id:<20} {description}")


