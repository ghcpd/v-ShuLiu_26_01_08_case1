"""Lightweight CLI around the reporting library.

This module preserves the original public entry point `generate_report(csv_path)`
and the CLI behaviour while delegating implementation to smaller components in
the `transactions` package.
"""
from __future__ import annotations

import sys
import argparse
import json
from typing import Dict, Any

from transactions import reader as reader_mod
from transactions import aggregator as agg_mod
from transactions import formatters


def generate_report(csv_path: str) -> Dict[str, Any]:
    """Backward-compatible function that returns the same flat dict as before.

    Internally this streams rows, computes a structured report, and then
    returns the baseline scalar aggregates to keep callers a stable behavior.
    """
    rows = reader_mod.stream_transactions(csv_path)
    structured = agg_mod.compute_report(rows)

    # Preserve the original flat dict contract
    return {
        "total_rows": structured["summary"]["total_rows"],
        "completed": structured["summary"]["completed"],
        "failed": structured["summary"]["failed"],
        "sum_completed_amount": structured["summary"]["sum_completed_amount"],
        "avg_amount": structured["summary"]["avg_amount"],
    }


def _print_default(report: Dict[str, Any]) -> None:
    print("Transaction report:")
    print(f"  total_rows: {report['summary']['total_rows']}")
    print(f"  completed: {report['summary']['completed']}")
    print(f"  failed: {report['summary']['failed']}")
    print(f"  sum_completed_amount: {report['summary']['sum_completed_amount']}")
    print(f"  avg_amount: {report['summary']['avg_amount']}")


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="Generate a small transaction summary report"
    )
    parser.add_argument("csv_path", help="path to transactions CSV")
    parser.add_argument("-f", "--format", choices=["text", "json"], default="text", help="output format")
    parser.add_argument("-v", "--verbose", action="store_true", help="print extra diagnostics to stderr")

    args = parser.parse_args(argv)

    try:
        rows = reader_mod.stream_transactions(args.csv_path)
        structured = agg_mod.compute_report(rows)
    except FileNotFoundError:
        print(f"Error: file not found: {args.csv_path}")
        return 2
    except Exception as e:
        print(f"Error while processing {args.csv_path}: {e}")
        return 3

    if args.verbose:
        # Print small diagnostics to stderr
        meta = structured.get("meta", {})
        print(f"# diagnostics: rows_read={meta.get('rows_read', 0)} rows_invalid={meta.get('rows_invalid', 0)} duration_s={meta.get('duration_s', 0):.6f}", file=sys.stderr)

    if args.format == "json":
        print(formatters.format_json(structured))
    else:
        # default: text (keeps the original textual layout)
        _print_default(structured)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
