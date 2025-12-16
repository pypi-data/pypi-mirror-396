# -*- coding: utf-8 -*-

"""Download manager for application downloads."""

import os
import threading
import time
from dataclasses import dataclass
from typing import List
import httpx
from tqdm.auto import tqdm
from rc_cli.common_lib.config import DownloadConfig
from rc_cli.common_lib.http_helpers import HTTPClientFactory


@dataclass
class DownloadResult:
    """Download result data class."""
    success: bool
    app_name: str
    size: int = 0
    duration: float = 0.0
    error_message: str = ""


class DownloadManager:
    """Download manager - handles single file downloads."""
    
    def __init__(self):
        self.print_lock = threading.Lock()
        
    def _safe_print(self, message: str) -> None:
        """Thread-safe print function."""
        with self.print_lock:
            tqdm.write(message)

    def _format_size(self, size_bytes: int) -> str:
        """Format bytes to human-readable size."""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"

    def _log_download_result(self, result: DownloadResult) -> None:
        """Log download result."""
        if result.success:
            avg_speed = result.size / result.duration if result.duration > 0 else 0
            self._safe_print(
                f"✅ Download completed: {result.app_name} ({self._format_size(result.size)}) "
                f"Avg speed: {self._format_size(avg_speed)}/s "
                f"Duration: {int(result.duration)}s"
            )
        else:
            self._safe_print(f"❌ Download failed: {result.app_name} - {result.error_message}")

    def download_single_app(self, app_name: str) -> DownloadResult:
        """Download a single application."""
        app_name = app_name.strip()
        start_time = time.time()
        
        # Ensure download directory exists
        os.makedirs(DownloadConfig.FILE_DIR, exist_ok=True)
        file_path = os.path.join(DownloadConfig.FILE_DIR, app_name)
        download_url = f"{DownloadConfig.BASE_URL}/{app_name}"

        # Remove existing file if present
        if os.path.exists(file_path):
            self._safe_print(f"🗑️  Removing existing file: {app_name}")
            try:
                os.remove(file_path)
            except OSError as e:
                return DownloadResult(False, app_name, error_message=f"Failed to remove file: {e}")

        self._safe_print(f"⬇️  Starting download: {app_name}")
        
        progress_bar = None
        downloaded_size = 0

        try:
            auth = (DownloadConfig.AUTH_USERNAME, DownloadConfig.AUTH_PASSWORD)
            with HTTPClientFactory.create_sync_client(
                timeout=DownloadConfig.TIMEOUT_TOTAL,
                auth=auth,
                follow_redirects=True
            ) as client:
                with client.stream("GET", download_url) as response:
                    response.raise_for_status()
                    
                    total_size = response.headers.get("Content-Length")
                    if total_size:
                        total_size = int(total_size)
                        self._safe_print(f"📊 {app_name} file size: {self._format_size(total_size)}")
                        progress_bar = self._create_progress_bar(app_name, total_size)

                    with open(file_path, "wb") as f:
                        for chunk in response.iter_bytes(chunk_size=DownloadConfig.CHUNK_SIZE):
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            if progress_bar:
                                progress_bar.update(len(chunk))
                    
                    duration = time.time() - start_time
                    result = DownloadResult(True, app_name, downloaded_size, duration)
                    
                    # Verify download integrity
                    if total_size and downloaded_size < total_size:
                        result.success = False
                        result.error_message = f"Incomplete download (expected: {self._format_size(total_size)}, got: {self._format_size(downloaded_size)})"
                    
                    return result

        except httpx.TimeoutException as e:
            return DownloadResult(False, app_name, error_message=f"Download timeout: {e}")
        except httpx.HTTPStatusError as e:
            return DownloadResult(False, app_name, error_message=f"HTTP error status code {e.response.status_code}")
        except httpx.RequestError as e:
            return DownloadResult(False, app_name, error_message=f"Request error: {e}")
        except Exception as e:
            return DownloadResult(False, app_name, error_message=f"Unknown error: {e}")
        finally:
            if progress_bar:
                progress_bar.close()
                time.sleep(0.1)

    def _create_progress_bar(self, app_name: str, total_size: int) -> tqdm:
        """Create progress bar."""
        return tqdm(
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
            desc=f"📥 {app_name[:15]}...",
            leave=False,
            ncols=100,
            miniters=1,
            mininterval=DownloadConfig.PROGRESS_UPDATE_INTERVAL,
            dynamic_ncols=True,
        )

