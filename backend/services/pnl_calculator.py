from typing import Dict, Tuple, Optional
from decimal import Decimal
from dataclasses import dataclass
import math

@dataclass
class ImpermanentLossResult:
    """Result of IL calculation"""
    il_percent: float
    il_usd: float
    current_value_if_held: float
    current_value_in_pool: float
    
@dataclass
class PnLResult:
    """Complete P&L calculation result"""
    # Values
    current_value_usd: float
    initial_value_usd: float
    
    # Fees
    fees_earned_usd: float
    
    # Impermanent Loss
    impermanent_loss_usd: float
    impermanent_loss_percent: float
    
    # Net P&L
    gross_pnl_usd: float  # Without fees
    net_pnl_usd: float    # With fees
    net_pnl_percent: float
    
    # Breakdown
    price_change_pnl: float  # P&L from price changes
    
    # Time metrics
    break_even_days: Optional[float] = None
    current_apy: Optional[float] = None

@dataclass
class BreakEvenResult:
    """Break-even calculation result"""
    days_to_break_even: float
    fees_needed_usd: float
    daily_fees_usd: float
    is_profitable_now: bool


class PnLCalculator:
    """Calculate profit/loss including impermanent loss for liquidity positions"""
    
    def calculate_impermanent_loss(
        self,
        entry_price_a: float,
        entry_price_b: float,
        current_price_a: float,
        current_price_b: float,
        entry_amount_a: float,
        entry_amount_b: float
    ) -> ImpermanentLossResult:
        """
        Calculate impermanent loss for a liquidity position
        
        Formula: IL = 2 * sqrt(price_ratio) / (1 + price_ratio) - 1
        """
        # Calculate initial value
        initial_value = (entry_amount_a * entry_price_a) + (entry_amount_b * entry_price_b)
        
        # Calculate price ratio change
        initial_ratio = entry_price_a / entry_price_b
        current_ratio = current_price_a / current_price_b
        price_ratio_change = current_ratio / initial_ratio
        
        # Calculate IL percentage using the standard formula
        if price_ratio_change > 0:
            sqrt_ratio = math.sqrt(price_ratio_change)
            il_factor = 2 * sqrt_ratio / (1 + price_ratio_change)
            il_percent = (il_factor - 1) * 100
        else:
            il_percent = -100  # Total loss
        
        # Calculate what the value would be if just held
        value_if_held = (entry_amount_a * current_price_a) + (entry_amount_b * current_price_b)
        
        # Calculate current value in pool (with IL applied)
        # When prices change, the pool rebalances to maintain k = x * y
        k = entry_amount_a * entry_amount_b
        
        # New amounts after rebalancing
        new_amount_a = math.sqrt(k * current_price_b / current_price_a)
        new_amount_b = math.sqrt(k * current_price_a / current_price_b)
        
        current_value_in_pool = (new_amount_a * current_price_a) + (new_amount_b * current_price_b)
        
        # IL in USD
        il_usd = value_if_held - current_value_in_pool
        
        return ImpermanentLossResult(
            il_percent=il_percent,
            il_usd=il_usd,
            current_value_if_held=value_if_held,
            current_value_in_pool=current_value_in_pool
        )
    
    def calculate_fees_earned(
        self,
        pool_volume_24h: float,
        pool_tvl: float,
        position_share: float,
        fee_tier: float = 0.0025  # 0.25% default for most pools
    ) -> float:
        """
        Calculate estimated fees earned based on pool volume and position share
        """
        if pool_tvl <= 0:
            return 0
        
        # Daily fees = volume * fee_tier * position_share
        daily_fees = pool_volume_24h * fee_tier * position_share
        
        return daily_fees
    
    def calculate_position_share(
        self,
        position_value: float,
        pool_tvl: float
    ) -> float:
        """Calculate position's share of the pool"""
        if pool_tvl <= 0:
            return 0
        return position_value / pool_tvl
    
    def calculate_net_pnl(
        self,
        entry_price_a: float,
        entry_price_b: float,
        current_price_a: float,
        current_price_b: float,
        entry_amount_a: float,
        entry_amount_b: float,
        fees_earned_a: float,
        fees_earned_b: float,
        current_apy: Optional[float] = None
    ) -> PnLResult:
        """
        Calculate complete P&L including fees and impermanent loss
        """
        # Calculate initial value
        initial_value = (entry_amount_a * entry_price_a) + (entry_amount_b * entry_price_b)
        
        # Calculate IL
        il_result = self.calculate_impermanent_loss(
            entry_price_a, entry_price_b,
            current_price_a, current_price_b,
            entry_amount_a, entry_amount_b
        )
        
        # Calculate fees earned in USD
        fees_usd = (fees_earned_a * current_price_a) + (fees_earned_b * current_price_b)
        
        # Current value (with IL) + fees
        current_value_with_fees = il_result.current_value_in_pool + fees_usd
        
        # Gross P&L (without fees)
        gross_pnl = il_result.current_value_in_pool - initial_value
        
        # Net P&L (with fees)
        net_pnl = current_value_with_fees - initial_value
        net_pnl_percent = (net_pnl / initial_value) * 100 if initial_value > 0 else 0
        
        # Price change P&L (if just held)
        price_change_pnl = il_result.current_value_if_held - initial_value
        
        return PnLResult(
            current_value_usd=current_value_with_fees,
            initial_value_usd=initial_value,
            fees_earned_usd=fees_usd,
            impermanent_loss_usd=il_result.il_usd,
            impermanent_loss_percent=il_result.il_percent,
            gross_pnl_usd=gross_pnl,
            net_pnl_usd=net_pnl,
            net_pnl_percent=net_pnl_percent,
            price_change_pnl=price_change_pnl,
            current_apy=current_apy
        )
    
    def calculate_break_even_time(
        self,
        il_usd: float,
        daily_fees_usd: float,
        fees_already_earned_usd: float = 0
    ) -> BreakEvenResult:
        """
        Calculate time needed to recover impermanent loss through fees
        """
        # Already profitable?
        if fees_already_earned_usd >= il_usd:
            return BreakEvenResult(
                days_to_break_even=0,
                fees_needed_usd=0,
                daily_fees_usd=daily_fees_usd,
                is_profitable_now=True
            )
        
        # Fees still needed
        fees_needed = il_usd - fees_already_earned_usd
        
        # Days to break even
        if daily_fees_usd > 0:
            days_to_break_even = fees_needed / daily_fees_usd
        else:
            days_to_break_even = float('inf')
        
        return BreakEvenResult(
            days_to_break_even=days_to_break_even,
            fees_needed_usd=fees_needed,
            daily_fees_usd=daily_fees_usd,
            is_profitable_now=False
        )
    
    def calculate_apy_from_fees(
        self,
        daily_fees_usd: float,
        position_value_usd: float
    ) -> float:
        """Calculate APY based on fee earnings"""
        if position_value_usd <= 0:
            return 0
        
        daily_return = daily_fees_usd / position_value_usd
        apy = (1 + daily_return) ** 365 - 1
        return apy * 100  # Return as percentage
    
    def should_exit_position(
        self,
        pnl_result: PnLResult,
        current_apy: float,
        entry_apy: float,
        stop_loss_percent: float = -10,
        take_profit_percent: float = 50,
        apy_drop_threshold: float = 0.5
    ) -> Tuple[bool, str]:
        """
        Determine if position should be exited based on rules
        
        Returns: (should_exit, reason)
        """
        # Stop loss triggered
        if pnl_result.net_pnl_percent <= stop_loss_percent:
            return True, f"Stop loss triggered: {pnl_result.net_pnl_percent:.1f}%"
        
        # Take profit triggered
        if pnl_result.net_pnl_percent >= take_profit_percent:
            return True, f"Take profit triggered: {pnl_result.net_pnl_percent:.1f}%"
        
        # APY dropped too much
        if current_apy < entry_apy * apy_drop_threshold:
            return True, f"APY dropped from {entry_apy:.1f}% to {current_apy:.1f}%"
        
        # IL too high and won't recover
        if pnl_result.impermanent_loss_percent < -20:  # More than 20% IL
            return True, f"High impermanent loss: {pnl_result.impermanent_loss_percent:.1f}%"
        
        return False, "Position healthy"


