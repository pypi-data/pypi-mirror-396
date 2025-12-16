# -*- coding: utf-8 -*-

import logging
from typing import Dict, List

import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rc_cli.common_lib.pagination import paginated_display
from rc_cli.common_lib.config import BaseConfig

logger = logging.getLogger(__name__)
console = Console()


class Config(BaseConfig):
    pass


class BaseDisplayManager:
    """Base class for display managers with common utilities."""
    
    @staticmethod
    def get_safe_value(data: Dict, key: str, default: str = "N/A") -> str:
        """Safely get value from dictionary with default."""
        return str(data.get(key, default) or default)
    
    @staticmethod
    def format_percentage(current: int, total: int) -> str:
        """Format percentage with proper handling of division by zero."""
        if total == 0:
            return "N/A"
        return f"{round((current / total) * 100, 1)}%"
    
    @staticmethod
    def truncate_udid(udid: str, length: int = 8) -> str:
        """Truncate UDID for better readability."""
        return f"{udid[:length]}..." if len(udid) > length else udid


class DeviceDisplayManager(BaseDisplayManager):
    """Handles device information display."""
    
    @staticmethod
    def display_device_info(device: Dict, host_alias: str = None) -> None:
        """Display device information in a user-friendly format using rich table."""
        console.print(f"\n📱 [bold cyan]Device Information[/bold cyan]")
        
        # Create a rich table for perfect alignment
        table = Table(show_header=False, show_lines=False, padding=(0, 1))
        table.add_column("Field", style="bold", no_wrap=True, min_width=18)
        table.add_column("Value", overflow="fold")
        
        # Basic fields
        table.add_row("📋 UDID:", BaseDisplayManager.get_safe_value(device, "udid"))
        
        # Add name field if it exists
        name = device.get("name")
        if name and name != "N/A":
            table.add_row("📛 Name:", str(name))
            
        table.add_row("🔧 Platform:", BaseDisplayManager.get_safe_value(device, "platform"))
        table.add_row("📟 Model:", BaseDisplayManager.get_safe_value(device, "model"))
        table.add_row("🎯 OS Version:", BaseDisplayManager.get_safe_value(device, "platform_version"))
        table.add_row("🖥️  Host:", BaseDisplayManager.get_safe_value(device, "hostname"))
        
        # Add host alias if available
        if host_alias and host_alias != "N/A":
            table.add_row("🏷️  Host Alias:", str(host_alias))
        
        # Optional fields
        host_ip = device.get("host_ip")
        if host_ip and host_ip != "N/A":
            table.add_row("🌐 Host IP:", str(host_ip))
            
        location = device.get("location")
        if location and location != "N/A":
            table.add_row("📍 Location:", str(location))
            
        ip_port = device.get("ip_port")
        if ip_port and ip_port != "N/A":
            table.add_row("🌐 IP:Port:", str(ip_port))
        
        # Labels field
        labels = device.get("labels", [])
        if labels:
            labels_text = ", ".join(labels) if isinstance(labels, list) else str(labels)
            table.add_row("🏷️  Labels:", labels_text)
        
        # Status
        is_locked = device.get("is_locked", False)
        status_text = "🔒 Locked" if is_locked else "✅ Available"
        status_style = "red" if is_locked else "green"
        table.add_row("🔐 Status:", Text(status_text, style=status_style))
        
        console.print(table)

    @staticmethod
    def display_device_list(devices: List[Dict], title: str) -> None:
        """Display a list of devices with pagination."""
        def display_device(device: Dict, index: int) -> None:
            model = BaseDisplayManager.get_safe_value(device, "model")
            os_version = BaseDisplayManager.get_safe_value(device, "platform_version")
            udid = BaseDisplayManager.get_safe_value(device, "udid")
            hostname = BaseDisplayManager.get_safe_value(device, "hostname")
            
            typer.echo(f"\n{index}. {model} ({os_version})")
            typer.echo(f"   UDID: {udid}")
            typer.echo(f"   Host: {hostname}")
            
            # Show labels in device list too
            labels = device.get("labels", [])
            if labels:
                labels_text = ", ".join(labels) if isinstance(labels, list) else str(labels)
                typer.echo(f"   Labels: {labels_text}")
        
        paginated_display(devices, display_device, title, Config.PAGE_SIZE, Config.DISPLAY_WIDTH)
        
        typer.echo("\n" + "=" * Config.DISPLAY_WIDTH)
        typer.echo(f"💡 Use 'ds udid <udid>' to get detailed information")
        typer.echo("=" * Config.DISPLAY_WIDTH) 