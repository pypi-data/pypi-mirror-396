# -*- coding: utf-8 -*-

"""Service Parameter (SP) commands for RC CLI.

This file defines the public `sp_app` Typer sub-command group, while each command
implementation is registered from smaller modules in `rc_cli.service_parameter.cli`.
"""

import typer

from rc_cli.service_parameter.cli import (
    register_definition,
    register_get,
    register_list,
    register_search,
    register_server_info,
    register_tui,
)

sp_app = typer.Typer(
    name="sp",
    help="🔧 Service Parameter (SP) management commands",
    add_completion=False,
    rich_markup_mode="rich",
)

register_list.register(sp_app)
register_search.register(sp_app)
register_get.register(sp_app)
register_definition.register(sp_app)
register_server_info.register(sp_app)
register_tui.register(sp_app)

__all__ = ["sp_app"]


