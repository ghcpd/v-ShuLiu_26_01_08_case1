"""Aggregation core: compute metrics from an iterator of transactions."""
from __future__ import annotations
from typing import Dict, Any, Iterable


def aggregate_transactions(transactions: Iterable[Dict[str, str]], observability: Dict[str, int] | None = None) -> Dict[str, Any]:
    """Compute a structured report from transactions iterator.

    Returns a dict with keys:
      - summary: dict with required aggregates
      - meta: observability dict (counters/timings)
    """
    total_rows = 0
    completed = 0
    failed = 0
    sum_completed_amount = 0
    sum_all_amount = 0

    if observability is not None:
        observability.setdefault("invalid_amounts", 0)

    for row in transactions:
        total_rows += 1
        status = (row.get("status") or "").strip()
        amount_raw = (row.get("amount_cents") or "0").strip()
        try:
            amount = int(amount_raw)
        except Exception:
            amount = 0
            if observability is not None:
                observability["invalid_amounts"] += 1

        sum_all_amount += amount

        if status == "completed":
            completed += 1
            sum_completed_amount += amount
        elif status == "failed":
            failed += 1

    avg_amount = sum_all_amount / total_rows if total_rows > 0 else 0.0

    summary = {
        "total_rows": total_rows,
        "completed": completed,
        "failed": failed,
        "sum_completed_amount": sum_completed_amount,
        "avg_amount": avg_amount,
        # keep internal total sum available in structured report
        "sum_all_amount": sum_all_amount,
    }

    return {"summary": summary, "meta": dict(observability or {})}
