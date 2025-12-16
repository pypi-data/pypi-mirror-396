"""Validation helpers for connection operations."""

from __future__ import annotations

from typing import Dict

from returns.result import Failure, Result, Success

from rc_cli.device_spy.result_types import AppError, validation_error


class DeviceValidator:
    """Validates device for ADB connection."""

    @staticmethod
    def validate_for_adb(device: Dict) -> Result[Dict, AppError]:
        if device.get("is_locked"):
            return Failure(validation_error(f"Device {device.get('udid', 'unknown')} is locked"))

        if device.get("platform") != "android":
            return Failure(validation_error("Only Android devices support ADB connect"))

        if not device.get("adb_port"):
            return Failure(validation_error("Device has no adb_port information"))

        if not device.get("hostname"):
            return Failure(validation_error("Device has no hostname information"))

        return Success(device)


