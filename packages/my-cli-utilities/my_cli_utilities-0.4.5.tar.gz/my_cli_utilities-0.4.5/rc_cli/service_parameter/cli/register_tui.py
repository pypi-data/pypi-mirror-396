"""Register `rc sp tui` command."""

from __future__ import annotations

import typer

from rc_cli.service_parameter.tui import run_tui


def register(app: typer.Typer) -> None:
    @app.command("tui")
    def tui() -> None:
        """🖥️ Launch interactive TUI for Service Parameters."""
        run_tui()


