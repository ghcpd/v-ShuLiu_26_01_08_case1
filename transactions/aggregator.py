"""Aggregates transaction rows into a structured in-memory report.

The returned report is a dict with at least the following structure:
{
    "summary": { ... },
    "meta": { rows_read, rows_invalid, duration_s }
}

The `generate_report` facade in the top-level module converts the
`summary` into the original flat dict expected by callers.
"""
from __future__ import annotations

import time
from typing import Iterator, Dict, Any


def _parse_amount(amount_raw: str) -> int:
    try:
        return int(amount_raw.strip())
    except Exception:
        return 0


def compute_report(rows: Iterator[Dict[str, str]]) -> Dict[str, Any]:
    start = time.perf_counter()

    total_rows = 0
    completed = 0
    failed = 0
    sum_completed_amount = 0
    sum_all_amount = 0
    rows_invalid = 0

    for row in rows:
        total_rows += 1
        status = (row.get("status") or "").strip()
        amount_raw = (row.get("amount_cents") or "0").strip()

        # robust parsing: invalid numeric values count as invalid and are treated as 0
        try:
            amount = _parse_amount(amount_raw)
        except Exception:
            amount = 0
            rows_invalid += 1

        sum_all_amount += amount

        if status == "completed":
            completed += 1
            sum_completed_amount += amount
        elif status == "failed":
            failed += 1

    avg_amount = sum_all_amount / total_rows if total_rows > 0 else 0.0

    end = time.perf_counter()

    return {
        "summary": {
            "total_rows": total_rows,
            "completed": completed,
            "failed": failed,
            "sum_completed_amount": sum_completed_amount,
            "avg_amount": avg_amount,
        },
        "meta": {
            "rows_read": total_rows,
            "rows_invalid": rows_invalid,
            "duration_s": end - start,
        },
    }
