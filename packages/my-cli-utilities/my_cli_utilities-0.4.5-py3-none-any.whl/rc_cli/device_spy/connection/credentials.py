"""Credential providers for SSH / ADB."""

from __future__ import annotations

from returns.result import Failure, Result, Success

from rc_cli.common_lib.system_helpers import SSHConfig
from rc_cli.device_spy.result_types import AppError, system_error


class SSHCredentialProvider:
    """Provides SSH credentials."""

    @staticmethod
    def get_credentials(host_ip: str) -> Result[tuple[str, str], AppError]:
        try:
            ssh_config = SSHConfig()
            user, password, _ = ssh_config.get_ssh_credentials(host_ip)
            return Success((user, password))
        except Exception as e:
            return Failure(system_error("Failed to get SSH credentials", str(e)))


