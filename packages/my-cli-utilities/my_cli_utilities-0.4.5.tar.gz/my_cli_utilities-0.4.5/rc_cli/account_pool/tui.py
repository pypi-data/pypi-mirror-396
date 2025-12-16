"""Account Pool TUI facade.

This module keeps public import paths stable while the implementation lives in
smaller modules under `rc_cli.account_pool.tui_components`.
"""

from rc_cli.account_pool.tui_components.app import AccountPoolTUIApp, run_tui
from rc_cli.account_pool.tui_components.get_by_alias import GetAccountByAliasScreen, GetAccountByAliasWidget
from rc_cli.account_pool.tui_components.get_by_phone import GetAccountByPhoneScreen, GetAccountByPhoneWidget
from rc_cli.account_pool.tui_components.list_aliases import ListAliasesScreen, ListAliasesWidget
from rc_cli.account_pool.tui_components.menu import AccountPoolMenuWidget
from rc_cli.account_pool.tui_components.modal import AccountQueryResultScreen

__all__ = [
    "AccountPoolTUIApp",
    "AccountPoolMenuWidget",
    "GetAccountByPhoneWidget",
    "GetAccountByPhoneScreen",
    "GetAccountByAliasWidget",
    "GetAccountByAliasScreen",
    "ListAliasesWidget",
    "ListAliasesScreen",
    "AccountQueryResultScreen",
    "run_tui",
]


