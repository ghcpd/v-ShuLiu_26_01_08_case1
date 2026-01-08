# Transaction Report Generator

A command-line tool for generating summary reports from CSV files containing payment transaction data.

## Overview

This tool reads a CSV file of transactions and computes summary metrics such as total rows, completed/failed counts, sums, and averages. It has been enhanced for better modularity, performance, and output flexibility while preserving backward compatibility.

### Original Limitations and Improvements

**Original Issues:**
- Monolithic script with mixed responsibilities
- Loaded entire CSV into memory (inefficient for large files)
- Only plain text output
- Minimal error handling
- Hard to extend with new features

**Enhancements:**
- Modular architecture with separate components for reading, aggregating, and formatting
- Streaming CSV processing to reduce memory usage
- Support for JSON output in addition to text
- Improved error handling for common issues
- Easier to extend with new metrics or formats
- Comprehensive test suite

## Architecture

The tool is structured into the following components:

- **TransactionReader**: Streams transactions from CSV files without loading everything into memory
- **TransactionAggregator**: Computes metrics from a stream of transaction data
- **Report**: Structured representation of the report data
- **Formatters** (TextFormatter, JsonFormatter): Render reports in different output formats
- **CLI Layer**: Argument parsing and orchestration using argparse

The original `generate_report()` function remains unchanged for backward compatibility.

## Environment Setup

- **Python Version**: Python 3.10 or later
- **Platform**: Windows 10 or later
- **Dependencies**: None (uses only Python standard library)

No external libraries or system tools are required.

## Running Tests

Execute the test suite with:

```bash
./run_tests
```

Or on Windows:

```cmd
run_tests.bat
```

All tests must pass for the build to be considered successful.

## Usage

### Command Line

Generate a text report (default):
```bash
python transaction_reporter.py examples/sample_transactions.csv
```

Generate a JSON report:
```bash
python transaction_reporter.py examples/sample_transactions.csv --format json
```

### Programmatic API

```python
from transaction_reporter import generate_report, generate_full_report

# Original API - returns flat dict
aggregates = generate_report("examples/sample_transactions.csv")

# Enhanced API - returns structured Report object
report = generate_full_report("examples/sample_transactions.csv")
```

## Examples

### Sample Input (examples/sample_transactions.csv)
```
id,timestamp,amount_cents,currency,status
1,2025-01-01T10:00:00Z,1000,USD,completed
2,2025-01-01T10:05:00Z,-500,USD,completed
3,2025-01-01T10:10:00Z,0,USD,failed
4,2025-01-01T10:15:00Z,2500,EUR,completed
5,2025-01-01T10:20:00Z,foo,USD,completed
```

### Text Output (Original/Default)
```
Transaction report:
  total_rows: 5
  completed: 4
  failed: 1
  sum_completed_amount: 3000
  avg_amount: 600.0
```

### JSON Output (New)
```json
{
  "total_rows": 5,
  "completed": 4,
  "failed": 1,
  "sum_completed_amount": 3000,
  "avg_amount": 600.0
}
```

## Backward Compatibility

- The `generate_report()` function returns identical results for valid inputs
- Default CLI behavior produces the same text output
- Existing scripts and integrations continue to work unchanged