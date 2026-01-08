import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

import transaction_reporter as tr


SAMPLE = os.path.join("examples", "sample_transactions.csv")


class TestTransactionReporter(unittest.TestCase):

    def test_generate_report_matches_baseline_on_sample(self):
        r = tr.generate_report(SAMPLE)
        expected = {
            "total_rows": 5,
            "completed": 4,
            "failed": 1,
            "sum_completed_amount": 3000,
            "avg_amount": 600.0,
        }
        self.assertEqual(r, expected)

    def test_cli_default_output_and_exit_code(self):
        f = io.StringIO()
        rc = None
        with redirect_stdout(f):
            rc = tr.main([SAMPLE])
        out = f.getvalue().strip()
        self.assertEqual(rc, 0)
        self.assertIn("Transaction report:", out)
        # Ensure default text contains the same numbers as the API
        self.assertIn("total_rows: 5", out)
        self.assertIn("sum_completed_amount: 3000", out)
        self.assertIn("avg_amount: 600.0", out)

    def test_cli_json_output(self):
        f = io.StringIO()
        with redirect_stdout(f):
            rc = tr.main([SAMPLE, "--format", "json"])
        self.assertEqual(rc, 0)
        out = f.getvalue().strip()
        parsed = json.loads(out)
        # JSON output should include the structured shape
        self.assertIn("metrics", parsed)
        self.assertEqual(parsed["metrics"]["total_rows"], 5)

    def test_missing_file_returns_code_2(self):
        f = io.StringIO()
        with redirect_stdout(f):
            rc = tr.main(["no-such-file.csv"])
        self.assertEqual(rc, 2)

    def test_malformed_amount_treated_as_zero_and_report_includes_invalid_count(self):
        # sample CSV already contains a malformed amount ("foo").
        structured = tr.generate_structured_report(SAMPLE)
        self.assertIn("observability", structured)
        self.assertIsInstance(structured["observability"].get("invalid_amounts"), int)
        self.assertGreaterEqual(structured["observability"]["invalid_amounts"], 1)

    def test_reader_is_streaming_like(self):
        # Ensure the reader yields rows without returning a list
        from reader import stream_transactions

        it = stream_transactions(SAMPLE)
        self.assertTrue(hasattr(it, "__iter__"))
        # consuming just one row should work
        first = next(it)
        self.assertIn("id", first)

    def test_generate_report_on_large_file_streams(self):
        # create a temporary large-ish CSV and ensure generate_report completes
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        try:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("id,timestamp,amount_cents,currency,status\n")
                for i in range(2000):
                    f.write(f"{i},2025-01-01T00:00:00Z,100,USD,completed\n")
            r = tr.generate_report(path)
            self.assertEqual(r["total_rows"], 2000)
            self.assertEqual(r["completed"], 2000)
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
