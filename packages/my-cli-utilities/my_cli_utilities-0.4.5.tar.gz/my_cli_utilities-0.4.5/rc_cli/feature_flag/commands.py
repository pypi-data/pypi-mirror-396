# -*- coding: utf-8 -*-

"""Feature Flag Service (FFS) commands for RC CLI."""

import json
from typing import Optional, Dict, Any
import typer
from .service import ffs_service
from .display_manager import FFSDisplayManager
from ..common import async_command, format_separator, SHORT_SEPARATOR_WIDTH, DEFAULT_SEPARATOR_WIDTH
from rc_cli.common_lib.config import DisplayUtils

# Create FFS sub-app
ffs_app = typer.Typer(
    name="ffs",
    help="🚩 Feature Flag Service (FFS) management commands",
    add_completion=False,
    rich_markup_mode="rich"
)


@ffs_app.command("get")
@async_command
async def get_feature_flag(
    flag_id: str = typer.Argument(..., help="Feature flag ID")
):
    """📖 Get feature flag configuration by ID
    
    Examples:
    
        rc ffs get "rc-app-mobile.user.sms_translate_sms"
    """
    DisplayUtils.format_search_info("Feature Flag", {
        "Flag ID": flag_id
    })
    
    result = await ffs_service.get_feature_flag(flag_id)
    
    if not result.success:
        DisplayUtils.format_error(result.error_message)
        raise typer.Exit(1)
    
    flag_data = result.data
    
    typer.echo(f"\n📖 Feature Flag Configuration:")
    typer.echo(format_separator(SHORT_SEPARATOR_WIDTH))
    
    formatted_output = FFSDisplayManager.format_flag(flag_data)
    typer.echo(formatted_output)
    
    typer.echo(format_separator(SHORT_SEPARATOR_WIDTH))
    DisplayUtils.format_success("Successfully retrieved feature flag")


@ffs_app.command("search")
@async_command
async def search_feature_flags(
    query: str = typer.Argument(..., help="Search query string"),
    limit: Optional[int] = typer.Option(
        None,
        "--limit", "-l",
        help="Limit the number of results to display"
    )
):
    """🔍 Search feature flags by name pattern
    
    Examples:
    
        rc ffs search "sms_opt_out"        # Search for SMS opt out flags
        rc ffs search "sms" --limit 10     # Search for SMS flags, limit to 10 results
    """
    DisplayUtils.format_search_info("Feature Flags Search", {"Query": query})
    
    result = await ffs_service.search_feature_flags(query)
    
    if not result.success:
        DisplayUtils.format_error(result.error_message)
        raise typer.Exit(1)
    
    flags = result.data
    total_count = result.count
    
    if total_count == 0:
        typer.echo(f"\n❌ No feature flags found matching '{query}'")
        return
    
    typer.echo(f"\n📊 Found {total_count} matching feature flags")
    typer.echo(format_separator(DEFAULT_SEPARATOR_WIDTH))
    
    # Apply limit if specified
    items_to_show = flags
    if limit and limit > 0:
        items_to_show = flags[:limit]
        if limit < total_count:
            typer.echo(f"Showing first {limit} of {total_count} results:")
    
    # Display feature flags
    for flag in items_to_show:
        flag_id = flag.get("id", "N/A")
        description = flag.get("description", "N/A")
        status = flag.get("status", "N/A")
        
        # Truncate description if too long
        if len(description) > 60:
            description = description[:57] + "..."
        
        typer.echo(f"  {flag_id:<40} {status:<10} {description}")
    
    if limit and limit < total_count:
        typer.echo(f"\n... and {total_count - limit} more flags")
    
    typer.echo("-" * 60)
    DisplayUtils.format_success(f"Found {len(items_to_show)} matching feature flags")


@ffs_app.command("evaluate")
@async_command
async def evaluate_feature_flag(
    flag_id: str = typer.Argument(..., help="Feature flag ID"),
    account_id: Optional[str] = typer.Option(None, "--account-id", "-a", help="Account ID"),
    extension_id: Optional[str] = typer.Option(None, "--extension-id", "-e", help="Extension ID"),
    email_domain: Optional[str] = typer.Option(None, "--email-domain", "-d", help="Email domain"),
    context_json: Optional[str] = typer.Option(None, "--context", "-c", help="Context as JSON string")
):
    """📊 Evaluate feature flag with context
    
    Examples:
    
        rc ffs evaluate "flag-id" --account-id "5140195004"
        rc ffs evaluate "flag-id" -a "5140195004" -e "953563004"
        rc ffs evaluate "flag-id" --context '{"accountId": "5140195004"}'
    """
    # Build context
    context: Dict[str, Any] = {}
    
    if context_json:
        try:
            context = json.loads(context_json)
        except json.JSONDecodeError:
            DisplayUtils.format_error("Invalid JSON in context parameter")
            raise typer.Exit(1)
    else:
        if account_id:
            context["accountId"] = account_id
        if extension_id:
            context["extensionId"] = extension_id
        if email_domain:
            context["emailDomain"] = email_domain
    
    DisplayUtils.format_search_info("Feature Flag Evaluation", {
        "Flag ID": flag_id,
        "Context": json.dumps(context) if context else "{}"
    })
    
    result = await ffs_service.evaluate_feature_flag(flag_id, context)
    
    if not result.success:
        DisplayUtils.format_error(result.error_message)
        raise typer.Exit(1)
    
    eval_data = result.data
    
    typer.echo(f"\n📊 Feature Flag Evaluation Result:")
    typer.echo("-" * 40)
    
    formatted_output = FFSDisplayManager.format_evaluation(eval_data)
    typer.echo(formatted_output)
    
    typer.echo("-" * 40)
    DisplayUtils.format_success("Successfully evaluated feature flag")


