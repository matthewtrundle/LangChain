"""
Automated Trading Bot Service
Implements intelligent entry/exit logic for yield farming positions
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal

from models.trading_strategy import (
    TradingStrategy, StrategyType, ExitReason,
    STRATEGY_PRESETS
)
from models.position import Position, PositionStatus
from services.position_manager import position_manager
from services.risk_analysis_service import risk_analysis_service
from database.connection import get_db_connection
from utils.cache import api_cache
from websocket_manager import ws_manager

logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self, strategy: TradingStrategy = None):
        self.strategy = strategy or STRATEGY_PRESETS[StrategyType.BALANCED]
        self.enabled = False
        self.position_limits = {}  # Track positions per protocol/token
        self.last_check = datetime.now()
        self.performance_tracker = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_pnl': 0.0,
            'best_trade': 0.0,
            'worst_trade': 0.0
        }
        
    async def start(self):
        """Start the trading bot"""
        self.enabled = True
        logger.info(f"Trading bot started with {self.strategy.name} strategy")
        
        # Main trading loop
        while self.enabled:
            try:
                await self.trading_cycle()
                await asyncio.sleep(60)  # Run every minute
            except Exception as e:
                logger.error(f"Trading bot error: {e}")
                await asyncio.sleep(30)
    
    async def stop(self):
        """Stop the trading bot"""
        self.enabled = False
        logger.info("Trading bot stopped")
    
    async def trading_cycle(self):
        """Main trading cycle - check for entries and exits"""
        # 1. Check existing positions for exit signals
        await self.check_exit_signals()
        
        # 2. Check portfolio risk limits
        if not self.check_portfolio_limits():
            logger.warning("Portfolio risk limits exceeded, skipping new entries")
            return
        
        # 3. Find new entry opportunities
        await self.find_entry_opportunities()
        
        # 4. Rebalance if needed
        await self.check_rebalancing()
        
        # 5. Broadcast status update
        await self.broadcast_status()
    
    async def check_exit_signals(self):
        """Check all positions for exit conditions"""
        positions = position_manager.get_active_positions()
        
        for position in positions:
            exit_reason = await self.should_exit_position(position)
            if exit_reason:
                await self.exit_position(position, exit_reason)
    
    async def should_exit_position(self, position: Position) -> Optional[ExitReason]:
        """Determine if a position should be exited"""
        # Get current metrics
        current_pnl_percent = position.pnl_percent
        hours_held = (datetime.now() - position.entry_time).total_seconds() / 3600
        
        # 1. Stop loss
        if current_pnl_percent <= self.strategy.exit_rules.stop_loss_percent:
            return ExitReason.STOP_LOSS
        
        # 2. Take profit
        if current_pnl_percent >= self.strategy.exit_rules.take_profit_percent:
            return ExitReason.TAKE_PROFIT
        
        # 3. Time limit
        if hours_held >= self.strategy.exit_rules.max_position_hours:
            return ExitReason.TIME_LIMIT
        
        # 4. IL threshold
        il_percent = self._calculate_il_percent(position)
        if il_percent <= self.strategy.exit_rules.max_il_percent:
            return ExitReason.IL_THRESHOLD
        
        # 5. Risk deterioration
        current_risk = await self._get_current_risk_score(position.pool_address)
        if current_risk and position.entry_risk_score:
            risk_increase = current_risk - position.entry_risk_score
            if risk_increase > self.strategy.exit_rules.max_risk_score_increase:
                return ExitReason.RISK_INCREASE
        
        # 6. Rug pull detection
        if await self._detect_rug_pull(position):
            return ExitReason.RUG_DETECTION
        
        # 7. Better opportunity (if we're at capacity)
        if len(position_manager.get_active_positions()) >= self.strategy.risk_limits.max_total_positions:
            if await self._has_better_opportunity(position):
                return ExitReason.BETTER_OPPORTUNITY
        
        return None
    
    async def _detect_rug_pull(self, position: Position) -> bool:
        """Detect potential rug pull based on TVL/volume drops"""
        pool_data = await self._get_pool_data(position.pool_address)
        if not pool_data:
            return False
        
        current_tvl = pool_data.get('tvl', 0)
        current_volume = pool_data.get('volume_24h', 0)
        
        # Compare with entry values
        entry_tvl = position.pool_data.get('tvl', current_tvl)
        entry_volume = position.pool_data.get('volume_24h', current_volume)
        
        if entry_tvl > 0:
            tvl_change = ((current_tvl - entry_tvl) / entry_tvl) * 100
            if tvl_change <= self.strategy.exit_rules.rug_pull_tvl_drop_percent:
                logger.warning(f"Rug pull detected for {position.pool_address}: TVL dropped {tvl_change:.1f}%")
                return True
        
        if entry_volume > 0:
            volume_change = ((current_volume - entry_volume) / entry_volume) * 100
            if volume_change <= self.strategy.exit_rules.rug_pull_volume_drop_percent:
                logger.warning(f"Rug pull detected for {position.pool_address}: Volume dropped {volume_change:.1f}%")
                return True
        
        return False
    
    async def exit_position(self, position: Position, reason: ExitReason):
        """Execute position exit"""
        logger.info(f"Exiting position {position.id} due to {reason.value}")
        
        # Update position status
        position.status = PositionStatus.CLOSED
        position.exit_time = datetime.now()
        position.exit_reason = reason
        
        # Track performance
        self.performance_tracker['total_trades'] += 1
        if position.pnl_amount > 0:
            self.performance_tracker['winning_trades'] += 1
        self.performance_tracker['total_pnl'] += position.pnl_amount
        
        if position.pnl_amount > self.performance_tracker['best_trade']:
            self.performance_tracker['best_trade'] = position.pnl_amount
        if position.pnl_amount < self.performance_tracker['worst_trade']:
            self.performance_tracker['worst_trade'] = position.pnl_amount
        
        # Broadcast exit event
        await ws_manager.broadcast({
            'type': 'position_exit',
            'position_id': position.id,
            'pool': position.pool_data.get('token_symbols', 'Unknown'),
            'pnl': position.pnl_amount,
            'pnl_percent': position.pnl_percent,
            'reason': reason.value,
            'strategy': self.strategy.name
        })
    
    async def find_entry_opportunities(self):
        """Find and evaluate new pool opportunities"""
        # Get available capital
        available_capital = self._get_available_capital()
        if available_capital < self.strategy.position_sizing.min_position_size_usd:
            logger.info("Insufficient capital for new positions")
            return
        
        # Get candidate pools
        pools = await self._get_candidate_pools()
        
        # Evaluate each pool
        opportunities = []
        for pool in pools:
            score = await self._evaluate_opportunity(pool)
            if score > 0:
                opportunities.append((pool, score))
        
        # Sort by score and take the best
        opportunities.sort(key=lambda x: x[1], reverse=True)
        
        # Enter positions for top opportunities
        for pool, score in opportunities[:3]:  # Max 3 new positions per cycle
            if await self._can_enter_position(pool):
                position_size = self._calculate_position_size(pool, score)
                if position_size >= self.strategy.position_sizing.min_position_size_usd:
                    await self.enter_position(pool, position_size, score)
                    
                    # Update available capital
                    available_capital -= position_size
                    if available_capital < self.strategy.position_sizing.min_position_size_usd:
                        break
    
    async def _get_candidate_pools(self) -> List[Dict]:
        """Get pools that meet basic entry criteria"""
        conn = await get_db_connection()
        try:
            query = """
                SELECT DISTINCT p.*, r.* 
                FROM pools_enhanced p
                JOIN pool_risk_analysis r ON p.pool_address = r.pool_address
                WHERE r.analyzed_at > NOW() - INTERVAL '30 minutes'
                  AND r.apy >= $1
                  AND r.apy <= $2
                  AND r.tvl >= $3
                  AND r.overall_risk_score <= $4
                  AND r.sustainability_score >= $5
                  AND NOT p.is_flagged
                ORDER BY r.apy DESC
                LIMIT 50
            """
            
            rows = await conn.fetch(
                query,
                self.strategy.entry_rules.min_apy,
                self.strategy.entry_rules.max_apy,
                self.strategy.entry_rules.min_tvl,
                self.strategy.entry_rules.max_risk_score,
                self.strategy.entry_rules.min_sustainability_score
            )
            
            pools = []
            for row in rows:
                pool = dict(row)
                # Convert Decimal to float
                for key, value in pool.items():
                    if hasattr(value, 'to_decimal'):
                        pool[key] = float(value)
                pools.append(pool)
            
            return pools
            
        finally:
            await conn.close()
    
    async def _evaluate_opportunity(self, pool: Dict) -> float:
        """Score a pool opportunity (0-100)"""
        score = 0.0
        
        # APY component (30%)
        apy_score = min(pool['apy'] / 1000, 1.0) * 30
        score += apy_score
        
        # Risk component (30%) - inverse
        risk_score = (100 - pool['overall_risk_score']) / 100 * 30
        score += risk_score
        
        # Sustainability component (20%)
        sustainability_score = pool['sustainability_score'] / 10 * 20
        score += sustainability_score
        
        # Volume/TVL ratio component (10%)
        volume_ratio = pool.get('volume_to_tvl_ratio', 0)
        if 0.2 <= volume_ratio <= 2.0:  # Healthy range
            volume_score = 10
        else:
            volume_score = 5
        score += volume_score
        
        # Liquidity component (10%)
        tvl_score = min(pool['tvl'] / 1000000, 1.0) * 10  # Up to $1M
        score += tvl_score
        
        # Apply strategy-specific adjustments
        if self.strategy.strategy_type == StrategyType.DEGEN:
            # Degens love high APY
            if pool['apy'] > 2000:
                score *= 1.2
        elif self.strategy.strategy_type == StrategyType.CONSERVATIVE:
            # Conservative prefers stability
            if pool['sustainability_score'] < 7:
                score *= 0.7
        
        return score
    
    async def _can_enter_position(self, pool: Dict) -> bool:
        """Check if we can enter this position given current limits"""
        active_positions = position_manager.get_active_positions()
        
        # Check total position limit
        if len(active_positions) >= self.strategy.risk_limits.max_total_positions:
            return False
        
        # Check protocol limit
        protocol = pool.get('protocol', 'unknown')
        protocol_count = sum(1 for p in active_positions if p.pool_data.get('protocol') == protocol)
        if protocol_count >= self.strategy.risk_limits.max_positions_per_protocol:
            return False
        
        # Check token exposure
        token_a = pool.get('token_a_symbol', '')
        token_b = pool.get('token_b_symbol', '')
        
        for token in [token_a, token_b]:
            if token:
                token_count = sum(1 for p in active_positions 
                                if token in p.pool_data.get('token_symbols', ''))
                if token_count >= self.strategy.risk_limits.max_positions_per_token:
                    return False
        
        # Check blocked tokens
        if self.strategy.entry_rules.blocked_tokens:
            for token in [token_a, token_b]:
                if token in self.strategy.entry_rules.blocked_tokens:
                    return False
        
        return True
    
    def _calculate_position_size(self, pool: Dict, score: float) -> float:
        """Calculate position size based on strategy and score"""
        wallet_balance = position_manager.wallet.get_balance()
        
        if self.strategy.position_sizing.sizing_method == "fixed":
            size = self.strategy.position_sizing.fixed_size_usd
            
        elif self.strategy.position_sizing.sizing_method == "portfolio_percent":
            size = wallet_balance * self.strategy.position_sizing.max_portfolio_percent
            
        elif self.strategy.position_sizing.sizing_method == "risk_based":
            # Higher risk = smaller position
            risk_factor = (100 - pool['overall_risk_score']) / 100
            base_size = self.strategy.position_sizing.fixed_size_usd
            size = base_size * risk_factor * self.strategy.position_sizing.risk_multiplier
            
        elif self.strategy.position_sizing.sizing_method == "kelly":
            # Simplified Kelly Criterion
            win_rate = self.get_win_rate()
            avg_win = self.get_average_win()
            avg_loss = abs(self.get_average_loss())
            
            if avg_loss > 0:
                kelly_percent = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
                kelly_percent = max(0, min(kelly_percent, 1))  # Bound between 0 and 1
                size = wallet_balance * kelly_percent * self.strategy.position_sizing.kelly_fraction
            else:
                size = self.strategy.position_sizing.fixed_size_usd
        else:
            size = self.strategy.position_sizing.fixed_size_usd
        
        # Apply limits
        size = max(size, self.strategy.position_sizing.min_position_size_usd)
        size = min(size, self.strategy.position_sizing.max_position_size_usd)
        
        # Ensure we don't exceed cash reserves
        available = self._get_available_capital()
        size = min(size, available)
        
        return round(size, 2)
    
    async def enter_position(self, pool: Dict, size: float, score: float):
        """Execute position entry"""
        logger.info(f"Entering position in {pool['token_pair']} with ${size}")
        
        # Create position
        position = Position(
            pool_address=pool['pool_address'],
            pool_data=pool,
            entry_amount=size,
            entry_apy=pool['apy'],
            entry_risk_score=pool['overall_risk_score']
        )
        
        # Add to position manager
        position_manager.enter_position(
            pool_address=pool['pool_address'],
            pool_data=pool,
            amount=size
        )
        
        # Broadcast entry event
        await ws_manager.broadcast({
            'type': 'position_entry',
            'pool': pool['token_pair'],
            'amount': size,
            'apy': pool['apy'],
            'risk_score': pool['overall_risk_score'],
            'score': round(score, 2),
            'strategy': self.strategy.name
        })
    
    async def check_rebalancing(self):
        """Check if portfolio needs rebalancing"""
        positions = position_manager.get_active_positions()
        if not positions:
            return
        
        total_value = sum(p.current_value for p in positions)
        
        for position in positions:
            weight = position.current_value / total_value
            
            # Check if position is too large
            if weight > self.strategy.risk_limits.rebalance_threshold_percent:
                # Trim position
                excess = position.current_value - (total_value * self.strategy.risk_limits.rebalance_threshold_percent)
                logger.info(f"Rebalancing: Trimming {position.id} by ${excess:.2f}")
                # In real implementation, this would execute a partial exit
    
    def check_portfolio_limits(self) -> bool:
        """Check if portfolio is within risk limits"""
        positions = position_manager.get_active_positions()
        
        # Check daily loss limit
        daily_pnl = sum(p.pnl_amount for p in positions 
                       if (datetime.now() - p.entry_time).days < 1)
        wallet_balance = position_manager.wallet.get_balance()
        
        if wallet_balance > 0:
            daily_pnl_percent = (daily_pnl / wallet_balance) * 100
            if daily_pnl_percent <= self.strategy.risk_limits.max_daily_loss_percent:
                logger.warning(f"Daily loss limit hit: {daily_pnl_percent:.1f}%")
                return False
        
        # Check average portfolio risk
        if positions:
            avg_risk = sum(p.entry_risk_score or 50 for p in positions) / len(positions)
            if avg_risk > self.strategy.risk_limits.max_portfolio_risk_score:
                logger.warning(f"Portfolio risk too high: {avg_risk:.1f}")
                return False
        
        return True
    
    def _get_available_capital(self) -> float:
        """Get available capital for new positions"""
        wallet_balance = position_manager.wallet.get_balance()
        active_positions_value = sum(p.current_value for p in position_manager.get_active_positions())
        
        # Reserve requirement
        min_reserve = wallet_balance * self.strategy.risk_limits.min_cash_reserve_percent
        
        available = wallet_balance - active_positions_value - min_reserve
        return max(0, available)
    
    async def _get_pool_data(self, pool_address: str) -> Optional[Dict]:
        """Get current pool data"""
        # Check cache
        cache_key = f"pool_data:{pool_address}"
        cached = api_cache.get(cache_key)
        if cached:
            return cached
        
        # Fetch from database
        conn = await get_db_connection()
        try:
            query = """
                SELECT * FROM pool_risk_analysis 
                WHERE pool_address = $1 
                ORDER BY analyzed_at DESC 
                LIMIT 1
            """
            row = await conn.fetchrow(query, pool_address)
            if row:
                data = dict(row)
                for key, value in data.items():
                    if hasattr(value, 'to_decimal'):
                        data[key] = float(value)
                api_cache.set(cache_key, data, expire=300)
                return data
        finally:
            await conn.close()
        
        return None
    
    async def _get_current_risk_score(self, pool_address: str) -> Optional[int]:
        """Get current risk score for a pool"""
        pool_data = await self._get_pool_data(pool_address)
        return pool_data.get('overall_risk_score') if pool_data else None
    
    def _calculate_il_percent(self, position: Position) -> float:
        """Calculate impermanent loss percentage"""
        # Simplified IL calculation
        # In production, this would use actual price data
        return -5.0  # Placeholder
    
    async def _has_better_opportunity(self, position: Position) -> bool:
        """Check if there's a significantly better opportunity available"""
        # Get current position score
        current_score = await self._evaluate_opportunity(position.pool_data)
        
        # Find best available opportunity
        pools = await self._get_candidate_pools()
        best_score = 0
        for pool in pools[:5]:  # Check top 5
            score = await self._evaluate_opportunity(pool)
            if score > best_score:
                best_score = score
        
        # Need 50% better opportunity to switch
        return best_score > current_score * 1.5
    
    async def broadcast_status(self):
        """Broadcast bot status"""
        status = {
            'type': 'bot_status',
            'enabled': self.enabled,
            'strategy': self.strategy.name,
            'active_positions': len(position_manager.get_active_positions()),
            'total_value': sum(p.current_value for p in position_manager.get_active_positions()),
            'available_capital': self._get_available_capital(),
            'performance': {
                'win_rate': self.get_win_rate(),
                'total_pnl': self.performance_tracker['total_pnl'],
                'best_trade': self.performance_tracker['best_trade'],
                'worst_trade': self.performance_tracker['worst_trade']
            }
        }
        await ws_manager.broadcast(status)
    
    def get_win_rate(self) -> float:
        """Calculate win rate"""
        if self.performance_tracker['total_trades'] == 0:
            return 0.5  # Default 50%
        return self.performance_tracker['winning_trades'] / self.performance_tracker['total_trades']
    
    def get_average_win(self) -> float:
        """Calculate average winning trade"""
        winning_trades = self.performance_tracker['winning_trades']
        if winning_trades == 0:
            return 100.0  # Default
        # This is simplified - in production, track individual wins
        return self.performance_tracker['best_trade'] * 0.6
    
    def get_average_loss(self) -> float:
        """Calculate average losing trade"""
        losing_trades = self.performance_tracker['total_trades'] - self.performance_tracker['winning_trades']
        if losing_trades == 0:
            return -50.0  # Default
        # This is simplified - in production, track individual losses
        return self.performance_tracker['worst_trade'] * 0.6
    
    def set_strategy(self, strategy: TradingStrategy):
        """Update trading strategy"""
        if strategy.validate():
            self.strategy = strategy
            logger.info(f"Strategy updated to {strategy.name}")
        else:
            raise ValueError("Invalid strategy configuration")
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            'enabled': self.enabled,
            'strategy': {
                'name': self.strategy.name,
                'type': self.strategy.strategy_type.value,
                'description': self.strategy.description
            },
            'performance': self.performance_tracker,
            'limits': {
                'active_positions': len(position_manager.get_active_positions()),
                'max_positions': self.strategy.risk_limits.max_total_positions,
                'available_capital': self._get_available_capital()
            }
        }

# Global trading bot instance
trading_bot = TradingBot()