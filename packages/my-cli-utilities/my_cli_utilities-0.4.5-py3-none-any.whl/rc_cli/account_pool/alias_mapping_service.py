# -*- coding: utf-8 -*-

"""
Service for fetching and managing alias-to-kaminoKey mappings from GitLab.
This module retrieves the YAML configuration file from Git repository
and provides mapping between alias, brand, and kaminoKey.
"""

import os
import logging
import time
from typing import Dict, Optional, List
from dataclasses import dataclass
from urllib.parse import quote

import httpx
import yaml

from rc_cli.common_lib.http_helpers import HTTPClientFactory

logger = logging.getLogger(__name__)


@dataclass
class AliasMapping:
    """Data class representing an alias mapping entry."""
    alias: str
    brand: str
    kamino_key: str


class AliasMappingConfig:
    """Configuration for alias mapping service."""
    
    # Default brand
    DEFAULT_BRAND = "RC"
    
    # Cache settings
    CACHE_TTL = 3600  # 1 hour
    
    @staticmethod
    def get_gitlab_base_url() -> str:
        """Get GitLab base URL from environment. Priority: MTHOR_ > AP_ > SP_"""
        return os.environ.get(
            "MTHOR_GITLAB_BASE_URL",
            os.environ.get(
                "AP_GITLAB_BASE_URL",
                os.environ.get("SP_GITLAB_BASE_URL", "https://git.example.com/api/v4")
            )
        )
    
    @staticmethod
    def get_gitlab_project_id() -> str:
        """Get GitLab project ID from environment. Priority: MTHOR_ > AP_"""
        return os.environ.get(
            "MTHOR_GITLAB_PROJECT_ID",
            os.environ.get("AP_GITLAB_PROJECT_ID", "")
        )
    
    @staticmethod
    def get_gitlab_file_path() -> str:
        """Get GitLab file path from environment. Priority: MTHOR_ > AP_"""
        return os.environ.get(
            "MTHOR_GITLAB_FILE_PATH",
            os.environ.get(
                "AP_GITLAB_FILE_PATH",
                "src/main/resources/account/mThor-mZeus-account.yaml"
            )
        )
    
    @staticmethod
    def get_gitlab_branch() -> str:
        """Get GitLab branch from environment. Priority: MTHOR_ > AP_"""
        return os.environ.get(
            "MTHOR_GITLAB_BRANCH",
            os.environ.get("AP_GITLAB_BRANCH", "master")
        )


