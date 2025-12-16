# -*- coding: utf-8 -*-

"""Enhanced DataManager using returns library for better error handling."""

import os
import time
import logging
from typing import Optional, Dict, List
from returns.result import Result, Success, Failure
from returns.maybe import Maybe, Some, Nothing
from returns.curry import curry

from rc_cli.common_lib.config import BaseConfig
from rc_cli.common_lib.http_helpers import make_sync_request
from .result_types import (
    AppError, ErrorType, DeviceListResult, HostListResult,
    network_error, data_not_found_error, system_error
)

logger = logging.getLogger(__name__)


class Config(BaseConfig):
    """Configuration constants for Device Spy CLI."""
    BASE_URL = os.environ.get(
        "DS_BASE_URL",
        "https://device-spy.example.com"
    )
    HOSTS_ENDPOINT = f"{BASE_URL}/api/v1/hosts"
    ALL_DEVICES_ENDPOINT = f"{BASE_URL}/api/v1/hosts/get_all_devices"
    DEVICE_ASSETS_ENDPOINT = f"{BASE_URL}/api/v1/device_assets/"
    DISPLAY_WIDTH = 60  # Width for status display formatting


class DataManager:
    """Enhanced data management with functional error handling using returns library."""
    
    def __init__(self, cache_timeout: int = 300):  # 5 minutes default
        # Load config file environment variables when used as a library.
        # (CLI entrypoint already loads env early, but we avoid relying on import order.)
        from rc_cli.env_loader import load_env
        load_env()

        self._devices_cache = None
        self._hosts_cache = None
        self._devices_cache_time = 0
        self._hosts_cache_time = 0
        self.cache_timeout = cache_timeout
    
    def _is_cache_expired(self, cache_time: float) -> bool:
        """Check if cache has expired."""
        return time.time() - cache_time > self.cache_timeout
    
    def _fetch_from_api(self, endpoint: str) -> Result[Dict, AppError]:
        """Fetch data from API endpoint with error handling."""
        try:
            response_data = make_sync_request(endpoint)
            if response_data is None:
                return Failure(network_error(
                    "No response from API",
                    f"Failed to get response from {endpoint}"
                ))
            
            if "data" not in response_data:
                return Failure(data_not_found_error(
                    "Invalid API response format",
                    ["Expected 'data' field in response", "Check API endpoint"]
                ))
            
            return Success(response_data)
        
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return Failure(network_error(
                "API request failed",
                str(e)
            ))
    
    def _update_cache(self, cache_attr: str, time_attr: str, data: List[Dict], data_type: str) -> None:
        """Update cache with new data."""
        setattr(self, cache_attr, data)
        setattr(self, time_attr, time.time())
        logger.debug(f"Cached {len(data)} {data_type}")
    
    def _get_cached_data(self, cache_attr: str, time_attr: str) -> Maybe[List[Dict]]:
        """Get cached data if available and not expired."""
        cache_data = getattr(self, cache_attr)
        cache_time = getattr(self, time_attr)
        
        if cache_data is None or self._is_cache_expired(cache_time):
            return Nothing
        
        return Some(cache_data)
    
    def _fetch_and_cache_data(self, endpoint: str, cache_attr: str, time_attr: str, 
                            data_type: str) -> Result[List[Dict], AppError]:
        """Fetch data from API and update cache."""
        return self._fetch_from_api(endpoint).map(
            lambda response: response["data"]
        ).map(
            lambda data: self._update_cache_and_return(cache_attr, time_attr, data, data_type)
        )
    
    def _update_cache_and_return(self, cache_attr: str, time_attr: str, 
                               data: List[Dict], data_type: str) -> List[Dict]:
        """Helper to update cache and return data."""
        self._update_cache(cache_attr, time_attr, data, data_type)
        return data
    
    def _get_data_with_cache(self, endpoint: str, cache_attr: str, time_attr: str,
                           data_type: str, force_refresh: bool = False) -> Result[List[Dict], AppError]:
        """Get data with caching logic using functional approach."""
        if force_refresh:
            return self._fetch_and_cache_data(endpoint, cache_attr, time_attr, data_type)
        
        cached_result = self._get_cached_data(cache_attr, time_attr)
        
        # If we have cached data, return it wrapped in Success
        if cached_result != Nothing:
            return Success(cached_result.unwrap())
        
        # Otherwise fetch from API
        return self._fetch_and_cache_data(endpoint, cache_attr, time_attr, data_type)
    
    def get_devices(self, force_refresh: bool = False) -> DeviceListResult:
        """Get all devices data with caching and error handling."""
        return self._get_data_with_cache(
            endpoint=Config.ALL_DEVICES_ENDPOINT,
            cache_attr='_devices_cache',
            time_attr='_devices_cache_time',
            data_type='devices',
            force_refresh=force_refresh
        )
    
    def get_hosts(self, force_refresh: bool = False) -> HostListResult:
        """Get all hosts data with caching and error handling."""
        return self._get_data_with_cache(
            endpoint=Config.HOSTS_ENDPOINT,
            cache_attr='_hosts_cache',
            time_attr='_hosts_cache_time',
            data_type='hosts',
            force_refresh=force_refresh
        )
    
    def clear_cache(self) -> None:
        """Clear all cached data to free memory."""
        self._devices_cache = None
        self._hosts_cache = None
        self._devices_cache_time = 0
        self._hosts_cache_time = 0
    
    def is_devices_cached(self) -> bool:
        """Check if devices are currently cached."""
        return self._devices_cache is not None
    
    def is_hosts_cached(self) -> bool:
        """Check if hosts are currently cached."""
        return self._hosts_cache is not None
    
    def get_cached_device_count(self) -> int:
        """Get the number of cached devices."""
        return len(self._devices_cache) if self._devices_cache else 0
    
    def get_cached_host_count(self) -> int:
        """Get the number of cached hosts."""
        return len(self._hosts_cache) if self._hosts_cache else 0


