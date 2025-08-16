# Trading Bot System Analysis

## Current Issues Identified

1. **Single Strategy Limitation**: The trading bot currently only runs ONE strategy at a time (stored in `self.strategy`)
2. **No Strategy-Specific UIs**: All strategies use the same UI - there's no differentiated view per strategy
3. **Wallet Connection Confusion**: The portfolio/wallet dashboard fetches from `/wallet` endpoint which seems to require a real wallet connection
4. **Paper Trading Integration**: Paper trading exists but isn't well integrated with the UI components

## Current Architecture

### Backend
- `TradingBot` class: Single strategy instance
- `STRATEGY_PRESETS`: Conservative, Balanced, Degen strategies defined
- `paper_trading.py`: Separate paper wallet implementation
- Position tracking in database

### Frontend  
- `TradingBotControl.tsx`: Controls bot on/off and strategy selection
- `WalletDashboard.tsx`: Shows wallet balance and P&L
- `PositionDashboard.tsx`: Shows active positions
- No strategy-specific views

## What's Missing

1. **Multi-Strategy Support**
   - Bot can only run one strategy
   - No way to run Conservative + Degen simultaneously
   - No strategy isolation

2. **Paper Trading UI Integration**
   - Paper trading endpoints exist (`/paper-trading/*`)
   - But UI components use real wallet endpoints (`/wallet`)
   - No clear switch between paper/real modes

3. **Strategy-Specific Dashboards**
   - All strategies share same UI
   - No custom views for different risk profiles
   - No strategy comparison view

## Proposed Improvements

### 1. Multi-Strategy Architecture
```python
class MultiStrategyBot:
    def __init__(self):
        self.strategies = {}  # strategy_id -> TradingBot instance
        self.enabled_strategies = set()
    
    def add_strategy(self, strategy_id: str, strategy: TradingStrategy):
        self.strategies[strategy_id] = TradingBot(strategy)
    
    def enable_strategy(self, strategy_id: str):
        self.enabled_strategies.add(strategy_id)
        asyncio.create_task(self.strategies[strategy_id].start())
```

### 2. Paper Trading Mode Toggle
- Add global paper trading mode switch
- Route wallet/position calls to paper trading endpoints when enabled
- Clear visual indicator of paper vs real mode

### 3. Strategy-Specific UI Components
- Conservative Strategy View: Focus on safety metrics, stable pools
- Balanced Strategy View: Mix of metrics, moderate opportunities  
- Degen Strategy View: High-risk pools, APY focus, quick actions

### 4. Unified Portfolio View
- Show all strategies' performance side-by-side
- Compare P&L across strategies
- Aggregate and per-strategy metrics

## Questions for GPT-4o

1. Should we implement a Strategy Manager service that coordinates multiple bots?
2. How should we handle position limits across multiple strategies?
3. What's the best way to switch between paper/real trading in the UI?
4. Should each strategy have its own wallet/capital allocation?
5. How to visualize multi-strategy performance effectively?