class AliasMappingService:
    """Service for fetching and managing alias mappings."""
    
    def __init__(self):
        self._cache: Dict[str, AliasMapping] = {}
        self._cache_time = 0
        self._cache_ttl = AliasMappingConfig.CACHE_TTL
        self._gitlab_token: Optional[str] = None
    
    def _get_gitlab_token(self) -> str:
        """Get GitLab token from environment variable."""
        token = os.environ.get("GITLAB_TOKEN", "")
        if not token:
            raise ValueError(
                "GITLAB_TOKEN not found in environment variables.\n"
                "Please set it using: export GITLAB_TOKEN='your-token-here'"
            )
        return token
    
    def _is_cache_expired(self) -> bool:
        """Check if cache has expired."""
        return time.time() - self._cache_time > self._cache_ttl
    
    def _validate_config(self) -> None:
        """Validate configuration before making API request."""
        if not AliasMappingConfig.get_gitlab_project_id():
            raise ValueError(
                "GitLab Project ID not configured.\n"
                "Please set AP_GITLAB_PROJECT_ID environment variable."
            )
        
        if AliasMappingConfig.get_gitlab_base_url() == "https://git.example.com/api/v4":
            raise ValueError(
                "GitLab URL not configured.\n"
                "Please set AP_GITLAB_BASE_URL or SP_GITLAB_BASE_URL environment variable."
            )
    
    def _fetch_yaml_from_gitlab(self) -> str:
        """
        Fetch YAML file content from GitLab repository.
        
        Returns:
            YAML file content as string
            
        Raises:
            ValueError: If configuration is invalid
            httpx.HTTPError: If API request fails
        """
        self._validate_config()
        
        if not self._gitlab_token:
            self._gitlab_token = self._get_gitlab_token()
        
        # Encode file path for URL - use quote with safe='' to encode all special chars including /
        encoded_path = quote(AliasMappingConfig.get_gitlab_file_path(), safe='')
        
        url = (
            f"{AliasMappingConfig.get_gitlab_base_url()}"
            f"/projects/{AliasMappingConfig.get_gitlab_project_id()}"
            f"/repository/files/{encoded_path}/raw"
        )
        
        params = {"ref": AliasMappingConfig.get_gitlab_branch()}
        headers = {"PRIVATE-TOKEN": self._gitlab_token}
        
        logger.info(f"Fetching alias mappings from GitLab: {url}")
        
        with HTTPClientFactory.create_sync_client(
            timeout=30.0,
            headers=headers
        ) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.text
    
    def _parse_yaml_content(self, yaml_content: str) -> Dict[str, AliasMapping]:
        """
        Parse YAML content and extract alias mappings.
        
        Args:
            yaml_content: YAML file content as string
            
        Returns:
            Dictionary mapping alias to AliasMapping objects
        """
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML: {e}")
            raise ValueError(f"Invalid YAML format: {e}")
        
        mappings: Dict[str, AliasMapping] = {}
        
        # Parse the YAML structure
        # Expected structure: list of dictionaries with alias, brand, kaminoKey
        if not isinstance(data, list):
            logger.warning("YAML root is not a list, attempting to extract mappings")
            # If it's a dict, try to find list entries
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, list):
                        data = value
                        break
        
        if isinstance(data, list):
            for entry in data:
                if not isinstance(entry, dict):
                    continue
                
                alias = entry.get("alias", "").strip()
                if not alias:
                    logger.debug(f"Skipping entry without alias: {entry}")
                    continue
                
                # Check if brand and kaminoKey are in brandingGroup array
                branding_group = entry.get("brandingGroup", [])
                if isinstance(branding_group, list) and len(branding_group) > 0:
                    # Use first branding group entry
                    first_brand_entry = branding_group[0]
                    brand = first_brand_entry.get("brand", AliasMappingConfig.DEFAULT_BRAND)
                    kamino_key = first_brand_entry.get("kaminoKey", "")
                else:
                    # Fallback: try to get from top level (for backward compatibility)
                    brand = entry.get("brand", AliasMappingConfig.DEFAULT_BRAND)
                    kamino_key = entry.get("kaminoKey", "")
                
                if not kamino_key:
                    logger.debug(f"Skipping entry without kaminoKey: alias={alias}")
                    continue
                
                brand = brand.strip() if brand else AliasMappingConfig.DEFAULT_BRAND
                kamino_key = kamino_key.strip()
                
                mappings[alias.lower()] = AliasMapping(
                    alias=alias,
                    brand=brand,
                    kamino_key=kamino_key
                )
        
        logger.info(f"Parsed {len(mappings)} alias mappings")
        return mappings
    
    def refresh_mappings(self) -> None:
        """
        Force refresh mappings from GitLab.
        
        Raises:
            ValueError: If configuration is invalid
            Exception: If fetching or parsing fails
        """
        try:
            yaml_content = self._fetch_yaml_from_gitlab()
            self._cache = self._parse_yaml_content(yaml_content)
            self._cache_time = time.time()
            logger.info(f"Successfully refreshed {len(self._cache)} alias mappings")
        except Exception as e:
            logger.error(f"Failed to refresh alias mappings: {e}")
            raise
    
    def get_mappings(self, force_refresh: bool = False) -> Dict[str, AliasMapping]:
        """
        Get all alias mappings, using cache if available.
        
        Args:
            force_refresh: If True, force refresh from GitLab
            
        Returns:
            Dictionary mapping alias to AliasMapping objects
        """
        if force_refresh or not self._cache or self._is_cache_expired():
            self.refresh_mappings()
        
        return self._cache
    
    def get_mapping_by_alias(
        self,
        alias: str,
        force_refresh: bool = False
    ) -> Optional[AliasMapping]:
        """
        Get mapping for a specific alias.
        
        Args:
            alias: Alias to lookup (case-insensitive)
            force_refresh: If True, force refresh from GitLab
            
        Returns:
            AliasMapping object if found, None otherwise
        """
        mappings = self.get_mappings(force_refresh)
        return mappings.get(alias.lower())
    
    def get_kamino_key(
        self,
        alias: str,
        force_refresh: bool = False
    ) -> Optional[str]:
        """
        Get kaminoKey for a specific alias.
        
        Args:
            alias: Alias to lookup (case-insensitive)
            force_refresh: If True, force refresh from GitLab
            
        Returns:
            kaminoKey string if found, None otherwise
        """
        mapping = self.get_mapping_by_alias(alias, force_refresh)
        return mapping.kamino_key if mapping else None
    
    def list_all_aliases(self, force_refresh: bool = False) -> List[str]:
        """
        Get list of all available aliases.
        
        Args:
            force_refresh: If True, force refresh from GitLab
            
        Returns:
            List of alias strings
        """
        mappings = self.get_mappings(force_refresh)
        return sorted(mappings.keys())

