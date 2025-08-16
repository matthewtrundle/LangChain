"""
Strategy Manager Service
Manages multiple concurrent trading strategies with isolated capital and risk limits
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass
import uuid

from models.trading_strategy import TradingStrategy, StrategyType, STRATEGY_PRESETS
from services.trading_bot import TradingBot
from services.paper_trading import PaperWallet
from database.connection import get_db_connection
from websocket_manager import ws_manager

logger = logging.getLogger(__name__)

@dataclass
class StrategyInstance:
    """Represents a running strategy instance"""
    id: str
    strategy_type: StrategyType
    trading_bot: TradingBot
    paper_wallet: Optional[PaperWallet]
    capital_allocation: float  # Percentage 0-100
    is_active: bool
    created_at: datetime
    performance: Dict

class StrategyManager:
    """Manages multiple concurrent trading strategies"""
    
    def __init__(self):
        self.strategies: Dict[str, StrategyInstance] = {}
        self.total_capital = 0.0
        self.paper_trading_enabled = False
        self._running_tasks: Dict[str, asyncio.Task] = {}
        
    async def initialize(self):
        """Initialize strategy manager and load saved strategies"""
        logger.info("Initializing Strategy Manager...")
        
        # Load strategies from database
        await self._load_strategies_from_db()
        
        # Start WebSocket update loop
        asyncio.create_task(self._broadcast_updates())
        
    async def add_strategy(
        self,
        strategy_type: StrategyType,
        capital_allocation: float,
        custom_config: Optional[Dict] = None
    ) -> str:
        """Add a new strategy instance"""
        
        # Validate capital allocation
        if not self._validate_capital_allocation(capital_allocation):
            raise ValueError("Invalid capital allocation. Total would exceed 100%")
        
        # Create strategy ID
        strategy_id = str(uuid.uuid4())
        
        # Get strategy preset or use custom config
        strategy_config = STRATEGY_PRESETS.get(strategy_type)
        if not strategy_config:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
            
        # Create trading bot instance
        trading_bot = TradingBot(strategy=strategy_config)
        
        # Create paper wallet if in paper trading mode
        paper_wallet = None
        if self.paper_trading_enabled:
            allocated_capital = self.total_capital * (capital_allocation / 100)
            paper_wallet = PaperWallet(initial_balance=allocated_capital)
            
        # Create strategy instance
        instance = StrategyInstance(
            id=strategy_id,
            strategy_type=strategy_type,
            trading_bot=trading_bot,
            paper_wallet=paper_wallet,
            capital_allocation=capital_allocation,
            is_active=False,
            created_at=datetime.now(),
            performance={
                'total_pnl': 0.0,
                'win_rate': 0.0,
                'total_trades': 0,
                'active_positions': 0
            }
        )
        
        # Store instance
        self.strategies[strategy_id] = instance
        
        # Save to database
        await self._save_strategy_to_db(instance)
        
        logger.info(f"Added strategy {strategy_type.value} with ID {strategy_id}")
        return strategy_id
        
    async def start_strategy(self, strategy_id: str):
        """Start a specific strategy"""
        instance = self.strategies.get(strategy_id)
        if not instance:
            raise ValueError(f"Strategy {strategy_id} not found")
            
        if instance.is_active:
            logger.warning(f"Strategy {strategy_id} is already active")
            return
            
        instance.is_active = True
        
        # Create and store the task
        task = asyncio.create_task(self._run_strategy(instance))
        self._running_tasks[strategy_id] = task
        
        logger.info(f"Started strategy {strategy_id}")
        
    async def stop_strategy(self, strategy_id: str):
        """Stop a specific strategy"""
        instance = self.strategies.get(strategy_id)
        if not instance:
            raise ValueError(f"Strategy {strategy_id} not found")
            
        instance.is_active = False
        
        # Cancel the running task
        task = self._running_tasks.get(strategy_id)
        if task and not task.done():
            task.cancel()
            
        logger.info(f"Stopped strategy {strategy_id}")
        
    async def _run_strategy(self, instance: StrategyInstance):
        """Run a strategy instance"""
        logger.info(f"Running strategy {instance.id} ({instance.strategy_type.value})")
        
        while instance.is_active:
            try:
                # Use paper wallet if enabled
                if self.paper_trading_enabled and instance.paper_wallet:
                    instance.trading_bot.paper_wallet = instance.paper_wallet
                    
                # Run one trading cycle
                await instance.trading_bot.trading_cycle()
                
                # Update performance metrics
                await self._update_strategy_performance(instance)
                
                # Wait before next cycle
                await asyncio.sleep(60)  # 1 minute between cycles
                
            except asyncio.CancelledError:
                logger.info(f"Strategy {instance.id} cancelled")
                break
            except Exception as e:
                logger.error(f"Error in strategy {instance.id}: {e}")
                await asyncio.sleep(5)  # Short delay on error
                
    async def _update_strategy_performance(self, instance: StrategyInstance):
        """Update performance metrics for a strategy"""
        # Get performance from trading bot
        bot_performance = instance.trading_bot.performance_tracker
        
        instance.performance.update({
            'total_pnl': bot_performance.get('total_pnl', 0),
            'win_rate': self._calculate_win_rate(bot_performance),
            'total_trades': bot_performance.get('total_trades', 0),
            'active_positions': len(instance.trading_bot.position_limits)
        })
        
        # Save to database
        await self._save_performance_to_db(instance.id, instance.performance)
        
    def _calculate_win_rate(self, performance: Dict) -> float:
        """Calculate win rate from performance data"""
        total_trades = performance.get('total_trades', 0)
        if total_trades == 0:
            return 0.0
        winning_trades = performance.get('winning_trades', 0)
        return (winning_trades / total_trades) * 100
        
    def _validate_capital_allocation(self, new_allocation: float) -> bool:
        """Validate that total capital allocation doesn't exceed 100%"""
        total = sum(s.capital_allocation for s in self.strategies.values())
        return (total + new_allocation) <= 100
        
    async def get_all_strategies(self) -> List[Dict]:
        """Get all strategies with their current status"""
        strategies = []
        for instance in self.strategies.values():
            strategies.append({
                'id': instance.id,
                'type': instance.strategy_type.value,
                'capital_allocation': instance.capital_allocation,
                'is_active': instance.is_active,
                'created_at': instance.created_at.isoformat(),
                'performance': instance.performance,
                'paper_trading': self.paper_trading_enabled
            })
        return strategies
        
    async def get_aggregate_performance(self) -> Dict:
        """Get aggregated performance across all strategies"""
        total_pnl = 0.0
        total_trades = 0
        active_positions = 0
        
        for instance in self.strategies.values():
            total_pnl += instance.performance.get('total_pnl', 0)
            total_trades += instance.performance.get('total_trades', 0)
            active_positions += instance.performance.get('active_positions', 0)
            
        return {
            'total_pnl': total_pnl,
            'total_trades': total_trades,
            'active_positions': active_positions,
            'active_strategies': sum(1 for s in self.strategies.values() if s.is_active),
            'total_strategies': len(self.strategies),
            'paper_trading': self.paper_trading_enabled
        }
        
    async def enable_paper_trading(self, total_capital: float = 10000):
        """Enable paper trading mode for all strategies"""
        self.paper_trading_enabled = True
        self.total_capital = total_capital
        
        # Create paper wallets for existing strategies
        for instance in self.strategies.values():
            if not instance.paper_wallet:
                allocated_capital = total_capital * (instance.capital_allocation / 100)
                instance.paper_wallet = PaperWallet(initial_balance=allocated_capital)
                
        logger.info(f"Paper trading enabled with ${total_capital} total capital")
        
    async def disable_paper_trading(self):
        """Disable paper trading mode"""
        self.paper_trading_enabled = False
        
        # Clear paper wallets
        for instance in self.strategies.values():
            instance.paper_wallet = None
            
        logger.info("Paper trading disabled")
        
    async def _broadcast_updates(self):
        """Broadcast strategy updates via WebSocket"""
        while True:
            try:
                # Get current state
                strategies = await self.get_all_strategies()
                aggregate = await self.get_aggregate_performance()
                
                # Broadcast via WebSocket
                await ws_manager.broadcast({
                    'type': 'strategy_update',
                    'data': {
                        'strategies': strategies,
                        'aggregate': aggregate,
                        'timestamp': datetime.now().isoformat()
                    }
                })
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error broadcasting updates: {e}")
                await asyncio.sleep(10)
                
    async def _load_strategies_from_db(self):
        """Load saved strategies from database"""
        conn = await get_db_connection()
        try:
            query = """
                SELECT id, strategy_type, capital_allocation, is_active, 
                       created_at, performance_data
                FROM trading_strategies
                WHERE deleted_at IS NULL
            """
            rows = await conn.fetch(query)
            
            for row in rows:
                # Recreate strategy instance
                strategy_type = StrategyType(row['strategy_type'])
                strategy_config = STRATEGY_PRESETS.get(strategy_type)
                
                instance = StrategyInstance(
                    id=row['id'],
                    strategy_type=strategy_type,
                    trading_bot=TradingBot(strategy=strategy_config),
                    paper_wallet=None,
                    capital_allocation=row['capital_allocation'],
                    is_active=False,  # Don't auto-start
                    created_at=row['created_at'],
                    performance=row['performance_data'] or {}
                )
                
                self.strategies[row['id']] = instance
                
        finally:
            await conn.close()
            
    async def _save_strategy_to_db(self, instance: StrategyInstance):
        """Save strategy to database"""
        conn = await get_db_connection()
        try:
            query = """
                INSERT INTO trading_strategies 
                (id, strategy_type, capital_allocation, is_active, created_at)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (id) DO UPDATE SET
                    capital_allocation = $3,
                    is_active = $4,
                    updated_at = NOW()
            """
            await conn.execute(
                query,
                instance.id,
                instance.strategy_type.value,
                instance.capital_allocation,
                instance.is_active,
                instance.created_at
            )
        finally:
            await conn.close()
            
    async def _save_performance_to_db(self, strategy_id: str, performance: Dict):
        """Save performance metrics to database"""
        conn = await get_db_connection()
        try:
            query = """
                UPDATE trading_strategies 
                SET performance_data = $2, updated_at = NOW()
                WHERE id = $1
            """
            import json
            await conn.execute(query, strategy_id, json.dumps(performance))
        finally:
            await conn.close()

# Global instance
strategy_manager = StrategyManager()