"""
Enhanced P&L Calculator with DeFi Strategist Formulas
Implements concentrated liquidity, multi-token positions, and gas tracking
"""
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np

@dataclass
class ConcentratedLiquidityPosition:
    """Concentrated liquidity position with price range"""
    token_a_amount: float
    token_b_amount: float
    price_lower: float
    price_upper: float
    current_price: float
    liquidity: float = 0
    
    def __post_init__(self):
        """Calculate liquidity value"""
        if self.liquidity == 0:
            self.liquidity = self._calculate_liquidity()
    
    def _calculate_liquidity(self) -> float:
        """Calculate liquidity based on amounts and price range"""
        sqrt_price_lower = math.sqrt(self.price_lower)
        sqrt_price_upper = math.sqrt(self.price_upper)
        sqrt_current = math.sqrt(self.current_price)
        
        if self.current_price <= self.price_lower:
            # All in token B
            return self.token_b_amount / (sqrt_price_upper - sqrt_price_lower)
        elif self.current_price >= self.price_upper:
            # All in token A
            return self.token_a_amount * sqrt_price_upper * sqrt_price_lower / (sqrt_price_upper - sqrt_price_lower)
        else:
            # In range - use current amounts
            L_from_a = self.token_a_amount * sqrt_current * sqrt_price_upper / (sqrt_price_upper - sqrt_current)
            L_from_b = self.token_b_amount / (sqrt_current - sqrt_price_lower)
            return min(L_from_a, L_from_b)
    
    def get_amounts_at_price(self, price: float) -> Tuple[float, float]:
        """Get token amounts at a specific price"""
        sqrt_price = math.sqrt(price)
        sqrt_price_lower = math.sqrt(self.price_lower)
        sqrt_price_upper = math.sqrt(self.price_upper)
        
        if price <= self.price_lower:
            # All in token B
            amount_a = 0
            amount_b = self.liquidity * (sqrt_price_upper - sqrt_price_lower)
        elif price >= self.price_upper:
            # All in token A
            amount_a = self.liquidity * (sqrt_price_upper - sqrt_price_lower) / (sqrt_price_upper * sqrt_price_lower)
            amount_b = 0
        else:
            # In range
            amount_a = self.liquidity * (sqrt_price_upper - sqrt_price) / (sqrt_price * sqrt_price_upper)
            amount_b = self.liquidity * (sqrt_price - sqrt_price_lower)
            
        return amount_a, amount_b

@dataclass
class MultiTokenPosition:
    """Position with multiple tokens (3+)"""
    tokens: Dict[str, float]  # token_symbol -> amount
    prices: Dict[str, float]   # token_symbol -> price_usd
    weights: Dict[str, float]  # token_symbol -> target_weight (sum to 1.0)
    
    def get_total_value(self) -> float:
        """Calculate total position value in USD"""
        return sum(amount * self.prices.get(token, 0) 
                  for token, amount in self.tokens.items())
    
    def get_rebalance_trades(self) -> Dict[str, float]:
        """Calculate trades needed to rebalance to target weights"""
        total_value = self.get_total_value()
        trades = {}
        
        for token, target_weight in self.weights.items():
            current_value = self.tokens.get(token, 0) * self.prices.get(token, 0)
            target_value = total_value * target_weight
            value_diff = target_value - current_value
            
            if abs(value_diff) > 0.01:  # Only rebalance if difference > $0.01
                trades[token] = value_diff / self.prices.get(token, 1)
                
        return trades

