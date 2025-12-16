# -*- coding: utf-8 -*-

"""Service Factory for dependency injection.

This module provides a centralized way to create and manage service instances,
enabling better testability and dependency management.
"""

from typing import Optional


class ServiceFactory:
    """Factory for creating and managing service instances."""
    
    # Service instances cache
    _sp_service: Optional[object] = None
    _ffs_service: Optional[object] = None
    _account_service: Optional[object] = None
    _download_manager: Optional[object] = None
    
    @classmethod
    def get_sp_service(cls):
        """Get or create SP service instance."""
        if cls._sp_service is None:
            from ..service_parameter.service import SPService
            cls._sp_service = SPService()
        return cls._sp_service
    
    @classmethod
    def get_ffs_service(cls):
        """Get or create FFS service instance."""
        if cls._ffs_service is None:
            from ..feature_flag.service import FFSService
            cls._ffs_service = FFSService()
        return cls._ffs_service
    
    @classmethod
    def get_account_service(cls):
        """Get or create Account service instance."""
        if cls._account_service is None:
            from ..account_pool.service import AccountService
            cls._account_service = AccountService()
        return cls._account_service
    
    @classmethod
    def get_download_manager(cls):
        """Get or create Download manager instance."""
        if cls._download_manager is None:
            from ..download.manager import DownloadManager
            cls._download_manager = DownloadManager()
        return cls._download_manager
    
    @classmethod
    def reset(cls):
        """Reset all service instances (useful for testing)."""
        cls._sp_service = None
        cls._ffs_service = None
        cls._account_service = None
        cls._download_manager = None
    
    @classmethod
    def set_sp_service(cls, service):
        """Set SP service instance (useful for testing)."""
        cls._sp_service = service
    
    @classmethod
    def set_ffs_service(cls, service):
        """Set FFS service instance (useful for testing)."""
        cls._ffs_service = service
    
    @classmethod
    def set_account_service(cls, service):
        """Set Account service instance (useful for testing)."""
        cls._account_service = service
    
    @classmethod
    def set_download_manager(cls, manager):
        """Set Download manager instance (useful for testing)."""
        cls._download_manager = manager

