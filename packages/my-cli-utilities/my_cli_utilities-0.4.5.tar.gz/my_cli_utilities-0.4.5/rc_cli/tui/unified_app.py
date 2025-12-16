"""Unified Textual app for RC CLI."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from textual.app import App
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import ContentSwitcher, Footer, Header, TabbedContent, TabPane
from textual.widget import Widget

from rc_cli.device_spy.data_manager import DataManager as DSDataManager
from rc_cli.feature_flag.tui.check_screen import FFSCheckWidget
from rc_cli.feature_flag.tui.evaluate_screen import FFSEvaluateWidget
from rc_cli.feature_flag.tui.get_screen import FFSGetWidget
from rc_cli.feature_flag.tui.info_screen import FFSInfoWidget
from rc_cli.feature_flag.tui.menu_screen import FFSMenuWidget
from rc_cli.feature_flag.tui.search_screen import FFSSearchWidget
from rc_cli.service_parameter.tui.definition_screen import SPDefinitionWidget
from rc_cli.service_parameter.tui.get_value_screen import SPGetValueWidget
from rc_cli.service_parameter.tui.info_screen import SPInfoWidget
from rc_cli.service_parameter.tui.list_screen import SPListWidget
from rc_cli.service_parameter.tui.menu_screen import SPMenuWidget
from rc_cli.service_parameter.tui.search_screen import SPSearchWidget
from rc_cli.device_spy.tui.device_screen import DeviceInfoWidget
from rc_cli.device_spy.tui.host_screen import HostInfoWidget
from rc_cli.device_spy.tui.menu_screen import DeviceSpyMenuWidget
from rc_cli.account_pool.tui import (
    AccountPoolMenuWidget,
    GetAccountByAliasWidget,
    GetAccountByPhoneWidget,
    ListAliasesWidget,
)
from rc_cli.tui.unified_css import UNIFIED_TUI_CSS


TabId = str
ScreenId = str


TAB_TO_SWITCHER_ID: dict[TabId, str] = {
    "tab-ds": "switcher-ds",
    "tab-ap": "switcher-ap",
    "tab-sp": "switcher-sp",
    "tab-ffs": "switcher-ffs",
}

TAB_ROOT_SCREEN_ID: dict[TabId, ScreenId] = {
    "tab-ds": "ds_menu",
    "tab-ap": "ap_menu",
    "tab-sp": "sp_menu",
    "tab-ffs": "ffs_menu",
}


class UnifiedTUIApp(App):
    """Unified TUI for Device Spy, Account Pool, Service Params, and Feature Flags."""

    CSS = UNIFIED_TUI_CSS
    TITLE = "RC CLI Unified Manager"

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("d", "switch_to_ds", "Device Spy", priority=True),
        Binding("a", "switch_to_ap", "Account Pool", priority=True),
        Binding("s", "switch_to_sp", "Service Params", priority=True),
        Binding("f", "switch_to_ffs", "Feature Flags", priority=True),
    ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.screen_cache: dict[ScreenId, Widget] = {}
        self.nav_stacks: dict[TabId, list[ScreenId]] = {
            tab_id: [root_id] for tab_id, root_id in TAB_ROOT_SCREEN_ID.items()
        }
        self.ds_data_manager = DSDataManager()
        # Alias for DS screens that expect app.data_manager
        self.data_manager = self.ds_data_manager

    def action_switch_to_ds(self) -> None:
        self.query_one(TabbedContent).active = "tab-ds"

    def action_switch_to_sp(self) -> None:
        self.query_one(TabbedContent).active = "tab-sp"

    def action_switch_to_ap(self) -> None:
        self.query_one(TabbedContent).active = "tab-ap"

    def action_switch_to_ffs(self) -> None:
        self.query_one(TabbedContent).active = "tab-ffs"

    def compose(self):  # type: ignore[override]
        yield Header()
        with TabbedContent(initial="tab-ds"):
            with TabPane("Device Spy", id="tab-ds"):
                with ContentSwitcher(initial="ds_menu", id="switcher-ds"):
                    yield DeviceSpyMenuWidget(id="ds_menu")
            with TabPane("Account Pool", id="tab-ap"):
                with ContentSwitcher(initial="ap_menu", id="switcher-ap"):
                    yield AccountPoolMenuWidget(id="ap_menu")
            with TabPane("Service Parameter", id="tab-sp"):
                with ContentSwitcher(initial="sp_menu", id="switcher-sp"):
                    yield SPMenuWidget(id="sp_menu")
            with TabPane("Feature Flags", id="tab-ffs"):
                with ContentSwitcher(initial="ffs_menu", id="switcher-ffs"):
                    yield FFSMenuWidget(id="ffs_menu")
        yield Footer()

    def push_screen(self, screen_name_or_instance) -> None:  # type: ignore[override]
        """
        Route navigation into the active tab switcher when possible.

        If the screen belongs to a known tab flow, we mount/switch within that tab
        instead of pushing a global Screen onto the app stack.
        """
        screen_name, screen_instance = self._normalize_screen_request(screen_name_or_instance)

        active_tab = self._get_active_tab_id()
        if active_tab is None:
            super().push_screen(screen_name_or_instance)
            return

        switcher_id = TAB_TO_SWITCHER_ID.get(active_tab)
        if switcher_id is None:
            super().push_screen(screen_name_or_instance)
            return

        switcher = self.query_one(f"#{switcher_id}", ContentSwitcher)

        instance = self._get_or_create_instance(screen_name, screen_instance)
        if instance is None:
            super().push_screen(screen_name_or_instance)
            return

        self._mount_if_needed(switcher, screen_name, instance)
        switcher.current = screen_name

        stack = self.nav_stacks.setdefault(active_tab, [TAB_ROOT_SCREEN_ID.get(active_tab, "")])
        if screen_name not in stack:
            stack.append(screen_name)

    def action_back(self) -> None:
        """Navigate back within the active tab, falling back to global pop."""
        active_tab = self._get_active_tab_id()
        if active_tab is None:
            if len(self.screen_stack) > 1:
                self.pop_screen()
            return

        stack = self.nav_stacks.get(active_tab)
        if not stack or len(stack) <= 1:
            if len(self.screen_stack) > 1:
                super().action_back()
            return

        stack.pop()
        prev_screen = stack[-1]
        switcher_id = TAB_TO_SWITCHER_ID.get(active_tab)
        if not switcher_id:
            return
        self.query_one(f"#{switcher_id}", ContentSwitcher).current = prev_screen

    @staticmethod
    def _normalize_screen_request(screen_name_or_instance) -> tuple[ScreenId, Widget | None]:
        if isinstance(screen_name_or_instance, str):
            return screen_name_or_instance, None
        return f"dynamic_{id(screen_name_or_instance)}", screen_name_or_instance

    def _get_active_tab_id(self) -> TabId | None:
        try:
            active = self.query_one(TabbedContent).active
        except Exception:
            return None
        return active if isinstance(active, str) and active else None

    def _get_or_create_instance(self, screen_name: ScreenId, instance: Widget | None) -> Widget | None:
        if instance is not None:
            return instance

        factory = self._screen_factories().get(screen_name)
        if factory is None:
            return None

        cached = self.screen_cache.get(screen_name)
        if cached is not None:
            return cached

        created = factory()
        self.screen_cache[screen_name] = created
        return created

    def _screen_factories(self) -> dict[ScreenId, Callable[[], Widget]]:
        # Keep factories as a method to avoid module import side effects and allow reuse.
        return {
            # SP Screens
            "sp_list": lambda: SPListWidget(),
            "sp_search": lambda: SPSearchWidget(),
            "sp_get_value": lambda: SPGetValueWidget(),
            "sp_definition": lambda: SPDefinitionWidget(),
            "sp_info": lambda: SPInfoWidget(),
            # FFS Screens
            "ffs_search": lambda: FFSSearchWidget(),
            "ffs_get": lambda: FFSGetWidget(),
            "ffs_evaluate": lambda: FFSEvaluateWidget(),
            "ffs_check": lambda: FFSCheckWidget(),
            "ffs_info": lambda: FFSInfoWidget(),
            # DS Screens
            "ds_host_info": lambda: HostInfoWidget(),
            "ds_device_info": lambda: DeviceInfoWidget(),
            # AP Screens
            "ap_get_by_phone": lambda: GetAccountByPhoneWidget(),
            "ap_get_by_alias": lambda: GetAccountByAliasWidget(),
            "ap_list_aliases": lambda: ListAliasesWidget(),
        }

    @staticmethod
    def _mount_if_needed(switcher: ContentSwitcher, screen_name: ScreenId, widget: Widget) -> None:
        if widget.id != screen_name:
            widget.id = screen_name
        try:
            switcher.get_child_by_id(screen_name)
            return
        except Exception:
            switcher.mount(widget)


