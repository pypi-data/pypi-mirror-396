# -*- coding: utf-8 -*-

"""Device Spy core command implementations (split from commands.py)."""

from __future__ import annotations

import json
from enum import Enum
from typing import Dict, List

import typer
from returns.result import Failure, Success

from rc_cli.device_spy.connection_services import ConnectionManager
from rc_cli.device_spy.data_manager import (
    DataManager,
    get_available_devices_by_platform,
    get_device_by_udid,
    get_device_summary,
    get_devices_by_host,
    get_hosts_by_query,
)
from rc_cli.device_spy.display_managers import DeviceDisplayManager
from rc_cli.device_spy.host_display import HostDisplayManager
from rc_cli.device_spy.result_types import (
    AppError,
    ErrorDisplay,
    ErrorType,
    ResultHandler,
    validation_error,
)


class Platform(str, Enum):
    """Supported device platforms."""

    ANDROID = "android"
    IOS = "ios"


class InputValidator:
    """Input validation utilities for CLI commands."""

    @staticmethod
    def validate_non_empty(value: str, field_name: str) -> str:
        value = value.strip()
        if not value:
            error = validation_error(f"{field_name} cannot be empty")
            ErrorDisplay.show_error(error)
            raise typer.Exit(1)
        return value

    @staticmethod
    def validate_platform(platform: str) -> str:
        platform = platform.lower().strip()
        if platform not in [p.value for p in Platform]:
            error = validation_error("Platform must be 'android' or 'ios'")
            ErrorDisplay.show_error(error)
            raise typer.Exit(1)
        return platform


