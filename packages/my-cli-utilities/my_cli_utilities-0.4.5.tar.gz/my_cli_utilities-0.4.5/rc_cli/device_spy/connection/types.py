"""Connection-related data structures."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SSHConnectionConfig:
    """SSH connection configuration."""

    host_ip: str
    username: str
    password: str
    timeout: int = 30

    def to_command(self) -> list[str]:
        return [
            "sshpass",
            "-p",
            self.password,
            "ssh",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-o",
            "ServerAliveInterval=60",
            "-o",
            "ServerAliveCountMax=30",
            "-o",
            "TCPKeepAlive=yes",
            "-o",
            f"ConnectTimeout={self.timeout}",
            f"{self.username}@{self.host_ip}",
        ]


@dataclass(frozen=True)
class ADBConnectionConfig:
    """ADB connection configuration."""

    ip_port: str
    timeout: int = 15

    def to_connect_command(self) -> list[str]:
        return ["adb", "connect", self.ip_port]

    def to_disconnect_command(self) -> list[str]:
        return ["adb", "disconnect", self.ip_port]