@dataclass 
class GasTracker:
    """Track gas costs on Solana"""
    transactions: List[Dict] = field(default_factory=list)
    sol_price: float = 100.0  # Current SOL price
    
    def add_transaction(self, signature: str, fee_lamports: int, description: str):
        """Add a transaction with gas cost"""
        self.transactions.append({
            "signature": signature,
            "timestamp": datetime.now(),
            "fee_lamports": fee_lamports,
            "fee_sol": fee_lamports / 1e9,
            "fee_usd": (fee_lamports / 1e9) * self.sol_price,
            "description": description
        })
    
    def get_total_gas_usd(self) -> float:
        """Get total gas spent in USD"""
        return sum(tx["fee_usd"] for tx in self.transactions)
    
    def get_gas_by_period(self, days: int = 30) -> float:
        """Get gas spent in the last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        return sum(tx["fee_usd"] for tx in self.transactions 
                  if tx["timestamp"] > cutoff)

@dataclass
class HistoricalPnL:
    """Track P&L over time"""
    snapshots: List[Dict] = field(default_factory=list)
    
    def add_snapshot(self, pnl_data: Dict):
        """Add a P&L snapshot"""
        self.snapshots.append({
            "timestamp": datetime.now(),
            "data": pnl_data
        })
    
    def get_pnl_series(self, metric: str = "net_pnl_usd") -> List[Tuple[datetime, float]]:
        """Get time series of a specific metric"""
        return [(s["timestamp"], s["data"].get(metric, 0)) 
                for s in self.snapshots]
    
    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio from historical returns"""
        if len(self.snapshots) < 2:
            return 0
            
        returns = []
        for i in range(1, len(self.snapshots)):
            prev_value = self.snapshots[i-1]["data"].get("total_value", 1)
            curr_value = self.snapshots[i]["data"].get("total_value", 1)
            if prev_value > 0:
                returns.append((curr_value - prev_value) / prev_value)
        
        if not returns:
            return 0
            
        returns_array = np.array(returns)
        mean_return = np.mean(returns_array) * 365  # Annualized
        std_return = np.std(returns_array) * np.sqrt(365)  # Annualized
        
        if std_return == 0:
            return 0
            
        return (mean_return - risk_free_rate) / std_return

