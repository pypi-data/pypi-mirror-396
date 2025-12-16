"""Host query resolution utilities."""

from __future__ import annotations

import re
from typing import Dict, List

from returns.pipeline import flow
from returns.pointfree import bind
from returns.result import Failure, Result, Success

from rc_cli.device_spy.data_manager import DataManager
from rc_cli.device_spy.result_types import (
    AppError,
    StringResult,
    data_not_found_error,
    multiple_matches_error,
    validation_error,
)


class HostResolver:
    """Resolves host queries to IP addresses."""

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    def resolve_host_ip(self, query: str) -> StringResult:
        return flow(
            self.data_manager.get_hosts(),
            bind(self._find_matching_host(query)),
            bind(self._extract_host_ip),
            bind(self._validate_ip),
        )

    def _find_matching_host(self, query: str):
        def find_host(hosts: List[Dict]) -> Result[Dict, AppError]:
            query_lower = query.lower()
            matching_hosts = [
                host
                for host in hosts
                if (
                    query_lower in host.get("hostname", "").lower()
                    or query_lower in host.get("alias", "").lower()
                )
            ]

            if not matching_hosts:
                return Failure(data_not_found_error(f"No host found matching '{query}'"))
            if len(matching_hosts) > 1:
                return Failure(multiple_matches_error(f"Multiple hosts found matching '{query}'", matching_hosts))
            return Success(matching_hosts[0])

        return find_host

    @staticmethod
    def _extract_host_ip(host: Dict) -> StringResult:
        hostname = host.get("hostname")
        if not hostname:
            return Failure(data_not_found_error("Host has no hostname"))
        return Success(hostname)

    @staticmethod
    def _validate_ip(ip: str) -> StringResult:
        pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        if not re.match(pattern, ip):
            return Failure(validation_error(f"Invalid IP address format: {ip}"))
        return Success(ip)


