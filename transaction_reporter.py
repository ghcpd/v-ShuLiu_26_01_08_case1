import csv
import sys
import json
import argparse
import os
from typing import Dict, Any, Iterator


class TransactionReader:
    """Streams transactions from a CSV file."""

    def __init__(self, csv_path: str):
        self.csv_path = csv_path

    def read_transactions(self) -> Iterator[Dict[str, str]]:
        try:
            with open(self.csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    yield row
        except FileNotFoundError:
            raise
        except csv.Error as e:
            raise ValueError(f"Invalid CSV format: {e}")


class TransactionAggregator:
    """Computes aggregates from a stream of transactions."""

    def __init__(self):
        self.total_rows = 0
        self.completed = 0
        self.failed = 0
        self.sum_completed_amount = 0
        self.sum_all_amount = 0

    def process_transaction(self, row: Dict[str, str]):
        self.total_rows += 1
        status = row.get("status", "").strip()
        amount_raw = row.get("amount_cents", "0").strip()
        try:
            amount = int(amount_raw)
        except ValueError:
            # Treat invalid amount as 0, consistent with baseline
            amount = 0

        self.sum_all_amount += amount

        if status == "completed":
            self.completed += 1
            self.sum_completed_amount += amount
        elif status == "failed":
            self.failed += 1

    def get_aggregates(self) -> Dict[str, Any]:
        avg_amount = self.sum_all_amount / self.total_rows if self.total_rows > 0 else 0.0
        return {
            "total_rows": self.total_rows,
            "completed": self.completed,
            "failed": self.failed,
            "sum_completed_amount": self.sum_completed_amount,
            "avg_amount": avg_amount,
        }


class Report:
    """Structured report representation."""

    def __init__(self, aggregates: Dict[str, Any]):
        self.aggregates = aggregates
        # Could add more fields like timings, errors, etc. in the future


def generate_report(csv_path: str) -> Dict[str, Any]:
    """Baseline API: returns flat dict of aggregates.

    Preserves original behavior and semantics.
    """
    reader = TransactionReader(csv_path)
    aggregator = TransactionAggregator()
    for row in reader.read_transactions():
        aggregator.process_transaction(row)
    return aggregator.get_aggregates()


def generate_full_report(csv_path: str) -> Report:
    """Enhanced API: returns structured report object."""
    aggregates = generate_report(csv_path)
    return Report(aggregates)


class TextFormatter:
    @staticmethod
    def format(report: Report) -> str:
        agg = report.aggregates
        lines = [
            "Transaction report:",
            f"  total_rows: {agg['total_rows']}",
            f"  completed: {agg['completed']}",
            f"  failed: {agg['failed']}",
            f"  sum_completed_amount: {agg['sum_completed_amount']}",
            f"  avg_amount: {agg['avg_amount']}",
        ]
        return "\n".join(lines)


class JsonFormatter:
    @staticmethod
    def format(report: Report) -> str:
        return json.dumps(report.aggregates, indent=2)


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Generate transaction reports.")
    parser.add_argument("csv_path", help="Path to the transactions CSV file")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    args = parser.parse_args(argv)

    try:
        report = generate_full_report(args.csv_path)
    except FileNotFoundError:
        print(f"Error: file not found: {args.csv_path}", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 3
    except Exception as e:
        print(f"Error while processing {args.csv_path}: {e}", file=sys.stderr)
        return 3

    if args.format == "text":
        print(TextFormatter.format(report))
    elif args.format == "json":
        print(JsonFormatter.format(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
