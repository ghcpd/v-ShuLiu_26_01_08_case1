"""Output formatting module.

Provides formatters for different output modes (text, JSON, etc.).
"""
import json
from typing import Dict, Any


class TextFormatter:
    """Formats metrics as human-readable text."""
    
    @staticmethod
    def format(metrics: Dict[str, Any]) -> str:
        """Format metrics as plain text.
        
        Args:
            metrics: Dict with transaction metrics.
        
        Returns:
            Human-readable text representation.
        """
        lines = [
            "Transaction report:",
            f"  total_rows: {metrics['total_rows']}",
            f"  completed: {metrics['completed']}",
            f"  failed: {metrics['failed']}",
            f"  sum_completed_amount: {metrics['sum_completed_amount']}",
            f"  avg_amount: {metrics['avg_amount']}",
        ]
        return "\n".join(lines)


class JSONFormatter:
    """Formats metrics as JSON."""
    
    @staticmethod
    def format(metrics: Dict[str, Any], pretty: bool = False) -> str:
        """Format metrics as JSON.
        
        Args:
            metrics: Dict with transaction metrics.
            pretty: If True, use indentation for readability.
        
        Returns:
            JSON representation of metrics.
        """
        indent = 2 if pretty else None
        return json.dumps(metrics, indent=indent)


def get_formatter(format_name: str):
    """Get a formatter instance by name.
    
    Args:
        format_name: Name of the format ('text', 'json').
    
    Returns:
        Formatter class or instance.
    
    Raises:
        ValueError: If format_name is not recognized.
    """
    formatters = {
        "text": TextFormatter,
        "json": JSONFormatter,
    }
    if format_name not in formatters:
        raise ValueError(f"Unknown format: {format_name}. Must be one of {list(formatters.keys())}")
    return formatters[format_name]