# Functional utilities for working with device/host data
@curry
def find_device_by_udid(udid: str, devices: List[Dict]) -> Maybe[Dict]:
    """Find device by UDID in a functional way."""
    matching_devices = [d for d in devices if d.get("udid") == udid]
    return Some(matching_devices[0]) if matching_devices else Nothing


@curry
def find_host_by_query(query: str, hosts: List[Dict]) -> Maybe[List[Dict]]:
    """Find hosts by query in a functional way."""
    query_lower = query.lower()
    matching_hosts = [
        host for host in hosts
        if (query_lower in host.get("hostname", "").lower() or
            query_lower in host.get("alias", "").lower())
    ]
    return Some(matching_hosts) if matching_hosts else Nothing


@curry
def filter_available_devices(platform: str, devices: List[Dict]) -> List[Dict]:
    """Filter available devices by platform."""
    return [
        device for device in devices
        if (device.get("platform") == platform and
            not device.get("is_locked", False))
    ]


@curry
def filter_devices_by_platform(platform: str, devices: List[Dict]) -> List[Dict]:
    """Filter devices by platform (both locked and available)."""
    return [
        device for device in devices
        if device.get("platform") == platform
    ]


@curry
def filter_devices_by_host(hostname: str, devices: List[Dict]) -> List[Dict]:
    """Filter devices by hostname."""
    return [device for device in devices if device.get("hostname") == hostname]


def get_device_summary(devices: List[Dict]) -> Dict[str, int]:
    """Get a summary of device counts by platform and status."""
    summary = {
        "android": 0,
        "ios": 0,
        "available": 0,
        "locked": 0,
        "total": len(devices)
    }
    for device in devices:
        if device.get("platform") == "android":
            summary["android"] += 1
        elif device.get("platform") == "ios":
            summary["ios"] += 1
        
        if not device.get("is_locked", False):
            summary["available"] += 1
        else:
            summary["locked"] += 1
            
    return summary


def get_devices_by_host(devices: List[Dict], hostname: str) -> List[Dict]:
    """Filter devices by a specific hostname."""
    return [device for device in devices if device.get("hostname") == hostname]


# Composition helpers for common operations
def get_device_by_udid(data_manager: DataManager, udid: str) -> Result[Dict, AppError]:
    """Get a specific device by UDID using functional composition."""
    return data_manager.get_devices().bind(
        lambda devices: find_device_by_udid(udid)(devices).map(
            lambda device: Success(device)
        ).value_or(
            Failure(data_not_found_error(
                f"Device with UDID '{udid}' not found",
                ["Use 'ds devices android' or 'ds devices ios' to see available devices"]
            ))
        )
    )


def get_all_devices_by_platform(data_manager: DataManager, 
                                    platform: str) -> Result[List[Dict], AppError]:
    """Get all devices for a platform (including locked) using functional composition."""
    return data_manager.get_devices().map(
        filter_devices_by_platform(platform)
    )


def get_available_devices_by_platform(data_manager: DataManager, 
                                    platform: str) -> Result[List[Dict], AppError]:
    """Get available devices for a platform using functional composition."""
    return data_manager.get_devices().map(
        filter_available_devices(platform)
    )


def get_hosts_by_query(data_manager: DataManager, 
                      query: str) -> Result[List[Dict], AppError]:
    """Get hosts by query using functional composition."""
    return data_manager.get_hosts().bind(
        lambda hosts: find_host_by_query(query)(hosts).map(
            lambda found_hosts: Success(found_hosts)
        ).value_or(
            Failure(data_not_found_error(
                f"No hosts found matching '{query}'",
                ["Try a partial hostname or alias (e.g., 'XMNA' or '106')"]
            ))
        )
    ) 