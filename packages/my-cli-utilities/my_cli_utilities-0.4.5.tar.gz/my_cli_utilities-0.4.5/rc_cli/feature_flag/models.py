# -*- coding: utf-8 -*-

"""Data models for Feature Flag Service (FFS) operations."""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from ..common import Result, DEFAULT_HTTP_TIMEOUT, DEFAULT_CACHE_TTL


# Use common Result class for consistency
FFSResult = Result


class FFSConfig:
    """Configuration for FFS operations."""
    
    # FFS API settings
    DEFAULT_BASE_URL = "http://aws16-c01-ffs01.ffs.svc.c01.eks02.k8s.aws16.lab.nordigy.ru:8080"
    # Request settings - use common constants
    DEFAULT_TIMEOUT = DEFAULT_HTTP_TIMEOUT
    CACHE_TTL = DEFAULT_CACHE_TTL
    
    # Request settings
    MAX_SEARCH_RESULTS = 100
    MAX_DESCRIPTION_LENGTH = 80