# Example usage
def example_calculation():
    """Example P&L calculation"""
    calculator = PnLCalculator()
    
    # Example: SOL-USDC position
    # Entry: 10 SOL @ $100, 1000 USDC @ $1
    # Current: SOL @ $120, USDC @ $1
    
    pnl_result = calculator.calculate_net_pnl(
        entry_price_a=100,      # SOL was $100
        entry_price_b=1,        # USDC was $1
        current_price_a=120,    # SOL now $120
        current_price_b=1,      # USDC still $1
        entry_amount_a=10,      # 10 SOL
        entry_amount_b=1000,    # 1000 USDC
        fees_earned_a=0.1,      # Earned 0.1 SOL in fees
        fees_earned_b=10,       # Earned 10 USDC in fees
        current_apy=250        # Current APY 250%
    )
    
    print(f"Initial Value: ${pnl_result.initial_value_usd:,.2f}")
    print(f"Current Value: ${pnl_result.current_value_usd:,.2f}")
    print(f"Impermanent Loss: {pnl_result.impermanent_loss_percent:.2f}% (${pnl_result.impermanent_loss_usd:,.2f})")
    print(f"Fees Earned: ${pnl_result.fees_earned_usd:,.2f}")
    print(f"Net P&L: {pnl_result.net_pnl_percent:.2f}% (${pnl_result.net_pnl_usd:,.2f})")
    
    # Check if should exit
    should_exit, reason = calculator.should_exit_position(pnl_result, 250, 500)
    print(f"Should Exit: {should_exit} - {reason}")


if __name__ == "__main__":
    example_calculation()