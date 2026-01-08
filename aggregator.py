"""Metrics aggregation module.

Computes transaction statistics from an iterator of transactions.
"""
from typing import Iterator, Dict, Any
from reader import Transaction


class MetricsAggregator:
    """Aggregates transaction metrics with streaming support."""
    
    def __init__(self):
        """Initialize a fresh aggregator."""
        self.total_rows = 0
        self.completed = 0
        self.failed = 0
        self.sum_completed_amount = 0
        self.sum_all_amount = 0
        self.transactions_processed = 0
    
    def process_transaction(self, transaction: Transaction) -> None:
        """Process a single transaction and update metrics.
        
        Args:
            transaction: Transaction object to process.
        """
        self.total_rows += 1
        self.transactions_processed += 1
        
        amount = transaction.amount_cents
        self.sum_all_amount += amount
        
        if transaction.status == "completed":
            self.completed += 1
            self.sum_completed_amount += amount
        elif transaction.status == "failed":
            self.failed += 1
    
    def process_transactions(self, transactions: Iterator[Transaction]) -> None:
        """Process multiple transactions from an iterator.
        
        Args:
            transactions: Iterator of Transaction objects.
        """
        for transaction in transactions:
            self.process_transaction(transaction)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Return computed metrics as a dict.
        
        Returns:
            Dict with keys: total_rows, completed, failed, sum_completed_amount, avg_amount.
        """
        avg_amount = self.sum_all_amount / self.total_rows if self.total_rows > 0 else 0.0
        
        return {
            "total_rows": self.total_rows,
            "completed": self.completed,
            "failed": self.failed,
            "sum_completed_amount": self.sum_completed_amount,
            "avg_amount": avg_amount,
        }
    
    def get_full_report(self) -> Dict[str, Any]:
        """Return a full structured report with metadata.
        
        Returns:
            Dict containing metrics and observability data.
        """
        metrics = self.get_metrics()
        return {
            "metrics": metrics,
            "observability": {
                "transactions_processed": self.transactions_processed,
            }
        }
