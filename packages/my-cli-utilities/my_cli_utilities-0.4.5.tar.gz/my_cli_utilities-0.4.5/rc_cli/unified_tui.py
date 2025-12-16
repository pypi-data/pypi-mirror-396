# -*- coding: utf-8 -*-

def run_unified_tui():
    """Run the unified TUI application."""
    from rc_cli.tui.unified_app import UnifiedTUIApp

    app = UnifiedTUIApp()
    app.run()
