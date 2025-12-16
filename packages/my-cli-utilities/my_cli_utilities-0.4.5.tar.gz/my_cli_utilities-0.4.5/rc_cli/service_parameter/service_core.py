"""Core Service Parameter (SP) service implementation."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from rc_cli.common_lib.config import SPConfig
from rc_cli.common_lib.http_helpers import HTTPClientFactory
from rc_cli.common import create_error_result, handle_http_error
from rc_cli.account_pool.resolvers import resolve_phone_to_account_id
from rc_cli.service_parameter.models import SPResult

logger = logging.getLogger(__name__)


class SPClientError(Exception):
    """Base exception for SP client errors."""


class SPService:
    """Service for interacting with Service Parameter API."""

    def __init__(self) -> None:
        self.gitlab_token: Optional[str] = None
        self.timeout = SPConfig.DEFAULT_TIMEOUT
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = SPConfig.CACHE_TTL

    def _get_gitlab_token(self) -> str:
        import os

        token = os.environ.get("GITLAB_TOKEN")
        if not token:
            raise SPClientError("GitLab token not found. Please set GITLAB_TOKEN environment variable.")
        return token

    async def get_all_service_parameters(self) -> SPResult:
        try:
            if SPConfig.GITLAB_BASE_URL == "https://git.example.com/api/v4":
                return SPResult(
                    success=False,
                    error_message=(
                        "GitLab URL not configured. Please set SP_GITLAB_BASE_URL environment variable.\n"
                        "Example: export SP_GITLAB_BASE_URL='https://git.example.com/api/v4'"
                    ),
                    count=0,
                )

            if not self.gitlab_token:
                self.gitlab_token = self._get_gitlab_token()

            url = (
                f"{SPConfig.GITLAB_BASE_URL}/projects/{SPConfig.GITLAB_PROJECT_ID}"
                f"/repository/files/{SPConfig.GITLAB_FILE_PATH}/raw"
            )
            params = {"ref": SPConfig.GITLAB_BRANCH}
            headers = {"PRIVATE-TOKEN": self.gitlab_token}

            async with HTTPClientFactory.create_async_client(timeout=self.timeout, headers=headers) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                assembly_data = response.json()
                service_parameters = assembly_data.get("service-parameters", {})
                return SPResult(success=True, data=service_parameters, count=len(service_parameters))
        except Exception as e:
            error_msg = handle_http_error(
                e,
                "retrieving service parameters",
                not_found_message="Service parameters not found in GitLab",
            )
            return create_error_result(SPResult, error_msg)

    async def get_service_parameter_value(self, sp_id: str, account_id: str, env_name: str = "webaqaxmn") -> SPResult:
        try:
            base_url = SPConfig.get_intapi_base_url(env_name)
            url = f"{base_url}/restapi/v1.0/internal/service-parameter/{sp_id}"
            params = {"accountId": account_id}
            headers = {"Authorization": SPConfig.INTAPI_AUTH_HEADER, "RCBrandId": SPConfig.INTAPI_BRAND_ID}

            async with HTTPClientFactory.create_async_client(timeout=self.timeout, headers=headers) as client:
                response = await client.get(url, params=params)
                if response.status_code >= 400:
                    logger.error("HTTP %s - Response body: %s", response.status_code, response.text[:500])
                response.raise_for_status()
                sp_data = response.json()
                return SPResult(success=True, data=sp_data, count=1)
        except Exception as e:
            error_msg = handle_http_error(
                e,
                f"retrieving service parameter '{sp_id}' value for account '{account_id}'",
                not_found_message=f"Service parameter {sp_id} or account {account_id} not found",
            )
            return create_error_result(SPResult, error_msg)

    async def get_service_parameter_value_by_phone(self, sp_id: str, phone_number: str, env_name: str = "webaqaxmn") -> SPResult:
        try:
            account_id = await self._resolve_phone_to_account_id(phone_number, env_name)
            if not account_id:
                return create_error_result(SPResult, f"Phone number {phone_number} not found in environment {env_name}")
            return await self.get_service_parameter_value(sp_id, account_id, env_name)
        except Exception as e:
            error_msg = handle_http_error(
                e,
                f"retrieving service parameter '{sp_id}' value for phone '{phone_number}'",
                not_found_message=f"Phone number {phone_number} not found",
            )
            return create_error_result(SPResult, error_msg)

    async def _resolve_phone_to_account_id(self, phone_number: str, env_name: str) -> Optional[str]:
        try:
            return resolve_phone_to_account_id(phone_number=phone_number, env_name=env_name)
        except Exception:
            logger.exception("Error resolving phone to account ID")
            return None

    async def search_service_parameters(self, query: str) -> SPResult:
        try:
            all_sps_result = await self.get_all_service_parameters()
            if not all_sps_result.success:
                return all_sps_result

            all_sps = all_sps_result.data
            query_lower = query.lower()
            matching_sps = {sp_id: desc for sp_id, desc in all_sps.items() if query_lower in desc.lower()}
            return SPResult(success=True, data=matching_sps, count=len(matching_sps))
        except Exception as e:
            logger.error("Error searching service parameters: %s", e)
            return SPResult(success=False, error_message=f"Search failed: {e}")

    async def get_service_parameter_definition(self, sp_id: str) -> SPResult:
        try:
            all_sps_result = await self.get_all_service_parameters()
            if not all_sps_result.success:
                return all_sps_result

            all_sps = all_sps_result.data
            if sp_id not in all_sps:
                return SPResult(success=False, error_message=f"Service parameter {sp_id} not found", count=0)

            return SPResult(success=True, data={"id": sp_id, "description": all_sps[sp_id]}, count=1)
        except Exception as e:
            logger.error("Error getting service parameter definition: %s", e)
            return SPResult(success=False, error_message=f"Failed to get SP definition: {e}")

    def get_server_info(self) -> Dict[str, Any]:
        return {
            "status": "connected",
            "server": {
                "intapiBaseUrl": SPConfig.INTAPI_BASE_URL,
                "gitlabBaseUrl": SPConfig.GITLAB_BASE_URL,
                "timeout": self.timeout,
            },
            "cache": {"size": len(self._cache), "enabled": True, "ttlSeconds": self._cache_ttl},
        }

    def clear_cache(self) -> None:
        self._cache.clear()
        logger.info("SP service cache cleared")


