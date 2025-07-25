from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from models.position import Position, PositionStatus, ExitReason, PositionSummary
from .wallet_service import get_wallet, TransactionType

class PositionManager:
    """Manages all user positions (simulated for now)"""
    
    def __init__(self):
        # In production, this would be a database
        self.positions: Dict[str, Position] = {}
        self.position_history: List[Position] = []
        
        # Get wallet instance
        self.wallet = get_wallet()
        
        # Risk limits
        self.max_positions = 5
        self.max_position_size = 1000  # $1000 max per position
        self.max_total_exposure = 5000  # $5000 total
        
    def can_enter_position(self, amount: float) -> Tuple[bool, str]:
        """Check if we can enter a new position"""
        active_positions = [p for p in self.positions.values() if p.status == PositionStatus.ACTIVE]
        
        # Check wallet balance
        wallet_balance = self.wallet.get_available_balance()
        if amount > wallet_balance:
            return False, f"Insufficient balance: ${wallet_balance:.2f} available"
        
        if len(active_positions) >= self.max_positions:
            return False, f"Maximum {self.max_positions} positions reached"
        
        if amount > self.max_position_size:
            return False, f"Position size ${amount} exceeds max ${self.max_position_size}"
        
        total_active = sum(p.entry_amount for p in active_positions)
        if total_active + amount > self.max_total_exposure:
            return False, f"Total exposure would exceed ${self.max_total_exposure}"
        
        return True, "OK"
    
    def enter_position(self, pool_data: Dict, amount: float) -> Position:
        """Enter a new position"""
        can_enter, reason = self.can_enter_position(amount)
        if not can_enter:
            raise ValueError(f"Cannot enter position: {reason}")
        
        # Create position
        position = Position(
            pool_address=pool_data.get("pool_address"),
            pool_data=pool_data,
            entry_price=1.0,  # Simulated price
            entry_amount=amount,
            entry_apy=pool_data.get("apy", 0),
            current_apy=pool_data.get("apy", 0),
            gas_spent=0.01,  # Simulated gas
            status=PositionStatus.ACTIVE
        )
        
        # Deduct from wallet
        pool_name = pool_data.get("token_symbols", "Unknown Pool")
        success = self.wallet.enter_position(
            position_id=position.id,
            amount=amount,
            pool_name=pool_name,
            apy=pool_data.get("apy", 0)
        )
        
        if not success:
            raise ValueError("Failed to enter position: wallet transaction failed")
        
        # Pay gas fee
        self.wallet.pay_fee(0.01, f"Gas fee for entering {pool_name}")
        
        self.positions[position.id] = position
        
        print(f"[PositionManager] Entered position {position.id} in {pool_name} with ${amount}")
        
        return position
    
    def update_position(self, position_id: str, current_metrics: Dict) -> Position:
        """Update position with current metrics"""
        position = self.positions.get(position_id)
        if not position:
            raise ValueError(f"Position {position_id} not found")
        
        # Calculate time elapsed
        hours_elapsed = (datetime.now() - position.entry_time).total_seconds() / 3600
        
        # Update APY
        position.current_apy = current_metrics.get("apy", position.current_apy)
        
        # Calculate current value
        current_price = current_metrics.get("price", 1.0) * position.entry_price
        position.calculate_current_value(current_price, hours_elapsed)
        
        # Check exit conditions
        should_exit, exit_reason = position.should_exit(current_metrics)
        
        if should_exit and position.status == PositionStatus.ACTIVE:
            self.exit_position(position_id, exit_reason)
        
        return position
    
    def exit_position(self, position_id: str, reason: ExitReason = ExitReason.MANUAL) -> Position:
        """Exit a position"""
        position = self.positions.get(position_id)
        if not position:
            raise ValueError(f"Position {position_id} not found")
        
        if position.status != PositionStatus.ACTIVE:
            raise ValueError(f"Position {position_id} is not active")
        
        # Update exit data
        position.status = PositionStatus.EXITED
        position.exit_time = datetime.now()
        position.exit_price = 1.0  # Simulated
        position.exit_reason = reason
        position.gas_spent += 0.01  # Exit gas
        
        # Final P&L calculation
        hours_elapsed = (position.exit_time - position.entry_time).total_seconds() / 3600
        position.calculate_current_value(position.exit_price, hours_elapsed)
        
        # Return funds to wallet
        pool_name = position.pool_data.get("token_symbols", "Unknown Pool")
        self.wallet.exit_position(
            position_id=position.id,
            amount=position.entry_amount,
            pnl=position.pnl_amount,
            pool_name=pool_name
        )
        
        # Pay exit gas fee
        self.wallet.pay_fee(0.01, f"Gas fee for exiting {pool_name}")
        
        # Move to history
        self.position_history.append(position)
        
        print(f"[PositionManager] Exited position {position.id} - Reason: {reason}, P&L: ${position.pnl_amount:.2f} ({position.pnl_percent:.1f}%)")
        
        return position
    
    def get_active_positions(self) -> List[Position]:
        """Get all active positions"""
        return [p for p in self.positions.values() if p.status == PositionStatus.ACTIVE]
    
    def get_position_summary(self) -> PositionSummary:
        """Get summary of all positions"""
        all_positions = list(self.positions.values()) + self.position_history
        active_positions = self.get_active_positions()
        
        if not all_positions:
            return PositionSummary(
                total_positions=0,
                active_positions=0,
                total_invested=0,
                current_value=0,
                total_pnl=0,
                total_pnl_percent=0,
                total_rewards=0,
                average_apy=0
            )
        
        total_invested = sum(p.entry_amount for p in all_positions)
        current_value = sum(p.current_value for p in active_positions)
        total_pnl = sum(p.pnl_amount for p in all_positions)
        total_rewards = sum(p.rewards_earned for p in all_positions)
        
        # Find best/worst
        sorted_by_pnl = sorted(all_positions, key=lambda p: p.pnl_percent)
        worst_performer = sorted_by_pnl[0] if sorted_by_pnl else None
        best_performer = sorted_by_pnl[-1] if sorted_by_pnl else None
        
        # Average APY of active positions
        avg_apy = sum(p.current_apy for p in active_positions) / len(active_positions) if active_positions else 0
        
        return PositionSummary(
            total_positions=len(all_positions),
            active_positions=len(active_positions),
            total_invested=total_invested,
            current_value=current_value,
            total_pnl=total_pnl,
            total_pnl_percent=(total_pnl / total_invested * 100) if total_invested > 0 else 0,
            best_performer=best_performer,
            worst_performer=worst_performer,
            total_rewards=total_rewards,
            average_apy=avg_apy
        )
    
    def simulate_position_updates(self):
        """Simulate position value changes (for demo)"""
        import random
        
        for position in self.get_active_positions():
            # Simulate price changes (-5% to +5%)
            price_change = 1 + random.uniform(-0.05, 0.05)
            
            # Simulate APY changes
            apy_change = random.uniform(-20, 20)  # +/- 20% change
            new_apy = max(0, position.current_apy * (1 + apy_change / 100))
            
            # Simulate TVL changes
            tvl = position.pool_data.get("tvl", 100000)
            tvl_change = random.uniform(-10, 10)  # +/- 10% change
            new_tvl = max(1000, tvl * (1 + tvl_change / 100))
            
            # Update position
            current_metrics = {
                "apy": new_apy,
                "tvl": new_tvl,
                "rug_risk": random.random() < 0.01,  # 1% chance of rug risk
                "price": price_change
            }
            
            self.update_position(position.id, current_metrics)
    
    def check_exit_conditions(self, position: Position):
        """Check if position should be exited"""
        should_exit, exit_reason = position.should_exit({"apy": position.current_apy, "tvl": position.pool_data.get("tvl", 100000)})
        if should_exit and position.status == PositionStatus.ACTIVE:
            self.exit_position(position.id, exit_reason)

# Global instance
position_manager = PositionManager()