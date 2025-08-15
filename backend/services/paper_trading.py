"""
Paper Trading Mode
Simulates trades without real money for testing strategies
"""

import logging
from typing import Dict, Optional
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)

class PaperWallet:
    """Simulated wallet for paper trading"""
    
    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.locked_balance = 0.0
        self.transactions = []
        self.positions = {}
        
    def get_balance(self) -> float:
        """Get current balance"""
        return self.balance
    
    def get_available_balance(self) -> float:
        """Get available balance (not locked in positions)"""
        return self.balance - self.locked_balance
    
    def lock_funds(self, amount: float, position_id: str) -> bool:
        """Lock funds for a position"""
        if amount > self.get_available_balance():
            return False
        
        self.locked_balance += amount
        self.positions[position_id] = amount
        
        self.transactions.append({
            'timestamp': datetime.now(),
            'type': 'lock',
            'amount': amount,
            'position_id': position_id,
            'balance_after': self.balance
        })
        
        logger.info(f"[Paper] Locked ${amount} for position {position_id}")
        return True
    
    def unlock_funds(self, position_id: str, exit_value: float) -> float:
        """Unlock funds and calculate P&L"""
        if position_id not in self.positions:
            return 0.0
        
        entry_value = self.positions[position_id]
        pnl = exit_value - entry_value
        
        # Update balances
        self.locked_balance -= entry_value
        self.balance += pnl
        
        del self.positions[position_id]
        
        self.transactions.append({
            'timestamp': datetime.now(),
            'type': 'unlock',
            'entry_value': entry_value,
            'exit_value': exit_value,
            'pnl': pnl,
            'position_id': position_id,
            'balance_after': self.balance
        })
        
        logger.info(f"[Paper] Closed position {position_id}: PnL ${pnl:.2f}")
        return pnl
    
    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics"""
        total_pnl = self.balance - self.initial_balance
        total_pnl_percent = (total_pnl / self.initial_balance) * 100
        
        winning_trades = [t for t in self.transactions if t.get('type') == 'unlock' and t.get('pnl', 0) > 0]
        losing_trades = [t for t in self.transactions if t.get('type') == 'unlock' and t.get('pnl', 0) <= 0]
        
        return {
            'initial_balance': self.initial_balance,
            'current_balance': self.balance,
            'total_pnl': total_pnl,
            'total_pnl_percent': total_pnl_percent,
            'total_trades': len(winning_trades) + len(losing_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / max(1, len(winning_trades) + len(losing_trades)),
            'active_positions': len(self.positions),
            'locked_balance': self.locked_balance
        }
    
    def reset(self):
        """Reset wallet to initial state"""
        self.balance = self.initial_balance
        self.locked_balance = 0.0
        self.transactions = []
        self.positions = {}
        logger.info("[Paper] Wallet reset to initial state")


class PaperTradingMode:
    """Wrapper to enable paper trading mode"""
    
    def __init__(self):
        self.enabled = False
        self.paper_wallet = None
        self.original_wallet = None
        self.trade_log = []
        
    def enable(self, initial_balance: float = 10000.0):
        """Enable paper trading mode"""
        from services.position_manager import position_manager
        
        # Save original wallet
        self.original_wallet = position_manager.wallet
        
        # Create paper wallet
        self.paper_wallet = PaperWallet(initial_balance)
        
        # Replace with paper wallet
        position_manager.wallet = self.paper_wallet
        
        self.enabled = True
        self.trade_log = []
        
        logger.info(f"[Paper Trading] Enabled with ${initial_balance} balance")
        
    def disable(self):
        """Disable paper trading and restore real wallet"""
        if not self.enabled:
            return
            
        from services.position_manager import position_manager
        
        # Restore original wallet
        if self.original_wallet:
            position_manager.wallet = self.original_wallet
        
        self.enabled = False
        
        # Log final performance
        if self.paper_wallet:
            metrics = self.paper_wallet.get_performance_metrics()
            logger.info(f"[Paper Trading] Final Performance: {metrics}")
        
        logger.info("[Paper Trading] Disabled")
    
    def log_trade(self, action: str, pool: str, amount: float, details: Dict):
        """Log a paper trade"""
        trade = {
            'timestamp': datetime.now(),
            'action': action,
            'pool': pool,
            'amount': amount,
            'details': details
        }
        self.trade_log.append(trade)
        
        logger.info(f"[Paper Trade] {action} {pool} ${amount}")
    
    def get_performance(self) -> Dict:
        """Get paper trading performance"""
        if not self.paper_wallet:
            return {}
        
        metrics = self.paper_wallet.get_performance_metrics()
        metrics['trade_count'] = len(self.trade_log)
        metrics['enabled'] = self.enabled
        
        return metrics
    
    def get_trade_log(self, limit: int = 50) -> list:
        """Get recent paper trades"""
        return self.trade_log[-limit:]
    
    def simulate_market_impact(self, amount: float, tvl: float) -> float:
        """Simulate slippage and market impact"""
        # Simple model: larger trades relative to TVL have more impact
        impact_ratio = amount / tvl if tvl > 0 else 0
        
        # Base slippage 0.3% + additional based on size
        slippage = 0.003 + (impact_ratio * 0.02)  # Up to 2% additional
        
        return min(slippage, 0.05)  # Cap at 5%
    
    def simulate_entry(self, pool_data: Dict, amount: float) -> Dict:
        """Simulate position entry with realistic conditions"""
        tvl = pool_data.get('tvl', 1000000)
        slippage = self.simulate_market_impact(amount, tvl)
        
        # Simulate gas costs (0.01 SOL = ~$1)
        gas_cost = 1.0
        
        # Effective entry amount after slippage and gas
        effective_amount = amount * (1 - slippage) - gas_cost
        
        return {
            'requested_amount': amount,
            'effective_amount': effective_amount,
            'slippage': slippage,
            'gas_cost': gas_cost,
            'entry_price_impact': slippage * 100  # As percentage
        }
    
    def simulate_exit(self, position: Dict, current_metrics: Dict) -> Dict:
        """Simulate position exit with IL and fees"""
        entry_value = position.get('entry_value', 0)
        apy = current_metrics.get('apy', 0)
        days_held = position.get('days_held', 1)
        
        # Calculate earned fees
        daily_rate = apy / 365 / 100
        fees_earned = entry_value * daily_rate * days_held
        
        # Simulate impermanent loss (simplified model)
        price_change = (current_metrics.get('price_change_24h', 0) / 100) * days_held
        il_factor = 0.5 * (price_change ** 2)  # Quadratic IL model
        il_loss = entry_value * il_factor
        
        # Exit value
        exit_value = entry_value + fees_earned - il_loss
        
        # Slippage on exit
        tvl = current_metrics.get('tvl', 1000000)
        exit_slippage = self.simulate_market_impact(exit_value, tvl)
        
        final_value = exit_value * (1 - exit_slippage) - 1.0  # Gas
        
        return {
            'entry_value': entry_value,
            'fees_earned': fees_earned,
            'impermanent_loss': il_loss,
            'exit_slippage': exit_slippage * 100,
            'gas_cost': 1.0,
            'final_value': final_value,
            'net_pnl': final_value - entry_value
        }

# Global paper trading instance
paper_trading = PaperTradingMode()