@ffs_app.command("check")
@async_command
async def check_feature_enabled(
    flag_id: str = typer.Argument(..., help="Feature flag ID"),
    account_id: Optional[str] = typer.Option(None, "--account-id", "-a", help="Account ID"),
    extension_id: Optional[str] = typer.Option(None, "--extension-id", "-e", help="Extension ID"),
    email_domain: Optional[str] = typer.Option(None, "--email-domain", "-d", help="Email domain"),
    context_json: Optional[str] = typer.Option(None, "--context", "-c", help="Context as JSON string")
):
    """✅ Check if feature is enabled
    
    Examples:
    
        rc ffs check "flag-id" --account-id "5140195004"
        rc ffs check "flag-id" -a "5140195004" -e "953563004"
    """
    # Build context
    context: Dict[str, Any] = {}
    
    if context_json:
        try:
            context = json.loads(context_json)
        except json.JSONDecodeError:
            DisplayUtils.format_error("Invalid JSON in context parameter")
            raise typer.Exit(1)
    else:
        if account_id:
            context["accountId"] = account_id
        if extension_id:
            context["extensionId"] = extension_id
        if email_domain:
            context["emailDomain"] = email_domain
    
    DisplayUtils.format_search_info("Feature Enabled Check", {
        "Flag ID": flag_id,
        "Context": json.dumps(context) if context else "{}"
    })
    
    result = await ffs_service.check_feature_enabled(flag_id, context)
    
    if not result.success:
        DisplayUtils.format_error(result.error_message)
        raise typer.Exit(1)
    
    check_data = result.data
    enabled = check_data.get("enabled", False)
    
    typer.echo(f"\n✅ Feature Enabled Status:")
    typer.echo("-" * 40)
    typer.echo(f"  Flag ID: {check_data.get('flagId', 'N/A')}")
    typer.echo(f"  Enabled: {enabled}")
    typer.echo(f"  Matched Rule ID: {check_data.get('matchedRuleId', 'N/A')}")
    typer.echo("-" * 40)
    
    if enabled:
        DisplayUtils.format_success("Feature is ENABLED")
    else:
        typer.echo("⚠️  Feature is DISABLED")


@ffs_app.command("server-info")
def get_server_info():
    """🔧 Get server information and configuration
    
    Examples:
    
        rc ffs server-info                  # Get server information
    """
    DisplayUtils.format_search_info("Server Information")
    
    server_info = ffs_service.get_server_info()
    
    typer.echo(f"\n🔧 Server Information:")
    typer.echo("-" * 40)
    
    formatted_output = FFSDisplayManager.format_server_info(server_info)
    typer.echo(formatted_output)
    
    typer.echo("-" * 40)
    DisplayUtils.format_success("Successfully retrieved server information")


@ffs_app.command("clear-cache")
def clear_cache():
    """🗑️  Clear the feature flag cache
    
    Examples:
    
        rc ffs clear-cache                  # Clear cache
    """
    DisplayUtils.format_search_info("Clear Cache")
    
    ffs_service.clear_cache()
    
    typer.echo("\n🗑️  Cache cleared successfully")
    typer.echo("-" * 40)
    DisplayUtils.format_success("Feature flag cache has been cleared")


@ffs_app.command("tui")
def launch_tui():
    """🖥️  Launch interactive TUI (Terminal User Interface)
    
    Examples:
    
        rc ffs tui                          # Launch interactive TUI
    """
    typer.echo("🚀 Launching FFS Management TUI...")
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


@ffs_app.command("info")
def show_ffs_info():
    """ℹ️  Show FFS service configuration and usage information"""
    typer.echo("\n🚩 Feature Flag Service (FFS) Management")
    typer.echo("=" * 50)
    
    typer.echo("📋 Available Commands:")
    typer.echo("  rc ffs tui                           # 🖥️  Launch interactive TUI")
    typer.echo("  rc ffs get <flag_id>                 # Get feature flag configuration")
    typer.echo("  rc ffs search <query> [--limit N]    # Search feature flags")
    typer.echo("  rc ffs evaluate <flag_id> [options]   # Evaluate feature flag with context")
    typer.echo("  rc ffs check <flag_id> [options]      # Check if feature is enabled")
    typer.echo("  rc ffs server-info                   # Get server information")
    typer.echo("  rc ffs clear-cache                   # Clear cache")
    typer.echo("  rc ffs info                          # Show this help")
    
    typer.echo("\n💡 Examples:")
    typer.echo("  rc ffs tui                           # Launch interactive TUI (recommended)")
    typer.echo("  rc ffs get 'flag-id'                 # Get flag configuration")
    typer.echo("  rc ffs search 'sms'                  # Search for SMS flags")
    typer.echo("  rc ffs evaluate 'flag-id' -a '123'   # Evaluate with account ID")
    typer.echo("  rc ffs check 'flag-id' -a '123'      # Check if enabled")
    typer.echo("  rc ffs server-info                   # Get server info")
    typer.echo("  rc ffs clear-cache                   # Clear cache")
    
    typer.echo("\n⚙️  Configuration:")
    typer.echo("  FFS Base URL: Set FFS_BASE_URL environment variable")
    typer.echo("  Default: http://aws16-c01-ffs01.ffs.svc.c01.eks02.k8s.aws16.lab.nordigy.ru:8080")
    
    typer.echo("\n🔗 Related:")
    typer.echo("  For more information, see the mcp-ffs project documentation")

