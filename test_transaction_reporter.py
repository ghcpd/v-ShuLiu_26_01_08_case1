"""Test suite for the transaction reporter tool.

Tests cover:
- Reader: CSV parsing and streaming
- Aggregator: Metrics computation
- Formatters: Output formatting
- CLI: Command-line interface
- Baseline API: Backward compatibility with generate_report()
"""
import unittest
import tempfile
import os
import sys
import json
from io import StringIO

# Import modules to test
from reader import Transaction, TransactionReader
from aggregator import MetricsAggregator
from formatters import TextFormatter, JSONFormatter, get_formatter
from transaction_reporter import generate_report, generate_full_report, main


class TestTransaction(unittest.TestCase):
    """Test Transaction class."""
    
    def test_transaction_creation(self):
        row = {
            "id": "1",
            "timestamp": "2025-01-01T10:00:00Z",
            "amount_cents": "1000",
            "currency": "USD",
            "status": "completed"
        }
        tx = Transaction(row)
        self.assertEqual(tx.id, "1")
        self.assertEqual(tx.amount_cents, 1000)
        self.assertEqual(tx.status, "completed")
    
    def test_transaction_invalid_amount(self):
        row = {"amount_cents": "foo", "status": "completed"}
        tx = Transaction(row)
        self.assertEqual(tx.amount_cents, 0)
    
    def test_transaction_negative_amount(self):
        row = {"amount_cents": "-500", "status": "completed"}
        tx = Transaction(row)
        self.assertEqual(tx.amount_cents, -500)


class TestTransactionReader(unittest.TestCase):
    """Test TransactionReader class."""
    
    def setUp(self):
        """Create temporary CSV files for testing."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files."""
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)
    
    def test_read_transactions(self):
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, "w", newline="") as f:
            f.write("id,timestamp,amount_cents,currency,status\n")
            f.write("1,2025-01-01T10:00:00Z,1000,USD,completed\n")
            f.write("2,2025-01-01T10:05:00Z,2000,USD,failed\n")
        
        reader = TransactionReader(csv_path)
        transactions = list(reader.read())
        
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0].amount_cents, 1000)
        self.assertEqual(transactions[1].status, "failed")
    
    def test_read_file_not_found(self):
        reader = TransactionReader("/nonexistent/path.csv")
        with self.assertRaises(FileNotFoundError):
            list(reader.read())
    
    def test_read_empty_csv(self):
        csv_path = os.path.join(self.temp_dir, "empty.csv")
        with open(csv_path, "w", newline="") as f:
            pass
        
        reader = TransactionReader(csv_path)
        with self.assertRaises(ValueError):
            list(reader.read())
    
    def test_read_all(self):
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, "w", newline="") as f:
            f.write("id,timestamp,amount_cents,currency,status\n")
            f.write("1,2025-01-01T10:00:00Z,1000,USD,completed\n")
        
        reader = TransactionReader(csv_path)
        transactions = reader.read_all()
        
        self.assertEqual(len(transactions), 1)
        self.assertIsInstance(transactions[0], Transaction)


class TestMetricsAggregator(unittest.TestCase):
    """Test MetricsAggregator class."""
    
    def test_single_transaction(self):
        agg = MetricsAggregator()
        tx = Transaction({
            "id": "1",
            "amount_cents": "1000",
            "status": "completed"
        })
        agg.process_transaction(tx)
        
        metrics = agg.get_metrics()
        self.assertEqual(metrics["total_rows"], 1)
        self.assertEqual(metrics["completed"], 1)
        self.assertEqual(metrics["sum_completed_amount"], 1000)
    
    def test_multiple_transactions(self):
        agg = MetricsAggregator()
        transactions = [
            Transaction({"amount_cents": "1000", "status": "completed"}),
            Transaction({"amount_cents": "2000", "status": "completed"}),
            Transaction({"amount_cents": "500", "status": "failed"}),
        ]
        
        for tx in transactions:
            agg.process_transaction(tx)
        
        metrics = agg.get_metrics()
        self.assertEqual(metrics["total_rows"], 3)
        self.assertEqual(metrics["completed"], 2)
        self.assertEqual(metrics["failed"], 1)
        self.assertEqual(metrics["sum_completed_amount"], 3000)
        self.assertEqual(metrics["avg_amount"], 1166.6666666666667)
    
    def test_invalid_amount_treated_as_zero(self):
        agg = MetricsAggregator()
        tx = Transaction({"amount_cents": "foo", "status": "completed"})
        agg.process_transaction(tx)
        
        metrics = agg.get_metrics()
        self.assertEqual(metrics["sum_completed_amount"], 0)
        self.assertEqual(metrics["avg_amount"], 0.0)
    
    def test_empty_aggregator(self):
        agg = MetricsAggregator()
        metrics = agg.get_metrics()
        
        self.assertEqual(metrics["total_rows"], 0)
        self.assertEqual(metrics["completed"], 0)
        self.assertEqual(metrics["failed"], 0)
        self.assertEqual(metrics["avg_amount"], 0.0)


