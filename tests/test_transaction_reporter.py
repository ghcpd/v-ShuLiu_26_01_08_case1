import os
import sys
import subprocess
import json
import unittest

from transaction_reporter import generate_report

BASE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(BASE, os.pardir))
SAMPLE = os.path.join(ROOT, "examples", "sample_transactions.csv")


class TransactionReporterTests(unittest.TestCase):
    def test_generate_report_matches_expected(self):
        expected = {
            "total_rows": 5,
            "completed": 4,
            "failed": 1,
            "sum_completed_amount": 3000,
            "avg_amount": 600.0,
        }
        got = generate_report(SAMPLE)
        self.assertEqual(got, expected)

    def test_cli_default_output(self):
        # Run the script with the sample file and capture stdout
        p = subprocess.run([sys.executable, os.path.join(ROOT, "transaction_reporter.py"), SAMPLE], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        expected_lines = [
            "Transaction report:",
            "  total_rows: 5",
            "  completed: 4",
            "  failed: 1",
            "  sum_completed_amount: 3000",
            "  avg_amount: 600.0",
        ]
        out = p.stdout.strip().splitlines()
        self.assertEqual(out, expected_lines)

    def test_cli_json_output(self):
        p = subprocess.run([sys.executable, os.path.join(ROOT, "transaction_reporter.py"), SAMPLE, "-f", "json"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        # parse the JSON and verify keys
        parsed = json.loads(p.stdout)
        self.assertIn("summary", parsed)
        self.assertEqual(parsed["summary"]["total_rows"], 5)
        self.assertEqual(parsed["summary"]["completed"], 4)

    def test_missing_file_returns_error(self):
        p = subprocess.run([sys.executable, os.path.join(ROOT, "transaction_reporter.py"), os.path.join(ROOT, "no_such_file.csv")], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertIn("Error: file not found", p.stdout)


if __name__ == "__main__":
    unittest.main()
