# -*- coding: utf-8 -*-

import threading
import time
from typing import Dict, List, Optional

import typer
from rich.text import Text
from rich.console import Console
from rc_cli.common_lib.pagination import paginated_display, get_single_key_input
from rc_cli.common_lib.config import BaseConfig

from .display_managers import BaseDisplayManager

console = Console()


class Config(BaseConfig):
    pass


class HostDisplayManager(BaseDisplayManager):
    """Handles host information display."""
    
    @staticmethod
    def display_host_results(hosts: List[Dict], query: str) -> None:
        """Display host search results."""
        typer.echo(f"\n🔍 Host Search Results for: '{query}'")
        typer.echo("=" * Config.DISPLAY_WIDTH)
        
        for i, host in enumerate(hosts, 1):
            hostname = BaseDisplayManager.get_safe_value(host, "hostname")
            alias = BaseDisplayManager.get_safe_value(host, "alias")
            typer.echo(f"{i}. {alias} ({hostname})")
        
        typer.echo("=" * Config.DISPLAY_WIDTH)

    @staticmethod
    def display_detailed_host_info(host: Dict, devices: List[Dict]) -> None:
        """Display comprehensive host information."""
        hostname = BaseDisplayManager.get_safe_value(host, "hostname")
        alias = BaseDisplayManager.get_safe_value(host, "alias")
        
        typer.echo(f"\n🖥️  Host Information: {alias}")
        typer.echo("=" * Config.DISPLAY_WIDTH)
        
        # Basic information
        HostDisplayManager._display_basic_info(host)
        HostDisplayManager._display_configuration(host)
        HostDisplayManager._display_device_statistics(host, devices)
        
        # Jenkins information
        typer.echo("\n💼 Jenkins Integration:")
        jenkins_info = HostDisplayManager._get_jenkins_info(alias, hostname)
        HostDisplayManager._display_jenkins_info(jenkins_info)
        
        # Start asynchronous system resource loading (background, no loading message)
        start_time = time.time()
        system_result = {}
        def load_system_resources():
            try:
                system_result['data'] = HostDisplayManager._get_system_resources(hostname)
                system_result['status'] = 'completed'
                system_result['time'] = time.time() - start_time
            except Exception as e:
                # Provide detailed error information for debugging
                error_msg = str(e)
                if "SSH password not found" in error_msg:
                    system_result['data'] = f"❌ Missing SSH credentials. Set SSH_PASSWORD_{hostname.upper().replace('.', '_').replace('-', '_')} or SSH_PASSWORD"
                elif "Authentication" in error_msg or "Permission denied" in error_msg:
                    system_result['data'] = f"❌ SSH authentication failed. Check password for {hostname}"
                elif "sshpass" in error_msg and "not found" in error_msg:
                    system_result['data'] = f"❌ sshpass not installed. Run: brew install hudochenkov/sshpass/sshpass"
                else:
                    system_result['data'] = f"❌ Error: {error_msg[:60]}..."
                system_result['status'] = 'error'
                system_result['time'] = time.time() - start_time
        
        system_thread = threading.Thread(target=load_system_resources)
        system_thread.start()
        
        # Device details (system resources load in background while user browses)
        if not HostDisplayManager._display_device_details(devices):
            return
        
        # Ask user whether to continue viewing system resources
        if not HostDisplayManager._confirm_continue_viewing():
            return
        
        # Wait and display system resources
        system_thread.join()
        exec_time = system_result.get('time', 0)
        
        if system_result.get('status') == 'completed':
            if 'data' in system_result:
                HostDisplayManager._display_result(system_result['data'], "💻 System Resources:")
        else:
            # Display specific error information
            if 'data' in system_result:
                HostDisplayManager._display_result(system_result['data'], "💻 System Resources:")
            else:
                typer.echo(f"\n💻 System Resources:")
                typer.echo(f"   ❌ Failed to load system information ({exec_time:.1f}s)")
        
        HostDisplayManager._display_usage_tips(alias)

    @staticmethod
    def _display_result(result: str, title: str) -> None:
        """Unified result display method"""
        typer.echo(f"\n{title}")
        for line in result.split('\n'):
            if line.strip():
                typer.echo(line if line.startswith('   ') else f"   {line}")

    @staticmethod
    def _get_system_resources(hostname: str) -> str:
        """Get system resource information"""
        try:
            import os
            perf_mode = os.environ.get('DS_PERF_MODE', 'fast')
            
            from rc_cli.common_lib.system_helpers import SimpleSystemHelper
            helper = SimpleSystemHelper(mode=perf_mode)
            resources = helper.get_system_resources(hostname)
            
            if not resources:
                raise Exception("Failed to retrieve system resources")
            
            cores_info = f"{resources.cpu_physical_cores}P/{resources.cpu_logical_cores}L"
            cpu_brand_short = resources.cpu_brand.replace("Apple ", "").replace(" with ", " w/")[:40]
            
            lines = [
                f"CPU:          {cpu_brand_short} ({cores_info}) - {'[No CPU monitoring]' if perf_mode == 'ultra_fast' else f'{resources.cpu_usage_percent}%'}",
                f"Memory:       {resources.memory_used_gb}GB / {resources.memory_total_gb}GB ({resources.memory_usage_percent}%)",
                f"Disk:         {resources.disk_used_gb}GB / {resources.disk_total_gb}GB ({resources.disk_usage_percent}%)",
                f"Load/Uptime:  {resources.load_average} | {resources.uptime_hours:.1f}h"
            ]
            
            if perf_mode != "fast":
                mode_desc = "super fast, no CPU monitoring" if perf_mode == "ultra_fast" else "set DS_PERF_MODE=fast for balance"
                lines.append(f"Perf Mode:    {resources.mode} ({mode_desc})")
            
            return "\n".join(lines)
        except Exception as e:
            # Re-raise exception to let upper layer handle specific error information
            raise e

    @staticmethod
    def _display_jenkins_info(jenkins_info: Optional[Dict]) -> None:
        """Displays formatted Jenkins information."""
        if not jenkins_info:
            typer.echo("   ❌ No Jenkins agent found or error fetching info.")
            return
        
        if jenkins_info.get('error'):
            typer.echo(f"   ⚠️  {jenkins_info['error']}")
            return

        online_status = "🟢 Online" if jenkins_info.get('online') else "🔴 Offline"
        total_executors = jenkins_info.get('total_executors', 0)
        busy_executors = jenkins_info.get('busy_executors', 0)
        
        typer.echo(f"   {online_status} • {total_executors} executors ({busy_executors} busy)")
        
        # Display busy executor details
        if busy_executors > 0:
            executors = jenkins_info.get('executors', [])
            for executor in executors:
                if not executor.get('idle'):
                    executable = executor.get('current_executable')
                    if executable:
                        display_name = executable.get('display_name', 'Unknown Job')
                        markup = f"     - Executing: [bold cyan]{display_name}[/bold cyan]"
                        console.print(Text.from_markup(markup))
        
        labels = jenkins_info.get('labels', [])
        if labels:
            typer.echo(f"   🏷️  Labels: {', '.join(labels)}")
        else:
            typer.echo(f"   🏷️  Labels: No labels")

    @staticmethod
    def _get_jenkins_info(alias: str, hostname: str) -> Optional[Dict]:
        """Get Jenkins information and return dictionary directly."""
        try:
            from rc_cli.common_lib.jenkins_helpers import get_jenkins_info_for_host
            
            jenkins_host = alias if alias.upper().startswith('XMNA') else hostname
            return get_jenkins_info_for_host(jenkins_host)

        except (ImportError, Exception) as e:
            # In case of any error, return a dictionary with an error message
            return {'error': f"Failed to get Jenkins info: {e}"}

    @staticmethod
    def _display_basic_info(host: Dict) -> None:
        """Display basic host information."""
        alias = BaseDisplayManager.get_safe_value(host, "alias")
        hostname = BaseDisplayManager.get_safe_value(host, "hostname")
        platform_name = host.get('platform', 'N/A')
        version = host.get('version', '')
        platform = f"{platform_name} {version}".strip() if version else platform_name
        
        info_lines = [
            f"Alias:        {alias}",
            f"Hostname:     {hostname}",
            f"Platform:     {platform}"
        ]
        
        remark = host.get("remark")
        if remark and remark != "N/A":
            info_lines.append(f"Description:  {remark}")
        
        ssh_status = host.get("ssh_status", False)
        ssh_icon = "✅" if ssh_status else "❌"
        info_lines.append(f"SSH Status:   {ssh_icon} {'Connected' if ssh_status else 'Disconnected'}")
        
        for line in info_lines:
            typer.echo(line)

    @staticmethod
    def _display_configuration(host: Dict) -> None:
        """Display host configuration information."""
        typer.echo(f"\n⚙️  Configuration:")
        
        ios_cap = host.get("default_ios_devices_amount", 0)
        android_cap = host.get("default_android_devices_amount", 0)
        appium_count = host.get("appium_count", 0)
        sim_max = host.get("max_ios_simulator_concurrency", 0)
        
        typer.echo(f"   Capacity: {ios_cap} iOS • {android_cap} Android • {appium_count} Appium • {sim_max} concurrent sims")

    @staticmethod
    def _display_device_statistics(host: Dict, devices: List[Dict]) -> None:
        """Display device statistics and utilization."""
        # Filter out host devices, only count mobile devices
        mobile_devices = [d for d in devices if d.get("platform") in ["android", "ios"]]
        android_devices = [d for d in mobile_devices if d.get("platform") == "android"]
        ios_devices = [d for d in mobile_devices if d.get("platform") == "ios"]
        locked_count = sum(1 for d in mobile_devices if d.get("is_locked", False))
        
        typer.echo(f"\n📊 Device Status:")
        typer.echo(f"   Live: {len(mobile_devices)} total ({len(ios_devices)} iOS, {len(android_devices)} Android) • {locked_count} locked • {len(mobile_devices) - locked_count} available")
        
        # Utilization rate
        usage_parts = []
        for platform, key, count in [("iOS", "default_ios_devices_amount", len(ios_devices)), 
                                     ("Android", "default_android_devices_amount", len(android_devices))]:
            default_count = host.get(key, 0)
            if default_count > 0:
                utilization = BaseDisplayManager.format_percentage(count, default_count)
                usage_parts.append(f"{platform} {utilization} ({count}/{default_count})")
        
        if usage_parts:
            typer.echo(f"   Usage: {' • '.join(usage_parts)}")

    @staticmethod
    def _display_device_details(devices: List[Dict]) -> bool:
        """Display detailed device list without pagination."""
        # Filter out host devices, only display mobile devices
        mobile_devices = [d for d in devices if d.get("platform") in ["android", "ios"]]
        
        if not mobile_devices:
            return True
        
        android_devices = [d for d in mobile_devices if d.get("platform") == "android"]
        ios_devices = [d for d in mobile_devices if d.get("platform") == "ios"]
        
        platforms = [("android", android_devices), ("ios", ios_devices)]
        available_platforms = [(name, devices) for name, devices in platforms if devices]
        
        # Add subtitle
        typer.echo(f"\n📋 Connected Devices:")
        typer.echo("=" * Config.DISPLAY_WIDTH)
        
        # Display devices for all platforms without pagination
        for platform_name, platform_devices in available_platforms:
            HostDisplayManager._display_platform_devices(platform_name, platform_devices)
        
        return True

    @staticmethod
    def _display_platform_devices(platform: str, devices: List[Dict]) -> bool:
        """Display devices for a specific platform without pagination."""
        platform_emoji = "🤖" if platform == "android" else "🍎"
        platform_name = platform.capitalize()
        
        title = f"{platform_emoji} {platform_name} ({len(devices)})"
        typer.echo(f"\n{title}")
        
        # Display all devices directly without pagination
        for i, device in enumerate(devices, 1):
            model = BaseDisplayManager.get_safe_value(device, "model")
            os_version = BaseDisplayManager.get_safe_value(device, "platform_version")
            udid = BaseDisplayManager.get_safe_value(device, "udid")
            status = "🔒" if device.get("is_locked", False) else "✅"
            
            typer.echo(f"   {i}. {status} {model} ({os_version}) - {udid}")
        
        return True

    @staticmethod
    def _confirm_continue_viewing() -> bool:
        """Ask user whether to continue viewing system resources, with 10-second timeout auto-exit"""
        result = get_single_key_input("\nPress Enter to view system resources or 'q' to exit (auto-exit in 10s): ", timeout=10)
        if result == 'quit':
            typer.echo("❌ Viewing stopped by user.")
            return False
        elif result == 'timeout':
            typer.echo("❌ Viewing stopped due to inactivity.")
            return False
        return True

    @staticmethod
    def _display_usage_tips(alias: str) -> None:
        """Display usage tips and suggestions."""
        typer.echo(f"\n💡 Quick tips:")
        typer.echo(f"   • ds devices android/ios - List all available devices")
        typer.echo(f"   • ds ssh {alias} - Connect to this host") 