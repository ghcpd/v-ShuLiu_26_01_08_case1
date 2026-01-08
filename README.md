# Transaction Report Generator

A small command-line tool to generate summary reports from CSV transaction files.

Features
- Keeps the original `generate_report(csv_path: str) -> dict` API and default CLI behavior.
- Modular components: streaming CSV reader, aggregation core, and formatters.
- Supports a machine-readable JSON output (`--format json`).
- Lower memory footprint via streaming; simple observability counters are exposed in the structured report.

Requirements
- Python 3.10+ (works on Windows 10/11 and other platforms)

Quick usage

- Default (text summary - preserves baseline output):

  ```bash
  python transaction_reporter.py examples/sample_transactions.csv
  ```

  Example output (before / after):

  Transaction report:
    total_rows: 5
    completed: 4
    failed: 1
    sum_completed_amount: 3000
    avg_amount: 600.0

- JSON output (machine-readable):

  ```bash
  python transaction_reporter.py --format json examples/sample_transactions.csv
  ```

  Example JSON output:

  {
    "meta": {"read": {"invalid_amounts": 1, "malformed_rows": 0, "read_time_ms": 12, "rows": 5}},
    "summary": {"avg_amount": 600.0, "completed": 4, "failed": 1, "sum_all_amount": 3000, "sum_completed_amount": 3000, "total_rows": 5}
  }

Testing

- Run the full test suite with:

  ```bash
  ./run_tests
  ```

  The script will use `pytest` if installed, otherwise it falls back to the standard `unittest` test discovery.

Design notes

- The code is split into small modules under `reporting/`:
  - `reader.py`: streams rows from CSV, collects basic read counters.
  - `core.py`: computes aggregates from an iterator of rows in a streaming fashion.
  - `formatters.py`: transforms structured report data into text or JSON outputs.
- `transaction_reporter.py` remains the public entrypoint and provides compatibility for existing tooling.

Compatibility

- Existing callers using `generate_report` will keep receiving the same keys and values as before.
- New functionality (structured report, JSON output, observability) is exposed through new APIs and CLI flags and does not change the default behavior.
