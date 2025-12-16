# -*- coding: utf-8 -*-

"""Host information screen for Device Spy TUI."""

from pathlib import Path
from typing import Dict, List, Tuple

from returns.result import Failure, Success
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
)

from ...tui_common import BaseScreen
from ..data_manager import DataManager, get_devices_by_host, get_hosts_by_query



from textual.widget import Widget

class HostInfoWidget(Widget):
    """Display host information along with connected devices and local apps."""
    
    def __init__(self) -> None:
        super().__init__()
        self._hosts: List[Dict] = []
        self._devices: List[Dict] = []
        self._host_options_loaded: bool = False
        self._all_host_options: List[Tuple[str, str]] = []

    def compose(self):
        # Header/Footer handled by parent screen or ignored in embedded mode
        with Vertical(id="host-container"):
            yield Label("🖥️ Host information", id="host-title")
            yield Input(
                placeholder="Enter hostname or alias...",
                id="host-query",
            )
            yield Select(
                options=[],
                prompt="Select host (auto-loaded)",
                id="host-select",
            )
            with Horizontal(id="host-buttons"):
                yield Button("Search", id="search-btn", variant="primary")
                yield Button("Refresh cache", id="refresh-btn")
                yield Button("Back", id="back-btn")

            # Use a container with overflow-y: scroll for native scrolling
            result_container = Container(
                Static(id="result-area", expand=True),
                id="result-container",
            )
            result_container.styles.height = 20
            result_container.styles.overflow_y = "scroll"
            yield result_container

    def on_mount(self) -> None:
        """Initialize screen state."""
        self.query_one("#host-query", Input).focus()
        self._update_status("Enter hostname or alias to load host information.")
        self.app.call_later(self._load_host_options)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button events."""
        if event.button.id == "search-btn":
            await self._load_host_info()
        elif event.button.id == "refresh-btn":
            await self._load_host_info(force_refresh=True)
            await self._load_host_options(force_refresh=True)
        elif event.button.id == "back-btn":
            # If embedded, app.action_back handles it. If standalone, we might need a custom signal or bubbling.
            # BaseScreen.action_back calls app.pop_screen. 
            # We can trigger action_back on the app.
            self.app.action_back()

    async def on_select_changed(self, event: Select.Changed) -> None:
        """Sync selected host to input box."""
        if event.select.id == "host-select":
            value = event.value
            if isinstance(value, str):
                self.query_one("#host-query", Input).value = value

    async def on_input_changed(self, event: Input.Changed) -> None:
        """Filter dropdown options as user types."""
        if event.input.id != "host-query":
            return
        query = (event.value or "").strip().lower()
        select = self.query_one("#host-select", Select)
        filtered = self._filter_options(query)
        select.set_options(filtered)
        current_value = select.value
        if current_value and current_value not in [v for _, v in filtered]:
            select.clear()
        self._show_live_matches(filtered, query)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Trigger search when Enter is pressed."""
        if event.input.id == "host-query":
            await self._load_host_info()

    async def _load_host_info(self, force_refresh: bool = False) -> None:
        query = self.query_one("#host-query", Input).value.strip()
        if not query:
            select_value = self.query_one("#host-select", Select).value
            query = select_value.strip() if isinstance(select_value, str) else ""

        if not query:
            self._update_status("Please enter or select a hostname/alias.")
            return

        self._update_status(f"Loading host data for '{query}'...")
        data_manager: DataManager = self.app.data_manager

        hosts_result = (
            data_manager.get_hosts(force_refresh=force_refresh)
            if query == "*"
            else get_hosts_by_query(data_manager, query)
        )

        if isinstance(hosts_result, Failure):
            error_msg = str(hosts_result.failure())
            self._update_status(f"Error: {error_msg}")
            self._update_result(f"Error loading hosts: {error_msg}")
            return

        devices_result = data_manager.get_devices(force_refresh=force_refresh)
        if isinstance(devices_result, Failure):
            error_msg = str(devices_result.failure())
            self._update_status(f"Error: {error_msg}")
            self._update_result(f"Error loading devices: {error_msg}")
            return

        self._hosts = hosts_result.unwrap()
        self._devices = devices_result.unwrap()

        if not self._hosts:
            message = f"No hosts found for '{query}'."
            self._update_status(message)
            self._update_result(message)
            return

        result_lines: List[str] = [
            f"Query: {query}",
            f"Matched hosts: {len(self._hosts)}",
            "-" * 60,
        ]

        for host in self._hosts:
            result_lines.extend(self._format_host_block(host))
            result_lines.append("-" * 60)

        result_lines.append(self._format_local_apps())

        self._update_result("\n".join(result_lines))
        self._update_status("Host information loaded.")

    async def _load_host_options(self, force_refresh: bool = False) -> None:
        """Populate dropdown with host list."""
        if self._host_options_loaded and not force_refresh:
            return

        data_manager: DataManager = self.app.data_manager
        hosts_result = data_manager.get_hosts(force_refresh=force_refresh)

        if isinstance(hosts_result, Failure):
            self._update_status(f"Dropdown load error: {hosts_result.failure()}")
            return

        hosts = hosts_result.unwrap()
        options = []
        for host in hosts:
            hostname = host.get("hostname", "")
            alias = host.get("alias", "")
            label = f"{alias or hostname} ({hostname})" if hostname else alias
            if not label:
                continue
            options.append((label, hostname))

        select = self.query_one("#host-select", Select)
        self._all_host_options = options
        select.set_options(options)
        self._host_options_loaded = True
        self._show_live_matches(options, "")

    def _filter_options(self, query: str) -> List[Tuple[str, str]]:
        if not query:
            return self._all_host_options
        query_lower = query.lower()
        return [
            (label, value)
            for label, value in self._all_host_options
            if query_lower in label.lower() or query_lower in value.lower()
        ]

    def _show_live_matches(self, options: List[Tuple[str, str]], query: str) -> None:
        """Display live match preview under the input."""
        if query is None:
            query = ""
        query_display = query if query else "all"
        lines = [f"Live matches ({len(options)}) for '{query_display}':"]
        preview = options[:10]
        for label, value in preview:
            lines.append(f"  - {label} [{value}]")
        if len(options) > len(preview):
            lines.append(f"  ... {len(options) - len(preview)} more")
        self._update_result("\n".join(lines))

    def _format_host_block(self, host: Dict) -> List[str]:
        hostname = host.get("hostname", "N/A")
        alias = host.get("alias", "N/A")
        platform_name = host.get("platform", "N/A")
        version = host.get("version", "")
        platform = f"{platform_name} {version}".strip()
        appium = host.get("appium_count", "N/A")

        host_devices = get_devices_by_host(self._devices, hostname)
        mobile_devices = [
            device
            for device in host_devices
            if device.get("platform") in ["android", "ios"]
        ]
        android_devices = [
            device for device in mobile_devices if device.get("platform") == "android"
        ]
        ios_devices = [
            device for device in mobile_devices if device.get("platform") == "ios"
        ]
        locked_count = sum(1 for device in mobile_devices if device.get("is_locked"))

        lines = [
            f"{alias} ({hostname})",
            f"Platform: {platform}",
            f"Appium services: {appium}",
            "Capacity: "
            f"{host.get('default_ios_devices_amount', 0)} iOS | "
            f"{host.get('default_android_devices_amount', 0)} Android | "
            f"{host.get('max_ios_simulator_concurrency', 0)} simulators",
            "Devices: "
            f"{len(mobile_devices)} total | "
            f"{len(ios_devices)} iOS | {len(android_devices)} Android | "
            f"{len(mobile_devices) - locked_count} available | {locked_count} locked",
            "Connected devices:",
        ]

        if not mobile_devices:
            lines.append("  - None")
            return lines

        for device in mobile_devices:
            lines.append(self._format_device_line(device))
        return lines

    def _format_device_line(self, device: Dict) -> str:
        model = device.get("model", "N/A")
        os_version = device.get("platform_version", "N/A")
        udid = device.get("udid", "N/A")
        status_icon = "🔒" if device.get("is_locked") else "✅"
        labels = device.get("labels") or []
        label_text = f" [{', '.join(labels)}]" if labels else ""
        return (
            f"  - {status_icon} {model} ({os_version}) "
            f"{device.get('platform', '')} • UDID: {udid}{label_text}"
        )

    def _format_local_apps(self) -> str:
        try:
            apps_dir = Path.home() / "Downloads" / "apps"
            if not apps_dir.exists() or not apps_dir.is_dir():
                return "Local packages: ~/Downloads/apps not found."

            files = [entry for entry in apps_dir.iterdir() if entry.is_file()]
            files.sort(key=lambda item: item.stat().st_mtime, reverse=True)
            if not files:
                return "Local packages: directory is empty."

            lines = ["Local packages (~/Downloads/apps):"]
            max_items = 20
            for file in files[:max_items]:
                size_mb = file.stat().st_size / (1024 * 1024)
                lines.append(f"  - {file.name} ({size_mb:.1f} MB)")

            if len(files) > max_items:
                lines.append(f"  - ... {len(files) - max_items} more files")

            return "\n".join(lines)
        except Exception as exc:
            return f"Local packages: failed to read directory ({exc})"

    def _update_status(self, message: str) -> None:
        self.query_one("#host-title", Label).update(message)

    def _update_result(self, content: str) -> None:
        self.query_one("#result-area", Static).update(content)


class HostInfoScreen(BaseScreen):
    """Display host information along with connected devices and local apps."""

    def compose(self):
        yield Header()
        yield HostInfoWidget()
        yield Footer()
