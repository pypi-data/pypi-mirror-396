# -*- coding: utf-8 -*-

"""Account Pool commands for RC CLI."""

# Load environment variables first
from .. import env_loader

from typing import Optional
import typer
from .service import AccountService
from .tui import run_tui
from ..common.service_factory import ServiceFactory

# Create Account Pool sub-app
ap_app = typer.Typer(
    name="ap",
    help="🏦 Account Pool management commands",
    add_completion=False,
    rich_markup_mode="rich"
)

# --- Service Instance ---
account_service = ServiceFactory.get_account_service()


@ap_app.command("get")
def get_random_account(
    account_type: str = typer.Argument(..., help="Account type string or index number from 'rc ap types'"),
    env_name: str = typer.Option(AccountService.DEFAULT_ENV_NAME, "--env", "-e", help="Environment name")
):
    """Get a random available account of a specific type.
    
    Examples:
    
        rc ap get webAqaXmn              # Get random account of type webAqaXmn
        rc ap get 1                      # Get random account using index from 'rc ap types'
        rc ap get webAqaXmn --env prod   # Get account from prod environment
    """
    account_service.get_random_account(account_type, env_name)


@ap_app.command("by-id")
def get_account_by_id(
    account_id: str = typer.Argument(..., help="Account ID to lookup"),
    env_name: str = typer.Option(AccountService.DEFAULT_ENV_NAME, "--env", "-e", help="Environment name")
):
    """Get account details by its specific Account ID.
    
    Examples:
    
        rc ap by-id 8023391076           # Get account by ID
        rc ap by-id 8023391076 --env prod # Get account from prod environment
    """
    account_service.get_account_by_id(account_id, env_name)


@ap_app.command("info")
def get_info_by_phone(
    main_number: str = typer.Argument(..., help="Phone number to lookup"),
    env_name: str = typer.Option(AccountService.DEFAULT_ENV_NAME, "--env", "-e", help="Environment name")
):
    """Get account details by its main phone number.
    
    Examples:
    
        rc ap info 16789350903           # Get account by phone number
        rc ap info +16789350903          # Phone number with + prefix
    """
    account_service.get_account_by_phone(main_number, env_name)


@ap_app.command("types")
def list_account_types(
    filter_keyword: Optional[str] = typer.Argument(None, help="Filter account types by keyword (optional)"),
    brand: str = typer.Option(AccountService.DEFAULT_BRAND, "--brand", "-b", help="Brand ID")
):
    """List all available account types for a given brand.
    
    Examples:
    
        rc ap types                      # List all account types
        rc ap types web                  # Filter account types by keyword 'web'
        rc ap types --brand 1210         # List types for brand 1210
    """
    account_service.list_account_types(brand, filter_keyword)


@ap_app.command("cache")
def manage_cache(
    action: Optional[str] = typer.Argument(None, help="Action: 'clear' to clear cache, empty to show status")
):
    """Manage the local cache. Shows status by default.
    
    Examples:
    
        rc ap cache                      # Show cache status
        rc ap cache clear                # Clear cache
    """
    account_service.manage_cache(action)


@ap_app.command("tui")
def launch_tui():
    """🖥️  Launch interactive TUI (Terminal User Interface)
    
    Examples:
    
        rc ap tui                        # Launch interactive TUI
    """
    typer.echo("🚀 Launching Account Pool TUI...")
    typer.echo("💡 Press 'q' or 'Ctrl+C' to exit, 'Esc' to go back")
    typer.echo("-" * 50)
    
    try:
        run_tui()
    except KeyboardInterrupt:
        typer.echo("\n\n👋 TUI closed by user")
    except Exception as e:
        typer.echo(f"\n❌ Error launching TUI: {e}", err=True)
        raise typer.Exit(1)


@ap_app.command("by-alias")
def get_account_by_alias(
    alias: str = typer.Argument(..., help="Alias to lookup (e.g., 'webAqaXmn')"),
    env_name: str = typer.Option(AccountService.DEFAULT_ENV_NAME, "--env", "-e", help="Environment name"),
    account_type: Optional[str] = typer.Option(None, "--type", "-t", help="Optional account type filter")
):
    """Get account by alias using kaminoKey mapping from GitLab.
    
    This command fetches the alias-to-kaminoKey mapping from GitLab repository
    and uses the kaminoKey to query the account pool for account information.
    
    Examples:
    
        rc ap by-alias webAqaXmn                    # Get account by alias
        rc ap by-alias webAqaXmn --env prod         # Get account from prod environment
        rc ap by-alias webAqaXmn --type aqa         # Filter by account type
    """
    account_service.get_account_by_alias(alias, env_name, account_type)


@ap_app.command("list-aliases")
def list_aliases(
    refresh: bool = typer.Option(False, "--refresh", "-r", help="Force refresh from GitLab")
):
    """List all available aliases from GitLab configuration.
    
    This command fetches the alias mappings from GitLab repository and displays
    them in a table showing alias, brand, and kaminoKey.
    
    Examples:
    
        rc ap list-aliases                          # List all aliases
        rc ap list-aliases --refresh                # Force refresh from GitLab
    """
    account_service.list_aliases(force_refresh=refresh)


@ap_app.command("alias-info")
def get_alias_info(
    alias: str = typer.Argument(..., help="Alias to lookup")
):
    """Get detailed information about a specific alias.
    
    Examples:
    
        rc ap alias-info webAqaXmn                  # Get alias details
    """
    account_service.get_alias_info(alias)

