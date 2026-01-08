"""Transactions reporting package.

Exports a small set of helper modules for reading, aggregating and formatting
reports. The top-level `generate_report` exported by the repository's
`transaction_reporter.py` delegates into these modules.
"""
from .reader import stream_transactions
from .aggregator import compute_report
from .formatters import format_json, format_text

__all__ = ["stream_transactions", "compute_report", "format_json", "format_text"]
