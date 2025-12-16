# -*- coding: utf-8 -*-

"""SP TUI application."""

from textual.app import App
from textual.binding import Binding
from .menu_screen import MainMenuScreen
from .list_screen import SPListScreen
from .search_screen import SPSearchScreen
from .get_value_screen import SPGetValueScreen
from .definition_screen import SPDefinitionScreen
from .info_screen import SPInfoScreen
from rc_cli.tui_css_common import COMMON_TUI_CSS


class SPTUIApp(App):
    """Main TUI application for SP management."""
    
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
    
    #search-container, #list-container, #get-container, 
    #definition-container, #info-container {
        width: 80;
        height: auto;
        border: solid $primary;
        padding: 1;
    }
    
    #search-title, #list-title, #get-title, 
    #definition-title, #info-title {
        text-align: center;
        width: 100%;
        margin: 1;
    }
    
    #search-results, #sp-list {
        height: 20;
        width: 100%;
    }
    
    #result-area, #info-area {
        height: 28;
        width: 100%;
        scrollbar-size: 1 1;
    }
    
    #search-input, #sp-id-input, #account-id-input {
        width: 100%;
        margin: 1;
    }
    
    #search-buttons, #list-buttons, #get-buttons, 
    #definition-buttons, #info-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    
    #search-buttons > Button, #list-buttons > Button,
    #get-buttons > Button, #definition-buttons > Button,
    #info-buttons > Button {
        margin: 1;
    }
    """
    
    TITLE = "SP Management TUI"
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        # Escape key is handled by each Screen individually, not at App level
    ]
    
    def on_mount(self) -> None:
        """Set up the initial screen."""
        # Push the main menu as the initial screen
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
            "sp_list": SPListScreen(),
            "sp_search": SPSearchScreen(),
            "sp_get_value": SPGetValueScreen(),
            "sp_definition": SPDefinitionScreen(),
            "sp_info": SPInfoScreen(),
        }
        
        if screen_name in screens:
            super().push_screen(screens[screen_name])


def run_tui():
    """Run the TUI application."""
    try:
        app = SPTUIApp()
        app.run()
    except Exception as e:
        import sys
        print(f"Error running TUI: {e}", file=sys.stderr)
        raise

