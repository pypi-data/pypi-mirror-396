# -*- coding: utf-8 -*-

"""Display formatting utilities for Feature Flag Service operations."""

import json
from typing import Dict, Any


class FFSDisplayManager:
    """Display formatting for FFS operations."""
    
    @staticmethod
    def format_flag(flag_data: Dict[str, Any]) -> str:
        """Format feature flag for display with detailed information."""
        flag_id = flag_data.get("id", "N/A")
        description = flag_data.get("description") or "N/A"
        status = flag_data.get("status", "N/A")
        data_type = flag_data.get("dataType", "N/A")
        public = flag_data.get("public", False)
        creation_time = flag_data.get("creationTime", "N/A")
        last_modified_time = flag_data.get("lastModifiedTime", "N/A")
        rules = flag_data.get("rules", [])
        
        lines = [
            f"Flag ID: {flag_id}",
            f"Description: {description}",
            f"Status: {status}",
            f"Data Type: {data_type}",
            f"Public: {public}",
            f"Creation Time: {creation_time}",
            f"Last Modified: {last_modified_time}",
            f"Rules Count: {len(rules)}",
            ""
        ]
        
        # Add detailed rules information
        for i, rule in enumerate(rules, 1):
            lines.append(f"Rule {i}:")
            value_obj = rule.get("value", {})
            value_str = value_obj.get("value", "{}")
            
            # Try to parse and format JSON value
            try:
                value_json = json.loads(value_str)
                value_formatted = json.dumps(value_json, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                value_formatted = value_str
            
            lines.append(f"  Value ID: {value_obj.get('id', 'N/A')}")
            lines.append(f"  Value Name: {value_obj.get('name', 'N/A')}")
            lines.append(f"  Value Description: {value_obj.get('description', 'N/A')}")
            lines.append(f"  Value:")
            # Indent the JSON value
            for line in value_formatted.split('\n'):
                lines.append(f"    {line}")
            
            conditions = rule.get("conditions", [])
            lines.append(f"  Conditions ({len(conditions)}):")
            
            for j, condition in enumerate(conditions, 1):
                lines.append(f"    Condition {j}:")
                lines.append(f"      ID: {condition.get('id', 'N/A')}")
                lines.append(f"      Description: {condition.get('description') or 'N/A'}")
                lines.append(f"      Priority: {condition.get('priority', 'N/A')}")
                lines.append(f"      Dimension: {condition.get('dimension') or 'N/A'}")
                lines.append(f"      Dimension Parameter: {condition.get('dimensionParameterName') or 'N/A'}")
                lines.append(f"      Operator: {condition.get('operator', 'N/A')}")
                lines.append(f"      Argument Data Type: {condition.get('argumentDataType') or 'N/A'}")
                lines.append(f"      Argument: {condition.get('argument') or 'N/A'}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_evaluation(eval_data: Dict[str, Any]) -> str:
        """Format evaluation result for display."""
        flag_id = eval_data.get("flagId", "N/A")
        value = eval_data.get("value", {})
        enabled = value.get("enabled", False)
        matched_rule_id = eval_data.get("matchedRuleId", "N/A")
        
        lines = [
            f"  Flag ID: {flag_id}",
            f"  Enabled: {enabled}",
            f"  Value: {json.dumps(value, indent=2)}",
            f"  Matched Rule ID: {matched_rule_id}"
        ]
        
        return "\n".join(lines)
    
    @staticmethod
    def format_server_info(server_info: Dict[str, Any]) -> str:
        """Format server information for display."""
        status = server_info.get("status", "N/A")
        server_config = server_info.get("server", {})
        cache_info = server_info.get("cache", {})
        
        lines = [
            f"  Status: {status}",
            f"  Base URL: {server_config.get('baseUrl', 'N/A')}",
            f"  Timeout: {server_config.get('timeout', 'N/A')}s",
            f"  Cache Size: {cache_info.get('size', 0)}",
            f"  Cache TTL: {cache_info.get('ttlSeconds', 0)}s"
        ]
        
        return "\n".join(lines)

