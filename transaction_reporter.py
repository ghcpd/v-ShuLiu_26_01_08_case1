"""Transaction reporter CLI and compatibility layer.

This module preserves the original entry points and behavior while delegating
parsing, aggregation and formatting to smaller components in the `reporting`
package.
"""
from __future__ import annotations
import sys
import json
from typing import Dict, Any

from reporting.reader import stream_transactions
from reporting.core import aggregate_transactions
from reporting.formatters import format_text, format_json


def generate_structured_report(csv_path: str) -> Dict[str, Any]:
    """Return a structured report (summary + meta) produced in a streaming fashion."""
    obs: Dict[str, int] = {}
    transactions = stream_transactions(csv_path, observability=obs)
    structured = aggregate_transactions(transactions, observability=obs)
    # attach observability to structured output
    structured.setdefault("meta", {}).update({"read": obs})
    return structured


def generate_report(csv_path: str) -> Dict[str, Any]:
    """Compatibility wrapper: return the same flat dict as the baseline.

    The function computes a structured report and then maps required fields into
    the original flat return shape so that callers depending on the baseline API
    continue to work unchanged.
    """
    structured = generate_structured_report(csv_path)
    s = structured["summary"]

    return {
        "total_rows": s.get("total_rows", 0),
        "completed": s.get("completed", 0),
        "failed": s.get("failed", 0),
        "sum_completed_amount": s.get("sum_completed_amount", 0),
        "avg_amount": s.get("avg_amount", 0),
    }


def _format_report_flat(report: Dict[str, Any]) -> str:
    # Keep the same textual layout as the original baseline
    lines = [
        "Transaction report:",
        f"  total_rows: {report['total_rows']}",
        f"  completed: {report['completed']}",
        f"  failed: {report['failed']}",
        f"  sum_completed_amount: {report['sum_completed_amount']}",
        f"  avg_amount: {report['avg_amount']}",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    # Simple CLI parsing to keep default behavior identical while allowing
    # opt-in machine-readable JSON output via "--format json".
    out_format = "text"
    args = list(argv)
    if len(args) >= 2 and args[0] in ("-f", "--format"):
        out_format = args[1]
        args = args[2:]

    if not args:
        print("Usage: python transaction_reporter.py <path_to_transactions_csv>")
        return 1

    csv_path = args[0]
    try:
        if out_format == "json":
            structured = generate_structured_report(csv_path)
            print(format_json(structured))
        else:
            report = generate_report(csv_path)
            print(_format_report_flat(report))
    except FileNotFoundError:
        print(f"Error: file not found: {csv_path}")
        return 2
    except Exception as e:  # intentionally simple diagnostics by default
        print(f"Error while processing {csv_path}: {e}")
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
