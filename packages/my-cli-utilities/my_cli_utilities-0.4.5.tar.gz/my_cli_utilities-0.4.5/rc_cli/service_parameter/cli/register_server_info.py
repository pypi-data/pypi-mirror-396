"""Register `rc sp server-info` and `rc sp clear-cache` commands."""

from __future__ import annotations

import typer

from rc_cli.common_lib.config import DisplayUtils
from rc_cli.service_parameter.service import sp_service


def register(app: typer.Typer) -> None:
    @app.command("server-info")
    def server_info() -> None:
        """🔧 Show SP service configuration and cache info."""
        info = sp_service.get_server_info()
        typer.echo("\n🔧 SP Server Info")
        typer.echo("-" * 60)
        typer.echo(f"  Internal API: {info.get('server', {}).get('intapiBaseUrl')}")
        typer.echo(f"  GitLab API:   {info.get('server', {}).get('gitlabBaseUrl')}")
        typer.echo(f"  Timeout:      {info.get('server', {}).get('timeout')}s")
        typer.echo(f"  Cache size:   {info.get('cache', {}).get('size')}")

    @app.command("clear-cache")
    def clear_cache() -> None:
        """🧹 Clear SP service in-memory cache."""
        sp_service.clear_cache()
        DisplayUtils.format_success("Cache cleared")