class CLICommands:
    """CLI commands with functional error handling."""

    def __init__(self):
        self.data_manager = DataManager()
        self.connection_manager = ConnectionManager(self.data_manager)
        self.result_handler = ResultHandler()

    def get_device_info(self, udid: str) -> None:
        udid = InputValidator.validate_non_empty(udid, "UDID")

        typer.echo("\n🔍 Looking up device information...")
        typer.echo(f"   UDID: {udid}")

        device_result = get_device_by_udid(self.data_manager, udid)
        device = self.result_handler.handle_result(device_result)

        ErrorDisplay.show_success("Device found")

        host_alias = None
        hostname = device.get("hostname")
        if hostname:
            hosts_result = self.data_manager.get_hosts()
            if isinstance(hosts_result, Success):
                hosts = hosts_result.unwrap()
                matching_host = next((h for h in hosts if h.get("hostname") == hostname), None)
                if matching_host:
                    host_alias = matching_host.get("alias")

        DeviceDisplayManager.display_device_info(device, host_alias)

    def list_available_devices(self, platform: str) -> None:
        platform = InputValidator.validate_platform(platform)

        typer.echo("\n🔍 Finding available devices...")
        typer.echo(f"   Platform: {platform}")

        devices_result = get_available_devices_by_platform(self.data_manager, platform)
        available_devices = self.result_handler.handle_result(devices_result)

        ErrorDisplay.show_success(f"Found {len(available_devices)} available {platform} devices")
        if available_devices:
            title = f"📱 Available {platform.capitalize()} Devices"
            DeviceDisplayManager.display_device_list(available_devices, title)
        else:
            ErrorDisplay.show_info(f"No available {platform} devices found")
            typer.echo("   💡 Tip: Try 'ds host <hostname> --detailed' to see all devices on a specific host")

    def find_host_info(self, query: str, detailed: bool = False) -> None:
        query = InputValidator.validate_non_empty(query, "Host query")
        found_hosts = self._search_hosts(query)
        self._display_host_results(found_hosts, query, detailed)

    def _search_hosts(self, query: str) -> List[Dict]:
        typer.echo("\n🔍 Searching for hosts...")
        typer.echo(f"   Query: '{query}'")

        hosts_result = get_hosts_by_query(self.data_manager, query)
        found_hosts = self.result_handler.handle_result(hosts_result)

        ErrorDisplay.show_success(f"Found {len(found_hosts)} matching host(s)")
        return found_hosts

    def _display_host_results(self, found_hosts: List[Dict], query: str, detailed: bool) -> None:
        if detailed and len(found_hosts) == 1:
            self._show_detailed_host_info(found_hosts[0])
        elif detailed and len(found_hosts) > 1:
            ErrorDisplay.show_warning("Multiple hosts found. Please be more specific for detailed view:")
            HostDisplayManager.display_host_results(found_hosts, query)
        else:
            HostDisplayManager.display_host_results(found_hosts, query)
            if len(found_hosts) == 1:
                typer.echo(f"\n💡 Use 'ds host {query} --detailed' for comprehensive host information")

    def _show_detailed_host_info(self, host: Dict) -> None:
        hostname = host.get("hostname", "")
        devices_result = self.data_manager.get_devices()

        if isinstance(devices_result, Success):
            devices = devices_result.unwrap()
            host_devices = get_devices_by_host(devices, hostname)
            HostDisplayManager.display_detailed_host_info(host, host_devices)
        else:
            ErrorDisplay.show_error(devices_result.failure())
            raise typer.Exit(1)

    def ssh_connect(self, query: str) -> None:
        query = InputValidator.validate_non_empty(query, "Host query")

        typer.echo("\n🔍 Looking up host...")
        typer.echo(f"   Query: '{query}'")

        connection_result = self.connection_manager.connect_ssh(query)

        if isinstance(connection_result, Failure):
            error: AppError = connection_result.failure()
            if error.error_type == ErrorType.MULTIPLE_MATCHES_FOUND:
                ErrorDisplay.show_error(error)
                HostDisplayManager.display_host_results(error.context, query)
                raise typer.Exit(1)

        self.result_handler.handle_result(connection_result)
        ErrorDisplay.show_success("SSH connection completed")

    def adb_connect(self, udid: str) -> None:
        udid = InputValidator.validate_non_empty(udid, "UDID")

        typer.echo("\n🔍 Looking up Android device...")
        typer.echo(f"   UDID: {udid}")

        connection_result = self.connection_manager.connect_adb(udid)
        self.result_handler.handle_result(connection_result)
        ErrorDisplay.show_success("ADB connection successful")

    def get_android_connection(self, udid: str) -> str:
        device_result = get_device_by_udid(self.data_manager, udid)
        if isinstance(device_result, Failure):
            typer.echo("not_found")
            return "not_found"

        device = device_result.unwrap()
        if device.get("is_locked"):
            typer.echo("locked")
            return "locked"
        if device.get("platform") == "android" and device.get("adb_port"):
            ip_port = f"{device.get('hostname')}:{device.get('adb_port')}"
            typer.echo(ip_port)
            return ip_port

        typer.echo("not_android")
        return "not_android"

    def get_host_ip_for_script(self, query: str) -> str:
        host_ip_result = self.connection_manager.host_resolver.resolve_host_ip(query)
        if isinstance(host_ip_result, Failure):
            typer.echo("not_found")
            return "not_found"

        host_ip = host_ip_result.unwrap()
        typer.echo(host_ip)
        return host_ip

    def show_system_status(self) -> None:
        from rc_cli.device_spy.data_manager import Config

        typer.echo("\n📊 Device Spy CLI Status")
        typer.echo("=" * Config.DISPLAY_WIDTH)

        typer.echo("🌐 API Connectivity:")
        typer.echo(f"   Base URL:     {Config.BASE_URL}")

        devices_cached = self.data_manager.is_devices_cached()
        hosts_cached = self.data_manager.is_hosts_cached()

        typer.echo("\n💾 Cache Status:")
        typer.echo(f"   Devices:      {'✅ Cached' if devices_cached else '❌ Not cached'}")
        typer.echo(f"   Hosts:        {'✅ Cached' if hosts_cached else '❌ Not cached'}")

        if devices_cached:
            device_count = self.data_manager.get_cached_device_count()
            typer.echo(f"   Device Count: {device_count}")
            if device_count > 0:
                summary = get_device_summary(self.data_manager._devices_cache)
                typer.echo(f"   Android:      {summary['android']}")
                typer.echo(f"   iOS:          {summary['ios']}")
                typer.echo(f"   Available:    {summary['available']}")
                typer.echo(f"   Locked:       {summary['locked']}")

        if hosts_cached:
            host_count = self.data_manager.get_cached_host_count()
            typer.echo(f"   Host Count:   {host_count}")

        typer.echo("\n🔍 Quick Connectivity Test:")
        devices_result = self.data_manager.get_devices(force_refresh=True)
        hosts_result = self.data_manager.get_hosts(force_refresh=True)

        if isinstance(devices_result, Success) and isinstance(hosts_result, Success):
            devices = devices_result.unwrap()
            hosts = hosts_result.unwrap()
            ErrorDisplay.show_success("Connected")
            typer.echo(f"   Devices:      {len(devices)} found")
            typer.echo(f"   Hosts:        {len(hosts)} found")
        else:
            ErrorDisplay.show_error("Connection failed")

        typer.echo("=" * Config.DISPLAY_WIDTH)

    def refresh_cache(self) -> None:
        typer.echo("\n🔄 Refreshing cached data...")

        devices_result = self.data_manager.get_devices(force_refresh=True)
        hosts_result = self.data_manager.get_hosts(force_refresh=True)

        if isinstance(devices_result, Success) and isinstance(hosts_result, Success):
            devices = devices_result.unwrap()
            hosts = hosts_result.unwrap()
            ErrorDisplay.show_success("Cache refreshed successfully")
            typer.echo(f"   📱 Devices: {len(devices)}")
            typer.echo(f"   🖥️  Hosts:   {len(hosts)}")
        else:
            if isinstance(devices_result, Failure):
                ErrorDisplay.show_error(devices_result.failure())
            if isinstance(hosts_result, Failure):
                ErrorDisplay.show_error(hosts_result.failure())
            raise typer.Exit(1)


