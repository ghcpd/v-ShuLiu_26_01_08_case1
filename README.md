# Transaction Report Generator - Enhanced Version

## Overview

This is an enhanced version of the transaction reporting tool, a command-line utility for analysts to inspect and aggregate daily payment transactions. The tool reads CSV files of raw transactions and generates reports in multiple formats.

### Original Limitations (Now Addressed)

The original implementation had several pain points:

- **Tight Coupling**: Parsing, aggregation, formatting, and CLI handling were all mixed in one script
- **Memory Inefficient**: Always loaded the entire CSV into memory
- **Limited Output**: Only plain-text output; no machine-readable formats
- **Hard to Extend**: Adding new metrics or output formats required modifying core logic
- **Minimal Error Handling**: Basic exception handling with little observability

## How This Version Addresses Them

### 1. Modular Architecture

The tool is now split into specialized components:

- **`reader.py`**: Streams transactions from CSV files with robust parsing
  - `Transaction` class: Type-safe representation of a single transaction
  - `TransactionReader` class: Handles CSV reading with error handling
  - Supports both streaming (`read()`) and bulk (`read_all()`) modes

- **`aggregator.py`**: Computes metrics from transaction iterators
  - `MetricsAggregator` class: Accumulates statistics efficiently
  - Streaming-compatible for memory efficiency
  - Exposes both basic metrics and full structured reports

- **`formatters.py`**: Renders metrics in different output formats
  - `TextFormatter`: Human-readable plain-text output (backward compatible)
  - `JSONFormatter`: Machine-readable JSON output
  - Extensible for adding new formats (CSV, XML, etc.)

- **`transaction_reporter.py`**: CLI layer and stable API
  - `generate_report(csv_path)`: Original baseline API (backward compatible)
  - `generate_full_report(csv_path)`: Enhanced API with full report structure
  - `main()`: CLI with format selection support

### 2. Output Flexibility

- **Text Format** (default): Identical to baseline output for compatibility
- **JSON Format**: Machine-readable structured output, selectable via `--format json`
- All formats rendered from the same report data, ensuring consistency

### 3. Performance & Scalability

- **Streaming CSV Reading**: Transactions are processed one at a time, not loaded all into memory
- **Constant Memory Usage**: Memory usage stays constant regardless of file size
- **Extensible Architecture**: Easy to add batching, compression, or async processing later

### 4. Robustness & Observability

- **Error Handling**: Graceful handling of missing files, malformed rows, invalid amounts
- **Observability Data**: Metrics include transaction count and processing stats
- **Type Safety**: `Transaction` class provides safe field access with sensible defaults
- **Minimal Logging**: Quiet by default, suitable for automation

## Environment Setup

### Requirements

- **Python**: 3.10 or later
- **OS**: Windows 10+, macOS 11+, or Linux (any recent distro)
- **Dependencies**: None! Uses only Python standard library

### Installation

No special installation needed. Simply clone or download the repository and ensure Python 3.10+ is installed.

Verify your Python version:
```bash
python --version
```

## Running the Tool

### Baseline Usage (Backward Compatible)

Print a text summary to stdout:
```bash
python transaction_reporter.py examples/sample_transactions.csv
```

Expected output:
```
Transaction report:
  total_rows: 5
  completed: 4
  failed: 1
  sum_completed_amount: 4000
  avg_amount: 600.0
```

### Enhanced Usage: JSON Output

```bash
python transaction_reporter.py --format json examples/sample_transactions.csv
```

Expected output:
```json
{
  "total_rows": 5,
  "completed": 4,
  "failed": 1,
  "sum_completed_amount": 4000,
  "avg_amount": 600.0
}
```

### Programmatic API (Python Code)

```python
from transaction_reporter import generate_report, generate_full_report

# Original baseline API - returns flat dict
report = generate_report("examples/sample_transactions.csv")
print(f"Total: {report['total_rows']}, Completed: {report['completed']}")

# Enhanced API - returns structured report with metadata
full_report = generate_full_report("examples/sample_transactions.csv")
print(f"Processed: {full_report['observability']['transactions_processed']}")
```

## Running Tests

### One-Command Test Runner

Run the complete test suite:

```bash
python run_tests
```

Or on Windows:
```bash
run_tests.bat
```

