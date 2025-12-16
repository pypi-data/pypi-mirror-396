"""Resolvers that bridge Account Pool data to other modules.

Keep these small and dependency-light so other modules (e.g. SP) can reuse them
without duplicating logic.
"""

from __future__ import annotations

import logging
from typing import Optional

from returns.pipeline import is_successful

from rc_cli.account_pool.data_manager import DataManager
from rc_cli.common_lib.config_base import ValidationUtils

logger = logging.getLogger(__name__)


def resolve_phone_to_account_id(phone_number: str, env_name: str) -> Optional[str]:
    """Resolve a phone number to accountId via Account Pool.

    Args:
        phone_number: Phone number (with or without leading '+')
        env_name: Environment name, e.g. 'webaqaxmn'

    Returns:
        Account ID if found, otherwise None.
    """
    if not phone_number:
        return None

    normalized_phone = ValidationUtils.normalize_phone_number(phone_number)

    data_manager = DataManager()
    accounts_result = data_manager.get_all_accounts_for_env(env_name)
    if not is_successful(accounts_result):
        error = accounts_result.failure()
        logger.warning("Failed to fetch accounts for env=%s: %s", env_name, getattr(error, "message", str(error)))
        return None

    accounts = accounts_result.unwrap()
    for account in accounts:
        if account.get("mainNumber") == normalized_phone:
            return account.get("accountId")

    return None


