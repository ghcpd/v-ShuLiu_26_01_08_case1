import sys
from typing import Dict, Any, Optional

from reader import TransactionReader
from aggregator import MetricsAggregator
from formatters import get_formatter


def generate_report(csv_path: str) -> Dict[str, Any]:
    """Generate a transaction report with the same semantics as baseline.

    Reads transactions from the CSV file and computes aggregates. This function
    maintains backward compatibility with the original API.
    
    Args:
        csv_path: Path to the CSV file.
    
    Returns:
        Dict with keys: total_rows, completed, failed, sum_completed_amount, avg_amount.
    """
    reader = TransactionReader(csv_path)
    aggregator = MetricsAggregator()
    
    # Stream process transactions
    aggregator.process_transactions(reader.read())
    
    # Return only the flat dict metrics for backward compatibility
    return aggregator.get_metrics()


def generate_full_report(csv_path: str) -> Dict[str, Any]:
    """Generate a full structured report including observability data.
    
    This is the enhanced API that exposes the full report structure.
    
    Args:
        csv_path: Path to the CSV file.
    
    Returns:
        Full report dict with metrics and observability.
    """
    reader = TransactionReader(csv_path)
    aggregator = MetricsAggregator()
    aggregator.process_transactions(reader.read())
    return aggregator.get_full_report()


def main(argv: Optional[list] = None) -> int:
    """CLI entry point with support for multiple output formats.
    
    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).
    
    Returns:
        Exit code (0 for success, non-zero for error).
    """
    if argv is None:
        argv = sys.argv[1:]

    # Parse command-line arguments
    csv_path = None
    output_format = "text"  # Default to text for backward compatibility
    
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--format", "-f"):
            if i + 1 >= len(argv):
                print("Error: --format requires an argument")
                return 1
            output_format = argv[i + 1]
            i += 2
        elif arg.startswith("-"):
            print(f"Error: unknown option: {arg}")
            return 1
        else:
            csv_path = arg
            i += 1
    
    if not csv_path:
        print("Usage: python transaction_reporter.py [--format {text|json}] <path_to_transactions_csv>")
        return 1

    try:
        # Use the full report for all output modes
        full_report = generate_full_report(csv_path)
        metrics = full_report["metrics"]
        
        # Get the appropriate formatter
        formatter_class = get_formatter(output_format)
        
        # Format and output
        if output_format == "json":
            output = formatter_class.format(metrics, pretty=True)
        else:
            output = formatter_class.format(metrics)
        
        print(output)
        return 0
        
    except FileNotFoundError:
        print(f"Error: file not found: {csv_path}")
        return 2
    except ValueError as e:
        print(f"Error: {e}")
        return 3
    except Exception as e:
        print(f"Error while processing {csv_path}: {e}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