class EnhancedPnLCalculator:
    """Enhanced P&L calculator with advanced DeFi features"""
    
    def __init__(self):
        self.gas_tracker = GasTracker()
        self.historical_pnl = HistoricalPnL()
    
    def calculate_concentrated_liquidity_pnl(
        self,
        position: ConcentratedLiquidityPosition,
        entry_price: float,
        fees_earned_usd: float = 0
    ) -> Dict:
        """Calculate P&L for concentrated liquidity position"""
        # Get current amounts
        current_a, current_b = position.get_amounts_at_price(position.current_price)
        
        # Get entry amounts
        entry_position = ConcentratedLiquidityPosition(
            token_a_amount=position.token_a_amount,
            token_b_amount=position.token_b_amount,
            price_lower=position.price_lower,
            price_upper=position.price_upper,
            current_price=entry_price,
            liquidity=position.liquidity
        )
        entry_a, entry_b = entry_position.get_amounts_at_price(entry_price)
        
        # Calculate values (assuming token B is USD-pegged)
        entry_value = entry_a * entry_price + entry_b
        current_value = current_a * position.current_price + current_b
        
        # Value if just held
        held_value = position.token_a_amount * position.current_price + position.token_b_amount
        
        # Impermanent loss
        il_usd = held_value - current_value
        il_percent = (il_usd / entry_value * 100) if entry_value > 0 else 0
        
        # Net P&L
        net_pnl = current_value - entry_value + fees_earned_usd - self.gas_tracker.get_total_gas_usd()
        net_pnl_percent = (net_pnl / entry_value * 100) if entry_value > 0 else 0
        
        # Check if position is in range
        in_range = position.price_lower <= position.current_price <= position.price_upper
        
        return {
            "entry_value": entry_value,
            "current_value": current_value,
            "held_value": held_value,
            "impermanent_loss_usd": il_usd,
            "impermanent_loss_percent": il_percent,
            "fees_earned_usd": fees_earned_usd,
            "gas_spent_usd": self.gas_tracker.get_total_gas_usd(),
            "net_pnl_usd": net_pnl,
            "net_pnl_percent": net_pnl_percent,
            "in_range": in_range,
            "current_amounts": {"token_a": current_a, "token_b": current_b}
        }
    
    def calculate_multi_token_pnl(
        self,
        entry_position: MultiTokenPosition,
        current_position: MultiTokenPosition,
        fees_earned: Dict[str, float]
    ) -> Dict:
        """Calculate P&L for multi-token position"""
        # Entry and current values
        entry_value = entry_position.get_total_value()
        current_value = current_position.get_total_value()
        
        # Value if just held (no rebalancing)
        held_value = sum(
            entry_position.tokens.get(token, 0) * current_position.prices.get(token, 0)
            for token in entry_position.tokens
        )
        
        # Fees in USD
        fees_usd = sum(
            amount * current_position.prices.get(token, 0)
            for token, amount in fees_earned.items()
        )
        
        # Impermanent loss (from rebalancing)
        il_usd = held_value - current_value
        il_percent = (il_usd / entry_value * 100) if entry_value > 0 else 0
        
        # Net P&L
        gas_costs = self.gas_tracker.get_total_gas_usd()
        net_pnl = current_value - entry_value + fees_usd - gas_costs
        net_pnl_percent = (net_pnl / entry_value * 100) if entry_value > 0 else 0
        
        # Token-by-token breakdown
        token_pnl = {}
        for token in set(entry_position.tokens.keys()) | set(current_position.tokens.keys()):
            entry_amount = entry_position.tokens.get(token, 0)
            current_amount = current_position.tokens.get(token, 0)
            entry_price = entry_position.prices.get(token, 0)
            current_price = current_position.prices.get(token, 0)
            
            token_pnl[token] = {
                "amount_change": current_amount - entry_amount,
                "price_change_percent": ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0,
                "value_change_usd": (current_amount * current_price) - (entry_amount * entry_price)
            }
        
        return {
            "entry_value": entry_value,
            "current_value": current_value,
            "held_value": held_value,
            "impermanent_loss_usd": il_usd,
            "impermanent_loss_percent": il_percent,
            "fees_earned_usd": fees_usd,
            "gas_spent_usd": gas_costs,
            "net_pnl_usd": net_pnl,
            "net_pnl_percent": net_pnl_percent,
            "token_breakdown": token_pnl,
            "rebalance_needed": current_position.get_rebalance_trades()
        }
    
    def calculate_historical_metrics(self) -> Dict:
        """Calculate historical performance metrics"""
        if len(self.historical_pnl.snapshots) < 2:
            return {"error": "Insufficient historical data"}
        
        # Get P&L series
        pnl_series = self.historical_pnl.get_pnl_series("net_pnl_percent")
        
        # Calculate metrics
        returns = [pnl_series[i][1] - pnl_series[i-1][1] 
                  for i in range(1, len(pnl_series))]
        
        max_pnl = max(p[1] for p in pnl_series)
        min_pnl = min(p[1] for p in pnl_series)
        current_pnl = pnl_series[-1][1] if pnl_series else 0
        
        # Max drawdown
        max_drawdown = 0
        peak = pnl_series[0][1]
        for _, pnl in pnl_series:
            if pnl > peak:
                peak = pnl
            drawdown = (peak - pnl) / peak if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
        
        # Win rate
        profitable_days = sum(1 for r in returns if r > 0)
        win_rate = profitable_days / len(returns) if returns else 0
        
        return {
            "total_return_percent": current_pnl,
            "max_return_percent": max_pnl,
            "min_return_percent": min_pnl,
            "max_drawdown_percent": max_drawdown * 100,
            "sharpe_ratio": self.historical_pnl.calculate_sharpe_ratio(),
            "win_rate": win_rate,
            "average_daily_return": np.mean(returns) if returns else 0,
            "volatility": np.std(returns) if returns else 0,
            "days_tracked": len(self.historical_pnl.snapshots)
        }
    
    def should_rebalance_concentrated_liquidity(
        self,
        position: ConcentratedLiquidityPosition,
        rebalance_threshold: float = 0.8
    ) -> Tuple[bool, str]:
        """Determine if concentrated liquidity position needs rebalancing"""
        price = position.current_price
        
        # Check if price is near range boundaries
        range_size = position.price_upper - position.price_lower
        distance_to_lower = price - position.price_lower
        distance_to_upper = position.price_upper - price
        
        # Calculate position in range (0 = at lower bound, 1 = at upper bound)
        position_in_range = distance_to_lower / range_size
        
        if price <= position.price_lower:
            return True, "Price below range - all assets in token B"
        elif price >= position.price_upper:
            return True, "Price above range - all assets in token A"
        elif position_in_range <= (1 - rebalance_threshold):
            return True, f"Price near lower bound ({position_in_range:.1%} from lower)"
        elif position_in_range >= rebalance_threshold:
            return True, f"Price near upper bound ({position_in_range:.1%} from lower)"
        
        return False, f"Position healthy - {position_in_range:.1%} in range"
    
    def optimize_range_for_fees(
        self,
        current_price: float,
        volatility: float,
        fee_tier: float
    ) -> Tuple[float, float]:
        """Calculate optimal price range for fee generation"""
        # Wider range for high volatility, narrower for stable pairs
        # This is a simplified model - real optimization would use historical data
        
        if fee_tier <= 0.0005:  # 0.05% - stable pairs
            range_multiplier = 0.005  # ±0.5% range
        elif fee_tier <= 0.003:   # 0.3% - standard pairs
            range_multiplier = 0.02 + (volatility * 0.1)  # Dynamic based on volatility
        else:  # 1% - volatile pairs
            range_multiplier = 0.05 + (volatility * 0.2)
        
        price_lower = current_price * (1 - range_multiplier)
        price_upper = current_price * (1 + range_multiplier)
        
        return price_lower, price_upper