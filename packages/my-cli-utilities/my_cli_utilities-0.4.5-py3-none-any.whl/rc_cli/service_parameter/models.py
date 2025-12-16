# -*- coding: utf-8 -*-

"""Data models for Service Parameter (SP) operations."""

from dataclasses import dataclass
from typing import Optional

from ..common import Result


@dataclass
class ServiceParameter:
    """Service parameter definition."""
    
    id: str
    description: str
    possible_values: Optional[str] = None


@dataclass
class ServiceParameterValue:
    """Service parameter value for a specific account."""
    
    id: int
    value: str
    account_id: str


# Use common Result class for consistency
SPResult = Result
