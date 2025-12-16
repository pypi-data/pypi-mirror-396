# -*- coding: utf-8 -*-

"""Device Spy commands for RC CLI."""

from typing import Optional
import typer
from .commands import CLICommands

# Create Device Spy sub-app
ds_app = typer.Typer(
    name="ds",
    help="📱 Device Spy management commands",
    add_completion=False,
    rich_markup_mode="rich"
)

# --- CLI Instance ---
cli_commands = CLICommands()


@ds_app.command("udid")
def get_device_info(udid: str = typer.Argument(..., help="Device UDID to lookup")):
    """📱 Display detailed information for a specific device.
    
    Examples:
    
        rc ds udid <UDID>                 # Get device info by UDID
    """
    cli_commands.get_device_info(udid)


@ds_app.command("devices")
def list_available_devices(platform: str = typer.Argument(..., help="Platform: android or ios")):
    """📋 List available devices for a platform.
    
    Examples:
    
        rc ds devices android              # List Android devices
        rc ds devices ios                  # List iOS devices
    """
    cli_commands.list_available_devices(platform)


@ds_app.command("host")
def find_host_info(
    query: str = typer.Argument(..., help="Host query string (hostname or alias)"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed host information")
):
    """🖥️  Find host information by query.
    
    Examples:
    
        rc ds host <hostname>              # Find host by hostname
        rc ds host <hostname> --detailed  # Show detailed host information
    """
    cli_commands.find_host_info(query, detailed)


@ds_app.command("ssh")
def ssh_connect(query: str = typer.Argument(..., help="Host query string to connect via SSH")):
    """🔗 Connect to a host via SSH.
    
    Examples:
    
        rc ds ssh <hostname>               # Connect via SSH
    """
    cli_commands.ssh_connect(query)


@ds_app.command("connect")
def adb_connect(udid: str = typer.Argument(..., help="Android device UDID to connect via ADB")):
    """🤖 Connect to Android device via ADB.
    
    Examples:
    
        rc ds connect <UDID>               # Connect to Android device via ADB
    """
    cli_commands.adb_connect(udid)


@ds_app.command("android-ip")
def get_android_connection(udid: str = typer.Argument(..., help="Android device UDID")):
    """🤖 Get Android device IP:Port for script usage.
    
    Examples:
    
        rc ds android-ip <UDID>           # Get Android device IP:Port
    """
    cli_commands.get_android_connection(udid)


@ds_app.command("host-ip")
def get_host_ip_for_script(query: str = typer.Argument(..., help="Host query string")):
    """🌐 Get host IP address for script usage.
    
    Examples:
    
        rc ds host-ip <hostname>          # Get host IP address
    """
    cli_commands.get_host_ip_for_script(query)


@ds_app.command("status")
def show_system_status():
    """📊 Show system status and cache information.
    
    Examples:
    
        rc ds status                       # Show system status
    """
    cli_commands.show_system_status()


@ds_app.command("refresh")
def refresh_cache():
    """🔄 Refresh cached data from server.
    
    Examples:
    
        rc ds refresh                      # Refresh cache
    """
    cli_commands.refresh_cache()


@ds_app.command("tui")
def launch_tui():
    """🖥️  Launch interactive TUI for Device Spy.
    
    Examples:
    
        rc ds tui                          # Launch interactive TUI
    """
    typer.echo("🚀 Launching Device Spy TUI...")
    typer.echo("💡 Press 'q' or 'Ctrl+C' to exit, 'Esc' to go back")
    typer.echo("-" * 50)
    
    try:
        from .tui import run_tui
        run_tui()
    except KeyboardInterrupt:
        typer.echo("\n\n👋 TUI closed by user")
    except Exception as e:
        typer.echo(f"\n❌ Error launching TUI: {e}", err=True)
        raise typer.Exit(1)

