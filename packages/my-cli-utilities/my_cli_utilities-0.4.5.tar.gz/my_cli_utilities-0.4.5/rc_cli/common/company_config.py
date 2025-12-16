# -*- coding: utf-8 -*-

"""String replacement utilities for company-specific configuration.

This module handles replacing placeholder strings with actual company values
from environment variables, avoiding hardcoded company information in the codebase.
"""

import os
from typing import Dict


def get_company_replacements() -> Dict[str, str]:
    """
    Get company-specific string replacements from environment variables.
    
    Returns:
        Dictionary mapping placeholder patterns to actual values
    """
    company_name = os.environ.get('COMPANY_NAME', 'yourcompany')
    
    return {
        # Lowercase company name
        'yourcompany': company_name.lower(),
        # Capitalized company name  
        'YourCompany': company_name,
        # Uppercase company name
        'YOURCOMPANY': company_name.upper(),
    }


def replace_company_placeholders(text: str) -> str:
    """
    Replace company placeholders in text with actual values from env vars.
    
    Args:
        text: String potentially containing company placeholders
        
    Returns:
        String with placeholders replaced
        
    Example:
        >>> os.environ['COMPANY_NAME'] = 'MyCompany'
        >>> replace_company_placeholders('https://git.yourcompany.com')
        'https://git.mycompany.com'
    """
    replacements = get_company_replacements()
    result = text
    
    for placeholder, actual in replacements.items():
        result = result.replace(placeholder, actual)
    
    return result


def apply_company_config(config_dict: Dict[str, str]) -> Dict[str, str]:
    """
    Apply company replacements to all values in a configuration dictionary.
    
    Args:
        config_dict: Configuration dictionary with potential placeholders
        
    Returns:
        New dictionary with all placeholders replaced
    """
    return {
        key: replace_company_placeholders(value) if isinstance(value, str) else value
        for key, value in config_dict.items()
    }

