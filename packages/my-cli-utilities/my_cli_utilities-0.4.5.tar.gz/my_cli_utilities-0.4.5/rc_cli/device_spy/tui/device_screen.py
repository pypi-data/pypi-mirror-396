# -*- coding: utf-8 -*-

"""Device information screen for Device Spy TUI."""

from typing import Dict, List, Optional

from returns.result import Failure, Success
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
)
from textual.widget import Widget

from ...tui_common import BaseScreen
from ..data_manager import (
    DataManager,
    get_available_devices_by_platform,
    get_device_by_udid,
)


class DeviceInfoWidget(Widget):
    """Device information widget."""

    def __init__(self) -> None:
        super().__init__()
        self._hosts_by_name: Dict[str, Dict] = {}
        self._devices: List[Dict] = []
        self._device_options_loaded: bool = False
        self._all_device_options: List[Dict] = []
        self._suppress_input_change: bool = False

    def compose(self):
        with Vertical(id="device-container"):
            yield Label("📱 Device information", id="device-title")
            yield Input(
                placeholder="Enter device UDID or model...",
                id="device-udid",
            )
            yield Select(
                options=[
                    ("Android", "android"),
                    ("iOS", "ios"),
                ],
                value="android",
                id="platform-select",
            )
            with Horizontal(id="device-buttons"):
                # "Get by UDID" is redundant with list selection, removing to simplify UI
                yield Button("List available", id="list-available-btn", variant="success")
                yield Button("List locked", id="list-locked-btn", variant="warning")
                yield Button("List all", id="list-btn", variant="primary")
                yield Button("Back", id="back-btn")
            
            # Main container that will swap between Result View and Table View
            with Container(id="main-content"):
                # Result Container for Details and Live Matches (Initially hidden if table is shown?)
                # We'll toggle visibility using styles.display
                result_container = Container(
                    Static(id="result-area", expand=True),
                    id="result-container",
                )
                result_container.styles.height = "100%"
                result_container.styles.overflow_y = "scroll"
                result_container.styles.border = ("solid", "green")
                # Hide result container initially if we want to show table
                result_container.styles.display = "none" 
                yield result_container

                yield DataTable(id="device-table")

    def on_mount(self) -> None:
        """Initialize screen state."""
        table = self.query_one("#device-table", DataTable)
        table.cursor_type = "row"
        # Table takes full height when visible
        table.styles.height = "100%"
        table.add_columns("Platform", "Model", "OS", "Host", "Status", "UDID")
        
        self.query_one("#device-udid", Input).focus()
        self._update_status("Enter a UDID/Model or list available devices.")
        self.app.call_later(self._load_device_options)

    async def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection."""
        try:
            row = event.data_table.get_row(event.row_key)
            # UDID is the last column (index 5)
            if len(row) > 5:
                udid = str(row[5])
                self._update_status(f"Selected: {udid}")
                
                # Switch to detail view
                self._show_detail_view()
                
                # Update input without triggering search results overwriting details
                current_val = self.query_one("#device-udid", Input).value
                if current_val != udid:
                    self._suppress_input_change = True
                    self.query_one("#device-udid", Input).value = udid
                
                # Clear result area immediately to show feedback
                self._update_result(f"Loading details for {udid}...")
                
                # Trigger load immediately
                self.run_worker(self._load_device_by_udid(udid))
        except Exception as e:
            self._update_status(f"Selection error: {e}")
            import traceback
            traceback.print_exc()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button events."""
        try:
            if event.button.id in ["list-btn", "list-available-btn", "list-locked-btn"]:
                # Switch to table view first
                self._show_table_view()
                
                if event.button.id == "list-btn":
                    await self._list_devices(filter_status=None)
                elif event.button.id == "list-available-btn":
                    await self._list_devices(filter_status="available")
                elif event.button.id == "list-locked-btn":
                    await self._list_devices(filter_status="locked")
            
            elif event.button.id == "back-btn":
                # If in detail view, go back to table view
                if self.query_one("#result-container").styles.display != "none":
                     self._show_table_view()
                else:
                    self.app.action_back()
        except Exception as e:
            self._update_status(f"Error handling button press: {e}")
            import traceback
            traceback.print_exc()

    def _show_table_view(self) -> None:
        """Show the device table and hide the result area."""
        self.query_one("#result-container").styles.display = "none"
        self.query_one("#device-table").styles.display = "block"
        self.query_one("#device-udid", Input).value = "" # Optional: clear input when going back to list

    def _show_detail_view(self) -> None:
        """Show the result area and hide the device table."""
        self.query_one("#result-container").styles.display = "block"
        self.query_one("#device-table").styles.display = "none"

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Trigger search when Enter is pressed."""
        if event.input.id == "device-udid":
            self._show_detail_view()
            await self._load_device()

    async def _load_device(self) -> None:
        udid = self.query_one("#device-udid", Input).value.strip()
        await self._load_device_by_udid(udid)

    async def _load_device_by_udid(self, udid: str) -> None:
        try:
            if not udid:
                self._update_status("Please enter a device UDID.")
                return

            self._update_status(f"Fetching details for {udid}...")
            data_manager: DataManager = self.app.data_manager
            
            device_result = get_device_by_udid(data_manager, udid)
            if isinstance(device_result, Failure):
                self._update_status(f"Error: {device_result.failure()}")
                self._update_result(f"Failed to load device: {device_result.failure()}")
                return

            hosts_result = data_manager.get_hosts()
            if isinstance(hosts_result, Success):
                self._hosts_by_name = {
                    host.get("hostname", ""): host for host in hosts_result.unwrap()
                }

            device = device_result.unwrap()
            self._update_result(self._format_device_detail(device))
            self._update_status("Device information loaded.")
            
            # Ensure result container is scrolled to top
            try:
                self.query_one("#result-container", Container).scroll_home(animate=False)
            except Exception:
                pass
        except Exception as e:
            self._update_status(f"Load error: {e}")
            self._update_result(f"Exception loading device: {e}")
            import traceback
            traceback.print_exc()

    async def _load_device_options(self) -> None:
        """Load all devices for search options."""
        data_manager: DataManager = self.app.data_manager
        devices_result = data_manager.get_devices()
        if isinstance(devices_result, Success):
            self._all_device_options = devices_result.unwrap()
            self._device_options_loaded = True
            self._show_live_matches(self._all_device_options, "")

    async def on_input_changed(self, event: Input.Changed) -> None:
        """Filter devices as user types."""
        if event.input.id != "device-udid":
            return
            
        if self._suppress_input_change:
            self._suppress_input_change = False
            return

        query = (event.value or "").strip().lower()
        
        # If input has content, we likely want to show matches.
        if query:
            self._show_detail_view()
        
        if not self._device_options_loaded:
            await self._load_device_options()
        
        filtered = self._filter_devices(query)
        self._show_live_matches(filtered, query)

    def _filter_devices(self, query: str) -> List[Dict]:
        if not query:
            return self._all_device_options
        query_lower = query.lower()
        return [
            d for d in self._all_device_options
            if query_lower in d.get("udid", "").lower() or 
               query_lower in d.get("model", "").lower() or
               query_lower in d.get("name", "").lower()
        ]

    def _show_live_matches(self, devices: List[Dict], query: str) -> None:
        """Display live match preview."""
        if query is None:
            query = ""
        query_display = query if query else "all"
        lines = [f"Live matches ({len(devices)}) for '{query_display}':"]
        
        # Prefer exact matches if any
        preview = devices[:10]
        for d in preview:
            model = d.get("model", "N/A")
            udid = d.get("udid", "N/A")
            status = "🔒" if d.get("is_locked") else "✅"
            lines.append(f"  - {status} {model} [{udid}]")
            
        if len(devices) > len(preview):
            lines.append(f"  ... {len(devices) - len(preview)} more")
            
        self._update_result("\n".join(lines))

    async def _list_devices(self, filter_status: Optional[str] = None) -> None:
        try:
            platform = self.query_one("#platform-select", Select).value or "android"
            data_manager: DataManager = self.app.data_manager

            from ..data_manager import filter_devices_by_platform
            
            self._update_status(f"Loading {platform} devices...")
            
            devices_result = data_manager.get_devices()
            if isinstance(devices_result, Failure):
                self._update_status(f"Error: {devices_result.failure()}")
                return

            all_devices = devices_result.unwrap()
            devices = filter_devices_by_platform(platform, all_devices)
            
            if filter_status == "available":
                devices = [d for d in devices if not d.get("is_locked")]
            elif filter_status == "locked":
                devices = [d for d in devices if d.get("is_locked")]
            
            table = self.query_one("#device-table", DataTable)
            table.clear()

            for device in devices:
                status = "Locked" if device.get("is_locked") else "Available"
                table.add_row(
                    device.get("platform", "N/A"),
                    device.get("model", "N/A"),
                    device.get("platform_version", "N/A"),
                    device.get("hostname", "N/A"),
                    status,
                    device.get("udid", "N/A"),
                )

            status_text = filter_status if filter_status else "all"
            self._update_status(f"Listed {len(devices)} {status_text} {platform} devices.")
        except Exception as e:
            self._update_status(f"Error listing devices: {e}")
            import traceback
            traceback.print_exc()

    def _format_device_detail(self, device: Dict) -> str:
        hostname = device.get('hostname')
        alias = self._hosts_by_name.get(hostname, {}).get("alias")
        
        host_display = alias if alias else (hostname if hostname else "N/A")
        ip_display = hostname if hostname else (device.get('host_ip') or "N/A")

        lines = [
            f"UDID: {device.get('udid', 'N/A')}",
            f"Name: {device.get('name', 'N/A')}",
            f"Platform: {device.get('platform', 'N/A')} {device.get('platform_version', '')}",
            f"Model: {device.get('model', 'N/A')}",
            f"Host: {host_display}",
            f"IP: {ip_display}",
            f"Status: {'Locked' if device.get('is_locked') else 'Available'}",
        ]

        adb_port = device.get("adb_port")
        if adb_port:
            lines.append(f"ADB: {device.get('hostname', 'N/A')}:{adb_port}")

        labels = device.get("labels")
        if labels:
            lines.append(f"Labels: {', '.join(labels)}")

        location = device.get("location")
        if location:
            lines.append(f"Location: {location}")

        return "\n".join(lines)

    def _format_host_alias(self, hostname: Optional[str]) -> str:
        if not hostname:
            return "N/A"
        alias = self._hosts_by_name.get(hostname, {}).get("alias")
        return f"{alias} ({hostname})" if alias else hostname

    def _update_status(self, message: str) -> None:
        self.query_one("#device-title", Label).update(message)

    def _update_result(self, content: str) -> None:
        self.query_one("#result-area", Static).update(content)


class DeviceInfoScreen(BaseScreen):
    """Display device information and available device lists."""

    def compose(self):
        yield Header()
        yield DeviceInfoWidget()
        yield Footer()
