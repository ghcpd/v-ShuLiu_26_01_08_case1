"""Transaction reporter - backwards compatible public API with improved internals.

This module preserves the original:

- generate_report(csv_path: str) -> dict   # same contract as before
- CLI: python transaction_reporter.py path/to/file.csv

But the implementation delegates to smaller components (reader, core, formatters)
so the code is easier to extend and can stream large CSV files.
"""
from __future__ import annotations

import sys
from typing import Dict, Any, Iterable

# Public surface remains in this module for backward compatibility.
from core import generate_structured_report  # convenience wrapper
from formatters import format_text, format_json


def generate_report(csv_path: str) -> Dict[str, Any]:
    """Backward-compatible API: return the same flat dict as the baseline.

    This delegates to the streaming implementation in `core.aggregate_transactions`
    but preserves the original return keys and semantics for well-formed input.
    """
    structured = generate_structured_report(csv_path)
    return structured["metrics"]


# Re-export the core implementation so callers can import the richer
# structured report directly from this module (convenience only).
# Example: `from transaction_reporter import generate_structured_report`
# The real implementation lives in `core.generate_structured_report`.
from core import generate_structured_report  # type: ignore


def _print_usage() -> None:
    print("Usage: python transaction_reporter.py <path_to_transactions_csv>")


def main(argv: Iterable[str] | None = None) -> int:
    """CLI entry point. New options are non-disruptive and opt-in.

    Default behavior (no flags) is unchanged.
    Exit codes:
      1 - usage error (no args)
      2 - file not found
      3 - other processing error
    """
    if argv is None:
        argv = sys.argv[1:]
    argv = list(argv)

    if not argv:
        _print_usage()
        return 1

    csv_path = argv[0]
    # Simple, opt-in CLI flags (do not change default behavior):
    fmt = "text"
    pretty = False
    show_diag = False

    if len(argv) > 1:
        # basic parsing so we don't add dependencies
        i = 1
        while i < len(argv):
            a = argv[i]
            if a in ("-f", "--format") and i + 1 < len(argv):
                fmt = argv[i + 1]
                i += 2
                continue
            if a == "--pretty":
                pretty = True
                i += 1
                continue
            if a == "--diagnostics":
                show_diag = True
                i += 1
                continue
            # unknown flag -> ignore (preserve backward compat)
            i += 1

    try:
        # Use the core streaming path
        from core import generate_structured_report as _gen_struct

        structured = _gen_struct(csv_path)
        if fmt == "json":
            out = format_json(structured, pretty=pretty)
        else:
            out = format_text(structured)

    except FileNotFoundError:
        print(f"Error: file not found: {csv_path}")
        return 2
    except Exception as e:
        print(f"Error while processing {csv_path}: {e}")
        return 3

    print(out)

    if show_diag:
        obs = structured.get("observability", {})
        print()
        print("Diagnostics:")
        for k, v in sorted(obs.items()):
            print(f"  {k}: {v}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
