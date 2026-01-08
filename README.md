Transaction Reporter
=====================

A small command-line tool used by analysts to inspect daily payment transactions.

What changed
------------
The original single-file script was functional but hard to extend and always read
an entire CSV into memory. This revision preserves the public API and the
default CLI output while improving structure, performance, and testability:

- Streaming reader (no full-file list allocation) ✅
- Separated responsibilities: reader, aggregator, formatters, CLI ✅
- Structured report + opt-in observability (counts and timing) ✅
- New machine-friendly JSON output mode (opt-in) ✅
- Automated tests and a one-command test runner ✅

Requirements
------------
- Python 3.10+ (the code uses only the standard library)
- Runs on Windows 10+ and other platforms

Quick usage
-----------
Print the default human-readable summary (preserves baseline behaviour):

    python transaction_reporter.py examples/sample_transactions.csv

Produce a machine-readable JSON report (includes observability data):

    python transaction_reporter.py examples/sample_transactions.csv --format json

Run tests
---------
Execute the full test suite with a single command:

    ./run_tests

The script will use pytest if available; otherwise it falls back to unittest
from the standard library.

Before / After (same sample CSV)
--------------------------------
Sample CSV (examples/sample_transactions.csv):

id,timestamp,amount_cents,currency,status
1,2025-01-01T10:00:00Z,1000,USD,completed
2,2025-01-01T10:05:00Z,-500,USD,completed
3,2025-01-01T10:10:00Z,0,USD,failed
4,2025-01-01T10:15:00Z,2500,EUR,completed
5,2025-01-01T10:20:00Z,foo,USD,completed

Original/default text output (preserved):

Transaction report:
  total_rows: 5
  completed: 4
  failed: 1
  sum_completed_amount: 3000
  avg_amount: 600.0

New JSON output (example):

{
  "metrics": {
    "total_rows": 5,
    "completed": 4,
    "failed": 1,
    "sum_completed_amount": 3000,
    "avg_amount": 600.0
  },
  "observability": {
    "rows_read": 5,
    "invalid_amounts": 1,
    "duration_seconds": 0.001234
  }
}

Design notes
------------
- The `generate_report(csv_path)` function remains the stable, backwards-
  compatible API and returns the same flat metrics dict as before.
- `generate_structured_report(csv_path)` provides the full report and
  lightweight observability data useful for tests and integrations.
- The code intentionally avoids noisy logging; diagnostics are available in
  structured output when requested (for example via `--format json`).
