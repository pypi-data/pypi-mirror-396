"""Small helper for one-key navigation between TUI pages.

Use case:
- Search/List screen selects an ID and navigates to another screen.
- Target screen pre-fills one or more inputs on first mount.
"""

from __future__ import annotations

from typing import Any


def set_prefill(app: Any, screen_id: str, values: dict[str, str]) -> None:
    """Set prefill values for a target screen (overwrites existing)."""
    store = getattr(app, "_rc_tui_prefill", None)
    if store is None:
        store = {}
        setattr(app, "_rc_tui_prefill", store)
    store[screen_id] = dict(values)


def consume_prefill(app: Any, screen_id: str) -> dict[str, str]:
    """Consume (get and remove) prefill values for a target screen."""
    store = getattr(app, "_rc_tui_prefill", None)
    if not isinstance(store, dict):
        return {}
    values = store.pop(screen_id, None)
    return dict(values) if isinstance(values, dict) else {}


