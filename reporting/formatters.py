"""Formatters for structured reports."""
from __future__ import annotations
import json
from typing import Dict, Any


def format_text(structured_report: Dict[str, Any]) -> str:
    s = structured_report.get("summary", {})
    lines = [
        "Transaction report:",
        f"  total_rows: {s.get('total_rows', 0)}",
        f"  completed: {s.get('completed', 0)}",
        f"  failed: {s.get('failed', 0)}",
        f"  sum_completed_amount: {s.get('sum_completed_amount', 0)}",
        f"  avg_amount: {s.get('avg_amount', 0)}",
    ]
    return "\n".join(lines)


def format_json(structured_report: Dict[str, Any]) -> str:
    # Use compact JSON that is easy to consume programmatically
    return json.dumps(structured_report, separators=(',', ':'), sort_keys=True)
