import os
import json
import io
from contextlib import redirect_stdout

import transaction_reporter


HERE = os.path.dirname(__file__)
SAMPLE = os.path.join(HERE, "..", "examples", "sample_transactions.csv")


def test_generate_report_matches_expected():
    result = transaction_reporter.generate_report(SAMPLE)
    assert result["total_rows"] == 5
    assert result["completed"] == 4
    assert result["failed"] == 1
    assert result["sum_completed_amount"] == 3000
    assert result["avg_amount"] == 600.0


def test_structured_report_includes_observability():
    structured = transaction_reporter.generate_structured_report(SAMPLE)
    assert "metrics" in structured and "observability" in structured
    metrics = structured["metrics"]
    obs = structured["observability"]

    assert metrics["total_rows"] == 5
    # sample contains one non-integer amount ("foo")
    assert obs["invalid_amounts"] == 1
    assert obs["rows_read"] == 5
    assert obs["duration_seconds"] >= 0


def test_cli_default_text_output(capsys):
    # Call main with the sample path and capture stdout
    rc = transaction_reporter.main([SAMPLE])
    assert rc == 0
    captured = capsys.readouterr()
    expected = """Transaction report:
  total_rows: 5
  completed: 4
  failed: 1
  sum_completed_amount: 3000
  avg_amount: 600.0
"""
    assert captured.out == expected


def test_cli_json_output(capsys):
    rc = transaction_reporter.main([SAMPLE, "--format", "json"])
    assert rc == 0
    captured = capsys.readouterr()
    # parse the JSON and sanity-check keys/values
    parsed = json.loads(captured.out)
    assert "metrics" in parsed and "observability" in parsed
    assert parsed["metrics"]["total_rows"] == 5
    assert parsed["observability"]["invalid_amounts"] == 1


def test_cli_missing_file_returns_code_and_message(capsys):
    rc = transaction_reporter.main(["nonexistent.csv"])
    assert rc == 2
    captured = capsys.readouterr()
    assert "Error: file not found" in captured.out
