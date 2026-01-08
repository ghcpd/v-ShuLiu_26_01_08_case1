"""Formatting helpers: text and JSON renderers for the structured report."""
from __future__ import annotations

import json
from typing import Dict, Any


def format_text(report: Dict[str, Any]) -> str:
    s = report["summary"]
    lines = [
        "Transaction report:",
        f"  total_rows: {s['total_rows']}",
        f"  completed: {s['completed']}",
        f"  failed: {s['failed']}",
        f"  sum_completed_amount: {s['sum_completed_amount']}",
        f"  avg_amount: {s['avg_amount']}",
    ]
    return "\n".join(lines)


def format_json(report: Dict[str, Any]) -> str:
    # produce a compact JSON string suitable for machine consumption
    return json.dumps(report, separators=(',', ':'), sort_keys=True)
