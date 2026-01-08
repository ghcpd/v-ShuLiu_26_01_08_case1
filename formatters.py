"""Formatters for the structured report.

Provides the legacy text formatter (exactly reproduces the baseline visible
summary) and a JSON formatter for machine consumption.
"""
from __future__ import annotations

import json
from typing import Dict, Any


def format_text(structured_report: Dict[str, Any]) -> str:
    m = structured_report["metrics"]
    # Preserve the original baseline text layout and metric names exactly.
    lines = [
        "Transaction report:",
        f"  total_rows: {m['total_rows']}",
        f"  completed: {m['completed']}",
        f"  failed: {m['failed']}",
        f"  sum_completed_amount: {m['sum_completed_amount']}",
        f"  avg_amount: {m['avg_amount']}",
    ]
    return "\n".join(lines)


def format_json(structured_report: Dict[str, Any], *, pretty: bool = False) -> str:
    if pretty:
        return json.dumps(structured_report, indent=2, sort_keys=True)
    return json.dumps(structured_report, separators=(",", ":"), sort_keys=True)
