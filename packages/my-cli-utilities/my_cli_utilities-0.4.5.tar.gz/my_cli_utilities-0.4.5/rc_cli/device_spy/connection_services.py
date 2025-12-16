"""Facade for device_spy connection services.

Public imports remain stable while implementation lives in `rc_cli.device_spy.connection`.
"""

from rc_cli.device_spy.connection.manager import ConnectionManager

__all__ = ["ConnectionManager"]


