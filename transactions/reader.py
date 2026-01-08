"""CSV reader that streams transaction rows.

This module intentionally yields dictionaries and keeps minimal state so the
rest of the system can operate without loading the entire file into memory.
"""
from __future__ import annotations

import csv
from typing import Iterator, Dict


def stream_transactions(csv_path: str) -> Iterator[Dict[str, str]]:
    """Yield rows (as dicts) from a CSV file.

    Raises FileNotFoundError if the path does not exist. Rows are yielded as
    raw dictionaries of strings (like csv.DictReader). Malformed rows are
    emitted as-is (higher-level code is responsible for validation).
    """
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row
