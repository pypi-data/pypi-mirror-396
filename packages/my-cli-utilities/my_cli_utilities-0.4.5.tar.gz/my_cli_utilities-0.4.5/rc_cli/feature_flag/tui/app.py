# -*- coding: utf-8 -*-

"""FFS TUI application."""

from textual.app import App
from textual.binding import Binding
from .menu_screen import MainMenuScreen
from .search_screen import FFSSearchScreen
from .get_screen import FFSGetScreen
from .evaluate_screen import FFSEvaluateScreen
from .check_screen import FFSCheckScreen
from .info_screen import FFSInfoScreen
from rc_cli.tui_css_common import COMMON_TUI_CSS


class FFSTUIApp(App):
    """Main TUI application for FFS management."""
    
    CSS = COMMON_TUI_CSS + """
    
    #menu-container {
        width: 60;
        height: auto;
        border: solid $primary;
        padding: 1;
    }
    
    #menu-title {
        text-align: center;
        width: 100%;
        margin: 1;
    }
    
    #menu-buttons {
        width: 100%;
        height: auto;
    }
    
    #menu-buttons > Button {
        width: 100%;
        margin: 1;
    }
    
    #search-container, #get-container, #evaluate-container,
    #check-container, #info-container {
        width: 90;
        height: auto;
        border: solid $primary;
        padding: 1;
    }
    
    #search-title, #get-title, #evaluate-title,
    #check-title, #info-title {
        text-align: center;
        width: 100%;
        margin: 1;
    }
    
    #search-results {
        height: 20;
        width: 100%;
    }
    
    #result-area, #info-area {
        height: 28;
        width: 100%;
        scrollbar-size: 1 1;
    }
    
    #search-input, #flag-id-input, #account-id-input,
    #extension-id-input, #email-domain-input {
        width: 100%;
        margin: 1;
    }
    
    #search-buttons, #get-buttons, #evaluate-buttons,
    #check-buttons, #info-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    
    #search-buttons > Button, #get-buttons > Button,
    #evaluate-buttons > Button, #check-buttons > Button,
    #info-buttons > Button {
        margin: 1;
    }
    """
    
    TITLE = "FFS Management TUI"
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        # Escape key is handled by each Screen individually, not at App level
    ]
    
    def on_mount(self) -> None:
        """Set up the initial screen."""
        self.push_screen("main")
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
    
    def action_back(self) -> None:
        """Go back to previous screen."""
        if len(self.screen_stack) > 1:
            self.pop_screen()
        # Note: Esc key on main screen is handled by MainMenuScreen's escape binding, won't call here
    
    def push_screen(self, screen_name: str) -> None:
        """Push a screen by name."""
        screens = {
            "main": MainMenuScreen(),
            "ffs_search": FFSSearchScreen(),
            "ffs_get": FFSGetScreen(),
            "ffs_evaluate": FFSEvaluateScreen(),
            "ffs_check": FFSCheckScreen(),
            "ffs_info": FFSInfoScreen(),
        }
        
        if screen_name in screens:
            super().push_screen(screens[screen_name])


def run_tui():
    """Run the TUI application."""
    try:
        app = FFSTUIApp()
        app.run()
    except Exception as e:
        import sys
        print(f"Error running TUI: {e}", file=sys.stderr)
        raise

