# -*- coding: utf-8 -*-

import logging
import typer

# ⚠️ IMPORTANT: Load environment variables FIRST before importing any config
from . import env_loader  # This will auto-load .env

from rc_cli.common_lib.config import LoggingUtils, DownloadConfig

from .service_parameter.commands import sp_app
from .feature_flag.commands import ffs_app
from .account_pool.commands import ap_app
from .device_spy.cli_commands import ds_app
from .download.commands import download_app
from .config_commands import config_app

# Initialize logger
logger = LoggingUtils.setup_logger('rc_cli')

# Disable httpx INFO level logs, keep only warnings and errors
logging.getLogger("httpx").setLevel(logging.WARNING)

# Create main app and subcommands
app = typer.Typer(
    name="rc",
    help="🚀 RC CLI - Development Tools",
    add_completion=False,
    rich_markup_mode="rich"
)

app.add_typer(download_app, name="download")
app.add_typer(download_app, name="d")
app.add_typer(download_app, name="down")

# Add SP sub-app
app.add_typer(sp_app, name="sp")

# Add FFS sub-app
app.add_typer(ffs_app, name="ffs")

# Add Account Pool sub-app
app.add_typer(ap_app, name="ap")

# Add Device Spy sub-app
app.add_typer(ds_app, name="ds")

# Add Config sub-app
app.add_typer(config_app, name="config")
app.add_typer(config_app, name="cfg")


# Main app commands
@app.command("info")
def show_info():
    """ℹ️  Show configuration information."""
    typer.echo("\n🚀 RC CLI - Development Tools")
    typer.echo(f"📁 Download directory: {DownloadConfig.FILE_DIR}")
    typer.echo(f"🔧 Max concurrent downloads: {DownloadConfig.MAX_CONCURRENT_DOWNLOADS}")
    typer.echo(f"🌐 Server URL: {DownloadConfig.BASE_URL}")
    
    available_types = ', '.join(DownloadConfig.get_app_types().keys())
    typer.echo(f"📱 Available application types: {available_types}")
    
    typer.echo("\n💡 Usage examples:")
    typer.echo("  rc download aqa          # Download AQA applications")
    typer.echo("  rc d up                  # Download UP applications")
    typer.echo("  rc d regress 24.1        # Download version 24.1 regression test apps")
    typer.echo("  rc sp tui                # 🖥️  Launch interactive TUI (recommended)")
    typer.echo("  rc sp list               # List all SP information")
    typer.echo("  rc sp search 'SMS'       # Search SMS-related SPs")
    typer.echo("  rc sp get 'SP-123' '8023391076'  # Get account SP value")
    typer.echo("  rc sp definition 'SP-123'  # Get SP definition")
    typer.echo("  rc sp server-info       # Get server information")
    typer.echo("  rc sp clear-cache       # Clear cache")
    typer.echo("  rc ffs tui              # 🖥️  Launch FFS interactive TUI")
    typer.echo("  rc ffs search 'sms'     # Search feature flags")
    typer.echo("  rc ffs get 'flag-id'    # Get feature flag configuration")
    typer.echo("  rc ffs evaluate 'flag-id' -a '123'  # Evaluate feature flag")
    typer.echo("  rc ffs check 'flag-id' -a '123'     # Check if feature is enabled")
    typer.echo("  rc ap tui                      # 🖥️  Launch Account Pool interactive TUI")
    typer.echo("                                 #     - Get Random Account")
    typer.echo("                                 #     - Get by ID / Phone / Alias")
    typer.echo("                                 #     - List Aliases & Types")
    typer.echo("  rc ap get webAqaXmn            # Get random account by type")
    typer.echo("  rc ap by-id 8023391076         # Get account by ID")
    typer.echo("  rc ap info 16789350903         # Get account by phone number")
    typer.echo("  rc ap by-alias webAqaXmn       # Get account by alias from GitLab")
    typer.echo("  rc ap list-aliases             # List all available aliases")
    typer.echo("  rc ap alias-info webAqaXmn     # Get alias details")
    typer.echo("  rc ap types                    # List all account types")
    typer.echo("  rc ap cache clear              # Clear cache")
    typer.echo("  rc ds udid <UDID>      # Get device info by UDID")
    typer.echo("  rc ds devices android  # List Android devices")
    typer.echo("  rc ds host <hostname>  # Find host information")
    typer.echo("  rc ds ssh <hostname>   # Connect via SSH")
    typer.echo("  rc ds connect <UDID>   # Connect to Android via ADB")
    typer.echo("  rc ds status           # Show system status")
    typer.echo("  rc ds refresh          # Refresh cache")
    typer.echo("\n⚙️  Configuration:")
    typer.echo("  rc config show         # Show configuration status")
    typer.echo("  rc config setup        # Interactive configuration setup")
    typer.echo("  rc config validate     # Validate configuration")


@app.command("tui")
def launch_unified_tui():
    """🖥️  Launch Unified Interactive TUI (Device Spy, Feature Flags, Service Params)"""
    from .unified_tui import run_unified_tui
    
    typer.echo("🚀 Launching Unified RC Manager...")
    typer.echo("💡 Press 'q' or 'Ctrl+C' to exit")
    typer.echo("💡 Navigation: 'd' (Device Spy), 'a' (Account Pool), 's' (Service Params), 'f' (Feature Flags)")
    typer.echo("-" * 50)
    
    try:
        run_unified_tui()
    except KeyboardInterrupt:
        typer.echo("\n\n👋 TUI closed by user")
    except Exception as e:
        typer.echo(f"\n❌ Error launching TUI: {e}", err=True)
        raise typer.Exit(1)


def main_rc_function():
    """Main entry point for RC CLI"""
    app()


if __name__ == "__main__":
    main_rc_function() 