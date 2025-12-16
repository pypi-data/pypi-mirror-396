"""Pagination utilities for displaying large datasets in CLI applications."""

from __future__ import annotations

import sys
from typing import Any, Callable, List, TypeVar

import typer

T = TypeVar("T")


def get_single_key_input(
    prompt: str,
    continue_keys: List[str] = ["\r", "\n"],
    quit_keys: List[str] = ["q"],
    timeout: int | None = None,
) -> str:
    """Get single key input with immediate exit and timeout support."""
    typer.echo(prompt, nl=False)
    try:
        import select
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(sys.stdin.fileno())
        try:
            if timeout is not None:
                ready, _, _ = select.select([sys.stdin], [], [], timeout)
                if not ready:
                    typer.echo("\n⏰ Timeout - automatically exiting...")
                    return "timeout"
            char = sys.stdin.read(1)
            if char.lower() in [k.lower() for k in quit_keys]:
                typer.echo(char)
                return "quit"
            if char in continue_keys:
                typer.echo("")
                return "continue"
            typer.echo("")
            return "other"
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except Exception:
        typer.echo("")
        if timeout is not None:
            import signal

            def timeout_handler(signum, frame):  # noqa: ARG001
                raise TimeoutError("Input timeout")

            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
            try:
                user_input = input().strip().lower()
                signal.alarm(0)
                if user_input in [k.lower() for k in quit_keys]:
                    return "quit"
                return "continue"
            except TimeoutError:
                signal.alarm(0)
                typer.echo("\n⏰ Timeout - automatically exiting...")
                return "timeout"
        user_input = input().strip().lower()
        if user_input in [k.lower() for k in quit_keys]:
            return "quit"
        return "continue"


def paginated_display(
    items: List[T],
    display_func: Callable[[T, int], None],
    title: str,
    page_size: int = 5,
    display_width: int = 50,
    start_index: int = 1,
) -> bool:
    """Display items with pagination support."""
    if not items:
        typer.echo(f"\n{title}")
        typer.echo("=" * display_width)
        typer.echo("   No items to display")
        typer.echo("=" * display_width)
        return True

    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size
    current_page = 1

    typer.echo(f"\n{title}")
    typer.echo("=" * display_width)

    if total_items <= page_size:
        for i, item in enumerate(items):
            display_func(item, start_index + i)
        return True

    while current_page <= total_pages:
        start_idx = (current_page - 1) * page_size
        end_idx = min(start_idx + page_size, total_items)

        for i in range(start_idx, end_idx):
            display_func(items[i], start_index + i)

        remaining = total_items - end_idx
        if remaining > 0:
            result = get_single_key_input(f"\n({remaining} more) Press Enter or 'q': ")
            if result in ["quit", "timeout"]:
                return False
        else:
            break

        current_page += 1

    return True


def simple_pagination(items: List[Any], items_per_page: int = 10) -> None:
    """Simple pagination for displaying lists without custom formatting."""
    if not items:
        typer.echo("No items to display.")
        return

    total_items = len(items)
    total_pages = (total_items + items_per_page - 1) // items_per_page

    for page in range(total_pages):
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)

        typer.echo(f"\n--- Page {page + 1}/{total_pages} ---")
        for i in range(start_idx, end_idx):
            typer.echo(f"{i + 1}. {items[i]}")

        if page < total_pages - 1:
            typer.echo("\nPress Enter to continue to next page...")
            input()


def get_user_choice(prompt: str, valid_choices: List[str]) -> str:
    """Get user input with validation."""
    while True:
        choice = input(f"{prompt} ({'/'.join(valid_choices)}): ").strip().lower()
        if choice in [c.lower() for c in valid_choices]:
            return choice
        typer.echo(f"Invalid choice. Please choose from: {', '.join(valid_choices)}")


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask user for yes/no confirmation."""
    default_text = "Y/n" if default else "y/N"
    choice = input(f"{message} [{default_text}]: ").strip().lower()
    if not choice:
        return default
    return choice in ["y", "yes", "true", "1"]