class TestFormatters(unittest.TestCase):
    """Test formatter classes."""
    
    def setUp(self):
        self.metrics = {
            "total_rows": 5,
            "completed": 3,
            "failed": 2,
            "sum_completed_amount": 3500,
            "avg_amount": 700.0,
        }
    
    def test_text_formatter(self):
        output = TextFormatter.format(self.metrics)
        
        self.assertIn("Transaction report:", output)
        self.assertIn("total_rows: 5", output)
        self.assertIn("completed: 3", output)
        self.assertIn("failed: 2", output)
        self.assertIn("sum_completed_amount: 3500", output)
        self.assertIn("avg_amount: 700", output)
    
    def test_json_formatter(self):
        output = JSONFormatter.format(self.metrics, pretty=False)
        data = json.loads(output)
        
        self.assertEqual(data["total_rows"], 5)
        self.assertEqual(data["completed"], 3)
        self.assertEqual(data["sum_completed_amount"], 3500)
    
    def test_json_formatter_pretty(self):
        output = JSONFormatter.format(self.metrics, pretty=True)
        
        # Check it's valid JSON and formatted with newlines
        self.assertIn("\n", output)
        data = json.loads(output)
        self.assertEqual(data["total_rows"], 5)
    
    def test_get_formatter_text(self):
        formatter = get_formatter("text")
        self.assertEqual(formatter, TextFormatter)
    
    def test_get_formatter_json(self):
        formatter = get_formatter("json")
        self.assertEqual(formatter, JSONFormatter)
    
    def test_get_formatter_unknown(self):
        with self.assertRaises(ValueError):
            get_formatter("xml")


class TestBaselineAPI(unittest.TestCase):
    """Test baseline API compatibility with generate_report()."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)
    
    def test_generate_report_baseline(self):
        """Test that generate_report returns expected dict structure."""
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, "w", newline="") as f:
            f.write("id,timestamp,amount_cents,currency,status\n")
            f.write("1,2025-01-01T10:00:00Z,1000,USD,completed\n")
            f.write("2,2025-01-01T10:05:00Z,-500,USD,completed\n")
            f.write("3,2025-01-01T10:10:00Z,0,USD,failed\n")
            f.write("4,2025-01-01T10:15:00Z,2500,EUR,completed\n")
            f.write("5,2025-01-01T10:20:00Z,foo,USD,completed\n")
        
        report = generate_report(csv_path)
        
        # Check structure
        self.assertIn("total_rows", report)
        self.assertIn("completed", report)
        self.assertIn("failed", report)
        self.assertIn("sum_completed_amount", report)
        self.assertIn("avg_amount", report)
        
        # Check values match baseline
        self.assertEqual(report["total_rows"], 5)
        self.assertEqual(report["completed"], 4)
        self.assertEqual(report["failed"], 1)
        self.assertEqual(report["sum_completed_amount"], 3000)
        # avg = (1000 - 500 + 0 + 2500 + 0) / 5 = 3000 / 5 = 600
        self.assertEqual(report["avg_amount"], 600.0)
    
    def test_generate_report_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            generate_report("/nonexistent/file.csv")


class TestCLI(unittest.TestCase):
    """Test command-line interface."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(self.csv_path, "w", newline="") as f:
            f.write("id,timestamp,amount_cents,currency,status\n")
            f.write("1,2025-01-01T10:00:00Z,1000,USD,completed\n")
            f.write("2,2025-01-01T10:05:00Z,2000,USD,failed\n")
    
    def tearDown(self):
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)
    
    def test_cli_no_args(self):
        exit_code = main([])
        self.assertEqual(exit_code, 1)
    
    def test_cli_file_not_found(self):
        exit_code = main(["/nonexistent/file.csv"])
        self.assertEqual(exit_code, 2)
    
    def test_cli_text_format(self):
        """Capture stdout and verify text format output."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            exit_code = main([self.csv_path])
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        
        self.assertEqual(exit_code, 0)
        self.assertIn("Transaction report:", output)
        self.assertIn("total_rows: 2", output)
        self.assertIn("completed: 1", output)
        self.assertIn("failed: 1", output)
    
    def test_cli_json_format(self):
        """Test JSON output format."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            exit_code = main([self.csv_path, "--format", "json"])
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        
        self.assertEqual(exit_code, 0)
        data = json.loads(output)
        self.assertEqual(data["total_rows"], 2)
        self.assertEqual(data["completed"], 1)
    
    def test_cli_json_format_short_flag(self):
        """Test JSON output format with short flag."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            exit_code = main(["-f", "json", self.csv_path])
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        
        self.assertEqual(exit_code, 0)
        data = json.loads(output)
        self.assertEqual(data["total_rows"], 2)
    
    def test_cli_invalid_format(self):
        exit_code = main([self.csv_path, "--format", "xml"])
        self.assertEqual(exit_code, 3)


class TestIntegration(unittest.TestCase):
    """Integration tests using the sample_transactions.csv."""
    
    def setUp(self):
        self.csv_path = "examples/sample_transactions.csv"
    
    def test_sample_transactions_report(self):
        """Test generate_report with sample data."""
        if not os.path.exists(self.csv_path):
            self.skipTest(f"Sample file {self.csv_path} not found")
        
        report = generate_report(self.csv_path)
        
        # Verify expected structure
        self.assertIsInstance(report, dict)
        self.assertIn("total_rows", report)
        self.assertIn("completed", report)
        self.assertIn("failed", report)
        self.assertIn("sum_completed_amount", report)
        self.assertIn("avg_amount", report)
        
        # With sample data: 5 rows
        # Completed: rows 1, 2, 4, 5 (invalid amount treated as 0) = 4
        # Failed: row 3 = 1
        self.assertEqual(report["total_rows"], 5)
        self.assertEqual(report["completed"], 4)
        self.assertEqual(report["failed"], 1)
    
    def test_sample_transactions_full_report(self):
        """Test generate_full_report with sample data."""
        if not os.path.exists(self.csv_path):
            self.skipTest(f"Sample file {self.csv_path} not found")
        
        full_report = generate_full_report(self.csv_path)
        
        # Verify structure includes observability
        self.assertIn("metrics", full_report)
        self.assertIn("observability", full_report)
        self.assertIn("transactions_processed", full_report["observability"])
        
        # Metrics should be identical to generate_report
        report = generate_report(self.csv_path)
        self.assertEqual(full_report["metrics"], report)


if __name__ == "__main__":
    unittest.main()
