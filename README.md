Transaction Reporter
====================

A small command-line tool to produce summary reports from a CSV of payment
transactions. This is an enhanced, modular, and streaming-friendly version of an
internal utility used by analysts.

Highlights
- Backward-compatible public API: `generate_report(csv_path: str) -> dict` (no
  behavioral changes for well-formed input).
- Streaming CSV reader to keep memory usage low on large files.
- Structured in-memory report + multiple formatters (plain text, JSON).
- Better error handling and lightweight observability (counters and timings).
- Full test coverage and a one-command test runner: `./run_tests`.

Requirements
- Python 3.10+
- Works on Windows 10+ (tested with PowerShell)
- No third-party dependencies required for runtime or tests

Quick usage
-----------
Default (preserves original contract and CLI output):

    python transaction_reporter.py examples/sample_transactions.csv

Machine-friendly JSON output:

    python transaction_reporter.py examples/sample_transactions.csv --format json

One-command test runner
-----------------------
Run the test-suite with:

    ./run_tests

The script will use pytest if installed, otherwise it falls back to
`python -m unittest discover`.

Design & changes (short)
------------------------
Problems with the original implementation:
- Loaded the entire CSV into memory
- Parsing, aggregation, and formatting were tightly coupled
- No structured output for automation

What changed
- Reader (streaming): `reader.stream_transactions` — yields CSV rows
- Core/aggregator: `core.aggregate_transactions` — computes a structured
  `report["metrics"]` + `report["observability"]`
- Formatters: `formatters.format_text` (legacy output) and
  `formatters.format_json` (machine-readable)
- Top-level `transaction_reporter.generate_report` preserves the original flat
  return dict and CLI behavior so existing users are unaffected.

Before / After (example)
------------------------
Sample input: `examples/sample_transactions.csv` (included)

Original text summary (unchanged):

Transaction report:
  total_rows: 5
  completed: 4
  failed: 1
  sum_completed_amount: 3000
  avg_amount: 600.0

JSON output (new):

{
  "metrics": { ... },
  "observability": { "duration_seconds": 0.0012, "invalid_amounts": 1 }
}

Testing
-------
- Unit tests are under the `tests/` directory and exercise both the
  programmatic API and the CLI (including error paths and the JSON output).
- Run the full suite with `./run_tests`.

Extending
---------
- Add new formatters in `formatters.py` and wire them in the CLI.
- Add new metrics in `core.aggregate_transactions` — they will be exposed to
  all formatters automatically.

Contact
-------
Internal tool maintained by the payments analytics team. For questions or
feature requests, open an internal ticket with the sample CSV and desired
output format.
