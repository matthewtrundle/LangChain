"""
Backtesting Framework
Test trading strategies on historical data
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import numpy as np
import pandas as pd

from models.trading_strategy import TradingStrategy, ExitReason
from database.connection import get_db_connection

logger = logging.getLogger(__name__)

@dataclass
class BacktestResult:
    """Results from a backtest run"""
    strategy_name: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_percent: float
    num_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    average_win: float
    average_loss: float
    profit_factor: float
    max_drawdown: float
    max_drawdown_percent: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    trades: List[Dict]
    equity_curve: List[Dict]
    
    def to_dict(self) -> Dict:
        return {
            'strategy_name': self.strategy_name,
            'period': f"{self.start_date.date()} to {self.end_date.date()}",
            'initial_capital': self.initial_capital,
            'final_capital': round(self.final_capital, 2),
            'total_return': round(self.total_return, 2),
            'total_return_percent': round(self.total_return_percent, 2),
            'num_trades': self.num_trades,
            'win_rate': round(self.win_rate * 100, 2),
            'average_win': round(self.average_win, 2),
            'average_loss': round(self.average_loss, 2),
            'profit_factor': round(self.profit_factor, 2),
            'max_drawdown_percent': round(self.max_drawdown_percent, 2),
            'sharpe_ratio': round(self.sharpe_ratio, 2),
            'sortino_ratio': round(self.sortino_ratio, 2),
            'calmar_ratio': round(self.calmar_ratio, 2)
        }

class Backtester:
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.trades = []
        self.equity_curve = []
        
    async def run_backtest(
        self,
        strategy: TradingStrategy,
        start_date: datetime,
        end_date: datetime,
        time_step: timedelta = timedelta(hours=1)
    ) -> BacktestResult:
        """Run backtest for a strategy over a time period"""
        logger.info(f"Starting backtest for {strategy.name} from {start_date} to {end_date}")
        
        # Initialize portfolio
        capital = self.initial_capital
        positions = {}  # Active positions
        self.trades = []
        self.equity_curve = []
        
        # Get historical data
        historical_data = await self._get_historical_data(start_date, end_date)
        
        # Simulate trading over time
        current_time = start_date
        while current_time <= end_date:
            # Update position values
            portfolio_value = capital
            for position_id, position in list(positions.items()):
                # Check exit conditions
                exit_reason = self._check_exit_conditions(
                    position, 
                    historical_data, 
                    current_time, 
                    strategy
                )
                
                if exit_reason:
                    # Exit position
                    exit_value = self._calculate_position_value(
                        position, 
                        historical_data, 
                        current_time
                    )
                    pnl = exit_value - position['entry_value']
                    pnl_percent = (pnl / position['entry_value']) * 100
                    
                    capital += exit_value
                    
                    # Record trade
                    self.trades.append({
                        'entry_time': position['entry_time'],
                        'exit_time': current_time,
                        'pool': position['pool'],
                        'entry_value': position['entry_value'],
                        'exit_value': exit_value,
                        'pnl': pnl,
                        'pnl_percent': pnl_percent,
                        'exit_reason': exit_reason.value
                    })
                    
                    del positions[position_id]
                else:
                    # Update position value
                    current_value = self._calculate_position_value(
                        position, 
                        historical_data, 
                        current_time
                    )
                    portfolio_value += current_value - capital
            
            # Find new opportunities
            if len(positions) < strategy.risk_limits.max_total_positions:
                opportunities = self._find_opportunities(
                    historical_data, 
                    current_time, 
                    strategy
                )
                
                for opp in opportunities:
                    if capital > strategy.position_sizing.min_position_size_usd:
                        # Enter position
                        position_size = min(
                            strategy.position_sizing.fixed_size_usd,
                            capital * 0.9  # Keep 10% cash
                        )
                        
                        positions[len(positions)] = {
                            'entry_time': current_time,
                            'pool': opp['pool'],
                            'entry_value': position_size,
                            'entry_apy': opp['apy'],
                            'entry_risk': opp['risk_score']
                        }
                        
                        capital -= position_size
                        
                        if len(positions) >= strategy.risk_limits.max_total_positions:
                            break
            
            # Record equity curve
            self.equity_curve.append({
                'timestamp': current_time,
                'value': portfolio_value,
                'positions': len(positions)
            })
            
            # Move to next time step
            current_time += time_step
        
        # Close any remaining positions
        for position in positions.values():
            exit_value = self._calculate_position_value(
                position, 
                historical_data, 
                end_date
            )
            pnl = exit_value - position['entry_value']
            pnl_percent = (pnl / position['entry_value']) * 100
            
            capital += exit_value
            
            self.trades.append({
                'entry_time': position['entry_time'],
                'exit_time': end_date,
                'pool': position['pool'],
                'entry_value': position['entry_value'],
                'exit_value': exit_value,
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'exit_reason': 'backtest_end'
            })
        
        # Calculate metrics
        return self._calculate_metrics(
            strategy.name,
            start_date,
            end_date,
            self.initial_capital,
            capital
        )
    
    async def _get_historical_data(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> pd.DataFrame:
        """Fetch historical pool data"""
        conn = await get_db_connection()
        try:
            query = """
                SELECT 
                    pool_address,
                    analyzed_at as timestamp,
                    apy,
                    tvl,
                    volume_24h,
                    overall_risk_score,
                    sustainability_score,
                    token_pair
                FROM pool_risk_analysis r
                JOIN pools_enhanced p ON r.pool_address = p.pool_address
                WHERE analyzed_at BETWEEN $1 AND $2
                ORDER BY analyzed_at
            """
            
            rows = await conn.fetch(query, start_date, end_date)
            
            data = []
            for row in rows:
                data.append({
                    'pool_address': row['pool_address'],
                    'timestamp': row['timestamp'],
                    'apy': float(row['apy']),
                    'tvl': float(row['tvl']),
                    'volume_24h': float(row['volume_24h']),
                    'risk_score': row['overall_risk_score'],
                    'sustainability_score': float(row['sustainability_score']),
                    'pool': row['token_pair']
                })
            
            return pd.DataFrame(data)
            
        finally:
            await conn.close()
    
    def _check_exit_conditions(
        self,
        position: Dict,
        data: pd.DataFrame,
        current_time: datetime,
        strategy: TradingStrategy
    ) -> Optional[ExitReason]:
        """Check if position should be exited"""
        # Calculate position metrics
        hours_held = (current_time - position['entry_time']).total_seconds() / 3600
        current_value = self._calculate_position_value(position, data, current_time)
        pnl_percent = ((current_value - position['entry_value']) / position['entry_value']) * 100
        
        # Time limit
        if hours_held >= strategy.exit_rules.max_position_hours:
            return ExitReason.TIME_LIMIT
        
        # Stop loss
        if pnl_percent <= strategy.exit_rules.stop_loss_percent:
            return ExitReason.STOP_LOSS
        
        # Take profit
        if pnl_percent >= strategy.exit_rules.take_profit_percent:
            return ExitReason.TAKE_PROFIT
        
        # Risk increase
        current_data = data[
            (data['pool'] == position['pool']) & 
            (data['timestamp'] <= current_time)
        ].iloc[-1] if len(data) > 0 else None
        
        if current_data is not None:
            risk_increase = current_data['risk_score'] - position['entry_risk']
            if risk_increase > strategy.exit_rules.max_risk_score_increase:
                return ExitReason.RISK_INCREASE
        
        return None
    
    def _calculate_position_value(
        self,
        position: Dict,
        data: pd.DataFrame,
        current_time: datetime
    ) -> float:
        """Calculate current value of a position"""
        # Get pool data at current time
        pool_data = data[
            (data['pool'] == position['pool']) & 
            (data['timestamp'] <= current_time)
        ]
        
        if pool_data.empty:
            return position['entry_value']
        
        latest = pool_data.iloc[-1]
        
        # Simulate returns based on APY
        days_held = (current_time - position['entry_time']).days
        if days_held > 0:
            daily_return = latest['apy'] / 365 / 100
            compound_return = (1 + daily_return) ** days_held - 1
            
            # Add some noise/randomness
            noise = np.random.normal(0, 0.02)  # 2% daily volatility
            
            # Apply impermanent loss simulation (simplified)
            il_factor = 0.98 if days_held > 3 else 1.0
            
            value = position['entry_value'] * (1 + compound_return + noise) * il_factor
            return max(0, value)  # Can't go negative
        
        return position['entry_value']
    
    def _find_opportunities(
        self,
        data: pd.DataFrame,
        current_time: datetime,
        strategy: TradingStrategy
    ) -> List[Dict]:
        """Find pools that meet entry criteria"""
        # Get latest data for each pool
        latest_data = data[data['timestamp'] <= current_time].groupby('pool').last()
        
        # Apply filters
        opportunities = []
        for pool, row in latest_data.iterrows():
            if (row['apy'] >= strategy.entry_rules.min_apy and
                row['apy'] <= strategy.entry_rules.max_apy and
                row['tvl'] >= strategy.entry_rules.min_tvl and
                row['risk_score'] <= strategy.entry_rules.max_risk_score and
                row['sustainability_score'] >= strategy.entry_rules.min_sustainability_score):
                
                opportunities.append({
                    'pool': pool,
                    'apy': row['apy'],
                    'tvl': row['tvl'],
                    'risk_score': row['risk_score']
                })
        
        # Sort by APY
        opportunities.sort(key=lambda x: x['apy'], reverse=True)
        return opportunities[:3]  # Top 3
    
    def _calculate_metrics(
        self,
        strategy_name: str,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float,
        final_capital: float
    ) -> BacktestResult:
        """Calculate backtest metrics"""
        total_return = final_capital - initial_capital
        total_return_percent = (total_return / initial_capital) * 100
        
        # Trade statistics
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] <= 0]
        
        num_trades = len(self.trades)
        win_rate = len(winning_trades) / num_trades if num_trades > 0 else 0
        
        average_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        average_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        
        # Profit factor
        total_wins = sum(t['pnl'] for t in winning_trades)
        total_losses = abs(sum(t['pnl'] for t in losing_trades))
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Drawdown
        equity_values = [p['value'] for p in self.equity_curve]
        running_max = np.maximum.accumulate(equity_values)
        drawdown = (running_max - equity_values) / running_max
        max_drawdown_percent = np.max(drawdown) * 100 if len(drawdown) > 0 else 0
        max_drawdown = np.max(running_max - equity_values) if len(equity_values) > 0 else 0
        
        # Risk-adjusted returns
        if len(equity_values) > 1:
            returns = np.diff(equity_values) / equity_values[:-1]
            
            # Sharpe ratio (assuming 0% risk-free rate)
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(365) if np.std(returns) > 0 else 0
            
            # Sortino ratio (downside deviation)
            downside_returns = returns[returns < 0]
            downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
            sortino_ratio = np.mean(returns) / downside_std * np.sqrt(365) if downside_std > 0 else 0
            
            # Calmar ratio
            annual_return = total_return_percent * (365 / (end_date - start_date).days)
            calmar_ratio = annual_return / max_drawdown_percent if max_drawdown_percent > 0 else 0
        else:
            sharpe_ratio = sortino_ratio = calmar_ratio = 0
        
        return BacktestResult(
            strategy_name=strategy_name,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            total_return_percent=total_return_percent,
            num_trades=num_trades,
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            average_win=average_win,
            average_loss=average_loss,
            profit_factor=profit_factor,
            max_drawdown=max_drawdown,
            max_drawdown_percent=max_drawdown_percent,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            trades=self.trades,
            equity_curve=self.equity_curve
        )
    
    async def compare_strategies(
        self,
        strategies: List[TradingStrategy],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, BacktestResult]:
        """Compare multiple strategies"""
        results = {}
        
        for strategy in strategies:
            result = await self.run_backtest(strategy, start_date, end_date)
            results[strategy.name] = result
            
        return results