"""Facade for Device Spy command implementations.

This keeps public imports stable (`from rc_cli.device_spy.commands import CLICommands`),
while the implementation lives in `commands_core.py`.
"""

from rc_cli.device_spy.commands_core import CLICommands

__all__ = ["CLICommands"]


