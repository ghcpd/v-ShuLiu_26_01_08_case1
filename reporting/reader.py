"""CSV reader that streams transactions with minimal validation and observability."""
from __future__ import annotations
import csv
import time
from typing import Dict, Iterator, Optional


def stream_transactions(csv_path: str, observability: Optional[Dict[str, int]] = None) -> Iterator[Dict[str, str]]:
    """Yield rows from a CSV file as dicts.

    observability is a mutable dict that, if provided, will be updated with counters:
      - rows: total rows seen
      - malformed_rows: rows that caused an exception while reading
      - read_time_ms: elapsed time in milliseconds
    """
    start = time.perf_counter()
    if observability is not None:
        observability.setdefault("rows", 0)
        observability.setdefault("malformed_rows", 0)

    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    if observability is not None:
                        observability["rows"] += 1
                    yield row
                except Exception:
                    # If a specific row causes an error while iterating, count it but continue
                    if observability is not None:
                        observability["malformed_rows"] += 1
                    continue
    finally:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        if observability is not None:
            observability["read_time_ms"] = elapsed_ms
