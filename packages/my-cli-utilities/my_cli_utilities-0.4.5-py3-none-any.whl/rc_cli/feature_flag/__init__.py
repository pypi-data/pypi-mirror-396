"""Feature Flag Service module for RC CLI."""

from .commands import ffs_app
from .service import ffs_service, FFSService

__all__ = ['ffs_app', 'ffs_service', 'FFSService']

