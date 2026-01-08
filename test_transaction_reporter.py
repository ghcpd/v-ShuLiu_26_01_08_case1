import unittest
import sys
import os
import io
from contextlib import redirect_stdout, redirect_stderr

# Add the current directory to sys.path to import transaction_reporter
sys.path.insert(0, os.path.dirname(__file__))

from transaction_reporter import generate_report, generate_full_report, main, Report


class TestTransactionReporter(unittest.TestCase):

    def setUp(self):
        self.sample_csv = "examples/sample_transactions.csv"

    def test_generate_report(self):
        report = generate_report(self.sample_csv)
        expected = {
            "total_rows": 5,
            "completed": 4,  # ids 1,2,4,5
            "failed": 1,     # id 3
            "sum_completed_amount": 3000,  # 1000 + (-500) + 2500 + 0 = 3000
            "avg_amount": 600.0,  # (1000-500+0+2500+0)/5 = 3000/5
        }
        self.assertEqual(report, expected)

    def test_generate_full_report(self):
        report = generate_full_report(self.sample_csv)
        self.assertIsInstance(report, Report)
        self.assertIn("total_rows", report.aggregates)
        self.assertEqual(report.aggregates["total_rows"], 5)

    def test_main_text_output(self):
        # Test CLI with text format (default)
        with redirect_stdout(io.StringIO()) as stdout, redirect_stderr(io.StringIO()) as stderr:
            exit_code = main([self.sample_csv])
        self.assertEqual(exit_code, 0)
        output = stdout.getvalue()
        self.assertIn("Transaction report:", output)
        self.assertIn("total_rows: 5", output)

    def test_main_json_output(self):
        # Test CLI with JSON format
        with redirect_stdout(io.StringIO()) as stdout, redirect_stderr(io.StringIO()) as stderr:
            exit_code = main([self.sample_csv, "--format", "json"])
        self.assertEqual(exit_code, 0)
        output = stdout.getvalue()
        import json
        data = json.loads(output)
        self.assertEqual(data["total_rows"], 5)

    def test_main_file_not_found(self):
        with redirect_stdout(io.StringIO()) as stdout, redirect_stderr(io.StringIO()) as stderr:
            exit_code = main(["nonexistent.csv"])
        self.assertEqual(exit_code, 2)
        error_output = stderr.getvalue()
        self.assertIn("file not found", error_output)

    def test_main_no_args(self):
        # Test CLI with no arguments
        try:
            exit_code = main([])
        except SystemExit as e:
            exit_code = e.code
        self.assertEqual(exit_code, 2)


if __name__ == "__main__":
    unittest.main()