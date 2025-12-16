"""Process execution helpers for SSH and ADB."""

from __future__ import annotations

import subprocess
from typing import Tuple

from returns.result import Failure, Result, Success

from rc_cli.device_spy.result_types import AppError, connection_error, system_error
from rc_cli.device_spy.connection.types import ADBConnectionConfig, SSHConnectionConfig


class ProcessExecutor:
    """Executes system processes with error handling."""

    @staticmethod
    def execute_ssh_command(config: SSHConnectionConfig) -> Result[int, AppError]:
        try:
            result = subprocess.run(config.to_command(), check=False)
            return Success(result.returncode)
        except subprocess.TimeoutExpired:
            return Failure(connection_error(f"SSH connection timeout after {config.timeout}s"))
        except FileNotFoundError:
            return Failure(system_error("sshpass not found", "Install with: brew install sshpass"))
        except KeyboardInterrupt:
            return Success(130)
        except Exception as e:
            return Failure(connection_error("SSH connection failed", str(e)))

    @staticmethod
    def execute_adb_command(command: list[str], timeout: int = 15) -> Result[subprocess.CompletedProcess, AppError]:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
            )
            return Success(result)
        except subprocess.TimeoutExpired:
            return Failure(connection_error(f"ADB command timeout after {timeout}s"))
        except FileNotFoundError:
            return Failure(system_error("adb not found", "Install Android SDK Platform Tools"))
        except Exception as e:
            return Failure(connection_error("ADB command failed", str(e)))


class SSHExitCodeInterpreter:
    """Interprets SSH exit codes."""

    @staticmethod
    def interpret_exit_code(exit_code: int) -> Tuple[str, str]:
        interpretations = {
            0: ("success", "SSH session ended normally"),
            130: ("interrupted", "SSH session interrupted by user"),
            255: ("connection_error", "SSH connection error"),
        }
        return interpretations.get(exit_code, ("unknown", f"SSH connection ended (exit code: {exit_code})"))


