# -*- coding: utf-8 -*-

"""
This module handles the display logic for the Account Pool CLI.
It uses the rich library to present data in a user-friendly format.
"""

from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from datetime import datetime
import rich.box

# Import the single-key input helper for pagination
from rc_cli.common_lib.pagination import get_single_key_input
from .data_manager import CacheManager, Config

console = Console()


class DisplayManager:
    """Handles all CLI output using the rich library."""

    @staticmethod
    def display_account_info(account: Dict):
        """Display account information in a rich, 2-column table like ds."""
        
        # --- Data Extraction ---
        account_id = account.get("accountId", "N/A")
        main_number = account.get("mainNumber", "N/A")
        account_type = account.get("accountType", "N/A")
        env_name = account.get("envName", "N/A")
        email_domain = account.get("companyEmailDomain", "N/A")
        created_at_str = account.get("createdAt", "N/A")
        mongo_id = account.get("_id", "N/A")

        # --- Data Formatting ---
        created_at = created_at_str
        if created_at_str != "N/A":
            try:
                dt = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                created_at = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass

        locked = account.get("locked", [])
        status_text = "🔒 Locked" if locked else "✅ Available"
        status_style = "red" if locked else "green"
        display_account_type = (account_type[:60] + '...') if len(account_type) > 63 else account_type
        
        # --- Rich Table Creation (mimicking ds style) ---
        console.print(f"\n✅ [bold cyan]Account Information[/bold cyan]")
        table = Table(show_header=False, show_lines=False, padding=(0, 1))
        table.add_column("Field", style="bold", no_wrap=True, min_width=18)
        table.add_column("Value", overflow="fold")

        # --- Adding Rows ---
        table.add_row("📱 Phone:", main_number.lstrip('+'))
        table.add_row("🆔 Account ID:", str(account_id))
        table.add_row("🏷️  Type:", display_account_type)
        table.add_row("🌐 Environment:", env_name)
        table.add_row("📧 Email Domain:", email_domain)
        table.add_row("📅 Created:", created_at)
        table.add_row("🔗 MongoDB ID:", mongo_id)
        table.add_row("🔐 Status:", Text(status_text, style=status_style))
        
        if locked:
            lock_details_text = Text()
            for item in locked:
                if isinstance(item, dict):
                    lock_details_text.append(f"• Type: {item.get('accountType', 'N/A')}\n")
            table.add_row("🛑 Lock Details:", lock_details_text)

        console.print(table)

    @staticmethod
    def display_account_types(settings: List[Dict], brand: str, filter_keyword: Optional[str], page_size: int = 10):
        """Display a list of account types in a rich table with pagination."""
        
        total_items = len(settings)
        if total_items == 0:
            console.print(Panel("No account types found for the given criteria.", title="Info", border_style="yellow"))
            return

        def _create_table(title: str) -> Table:
            """Helper to create a consistent table structure."""
            table = Table(title=title, show_header=True, header_style="bold magenta", border_style="blue")
            table.add_column("#", style="dim", width=4, justify="right")
            table.add_column("Account Type", style="cyan", overflow="fold")
            return table

        def _add_rows_to_table(table: Table, items: List[Dict], start_index: int):
            """Helper to add rows and truncate long text."""
            for i, setting in enumerate(items, start_index):
                account_type = setting.get("accountType", "N/A")
                
                table.add_row(
                    str(i),
                    account_type
                )

        # If the list is short, display it all at once without pagination.
        if total_items <= page_size:
            title = f"🏦 Account Types for Brand [bold]{brand}[/bold]"
            if filter_keyword:
                title += f" (filtered by '[bold]{filter_keyword}[/bold]')"
            
            table = _create_table(title)
            _add_rows_to_table(table, settings, 1)
            console.print(table)
            console.print("\n💡 Use the [#] or [cyan]Account Type[/cyan] with the 'rc ap get' command.", justify="center")
            return

        # --- Pagination Logic ---
        total_pages = (total_items + page_size - 1) // page_size
        current_page = 1

        while current_page <= total_pages:
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, total_items)
            page_items = settings[start_idx:end_idx]

            title = f"🏦 Account Types for Brand [bold]{brand}[/bold] - Page {current_page}/{total_pages}"
            if filter_keyword:
                title += f" (filtered by '[bold]{filter_keyword}[/bold]')"

            table = _create_table(title)
            _add_rows_to_table(table, page_items, start_idx + 1)
            
            console.print(table)

            if current_page < total_pages:
                remaining = total_items - end_idx
                result = get_single_key_input(f"   ({remaining} more) Press Enter to continue or 'q' to quit: ")
                if result == 'quit':
                    console.print("👋 Exited.", style="yellow")
                    break
            
            current_page += 1

        if current_page > total_pages:
             console.print("\n💡 Use the [#] or [cyan]Account Type[/cyan] with the 'rc ap get' command.", justify="center")

    @staticmethod
    def display_cache_status():
        """Displays the current status of the cache."""
        cache_data = CacheManager.load_cache()
        if not cache_data:
            console.print("ℹ️  Cache is empty.", style="yellow")
            return
        
        panel_content = ""
        for key, value in cache_data.items():
            # Truncate long lists for display
            display_value = value
            if isinstance(value, list) and len(value) > 10:
                display_value = f"[{len(value)} items] {value[:5]}..."
            
            panel_content += f"[bold cyan]{key.replace('_', ' ').title()}:[/bold] {display_value}\n"
            
        console.print(Panel(panel_content.strip(), title="Cache Status", border_style="blue", width=Config.DISPLAY_WIDTH))

    @staticmethod
    def display_error(message: str, details: Optional[str] = None, suggestions: Optional[List[str]] = None):
        """Display a formatted error message."""
        error_text = Text(f"❌ {message}", style="bold red")
        
        if details:
            error_text.append(f"\n   📄 Details: {details}", style="default")
        
        if suggestions:
            error_text.append("\n   💡 Suggestions:", style="default")
            for suggestion in suggestions:
                error_text.append(f"\n      - {suggestion}", style="default")
        
        console.print(Panel(error_text, title="Error", border_style="red"))

    @staticmethod
    def display_info(message: str):
        """Display an informational message."""
        console.print(f"ℹ️  {message}", style="blue")

    @staticmethod
    def display_success(message: str):
        """Display a success message."""
        console.print(f"✅ {message}", style="green")
    
    @staticmethod
    def display_warning(message: str):
        """Display a warning message."""
        console.print(f"⚠️  {message}", style="yellow")
    
    @staticmethod
    def display_aliases(mappings: List) -> None:
        """
        Display list of aliases in a rich table.
        
        Args:
            mappings: List of AliasMapping objects
        """
        if not mappings:
            console.print("ℹ️  No aliases found.", style="yellow")
            return
        
        table = Table(
            title="🏷️  Available Aliases",
            show_header=True,
            header_style="bold magenta",
            border_style="blue"
        )
        
        table.add_column("#", style="dim", width=4, justify="right")
        table.add_column("Alias", style="cyan", no_wrap=False)
        table.add_column("Brand", style="green", width=10)
        table.add_column("Kamino Key", style="yellow", no_wrap=False)
        
        for i, mapping in enumerate(mappings, 1):
            table.add_row(
                str(i),
                mapping.alias,
                mapping.brand,
                mapping.kamino_key
            )
        
        console.print(table)
        console.print(
            f"\n💡 Found {len(mappings)} alias(es). "
            f"Use 'rc ap by-alias <alias>' to get account info.",
            style="dim"
        )
    
    @staticmethod
    def display_alias_detail(mapping) -> None:
        """
        Display detailed information about a specific alias.
        
        Args:
            mapping: AliasMapping object
        """
        console.print(f"\n✅ [bold cyan]Alias Information[/bold cyan]")
        
        table = Table(show_header=False, show_lines=False, padding=(0, 1))
        table.add_column("Field", style="bold", no_wrap=True, min_width=18)
        table.add_column("Value", overflow="fold")
        
        table.add_row("🏷️  Alias:", mapping.alias)
        table.add_row("🏢 Brand:", mapping.brand)
        table.add_row("🔑 Kamino Key:", mapping.kamino_key)
        
        console.print(table)
        console.print(
            f"\n💡 Use 'rc ap by-alias {mapping.alias}' to get account info.",
            style="dim"
        ) 