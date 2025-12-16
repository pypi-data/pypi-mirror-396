"""Facade for Service Parameter service.

Keeps public imports stable (`from rc_cli.service_parameter.service import sp_service`)
while implementation lives in `service_core.py`.
"""

from rc_cli.service_parameter.service_core import SPClientError, SPService


def _get_sp_service():
    """Lazy import to avoid circular dependencies."""
    from rc_cli.common.service_factory import ServiceFactory

    return ServiceFactory.get_sp_service()


sp_service = _get_sp_service()

__all__ = ["SPClientError", "SPService", "sp_service"]


