"""Mock wallet service for testing position management and tracking performance."""

from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import os
from uuid import uuid4


class TransactionType(Enum):
    """Types of wallet transactions."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    POSITION_ENTRY = "position_entry"
    POSITION_EXIT = "position_exit"
    FEE = "fee"
    REWARD = "reward"


@dataclass
class Transaction:
    """Represents a wallet transaction."""
    id: str
    timestamp: datetime
    type: TransactionType
    amount: float
    balance_after: float
    position_id: Optional[str] = None
    description: str = ""
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert transaction to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "type": self.type.value,
            "amount": self.amount,
            "balance_after": self.balance_after,
            "position_id": self.position_id,
            "description": self.description,
            "metadata": self.metadata
        }


@dataclass
class PerformanceMetrics:
    """Wallet performance metrics."""
    total_pnl: float = 0.0
    total_pnl_percentage: float = 0.0
    winning_positions: int = 0
    losing_positions: int = 0
    total_positions: int = 0
    win_rate: float = 0.0
    best_position_pnl: float = 0.0
    worst_position_pnl: float = 0.0
    avg_position_pnl: float = 0.0
    total_fees_paid: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert metrics to dictionary."""
        return {
            "total_pnl": self.total_pnl,
            "total_pnl_percentage": self.total_pnl_percentage,
            "winning_positions": self.winning_positions,
            "losing_positions": self.losing_positions,
            "total_positions": self.total_positions,
            "win_rate": self.win_rate,
            "best_position_pnl": self.best_position_pnl,
            "worst_position_pnl": self.worst_position_pnl,
            "avg_position_pnl": self.avg_position_pnl,
            "total_fees_paid": self.total_fees_paid
        }


class MockWalletService:
    """Mock wallet service for testing."""
    
    def __init__(self, initial_balance: float = 10000.0):
        """Initialize wallet with starting balance."""
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.transactions: List[Transaction] = []
        self.position_pnl: Dict[str, float] = {}  # Track P&L per position
        
        # Add initial deposit transaction
        self._add_transaction(
            TransactionType.DEPOSIT,
            initial_balance,
            description="Initial deposit"
        )
    
    def _add_transaction(
        self,
        transaction_type: TransactionType,
        amount: float,
        position_id: Optional[str] = None,
        description: str = "",
        metadata: Dict = None
    ) -> Transaction:
        """Add a transaction to the wallet."""
        transaction = Transaction(
            id=str(uuid4()),
            timestamp=datetime.utcnow(),
            type=transaction_type,
            amount=amount,
            balance_after=self.balance,
            position_id=position_id,
            description=description,
            metadata=metadata or {}
        )
        self.transactions.append(transaction)
        return transaction
    
    def get_balance(self) -> float:
        """Get current wallet balance."""
        return self.balance
    
    def get_available_balance(self) -> float:
        """Get available balance (same as balance for mock wallet)."""
        return self.balance
    
    def enter_position(
        self,
        position_id: str,
        amount: float,
        pool_name: str,
        apy: float
    ) -> bool:
        """Enter a position with the specified amount."""
        if amount > self.balance:
            return False
        
        # Deduct amount from balance
        self.balance -= amount
        
        # Record transaction
        self._add_transaction(
            TransactionType.POSITION_ENTRY,
            -amount,
            position_id=position_id,
            description=f"Enter position: {pool_name}",
            metadata={"pool_name": pool_name, "apy": apy}
        )
        
        # Initialize P&L tracking for this position
        self.position_pnl[position_id] = 0.0
        
        return True
    
    def exit_position(
        self,
        position_id: str,
        amount: float,
        pnl: float,
        pool_name: str
    ) -> bool:
        """Exit a position and realize P&L."""
        # Add amount back to balance (including P&L)
        total_return = amount + pnl
        self.balance += total_return
        
        # Record transaction
        self._add_transaction(
            TransactionType.POSITION_EXIT,
            total_return,
            position_id=position_id,
            description=f"Exit position: {pool_name} (P&L: ${pnl:.2f})",
            metadata={"pool_name": pool_name, "pnl": pnl, "original_amount": amount}
        )
        
        # Update position P&L tracking
        if position_id in self.position_pnl:
            self.position_pnl[position_id] = pnl
        
        return True
    
    def pay_fee(self, amount: float, description: str = "Transaction fee") -> bool:
        """Pay a fee from the wallet."""
        if amount > self.balance:
            return False
        
        self.balance -= amount
        self._add_transaction(
            TransactionType.FEE,
            -amount,
            description=description
        )
        return True
    
    def add_reward(self, amount: float, description: str = "Reward earned"):
        """Add a reward to the wallet."""
        self.balance += amount
        self._add_transaction(
            TransactionType.REWARD,
            amount,
            description=description
        )
    
    def get_transactions(
        self,
        limit: int = 50,
        offset: int = 0,
        position_id: Optional[str] = None
    ) -> List[Transaction]:
        """Get transaction history."""
        transactions = self.transactions
        
        if position_id:
            transactions = [t for t in transactions if t.position_id == position_id]
        
        # Sort by timestamp descending (newest first)
        transactions = sorted(transactions, key=lambda t: t.timestamp, reverse=True)
        
        return transactions[offset:offset + limit]
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """Calculate and return performance metrics."""
        metrics = PerformanceMetrics()
        
        # Calculate total P&L
        metrics.total_pnl = self.balance - self.initial_balance
        metrics.total_pnl_percentage = (metrics.total_pnl / self.initial_balance) * 100
        
        # Analyze positions
        position_pnls = list(self.position_pnl.values())
        if position_pnls:
            metrics.total_positions = len(position_pnls)
            metrics.winning_positions = sum(1 for pnl in position_pnls if pnl > 0)
            metrics.losing_positions = sum(1 for pnl in position_pnls if pnl < 0)
            metrics.win_rate = (metrics.winning_positions / metrics.total_positions) * 100
            metrics.best_position_pnl = max(position_pnls)
            metrics.worst_position_pnl = min(position_pnls)
            metrics.avg_position_pnl = sum(position_pnls) / len(position_pnls)
        
        # Calculate total fees
        metrics.total_fees_paid = abs(sum(
            t.amount for t in self.transactions if t.type == TransactionType.FEE
        ))
        
        return metrics
    
    def get_balance_history(self, days: int = 30) -> List[Dict]:
        """Get balance history over time."""
        # For mock purposes, return current balance as constant
        # In a real implementation, this would track balance changes over time
        return [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "balance": self.balance
            }
        ]
    
    def reset(self):
        """Reset wallet to initial state."""
        self.balance = self.initial_balance
        self.transactions = []
        self.position_pnl = {}
        
        # Add initial deposit transaction
        self._add_transaction(
            TransactionType.DEPOSIT,
            self.initial_balance,
            description="Initial deposit"
        )
    
    def to_dict(self) -> Dict:
        """Export wallet state as dictionary."""
        return {
            "balance": self.balance,
            "initial_balance": self.initial_balance,
            "transaction_count": len(self.transactions),
            "performance": self.get_performance_metrics().to_dict()
        }


# Global wallet instance
_wallet_instance: Optional[MockWalletService] = None


def get_wallet() -> MockWalletService:
    """Get or create the global wallet instance."""
    global _wallet_instance
    if _wallet_instance is None:
        _wallet_instance = MockWalletService()
    return _wallet_instance


def reset_wallet():
    """Reset the global wallet instance."""
    global _wallet_instance
    if _wallet_instance:
        _wallet_instance.reset()