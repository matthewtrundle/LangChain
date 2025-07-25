from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
import uuid

class PositionStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    EXITED = "exited"
    FAILED = "failed"

class ExitReason(str, Enum):
    MANUAL = "manual"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    APY_DROP = "apy_drop"
    RUG_RISK = "rug_risk"
    LOW_LIQUIDITY = "low_liquidity"
    AUTO_REBALANCE = "auto_rebalance"

class Position(BaseModel):
    id: str = None
    user_wallet: str = "demo_wallet"  # For now, using demo
    pool_address: str
    pool_data: Dict
    entry_price: float
    entry_amount: float
    entry_time: datetime
    entry_apy: float
    current_value: float = 0
    current_apy: float = 0
    status: PositionStatus = PositionStatus.PENDING
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    exit_reason: Optional[ExitReason] = None
    pnl_amount: float = 0
    pnl_percent: float = 0
    rewards_earned: float = 0
    gas_spent: float = 0
    
    def __init__(self, **data):
        if not data.get('id'):
            data['id'] = str(uuid.uuid4())
        if not data.get('entry_time'):
            data['entry_time'] = datetime.now()
        super().__init__(**data)
    
    def calculate_current_value(self, current_price: float, hours_elapsed: float) -> float:
        """Calculate current value including APY rewards"""
        # Price appreciation/depreciation
        price_value = self.entry_amount * (current_price / self.entry_price)
        
        # APY rewards (compound daily)
        daily_rate = self.current_apy / 365 / 100
        days_elapsed = hours_elapsed / 24
        rewards_value = self.entry_amount * ((1 + daily_rate) ** days_elapsed - 1)
        
        self.current_value = price_value + rewards_value
        self.rewards_earned = rewards_value
        self.pnl_amount = self.current_value - self.entry_amount - self.gas_spent
        self.pnl_percent = (self.pnl_amount / self.entry_amount) * 100
        
        return self.current_value
    
    def should_exit(self, current_metrics: Dict) -> tuple[bool, Optional[ExitReason]]:
        """Check if position should be exited based on rules"""
        # Stop loss: -10%
        if self.pnl_percent <= -10:
            return True, ExitReason.STOP_LOSS
        
        # Take profit: +50%
        if self.pnl_percent >= 50:
            return True, ExitReason.TAKE_PROFIT
        
        # APY dropped significantly (more than 50%)
        if current_metrics.get('apy', self.current_apy) < self.entry_apy * 0.5:
            return True, ExitReason.APY_DROP
        
        # Liquidity too low
        if current_metrics.get('tvl', 0) < 10000:  # Less than $10k
            return True, ExitReason.LOW_LIQUIDITY
        
        # Rug risk detected
        if current_metrics.get('rug_risk', False):
            return True, ExitReason.RUG_RISK
        
        return False, None

class ExitTrigger(BaseModel):
    position_id: str
    trigger_type: str
    threshold: float
    active: bool = True
    triggered_at: Optional[datetime] = None

class PositionSummary(BaseModel):
    total_positions: int
    active_positions: int
    total_invested: float
    current_value: float
    total_pnl: float
    total_pnl_percent: float
    best_performer: Optional[Position] = None
    worst_performer: Optional[Position] = None
    total_rewards: float
    average_apy: float