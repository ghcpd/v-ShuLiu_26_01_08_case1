# Transaction Reporter

A small CLI tool to summarize daily payment transactions from CSV files.

Originally a single monolithic script, this repository refactors the tool into
modular components for streaming input, aggregation, and formatting while
preserving the original `generate_report(csv_path: str) -> dict` API and the
default CLI textual output that users rely on.

Requirements
- Python 3.10+ (the code uses standard library features available in 3.10)
- Works on Windows 10+ and other platforms

Architecture
- `transaction_reporter.py` - top-level CLI and the backward-compatible `generate_report` facade.
- `transactions/reader.py` - streams transaction rows from CSV without loading everything into memory.
- `transactions/aggregator.py` - computes structured report (summary + meta) from streamed rows.
- `transactions/formatters.py` - functions to render the structured report as text or JSON.

Behavior and Compatibility
- The public function `generate_report(csv_path: str)` still returns the same
  flat dict keys as the original implementation: `total_rows`, `completed`,
  `failed`, `sum_completed_amount`, and `avg_amount`.
- Running `python transaction_reporter.py path/to/transactions.csv` prints the
  same human-readable summary as before (same labels and values).
- Extra output mode: `-f json` will print a JSON representation of the structured
  report for machine consumption.

Improvements
- Streaming reader reduces peak memory usage for large CSV files.
- Clear separation of responsibilities makes it straightforward to add new
  metrics or output formats.
- Basic observability exposed in the structured report (`meta.rows_read`,
  `meta.rows_invalid`, `meta.duration_s`).
- Robust numeric parsing: invalid numeric `amount_cents` values are treated as
  zero (same semantics as the original script) but are also counted in
  `meta.rows_invalid`.

Running tests
- Run the full test suite using the helper script:

```bash
./run_tests
```

This script will use `pytest` if available, otherwise it falls back to the
standard library `unittest` runner.

Before / After example (using `examples/sample_transactions.csv`)

Original textual output (kept as default):

Transaction report:
  total_rows: 5
  completed: 4
  failed: 1
  sum_completed_amount: 3000
  avg_amount: 600.0

JSON output mode (new):

$ python transaction_reporter.py examples/sample_transactions.csv -f json
{"meta":{"duration_s":0.000xxx,"rows_invalid":1,"rows_read":5},"summary":{"avg_amount":600.0,"completed":4,"failed":1,"sum_completed_amount":3000,"total_rows":5}}

License: internal (example repository)
