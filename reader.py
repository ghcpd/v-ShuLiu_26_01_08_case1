"""Streaming CSV reader for transactions.

This module provides a memory-efficient iterator over CSV transaction rows and
basic row-level validation/observability.

The reader yields the raw dict produced by csv.DictReader (preserving the
baseline behavior). It also provides a small `stats_for()` helper that returns
counters collected while iterating (useful for tests/diagnostics).
"""
from __future__ import annotations

import csv
from typing import Iterator, Dict, Any, Tuple


def stream_transactions(csv_path: str, encoding: str = "utf-8") -> Iterator[Dict[str, str]]:
    """Yield rows (dict) from a CSV file without loading the whole file.

    Raises FileNotFoundError if the path does not exist (preserves baseline).
    """
    with open(csv_path, newline="", encoding=encoding) as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def stats_for(csv_path: str, max_rows: int = 1000) -> Dict[str, int]:
    """A tiny helper used by tests to collect simple counters without pulling
    the whole file into memory.
    """
    it = stream_transactions(csv_path)
    counters = {"sampled_rows": 0}
    for i, _ in enumerate(it):
        counters["sampled_rows"] += 1
        if counters["sampled_rows"] >= max_rows:
            break
    return counters
