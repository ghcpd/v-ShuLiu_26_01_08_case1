"""Transaction CSV reader module.

Provides streaming-style reading of transaction CSV files with robust error handling.
"""
import csv
from typing import Iterator, Dict, Any, Optional


class Transaction:
    """Represents a single transaction with type-safe field access."""
    
    def __init__(self, row: Dict[str, str]):
        self.raw_row = row
    
    @property
    def id(self) -> Optional[str]:
        return self.raw_row.get("id")
    
    @property
    def timestamp(self) -> Optional[str]:
        return self.raw_row.get("timestamp")
    
    @property
    def amount_cents(self) -> int:
        """Parse amount_cents as int, return 0 if invalid."""
        raw = self.raw_row.get("amount_cents", "0").strip()
        try:
            return int(raw)
        except ValueError:
            return 0
    
    @property
    def currency(self) -> Optional[str]:
        return self.raw_row.get("currency")
    
    @property
    def status(self) -> str:
        return self.raw_row.get("status", "").strip()
    
    def __repr__(self) -> str:
        return (f"Transaction(id={self.id}, amount_cents={self.amount_cents}, "
                f"currency={self.currency}, status={self.status})")


class TransactionReader:
    """Streams transactions from a CSV file."""
    
    def __init__(self, csv_path: str):
        """Initialize reader for the given CSV file path.
        
        Args:
            csv_path: Path to the CSV file to read.
        """
        self.csv_path = csv_path
    
    def read(self) -> Iterator[Transaction]:
        """Stream transactions from the CSV file.
        
        Yields:
            Transaction objects parsed from CSV rows.
        
        Raises:
            FileNotFoundError: If the CSV file does not exist.
            ValueError: If the CSV is malformed.
        """
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError("CSV file is empty or has no header")
            
            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                if row is None:
                    continue
                yield Transaction(row)
    
    def read_all(self) -> list[Transaction]:
        """Read all transactions into a list.
        
        Returns:
            List of all Transaction objects from the CSV.
        """
        return list(self.read())