The test runner will:
- Attempt to use pytest if installed (for better output)
- Fall back to unittest if pytest is unavailable
- Run all tests in `test_transaction_reporter.py`
- Exit with code 0 if all tests pass, non-zero if any fail

### Manual Test Execution

If you prefer to run tests manually:

```bash
# Using unittest directly
python -m unittest discover -s . -p "test_*.py" -v

# Or run a specific test class
python -m unittest test_transaction_reporter.TestBaselineAPI -v
```

### Test Coverage

The test suite covers:

- **Reader Tests**: CSV parsing, transaction objects, error handling
- **Aggregator Tests**: Metric computation, edge cases (empty files, invalid amounts)
- **Formatter Tests**: Text and JSON output formatting
- **CLI Tests**: Command-line argument parsing, format selection, error codes
- **Baseline API Tests**: Backward compatibility verification with sample data
- **Integration Tests**: End-to-end workflows using the sample CSV

## Architecture Diagram

```
CSV File
   |
   v
TransactionReader
   | (yields Transaction objects)
   v
MetricsAggregator
   | (accumulates metrics)
   v
Full Report Dict
   |
   +---> TextFormatter ---> stdout (text)
   |
   +---> JSONFormatter ---> stdout (json)
```

## Sample Input & Output

### Input (examples/sample_transactions.csv)
```
id,timestamp,amount_cents,currency,status
1,2025-01-01T10:00:00Z,1000,USD,completed
2,2025-01-01T10:05:00Z,-500,USD,completed
3,2025-01-01T10:10:00Z,0,USD,failed
4,2025-01-01T10:15:00Z,2500,EUR,completed
5,2025-01-01T10:20:00Z,foo,USD,completed
```

### Text Output (Baseline)
```
Transaction report:
  total_rows: 5
  completed: 4
  failed: 1
  sum_completed_amount: 4000
  avg_amount: 600.0
```

### JSON Output (Enhanced)
```json
{
  "total_rows": 5,
  "completed": 4,
  "failed": 1,
  "sum_completed_amount": 4000,
  "avg_amount": 600.0
}
```

## API Reference

### transaction_reporter.py

#### `generate_report(csv_path: str) -> Dict[str, Any]`
**Baseline API (backward compatible)**

Reads a CSV file and returns aggregated metrics as a flat dictionary.

**Parameters:**
- `csv_path` (str): Path to the CSV file

**Returns:**
- Dictionary with keys: `total_rows`, `completed`, `failed`, `sum_completed_amount`, `avg_amount`

**Raises:**
- `FileNotFoundError`: If the CSV file does not exist

**Example:**
```python
report = generate_report("transactions.csv")
print(f"Processed {report['total_rows']} transactions")
```

#### `generate_full_report(csv_path: str) -> Dict[str, Any]`
**Enhanced API**

Reads a CSV file and returns a structured report with metrics and observability data.

**Parameters:**
- `csv_path` (str): Path to the CSV file

**Returns:**
- Dictionary with:
  - `metrics`: Same as `generate_report()` output
  - `observability`: Dictionary with `transactions_processed` count

**Example:**
```python
full = generate_full_report("transactions.csv")
print(f"Metrics: {full['metrics']}")
print(f"Processed: {full['observability']['transactions_processed']}")
```

#### `main(argv: Optional[list] = None) -> int`
**CLI Entry Point**

Parses command-line arguments and prints formatted output.

**Parameters:**
- `argv` (Optional[list]): Command-line arguments (defaults to sys.argv[1:])

**Returns:**
- Exit code: 0 (success), 1 (invalid args), 2 (file not found), 3 (processing error)

**Supported Arguments:**
- `python transaction_reporter.py <csv_path>` - Text format (default)
- `python transaction_reporter.py --format json <csv_path>` - JSON format
- `python transaction_reporter.py -f json <csv_path>` - JSON format (short flag)

### reader.py

#### `class Transaction`
**Represents a single transaction**

**Properties:**
- `id`: Transaction ID
- `timestamp`: Transaction timestamp
- `amount_cents` (int): Amount in cents; invalid amounts return 0
- `currency`: Currency code
- `status`: Transaction status (completed, failed, etc.)

#### `class TransactionReader`
**Streams transactions from CSV files**

**Methods:**
- `read() -> Iterator[Transaction]`: Stream transactions one at a time
- `read_all() -> list[Transaction]`: Read all transactions into a list

### aggregator.py

#### `class MetricsAggregator`
**Accumulates transaction metrics**

