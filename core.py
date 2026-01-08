"""Aggregation core: compute metrics from an iterator of transaction rows.

Exports:
- aggregate_transactions(rows) -> structured report (nested dict)
- generate_structured_report(csv_path) -> convenience wrapper that uses the
  streaming reader and returns the full structured report.

The baseline `generate_report(csv_path)` in the top-level module will continue
to return the original flat dict for backward compatibility.
"""
from __future__ import annotations

import time
from typing import Iterator, Dict, Any


def _safe_int(value: str) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def aggregate_transactions(rows: Iterator[Dict[str, str]]) -> Dict[str, Any]:
    """Compute metrics and simple observability from an iterator of rows.

    The returned structure is intentionally richer than the legacy flat dict so
    formatters can render multiple output formats from the same data.
    """
    start = time.perf_counter()
    total_rows = 0
    completed = 0
    failed = 0
    sum_completed_amount = 0
    sum_all_amount = 0
    invalid_amounts = 0

    for row in rows:
        total_rows += 1
        status = (row.get("status") or "").strip()
        amount_raw = (row.get("amount_cents") or "0").strip()
        amount = _safe_int(amount_raw)
        if amount_raw and not amount and amount_raw != "0":
            invalid_amounts += 1

        sum_all_amount += amount
        if status == "completed":
            completed += 1
            sum_completed_amount += amount
        elif status == "failed":
            failed += 1

    avg_amount = float(sum_all_amount) / total_rows if total_rows > 0 else 0.0
    duration = time.perf_counter() - start

    structured = {
        "metrics": {
            "total_rows": total_rows,
            "completed": completed,
            "failed": failed,
            "sum_completed_amount": sum_completed_amount,
            "avg_amount": avg_amount,
        },
        "observability": {
            "duration_seconds": duration,
            "invalid_amounts": invalid_amounts,
        },
    }
    return structured


def generate_structured_report(csv_path: str) -> Dict[str, Any]:
    """Convenience helper that streams the CSV and returns the structured
    report. Raises FileNotFoundError like the baseline when the file is
    missing.
    """
    # Local import to avoid circular imports when used from top-level module
    from reader import stream_transactions

    rows = stream_transactions(csv_path)
    return aggregate_transactions(rows)
