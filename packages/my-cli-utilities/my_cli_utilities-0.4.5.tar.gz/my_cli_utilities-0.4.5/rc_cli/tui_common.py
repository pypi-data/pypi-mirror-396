# -*- coding: utf-8 -*-

"""Common TUI components and base classes for RC CLI."""

from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import TextArea
from textual.binding import Binding
from textual import events


class BaseScreen(Screen):
    """Base screen with common functionality."""
    
    BINDINGS = [
        Binding("escape", "back", "Back", priority=True),
    ]
    
    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()


class ScrollableTextAreaMixin:
    """Mixin for screens with scrollable TextArea."""
    
    async def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        """Handle scroll with reduced step for better UX."""
        control = event.control
        if isinstance(control, TextArea):
            control.action_scroll_up()
            event.stop()
    
    async def on_mouse_scroll_down(self, event: events.MouseScrollDown) -> None:
        """Handle scroll with reduced step for better UX."""
        control = event.control
        if isinstance(control, TextArea):
            control.action_scroll_down()
            event.stop()


class BaseInfoScreen(BaseScreen, ScrollableTextAreaMixin):
    """Base info screen with TextArea scrolling support."""
    
    BINDINGS = [
        *BaseScreen.BINDINGS,
        Binding("c", "copy_selected", "Copy Selected", show=True),
        Binding("a", "copy_all", "Copy All", show=True),
        Binding("A", "copy_all", "Copy All", show=False),
    ]

    def on_mount(self) -> None:
        """Initialize with scroll settings."""
        if hasattr(self, 'query_one'):
            try:
                text_area = self.query_one("#info-area", TextArea)
                text_area.show_line_numbers = False
            except Exception:
                # Fallback if info-area doesn't exist
                pass

    def action_copy_selected(self) -> None:
        """Copy selected text (or best-effort line at cursor) from the TextArea."""
        try:
            from rc_cli.tui_clipboard import copy_from_text_area

            text_area = self.query_one("#info-area", TextArea)
            copy_from_text_area(self.app, text_area, strip_phone_plus=True, timeout=2)
        except Exception:
            self.app.notify("Nothing to copy", severity="warning", timeout=2)

    def action_copy_all(self) -> None:
        """Copy entire TextArea content."""
        try:
            from rc_cli.tui_clipboard import copy_to_clipboard

            text_area = self.query_one("#info-area", TextArea)
            copy_to_clipboard(self.app, text_area.text or "", timeout=2)
        except Exception:
            self.app.notify("Nothing to copy", severity="warning", timeout=2)


class BaseResultScreen(BaseScreen, ScrollableTextAreaMixin):
    """Base screen for displaying results in TextArea."""
    
    BINDINGS = [
        *BaseScreen.BINDINGS,
        Binding("c", "copy_selected", "Copy Selected", show=True),
        Binding("a", "copy_all", "Copy All", show=True),
        Binding("A", "copy_all", "Copy All", show=False),
    ]

    def on_mount(self) -> None:
        """Initialize with scroll settings."""
        if hasattr(self, 'query_one'):
            try:
                result_area = self.query_one("#result-area", TextArea)
                result_area.show_line_numbers = False
            except Exception:
                # Fallback if result-area doesn't exist
                pass

    def action_copy_selected(self) -> None:
        """Copy selected text (or best-effort line at cursor) from the TextArea."""
        try:
            from rc_cli.tui_clipboard import copy_from_text_area

            result_area = self.query_one("#result-area", TextArea)
            copy_from_text_area(self.app, result_area, strip_phone_plus=True, timeout=2)
        except Exception:
            self.app.notify("Nothing to copy", severity="warning", timeout=2)

    def action_copy_all(self) -> None:
        """Copy entire TextArea content."""
        try:
            from rc_cli.tui_clipboard import copy_to_clipboard

            result_area = self.query_one("#result-area", TextArea)
            copy_to_clipboard(self.app, result_area.text or "", timeout=2)
        except Exception:
            self.app.notify("Nothing to copy", severity="warning", timeout=2)


class BaseInfoWidget(Widget, ScrollableTextAreaMixin):
    """Base info widget with TextArea scrolling support."""
    
    BINDINGS = [
        Binding("c", "copy_selected", "Copy Selected", show=True),
        Binding("a", "copy_all", "Copy All", show=True),
        Binding("A", "copy_all", "Copy All", show=False),
    ]

    def on_mount(self) -> None:
        """Initialize with scroll settings."""
        if hasattr(self, 'query_one'):
            try:
                text_area = self.query_one("#info-area", TextArea)
                text_area.show_line_numbers = False
            except Exception:
                pass

    def action_copy_selected(self) -> None:
        try:
            from rc_cli.tui_clipboard import copy_from_text_area

            text_area = self.query_one("#info-area", TextArea)
            copy_from_text_area(self.app, text_area, strip_phone_plus=True, timeout=2)
        except Exception:
            self.app.notify("Nothing to copy", severity="warning", timeout=2)

    def action_copy_all(self) -> None:
        try:
            from rc_cli.tui_clipboard import copy_to_clipboard

            text_area = self.query_one("#info-area", TextArea)
            copy_to_clipboard(self.app, text_area.text or "", timeout=2)
        except Exception:
            self.app.notify("Nothing to copy", severity="warning", timeout=2)


class BaseResultWidget(Widget, ScrollableTextAreaMixin):
    """Base widget for displaying results in TextArea."""
    
    BINDINGS = [
        Binding("c", "copy_selected", "Copy Selected", show=True),
        Binding("a", "copy_all", "Copy All", show=True),
        Binding("A", "copy_all", "Copy All", show=False),
    ]

    def on_mount(self) -> None:
        """Initialize with scroll settings."""
        if hasattr(self, 'query_one'):
            try:
                result_area = self.query_one("#result-area", TextArea)
                result_area.show_line_numbers = False
            except Exception:
                pass

    def action_copy_selected(self) -> None:
        try:
            from rc_cli.tui_clipboard import copy_from_text_area

            result_area = self.query_one("#result-area", TextArea)
            copy_from_text_area(self.app, result_area, strip_phone_plus=True, timeout=2)
        except Exception:
            self.app.notify("Nothing to copy", severity="warning", timeout=2)

    def action_copy_all(self) -> None:
        try:
            from rc_cli.tui_clipboard import copy_to_clipboard

            result_area = self.query_one("#result-area", TextArea)
            copy_to_clipboard(self.app, result_area.text or "", timeout=2)
        except Exception:
            self.app.notify("Nothing to copy", severity="warning", timeout=2)
