"""
Trading Strategy Models
Defines the structure for automated trading strategies
"""

from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum
from datetime import timedelta

class StrategyType(Enum):
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    DEGEN = "degen"
    CUSTOM = "custom"

class ExitReason(Enum):
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    RISK_INCREASE = "risk_increase"
    IL_THRESHOLD = "il_threshold"
    TIME_LIMIT = "time_limit"
    BETTER_OPPORTUNITY = "better_opportunity"
    MANUAL_EXIT = "manual_exit"
    RUG_DETECTION = "rug_detection"

@dataclass
class EntryRules:
    """Rules for entering a position"""
    max_risk_score: int = 60
    min_apy: float = 100.0
    max_apy: float = 10000.0  # Avoid obvious scams
    min_tvl: float = 50000.0
    min_volume_24h: float = 10000.0
    min_volume_to_tvl_ratio: float = 0.1
    max_volume_to_tvl_ratio: float = 5.0  # Avoid wash trading
    min_sustainability_score: float = 3.0
    max_il_risk: int = 70
    allowed_protocols: List[str] = None
    blocked_tokens: List[str] = None  # Known scam tokens
    require_liquidity_lock: bool = False
    min_pool_age_hours: int = 24

@dataclass
class ExitRules:
    """Rules for exiting a position"""
    stop_loss_percent: float = -10.0
    trailing_stop_percent: float = -5.0  # From peak
    take_profit_percent: float = 30.0
    max_risk_score_increase: int = 20
    max_il_percent: float = -15.0
    min_apy_threshold: float = 50.0  # Exit if APY drops below
    max_position_hours: int = 168  # 7 days
    rug_pull_tvl_drop_percent: float = -50.0
    rug_pull_volume_drop_percent: float = -70.0
    check_interval_minutes: int = 5

@dataclass
class PositionSizing:
    """Rules for position sizing"""
    sizing_method: str = "fixed"  # fixed, risk_based, kelly, portfolio_percent
    fixed_size_usd: float = 100.0
    max_position_size_usd: float = 1000.0
    max_portfolio_percent: float = 0.1  # 10%
    risk_multiplier: float = 1.0  # Lower position size for higher risk
    kelly_fraction: float = 0.25  # Conservative Kelly
    min_position_size_usd: float = 50.0
    gas_cost_limit_percent: float = 0.02  # Max 2% gas cost

@dataclass
class RiskLimits:
    """Portfolio-wide risk limits"""
    max_total_positions: int = 10
    max_positions_per_protocol: int = 3
    max_positions_per_token: int = 2
    max_portfolio_risk_score: float = 50.0  # Weighted average
    max_daily_loss_percent: float = -10.0
    max_drawdown_percent: float = -20.0
    min_cash_reserve_percent: float = 0.2  # Keep 20% in cash
    max_correlation_coefficient: float = 0.7
    rebalance_threshold_percent: float = 0.15  # Rebalance if position > 15%

@dataclass
class TradingStrategy:
    """Complete trading strategy configuration"""
    name: str
    strategy_type: StrategyType
    entry_rules: EntryRules
    exit_rules: ExitRules
    position_sizing: PositionSizing
    risk_limits: RiskLimits
    enabled: bool = True
    description: str = ""
    
    def validate(self) -> bool:
        """Validate strategy parameters"""
        if self.entry_rules.min_apy >= self.entry_rules.max_apy:
            return False
        if self.exit_rules.stop_loss_percent >= 0:
            return False
        if self.exit_rules.take_profit_percent <= 0:
            return False
        if self.position_sizing.max_portfolio_percent > 1.0:
            return False
        return True

# Preset Strategies
CONSERVATIVE_STRATEGY = TradingStrategy(
    name="Conservative",
    strategy_type=StrategyType.CONSERVATIVE,
    entry_rules=EntryRules(
        max_risk_score=40,
        min_apy=100.0,
        max_apy=2000.0,
        min_tvl=500000.0,
        min_volume_24h=50000.0,
        min_sustainability_score=7.0,
        max_il_risk=50,
        require_liquidity_lock=True,
        min_pool_age_hours=72
    ),
    exit_rules=ExitRules(
        stop_loss_percent=-5.0,
        trailing_stop_percent=-3.0,
        take_profit_percent=15.0,
        max_risk_score_increase=10,
        max_il_percent=-8.0,
        max_position_hours=336  # 14 days
    ),
    position_sizing=PositionSizing(
        sizing_method="portfolio_percent",
        max_portfolio_percent=0.05,  # 5%
        risk_multiplier=0.8
    ),
    risk_limits=RiskLimits(
        max_total_positions=5,
        max_positions_per_protocol=2,
        max_portfolio_risk_score=35.0,
        max_daily_loss_percent=-5.0,
        min_cash_reserve_percent=0.4
    ),
    description="Low risk strategy focusing on established pools with proven track records"
)

BALANCED_STRATEGY = TradingStrategy(
    name="Balanced",
    strategy_type=StrategyType.BALANCED,
    entry_rules=EntryRules(
        max_risk_score=60,
        min_apy=300.0,
        max_apy=5000.0,
        min_tvl=100000.0,
        min_volume_24h=20000.0,
        min_sustainability_score=5.0,
        max_il_risk=65,
        min_pool_age_hours=48
    ),
    exit_rules=ExitRules(
        stop_loss_percent=-10.0,
        trailing_stop_percent=-5.0,
        take_profit_percent=30.0,
        max_risk_score_increase=15,
        max_il_percent=-12.0,
        max_position_hours=168  # 7 days
    ),
    position_sizing=PositionSizing(
        sizing_method="risk_based",
        fixed_size_usd=200.0,
        max_portfolio_percent=0.1,  # 10%
        risk_multiplier=1.0
    ),
    risk_limits=RiskLimits(
        max_total_positions=8,
        max_positions_per_protocol=3,
        max_portfolio_risk_score=50.0,
        max_daily_loss_percent=-8.0,
        min_cash_reserve_percent=0.25
    ),
    description="Balanced risk/reward strategy for moderate returns"
)

DEGEN_STRATEGY = TradingStrategy(
    name="Degen",
    strategy_type=StrategyType.DEGEN,
    entry_rules=EntryRules(
        max_risk_score=80,
        min_apy=1000.0,
        max_apy=50000.0,
        min_tvl=50000.0,
        min_volume_24h=10000.0,
        min_sustainability_score=2.0,
        max_il_risk=80,
        min_pool_age_hours=6
    ),
    exit_rules=ExitRules(
        stop_loss_percent=-20.0,
        trailing_stop_percent=-10.0,
        take_profit_percent=100.0,
        max_risk_score_increase=20,
        max_il_percent=-20.0,
        max_position_hours=72,  # 3 days max
        check_interval_minutes=2  # More frequent monitoring
    ),
    position_sizing=PositionSizing(
        sizing_method="fixed",
        fixed_size_usd=100.0,
        max_portfolio_percent=0.2,  # 20%
        risk_multiplier=1.5
    ),
    risk_limits=RiskLimits(
        max_total_positions=15,
        max_positions_per_protocol=5,
        max_portfolio_risk_score=70.0,
        max_daily_loss_percent=-15.0,
        min_cash_reserve_percent=0.15,
        max_drawdown_percent=-30.0
    ),
    description="High risk, high reward strategy for experienced degens"
)

# Strategy registry
STRATEGY_PRESETS = {
    StrategyType.CONSERVATIVE: CONSERVATIVE_STRATEGY,
    StrategyType.BALANCED: BALANCED_STRATEGY,
    StrategyType.DEGEN: DEGEN_STRATEGY
}