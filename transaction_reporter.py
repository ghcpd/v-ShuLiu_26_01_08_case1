import csv
import sys
from typing import Dict, Any


def generate_report(csv_path: str) -> Dict[str, Any]:
    """Baseline implementation: load all rows into memory and compute simple aggregates.

    This function is intentionally simple and somewhat inefficient; your enhancement
    task should preserve the semantics of the returned dict for valid inputs while
    improving structure and extensibility in new code.
    """
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    total_rows = len(rows)
    completed = 0
    failed = 0
    sum_completed_amount = 0
    sum_all_amount = 0

    for row in rows:
        status = row.get("status", "").strip()
        amount_raw = row.get("amount_cents", "0").strip()
        try:
            amount = int(amount_raw)
        except ValueError:
            # Treat invalid amount as 0 in the baseline implementation
            amount = 0

        sum_all_amount += amount

        if status == "completed":
            completed += 1
            sum_completed_amount += amount
        elif status == "failed":
            failed += 1

    avg_amount = sum_all_amount / total_rows if total_rows > 0 else 0.0

    return {
        "total_rows": total_rows,
        "completed": completed,
        "failed": failed,
        "sum_completed_amount": sum_completed_amount,
        "avg_amount": avg_amount,
    }


def _format_report(report: Dict[str, Any]) -> str:
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

    if not argv:
        print("Usage: python transaction_reporter.py <path_to_transactions_csv>")
        return 1

    csv_path = argv[0]
    try:
        report = generate_report(csv_path)
    except FileNotFoundError:
        print(f"Error: file not found: {csv_path}")
        return 2
    except Exception as e:  # baseline: very simple catch-all
        print(f"Error while processing {csv_path}: {e}")
        return 3

    print(_format_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
