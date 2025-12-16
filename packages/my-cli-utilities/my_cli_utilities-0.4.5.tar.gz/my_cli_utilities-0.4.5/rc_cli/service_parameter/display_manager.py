# -*- coding: utf-8 -*-

"""Display formatting utilities for Service Parameter operations."""

from typing import Dict, Any, Optional

from rc_cli.common_lib.config import SPConfig


class SPDisplayManager:
    """Display formatting for SP operations."""
    
    @staticmethod
    def format_service_parameter(sp_id: str, description: str) -> str:
        """Format service parameter for display."""
        # Truncate description if too long
        if len(description) > SPConfig.MAX_DESCRIPTION_LENGTH:
            description = description[:SPConfig.MAX_DESCRIPTION_LENGTH - 3] + "..."
        
        return f"  {sp_id:<20} {description}"
    
    @staticmethod
    def format_sp_value(sp_data: Dict[str, Any], sp_description: Optional[str] = None) -> str:
        """Format service parameter value for display."""
        sp_id = sp_data.get('id', 'N/A')
        value = sp_data.get('value', 'N/A')
        account_id = sp_data.get('account_id', 'N/A')
        
        # Build the display string
        display_lines = []
        
        # SP ID and description
        if sp_description:
            display_lines.append(f"  📋 SP ID: {sp_id}")
            display_lines.append(f"  📝 Description: {sp_description}")
        else:
            display_lines.append(f"  📋 SP ID: {sp_id}")
        
        # Current value
        display_lines.append(f"  🔢 Current Value: {value}")
        
        # Account information
        if account_id != 'N/A':
            display_lines.append(f"  👤 Account ID: {account_id}")
        
        return "\n".join(display_lines)
    
    @staticmethod
    def format_sp_definition(sp_definition: Dict[str, Any]) -> str:
        """Format service parameter definition for display."""
        sp_id = sp_definition.get('id', 'N/A')
        description = sp_definition.get('description', 'N/A')
        
        return f"  SP ID: {sp_id}\n  Description: {description}"
    
    @staticmethod
    def format_server_info(server_info: Dict[str, Any]) -> str:
        """Format server information for display."""
        status = server_info.get('status', 'N/A')
        server_config = server_info.get('server', {})
        cache_info = server_info.get('cache', {})
        
        lines = [
            f"  Status: {status}",
            f"  Internal API: {server_config.get('intapiBaseUrl', 'N/A')}",
            f"  GitLab API: {server_config.get('gitlabBaseUrl', 'N/A')}",
            f"  Timeout: {server_config.get('timeout', 'N/A')}s",
            f"  Cache Size: {cache_info.get('size', 0)}",
            f"  Cache TTL: {cache_info.get('ttlSeconds', 0)}s"
        ]
        
        return "\n".join(lines)

