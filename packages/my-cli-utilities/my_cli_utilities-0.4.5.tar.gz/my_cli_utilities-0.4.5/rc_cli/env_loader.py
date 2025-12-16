# -*- coding: utf-8 -*-

"""Environment configuration loader for RC CLI.

This module provides utilities to load environment variables from config files.

Design goal:
- Treat config file as the source of truth and override any existing process
  environment variables for keys found in the config file.

Supported configuration locations (priority order):
1. Nearest .env found by walking up from current working directory
2. ~/.rc-cli.env
3. Fallback: .env next to the installed package (mainly for development)
"""

import logging
import os
import re
from pathlib import Path


_ENV_LINE_PATTERN = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$")

logger = logging.getLogger(__name__)


def _parse_env_line(line: str) -> tuple[str, str] | None:
    """
    Parse one .env line.

    Supports:
    - KEY=VALUE
    - export KEY=VALUE
    - KEY=VALUE # inline comment (for unquoted values)
    """
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    match = _ENV_LINE_PATTERN.match(stripped)
    if not match:
        return None

    key = match.group(1).strip()
    raw_value = match.group(2).strip()

    if not key:
        return None

    # Remove inline comments for unquoted values
    value = raw_value
    if value and not (value.startswith('"') or value.startswith("'")):
        hash_index = value.find("#")
        if hash_index >= 0:
            value = value[:hash_index].rstrip()

    # Remove quotes if present
    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        value = value[1:-1]
    elif value.startswith("'") and value.endswith("'") and len(value) >= 2:
        value = value[1:-1]

    return (key, value)


def _find_nearest_env_file(start_dir: Path) -> Path | None:
    """Find the nearest .env by walking up parent directories."""
    current = start_dir.resolve()
    for candidate_dir in (current, *current.parents):
        candidate = candidate_dir / ".env"
        if candidate.exists():
            return candidate
    return None


def get_config_paths() -> list[Path]:
    """
    Get list of possible configuration file paths in priority order.
    
    Returns:
        List of Path objects to check for configuration
    """
    paths: list[Path] = []

    nearest_env = _find_nearest_env_file(Path.cwd())
    if nearest_env is not None:
        paths.append(nearest_env)

    home = Path.home()
    paths.append(home / ".rc-cli.env")

    # Fallback: .env next to the installed package (dev convenience)
    current_file = Path(__file__).resolve()
    package_root = current_file.parent.parent
    paths.append(package_root / ".env")

    # De-duplicate while keeping order
    seen: set[Path] = set()
    unique_paths: list[Path] = []
    for p in paths:
        if p in seen:
            continue
        seen.add(p)
        unique_paths.append(p)
    return unique_paths


def load_env(env_file: str | None = None) -> tuple[bool, str | None]:
    """
    Load environment variables from a .env file.
    
    Args:
        env_file: Optional specific path to .env file
        
    Returns:
        Tuple of (success: bool, config_path: str or None)
    """
    paths_to_try = [Path(env_file)] if env_file else get_config_paths()

    for env_path in paths_to_try:
        if not env_path.exists():
            continue
        
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parsed = _parse_env_line(line)
                    if not parsed:
                        continue
                    key, value = parsed

                    # Config file is the source of truth: always override.
                    if key:
                        os.environ[key] = value

            return (True, str(env_path))
        except Exception as e:
            logger.warning("Failed to load env file: %s (%s)", env_path, e)
            continue
    return (False, None)


def get_env_status() -> dict[str, str | None]:
    """
    Get status of required environment variables.
    
    Returns:
        Dictionary with variable names and their status
    """
    required_vars = {
        'SP_GITLAB_BASE_URL': os.environ.get('SP_GITLAB_BASE_URL'),
        'SP_GITLAB_PROJECT_ID': os.environ.get('SP_GITLAB_PROJECT_ID'),
        'GITLAB_TOKEN': '***' if os.environ.get('GITLAB_TOKEN') else None,
    }
    return required_vars


def check_configuration() -> tuple[bool, list[str]]:
    """
    Check if configuration is properly set up.
    
    Returns:
        Tuple of (is_configured: bool, missing_vars: list)
    """
    status = get_env_status()
    missing = []
    
    # Check if using default placeholder values
    if status['SP_GITLAB_BASE_URL'] == 'https://git.example.com/api/v4':
        missing.append('SP_GITLAB_BASE_URL (using placeholder)')
    elif not status['SP_GITLAB_BASE_URL']:
        missing.append('SP_GITLAB_BASE_URL')
    
    if not status['GITLAB_TOKEN'] or status['GITLAB_TOKEN'] == 'your-token-here':
        missing.append('GITLAB_TOKEN')
    
    return (len(missing) == 0, missing)


# Auto-load .env file when module is imported
_loaded, _config_path = load_env()
if _loaded:
    # Silently loaded, only show in verbose mode
    logger.debug("Loaded environment from: %s", _config_path)


