# -*- coding: utf-8 -*-

"""Feature Flag Service (FFS) client service for RC CLI."""

import os
import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
import httpx
from .models import FFSResult, FFSConfig
from ..common import handle_http_error, create_error_result
from rc_cli.common_lib.config import BaseConfig, FFSConfig as UnifiedFFSConfig
from rc_cli.common_lib.http_helpers import HTTPClientFactory

logger = logging.getLogger(__name__)


class FFSClientError(Exception):
    """Base exception for FFS client errors."""
    pass


class FFSConnectionError(FFSClientError):
    """Exception raised when connection to FFS service fails."""
    pass


class FFSNotFoundError(FFSClientError):
    """Exception raised when requested resource is not found."""
    pass


class FFSService:
    """Service for interacting with Feature Flag Service API."""
    
    def __init__(self):
        """Initialize FFS service with configuration."""
        self.base_url = os.environ.get('FFS_BASE_URL', FFSConfig.DEFAULT_BASE_URL)
        self.timeout = float(os.environ.get('FFS_TIMEOUT', FFSConfig.DEFAULT_TIMEOUT))
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = FFSConfig.CACHE_TTL
    
    async def get_feature_flag(self, flag_id: str) -> FFSResult:
        """
        Get feature flag configuration by ID.
        
        Args:
            flag_id: Feature flag identifier
            
        Returns:
            FFSResult containing feature flag information
        """
        try:
            url = f"{self.base_url}/feature-flags/management/v1/flags/{flag_id}"
            
            async with HTTPClientFactory.create_async_client(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                flag_data = response.json()
                
                logger.info(f"Retrieved feature flag: {flag_id}")
                
                return FFSResult(
                    success=True,
                    data=flag_data,
                    count=1
                )
            
        except Exception as e:
            error_msg = handle_http_error(
                e,
                f"retrieving feature flag '{flag_id}'",
                not_found_message=f"Feature flag '{flag_id}' not found"
            )
            return create_error_result(FFSResult, error_msg)
    
    async def search_feature_flags(self, query: str) -> FFSResult:
        """
        Search feature flags by name pattern.
        
        Args:
            query: Search pattern for flag names
            
        Returns:
            FFSResult containing matching feature flags
        """
        try:
            if not query or not query.strip():
                return FFSResult(
                    success=False,
                    error_message="Search query cannot be empty"
                )
            
            url = f"{self.base_url}/feature-flags/management/v1/flags/"
            params = {"flagId": query}
            
            async with HTTPClientFactory.create_async_client(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                flags = data.get("flags", [])
            
            logger.info(f"Found {len(flags)} feature flags matching '{query}'")
            
            return FFSResult(
                success=True,
                data=flags,
                count=len(flags)
            )
            
        except Exception as e:
            error_msg = handle_http_error(
                e,
                f"searching feature flags with query '{query}'",
                not_found_message=f"No flags found matching query: {query}"
            )
            return create_error_result(FFSResult, error_msg)
    
    async def evaluate_feature_flag(self, flag_id: str, context: Dict[str, Any]) -> FFSResult:
        """
        Evaluate a feature flag with given context.
        
        Args:
            flag_id: Feature flag identifier
            context: Context parameters for evaluation (accountId, extensionId, etc.)
            
        Returns:
            FFSResult containing evaluation result
        """
        try:
            # First get the feature flag configuration
            flag_result = await self.get_feature_flag(flag_id)
            if not flag_result.success:
                return flag_result
            
            flag_data = flag_result.data
            
            # Evaluate locally (simplified evaluation)
            # In a real implementation, this would use the evaluation engine
            evaluation_result = self._evaluate_flag_locally(flag_data, context)
            
            return FFSResult(
                success=True,
                data=evaluation_result,
                count=1
            )
            
        except Exception as e:
            logger.error(f"Error evaluating feature flag: {e}")
            return FFSResult(
                success=False,
                error_message=f"Evaluation failed: {e}"
            )
    
    def _evaluate_flag_locally(self, flag_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate feature flag locally using rules."""
        rules = flag_data.get("rules", [])
        
        # Sort rules by priority
        sorted_rules = []
        for rule in rules:
            conditions = rule.get("conditions", [])
            if conditions:
                min_priority = min(c.get("priority", 999999) for c in conditions)
                sorted_rules.append((min_priority, rule))
            else:
                sorted_rules.append((999999, rule))
        
        sorted_rules.sort(key=lambda x: x[0])
        
        # Evaluate rules in priority order
        for _, rule in sorted_rules:
            if self._evaluate_rule(rule, context):
                value_obj = rule.get("value", {})
                value_str = value_obj.get("value", "{}")
                try:
                    value = json.loads(value_str)
                except json.JSONDecodeError:
                    value = {"enabled": False}
                
                return {
                    "flagId": flag_data.get("id"),
                    "value": value,
                    "matchedRuleId": value_obj.get("id"),
                    "matchedConditions": [c.get("id") for c in rule.get("conditions", [])]
                }
        
        # Default fallback
        default_value = {"enabled": False}
        if rules:
            try:
                first_value = rules[0].get("value", {}).get("value", "{}")
                default_value = json.loads(first_value)
            except (json.JSONDecodeError, (KeyError, IndexError)):
                pass
        
        return {
            "flagId": flag_data.get("id"),
            "value": default_value,
            "matchedRuleId": None,
            "matchedConditions": []
        }
    
    def _evaluate_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate if a rule matches the given context."""
        conditions = rule.get("conditions", [])
        if not conditions:
            return True  # Rule with no conditions always matches
        
        # All conditions must match (AND logic)
        for condition in conditions:
            if not self._evaluate_condition(condition, context):
                return False
        
        return True
    
    def _evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a single condition against the context."""
        operator = condition.get("operator", "")
        
        if operator == "DefaultValue":
            return True
        
        if operator == "SegmentMatch":
            segment_name = condition.get("argument", "")
            return any(
                segment_name in str(value)
                for value in context.values()
                if isinstance(value, (str, int))
            )
        
        # Get context value
        dimension = condition.get("dimension", "")
        dimension_param = condition.get("dimensionParameterName", "")
        
        context_value = None
        if dimension:
            dim_key = dimension.lower()
            if dim_key == "accountid":
                context_value = context.get("accountId") or context.get("account_id")
            elif dim_key == "extensionid":
                context_value = context.get("extensionId") or context.get("extension_id")
            else:
                context_value = context.get(dimension)
        elif dimension_param:
            context_value = context.get(dimension_param)
        
        if context_value is None:
            return False
        
        # Parse argument
        argument = condition.get("argument", "")
        argument_values = self._parse_argument(argument, condition.get("argumentDataType", ""))
        
        # Apply operator
        if operator == "IsOneOf":
            return str(context_value) in argument_values
        elif operator == "Contains":
            return any(arg in str(context_value) for arg in argument_values)
        elif operator == "Equals":
            return str(context_value) == argument
        
        return False
    
    def _parse_argument(self, argument: str, data_type: str) -> List[str]:
        """Parse condition argument based on its data type."""
        if data_type in ["ListInteger", "ListString"]:
            return [value.strip() for value in argument.split(",") if value.strip()]
        else:
            return [argument]
    
    async def check_feature_enabled(self, flag_id: str, context: Dict[str, Any]) -> FFSResult:
        """
        Check if a feature is enabled for given context.
        
        Args:
            flag_id: Feature flag identifier
            context: Context parameters for evaluation
            
        Returns:
            FFSResult containing enabled status
        """
        eval_result = await self.evaluate_feature_flag(flag_id, context)
        
        if not eval_result.success:
            return eval_result
        
        eval_data = eval_result.data
        enabled = eval_data.get("value", {}).get("enabled", False)
        
        return FFSResult(
            success=True,
            data={
                "flagId": flag_id,
                "enabled": enabled,
                "context": context,
                "matchedRuleId": eval_data.get("matchedRuleId")
            },
            count=1
        )
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Get server information including configuration and cache status.
        
        Returns:
            Dict containing server information
        """
        cache_size = len(self._cache)
        
        server_info = {
            "status": "connected",
            "server": {
                "baseUrl": self.base_url,
                "timeout": self.timeout
            },
            "cache": {
                "size": cache_size,
                "enabled": True,
                "ttlSeconds": self._cache_ttl
            }
        }
        
        return server_info
    
    def clear_cache(self):
        """Clear the service cache."""
        self._cache.clear()
        logger.info("FFS service cache cleared")
    

# Global FFS service instance (deprecated, use ServiceFactory.get_ffs_service() instead)
# Kept for backward compatibility
def _get_ffs_service():
    """Lazy import to avoid circular dependencies."""
    from ..common.service_factory import ServiceFactory
    return ServiceFactory.get_ffs_service()

ffs_service = _get_ffs_service()

