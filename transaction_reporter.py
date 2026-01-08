import csv
import sys
import time
import json
from typing import Dict, Any, Iterator, Tuple


def stream_transactions(csv_path: str) -> Iterator[Dict[str, str]]:
    """Yield rows from a CSV file as dictionaries (streaming).

    This replaces the "read everything into a list" behavior while keeping the
    same parsing semantics for valid inputs.
    """
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def generate_structured_report(csv_path: str) -> Dict[str, Any]:
    """Compute a structured report and basic observability information.

    The returned dict contains two top-level keys:
      - "metrics": the same aggregates the baseline exposed
      - "observability": simple counters and a duration in seconds

    This function is safe to call from tests and the CLI. It treats invalid
    numeric amounts the same way the baseline did (as 0) but also records the
    number of such occurrences in observability so callers can opt-in to
    diagnostics without changing default output.
    """
    start = time.perf_counter()
    rows = 0
    invalid_amounts = 0

    completed = 0
    failed = 0
    sum_completed_amount = 0
    sum_all_amount = 0

    for row in stream_transactions(csv_path):
        rows += 1
        status = row.get("status", "").strip()
        amount_raw = row.get("amount_cents", "0").strip()
        try:
            amount = int(amount_raw)
        except ValueError:
            # Preserve baseline behaviour: treat invalid amount as 0, but record it.
            amount = 0
            invalid_amounts += 1

        sum_all_amount += amount

        if status == "completed":
            completed += 1
            sum_completed_amount += amount
        elif status == "failed":
            failed += 1

    avg_amount = sum_all_amount / rows if rows > 0 else 0.0
    duration = time.perf_counter() - start

    return {
        "metrics": {
            "total_rows": rows,
            "completed": completed,
            "failed": failed,
            "sum_completed_amount": sum_completed_amount,
            "avg_amount": avg_amount,
        },
        "observability": {
            "rows_read": rows,
            "invalid_amounts": invalid_amounts,
            "duration_seconds": duration,
        },
    }


def generate_report(csv_path: str) -> Dict[str, Any]:
    """Compatibility wrapper kept for callers that expect the original flat dict.

    It delegates to the new structured pipeline but returns the same simple
    mapping the baseline returned for valid inputs.
    """
    structured = generate_structured_report(csv_path)
    return structured["metrics"]


def _format_text_report(metrics: Dict[str, Any]) -> str:
    # Keep the same textual layout and metric names as the baseline so the
    # default CLI output remains semantically equivalent.
    lines = [
        "Transaction report:",
        f"  total_rows: {metrics['total_rows']}",
        f"  completed: {metrics['completed']}",
        f"  failed: {metrics['failed']}",
        f"  sum_completed_amount: {metrics['sum_completed_amount']}",
        f"  avg_amount: {metrics['avg_amount']}",
    ]
    return "\n".join(lines)


def _format_json_report(structured: Dict[str, Any]) -> str:
    return json.dumps(structured, ensure_ascii=False, indent=2)


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        print("Usage: python transaction_reporter.py <path_to_transactions_csv>")
        return 1

    # Simple CLI with an opt-in machine-readable mode; default behaviour is
    # unchanged.
    import argparse

    parser = argparse.ArgumentParser(description="Generate a transaction report")
    parser.add_argument("csv_path")
    parser.add_argument(
        "-f",
        "--format",
        choices=["text", "json"],
        default="text",
        help="report output format (default: text)",
    )
    args = parser.parse_args(argv)

    try:
        structured = generate_structured_report(args.csv_path)
    except FileNotFoundError:
        print(f"Error: file not found: {args.csv_path}")
        return 2
    except Exception as e:
        # Keep a conservative, user-friendly failure mode as the baseline did.
        print(f"Error while processing {args.csv_path}: {e}")
        return 3

    if args.format == "text":
        print(_format_text_report(structured["metrics"]))
    else:
        print(_format_json_report(structured))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
