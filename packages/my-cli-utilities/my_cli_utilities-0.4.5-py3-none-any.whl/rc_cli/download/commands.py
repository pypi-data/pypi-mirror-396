# -*- coding: utf-8 -*-

"""Download commands for RC CLI."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
import typer
from rc_cli.common_lib.config import DownloadConfig
from .manager import DownloadManager, DownloadResult
from ..common.service_factory import ServiceFactory
from ..common import format_separator, MEDIUM_SEPARATOR_WIDTH

# Global download manager instance
download_manager = ServiceFactory.get_download_manager()

# Create download sub-app
download_app = typer.Typer(
    name="download",
    help="📥 Application download commands",
    add_completion=False
)


def _get_regression_apps(version_arg: Optional[str] = None) -> List[str]:
    """Get regression test application list with company name from environment."""
    import os
    # Get company name from environment
    company_name = os.environ.get('COMPANY_NAME', 'company').lower()
    
    version = f"-{version_arg}" if version_arg else ""
    base_patterns = [
        f"web-aqa-xmn-{company_name}-inhouse-debug{{version}}-{{suffix}}",
        "WEB-AQA-XMN-Glip{version}-{suffix}-Inhouse", 
        "WEB-AQA-XMN-Glip{version}-{suffix}",
        f"xmn-up-{company_name}-inhouse-debug{{version}}-{{suffix}}",
        "XMN-UP-Glip{version}-{suffix}-Inhouse",
        "XMN-UP-Glip{version}-{suffix}"
    ]
    
    extensions = [".apk", ".ipa", ".zip", ".apk", ".ipa", ".zip"]
    
    return [
        pattern.format(version=version, suffix=DownloadConfig.SUFFIX) + ext
        for pattern, ext in zip(base_patterns, extensions)
    ]


def _download_apps_batch(apps_list: List[str], app_type: str) -> None:
    """Batch download applications."""
    typer.echo(f"🚀 Starting download of {app_type} applications ({len(apps_list)} files)...")
    typer.echo(f"📁 Download directory: {DownloadConfig.FILE_DIR}")
    typer.echo(f"🔧 Max concurrent downloads: {DownloadConfig.MAX_CONCURRENT_DOWNLOADS}")
    typer.echo(format_separator(MEDIUM_SEPARATOR_WIDTH))
    
    results = []
    with ThreadPoolExecutor(max_workers=DownloadConfig.MAX_CONCURRENT_DOWNLOADS) as executor:
        future_to_app = {
            executor.submit(download_manager.download_single_app, app): app 
            for app in apps_list
        }
        
        for future in as_completed(future_to_app):
            result = future.result()
            results.append(result)
            download_manager._log_download_result(result)
    
    _print_summary(results, app_type)


def _format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size."""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"


def _print_summary(results: List[DownloadResult], app_type: str) -> None:
    """Print download summary."""
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    total_size = sum(r.size for r in successful)
    total_time = sum(r.duration for r in successful)
    
    typer.echo(format_separator(MEDIUM_SEPARATOR_WIDTH))
    typer.echo(f"🎉 {app_type} download completed!")
    typer.echo(f"📊 Success: {len(successful)} | Failed: {len(failed)} | Total: {len(results)}")
    if successful:
        typer.echo(f"📁 Total size: {_format_size(total_size)}")
        typer.echo(f"⏱️  Total duration: {int(total_time)}s")
    if failed:
        typer.echo(f"❌ Failed files: {', '.join(r.app_name for r in failed)}")


def _download_app_type(app_type: str) -> None:
    """Download applications of specified type."""
    if app_type not in DownloadConfig.get_app_types():
        available_types = ', '.join(DownloadConfig.get_app_types().keys())
        typer.echo(f"❌ Unknown application type: {app_type}", err=True)
        typer.echo(f"Available types: {available_types}")
        raise typer.Exit(1)
        
    apps_list = DownloadConfig.get_app_types()[app_type]
    _download_apps_batch(apps_list, app_type.upper())


# Download commands
@download_app.command("aqa")
def download_aqa():
    """📱 Download AQA version applications."""
    _download_app_type('aqa')


@download_app.command("up")
def download_up():
    """📱 Download UP version applications."""
    _download_app_type('up')


@download_app.command("df")
def download_df():
    """📱 Download DF (default fixed) version applications."""
    _download_app_type('df')


@download_app.command("regress")
def download_regress(
    version: Optional[str] = typer.Argument(
        None, 
        help="Version number, e.g. '23.4' or '24.1'. Omit to download latest version"
    )
):
    """🧪 Download regression test applications.
    
    Examples:
    
        rc download regress        # Download latest version
        
        rc d regress 24.1         # Download version 24.1
    """
    apps = _get_regression_apps(version)
    version_text = f"version {version}" if version else "latest version"
    _download_apps_batch(apps, f"Regression test ({version_text})")

