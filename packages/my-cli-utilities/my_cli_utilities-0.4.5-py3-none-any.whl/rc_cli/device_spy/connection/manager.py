"""High-level connection manager for device_spy."""

from __future__ import annotations

import subprocess
from typing import Dict

from returns.pipeline import flow
from returns.pointfree import bind
from returns.result import Failure, Result, Success

from rc_cli.device_spy.connection.credentials import SSHCredentialProvider
from rc_cli.device_spy.connection.executor import ProcessExecutor, SSHExitCodeInterpreter
from rc_cli.device_spy.connection.host_resolver import HostResolver
from rc_cli.device_spy.connection.types import ADBConnectionConfig, SSHConnectionConfig
from rc_cli.device_spy.connection.validators import DeviceValidator
from rc_cli.device_spy.data_manager import DataManager, get_device_by_udid
from rc_cli.device_spy.result_types import AppError, connection_error, validation_error


class ConnectionManager:
    """Connection manager with decomposed helpers."""

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.host_resolver = HostResolver(data_manager)
        self.credential_provider = SSHCredentialProvider()
        self.process_executor = ProcessExecutor()
        self.exit_code_interpreter = SSHExitCodeInterpreter()
        self.device_validator = DeviceValidator()

    def connect_ssh(self, query: str) -> Result[None, AppError]:
        return flow(
            self.host_resolver.resolve_host_ip(query),
            bind(self._create_ssh_config),
            bind(self._execute_ssh_connection),
            bind(self._handle_ssh_result),
        )

    def _create_ssh_config(self, host_ip: str) -> Result[SSHConnectionConfig, AppError]:
        return self.credential_provider.get_credentials(host_ip).map(
            lambda creds: SSHConnectionConfig(host_ip=host_ip, username=creds[0], password=creds[1])
        )

    def _execute_ssh_connection(self, config: SSHConnectionConfig) -> Result[int, AppError]:
        return self.process_executor.execute_ssh_command(config)

    def _handle_ssh_result(self, exit_code: int) -> Result[None, AppError]:
        status, message = self.exit_code_interpreter.interpret_exit_code(exit_code)
        if status == "connection_error":
            return Failure(
                connection_error(message, "Check network connectivity, host availability, or SSH service status")
            )
        return Success(None)

    def connect_adb(self, udid: str) -> Result[None, AppError]:
        return flow(
            get_device_by_udid(self.data_manager, udid),
            bind(self.device_validator.validate_for_adb),
            bind(self._create_adb_config),
            bind(self._execute_adb_connection),
        )

    @staticmethod
    def _create_adb_config(device: Dict) -> Result[ADBConnectionConfig, AppError]:
        hostname = device.get("hostname")
        adb_port = device.get("adb_port")
        if not hostname or not adb_port:
            return Failure(validation_error("Device missing hostname or ADB port"))
        return Success(ADBConnectionConfig(ip_port=f"{hostname}:{adb_port}"))

    def _execute_adb_connection(self, config: ADBConnectionConfig) -> Result[None, AppError]:
        # Best-effort disconnect
        _ = self.process_executor.execute_adb_command(config.to_disconnect_command(), timeout=5)
        return self.process_executor.execute_adb_command(config.to_connect_command(), config.timeout).bind(
            self._validate_adb_result
        )

    @staticmethod
    def _validate_adb_result(result: subprocess.CompletedProcess) -> Result[None, AppError]:
        if result.returncode == 0:
            return Success(None)
        error_message = result.stderr.strip() if result.stderr else "Unknown ADB error"
        return Failure(connection_error("ADB connection failed", error_message))


