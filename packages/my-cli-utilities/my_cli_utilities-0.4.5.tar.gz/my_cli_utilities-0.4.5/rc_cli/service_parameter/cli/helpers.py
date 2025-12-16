"""Shared helper functions for SP CLI commands."""

from __future__ import annotations

from typing import Any, Dict, Optional

import typer

from rc_cli.common_lib.config import DisplayUtils
from rc_cli.service_parameter.display_manager import SPDisplayManager
from rc_cli.common import DEFAULT_SEPARATOR_WIDTH, format_separator


def display_sp_value(sp_data: Dict[str, Any], sp_description: Optional[str] = None) -> None:
    typer.echo("\n📊 Service Parameter Value:")
    typer.echo(format_separator(DEFAULT_SEPARATOR_WIDTH))

    typer.echo(SPDisplayManager.format_sp_value(sp_data, sp_description))

    typer.echo(format_separator(DEFAULT_SEPARATOR_WIDTH))
    DisplayUtils.format_success("Successfully retrieved service parameter value")


