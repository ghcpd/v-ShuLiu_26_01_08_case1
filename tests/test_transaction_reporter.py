import io
import json
import os
import unittest
from contextlib import redirect_stdout

import transaction_reporter


SAMPLE = os.path.join("examples", "sample_transactions.csv")


class TransactionReporterTests(unittest.TestCase):
    def test_generate_report_matches_baseline(self):
        r = transaction_reporter.generate_report(SAMPLE)
        self.assertEqual(r["total_rows"], 5)
        self.assertEqual(r["completed"], 4)
        self.assertEqual(r["failed"], 1)
        self.assertEqual(r["sum_completed_amount"], 3000)
        self.assertEqual(r["avg_amount"], 600.0)

    def test_structured_report_includes_meta(self):
        structured = transaction_reporter.generate_structured_report(SAMPLE)
        # meta.read should have counters including rows and invalid_amounts
        meta_read = structured.get("meta", {}).get("read", {})
        self.assertEqual(meta_read.get("rows"), 5)
        # The sample has one invalid amount (the 'foo' entry)
        self.assertEqual(meta_read.get("invalid_amounts"), 1)

    def test_cli_prints_text_summary(self):
        f = io.StringIO()
        with redirect_stdout(f):
            rc = transaction_reporter.main([SAMPLE])
        out = f.getvalue().strip()
        self.assertIn("Transaction report:", out)
        self.assertIn("total_rows: 5", out)
        self.assertEqual(rc, 0)

    def test_cli_json_output(self):
        f = io.StringIO()
        with redirect_stdout(f):
            rc = transaction_reporter.main(["--format", "json", SAMPLE])
        out = f.getvalue().strip()
        parsed = json.loads(out)
        self.assertIn("summary", parsed)
        self.assertEqual(parsed["summary"]["total_rows"], 5)
        self.assertEqual(rc, 0)

    def test_file_not_found(self):
        f = io.StringIO()
        with redirect_stdout(f):
            rc = transaction_reporter.main(["this-file-does-not-exist.csv"])
        out = f.getvalue().strip()
        self.assertIn("Error: file not found", out)
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