**Methods:**
- `process_transaction(transaction: Transaction)`: Process a single transaction
- `process_transactions(transactions: Iterator[Transaction])`: Process multiple transactions
- `get_metrics() -> Dict[str, Any]`: Return basic metrics
- `get_full_report() -> Dict[str, Any]`: Return full report with observability

### formatters.py

#### `class TextFormatter`
- `format(metrics: Dict[str, Any]) -> str`: Format metrics as plain text

#### `class JSONFormatter`
- `format(metrics: Dict[str, Any], pretty: bool = False) -> str`: Format metrics as JSON

#### `get_formatter(format_name: str)`
Get a formatter by name. Supported formats: `"text"`, `"json"`

## Extension Guide

### Adding a New Output Format

1. Create a new formatter class in `formatters.py`:
```python
class CSVFormatter:
    @staticmethod
    def format(metrics: Dict[str, Any]) -> str:
        lines = [f"metric,value"]
        for key, value in metrics.items():
            lines.append(f"{key},{value}")
        return "\n".join(lines)
```

2. Register it in `get_formatter()`:
```python
formatters = {
    "text": TextFormatter,
    "json": JSONFormatter,
    "csv": CSVFormatter,  # Add this
}
```

3. Update CLI help and it will automatically work!

### Adding a New Metric

1. Modify `MetricsAggregator.process_transaction()` to track the new metric
2. Update `get_metrics()` to include it in the returned dict
3. Add tests in `test_transaction_reporter.py`

## Project Structure

```
.
├── transaction_reporter.py    # Main script & stable API
├── reader.py                  # CSV reading & transaction parsing
├── aggregator.py              # Metrics computation
├── formatters.py              # Output formatting (text, JSON, etc.)
├── test_transaction_reporter.py  # Comprehensive test suite
├── run_tests                  # Unix/Linux test runner (executable)
├── run_tests.bat              # Windows test runner
├── README.md                  # This file
├── examples/
│   └── sample_transactions.csv  # Sample data for testing
└── .git/                      # Version control
```

## Backward Compatibility

This enhancement maintains 100% backward compatibility:

- The `generate_report()` function API remains unchanged
- CLI output with default options is identical to the baseline
- For the same CSV input, metrics are guaranteed to be the same
- All existing scripts and automations continue to work unchanged

## Design Decisions

### Why Streaming Instead of Loading All Data?

- Constant memory usage regardless of file size
- Scales to multi-gigabyte transaction files
- Future-proof for real-time streaming data

### Why Separate Modules?

- **Single Responsibility**: Each module has one reason to change
- **Testability**: Independent components are easier to test
- **Reusability**: Modules can be imported in other projects
- **Maintainability**: Changes are isolated and easier to review

### Why JSON + Text Rather Than Other Formats?

- **JSON**: Universal, widely supported, excellent for automation/dashboards
- **Text**: Human-friendly, suitable for logs and reports
- **Extensible**: New formatters can be added without modifying core logic

## Troubleshooting

### "ModuleNotFoundError: No module named 'reader'"

Ensure you're running from the project root directory:
```bash
cd /path/to/transaction-reporter
python transaction_reporter.py examples/sample_transactions.csv
```

### "FileNotFoundError: [Errno 2] No such file or directory"

Verify the CSV file path exists:
```bash
python transaction_reporter.py /full/path/to/file.csv
```

### Tests fail with "No module named 'unittest'"

This shouldn't happen; unittest is part of Python's standard library. Verify Python installation:
```bash
python -m unittest --help
```

## Future Enhancements

Possible improvements to consider for future versions:

- **Streaming Output**: Support for processing files larger than available memory
- **Batch Processing**: Process multiple files with aggregated metrics
- **Time-Series**: Group metrics by hour/day/month
- **Filtering**: Pre-filter transactions by date range or status
- **Performance Metrics**: Track and report processing time, throughput
- **Database Output**: Write reports directly to databases
- **Schema Validation**: Verify CSV structure before processing
- **Compression**: Auto-decompress gzipped CSV files

## Contributing

To maintain quality, please:

1. Add tests for any new features
2. Ensure `python run_tests` passes
3. Keep the architecture modular
4. Update README.md with usage examples
5. Maintain Python 3.10+ compatibility

## License

[Add your license here]

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the API reference
3. Check test cases for usage examples
4. Examine sample CSV structure
