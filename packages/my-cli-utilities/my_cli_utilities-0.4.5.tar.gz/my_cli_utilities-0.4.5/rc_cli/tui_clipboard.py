"""Clipboard helpers for Textual TUI.

Goals:
- Consistent behavior across screens/widgets
- Safe fallbacks when selection is unavailable
- Friendly notifications via `app.notify`
"""

from __future__ import annotations

import logging
from typing import Optional, Sequence

from textual.widgets import DataTable, TextArea

logger = logging.getLogger(__name__)


def _notify_warning(app, message: str, timeout: int = 2) -> None:
    app.notify(message, severity="warning", timeout=timeout)


def _notify_error(app, message: str, timeout: int = 5) -> None:
    app.notify(message, severity="error", timeout=timeout)


def _notify_success(app, message: str, timeout: int = 2) -> None:
    app.notify(message, timeout=timeout)


def copy_to_clipboard(
    app,
    text: str,
    preview_len: int = 30,
    timeout: int = 2,
    notify_success: bool = True,
) -> bool:
    """Copy text to clipboard using pyperclip, with consistent errors/notifications."""
    if not text or not text.strip():
        _notify_warning(app, "No content to copy", timeout=timeout)
        return False

    try:
        import pyperclip

        pyperclip.copy(text)
        if notify_success:
            preview = text.strip().replace("\n", " ")
            preview = preview[:preview_len] + ("..." if len(preview) > preview_len else "")
            _notify_success(app, f"✅ Copied: {preview}", timeout=timeout)
        return True
    except ImportError:
        _notify_error(app, "⚠️  pyperclip not installed. Install with: pip install pyperclip", timeout=5)
        return False
    except Exception:
        logger.exception("Failed to copy to clipboard")
        _notify_error(app, "❌ Failed to copy", timeout=5)
        return False


def extract_textarea_copy_text(text_area: TextArea, strip_phone_plus: bool = False) -> Optional[str]:
    """Best-effort extract copy text from a TextArea selection or cursor line."""
    text = text_area.text or ""
    if not text.strip():
        return None

    lines = text.split("\n")

    # 1) Prefer Textual selection.selected_text (if present)
    try:
        selection = getattr(text_area, "selection", None)
        selected_text = getattr(selection, "selected_text", None) if selection else None
        if isinstance(selected_text, str) and selected_text.strip():
            return selected_text
    except Exception:
        pass

    # 2) Otherwise, try to infer cursor line via selection.start
    cursor_line: int | None = None
    try:
        selection = getattr(text_area, "selection", None)
        start = getattr(selection, "start", None) if selection else None
        if isinstance(start, tuple) and len(start) >= 1 and isinstance(start[0], int):
            cursor_line = start[0]
        elif isinstance(start, int):
            # Fallback: convert char offset to line number
            char_count = 0
            for i, line in enumerate(lines):
                line_len = len(line) + 1
                if char_count + line_len > start:
                    cursor_line = i
                    break
                char_count += line_len
    except Exception:
        cursor_line = None

    candidate = None
    if cursor_line is not None and 0 <= cursor_line < len(lines):
        line = lines[cursor_line].strip()
        if ":" in line:
            parts = line.split(":", 1)
            candidate = parts[1].strip() if len(parts) > 1 else line
        else:
            candidate = line
    else:
        candidate = text

    if not isinstance(candidate, str) or not candidate.strip():
        return None

    if strip_phone_plus and candidate.startswith("+"):
        # Only strip when the line likely represents a phone number field
        for ln in lines:
            if ("📱" in ln or "phone" in ln.lower()) and candidate in ln:
                return candidate[1:]

    return candidate


def copy_from_text_area(app, text_area: TextArea, strip_phone_plus: bool = False, timeout: int = 2) -> bool:
    """Extract then copy from a TextArea."""
    extracted = extract_textarea_copy_text(text_area, strip_phone_plus=strip_phone_plus)
    if not extracted:
        _notify_warning(app, "Nothing selected to copy", timeout=timeout)
        return False
    return copy_to_clipboard(app, extracted, timeout=timeout)


def copy_selected_cell_from_table(
    app,
    table: DataTable,
    columns: Sequence[str],
    timeout: int = 2,
) -> bool:
    """Copy the currently selected cell from a DataTable."""
    if table.row_count == 0:
        _notify_warning(app, "No data to copy", timeout=timeout)
        return False

    cursor_row = table.cursor_row
    cursor_col = table.cursor_column
    if cursor_row is None or cursor_col is None:
        _notify_warning(app, "No cell selected", timeout=timeout)
        return False

    try:
        cell_value = table.get_cell_at((cursor_row, cursor_col))
        copy_text = str(cell_value)
    except Exception:
        logger.exception("Failed to get selected DataTable cell")
        _notify_error(app, "❌ Copy failed", timeout=3)
        return False

    ok = copy_to_clipboard(app, copy_text, preview_len=40, timeout=timeout, notify_success=False)
    if ok:
        col_name = columns[cursor_col] if cursor_col < len(columns) else "Cell"
        preview = copy_text[:40] + ("..." if len(copy_text) > 40 else "")
        _notify_success(app, f"✅ Copied {col_name}: {preview}", timeout=timeout)
    return ok


