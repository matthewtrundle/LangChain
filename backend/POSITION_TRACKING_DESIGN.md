# Position Tracking & P&L System - Comprehensive Design Document

## Overview

The Position Tracking system is the core component that transforms our yield hunter from a discovery tool into a complete portfolio management system. It tracks user positions, calculates real-time P&L including impermanent loss, and provides actionable exit recommendations.

## System Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        Position Tracking System                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐      ┌─────────────────┐                 │
│  │ Position Manager│      │  Price Oracle    │                 │
│  │                 │◄────►│  (Helius/Jupiter)│                 │
│  └────────┬────────┘      └─────────────────┘                 │
│           │                                                     │
│  ┌────────▼────────┐      ┌─────────────────┐                 │
│  │ Position Store  │      │ P&L Calculator   │                 │
│  │ (In-Memory +    │◄────►│ - Fees Earned    │                 │
│  │  Persistent)    │      │ - IL Calculation │                 │
│  └────────┬────────┘      │ - Net Returns    │                 │
│           │               └─────────────────┘                 │
│  ┌────────▼────────┐      ┌─────────────────┐                 │
│  │ Monitor Agent   │      │ Alert Engine     │                 │
│  │ - Track Changes │─────►│ - APY Drops      │                 │
│  │ - Analyze Trends│      │ - IL Thresholds  │                 │
│  └─────────────────┘      │ - Exit Signals   │                 │
│                           └─────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

## Data Models

### 1. Position Model
```python
class Position:
    # Identity
    id: str                          # Unique position ID
    user_wallet: str                 # User's Solana wallet
    pool_address: str                # Pool contract address
    protocol: str                    # raydium/orca/meteora
    
    # Entry Data
    entry_timestamp: datetime
    entry_price_a: float            # Token A price at entry
    entry_price_b: float            # Token B price at entry
    entry_amount_a: float           # Amount of token A
    entry_amount_b: float           # Amount of token B
    entry_lp_tokens: float          # LP tokens received
    entry_tx_hash: str              # Solana transaction
    
    # Current State
    status: PositionStatus          # ACTIVE/CLOSED/PENDING
    current_amount_a: float         # Current token A in pool
    current_amount_b: float         # Current token B in pool
    fees_earned_a: float            # Accumulated fees token A
    fees_earned_b: float            # Accumulated fees token B
    
    # Exit Data (if closed)
    exit_timestamp: Optional[datetime]
    exit_price_a: Optional[float]
    exit_price_b: Optional[float]
    exit_amount_a: Optional[float]
    exit_amount_b: Optional[float]
    exit_tx_hash: Optional[str]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    last_sync: datetime             # Last on-chain sync
```

### 2. Position Snapshot Model
```python
class PositionSnapshot:
    # Track position value over time
    position_id: str
    timestamp: datetime
    
    # Prices
    price_a: float
    price_b: float
    
    # Values
    value_usd: float
    fees_earned_usd: float
    impermanent_loss_usd: float
    net_pnl_usd: float
    net_pnl_percent: float
    
    # Pool Metrics
    pool_tvl: float
    pool_apy: float
    pool_volume_24h: float
```

### 3. Alert Configuration Model
```python
class AlertConfig:
    user_wallet: str
    position_id: Optional[str]      # None for global alerts
    
    # Alert Types
    apy_drop_threshold: float       # Alert if APY drops by X%
    il_threshold: float             # Alert if IL exceeds X%
    profit_target: float            # Alert when profit hits X%
    stop_loss: float                # Alert when loss hits X%
    
    # Delivery
    webhook_url: Optional[str]
    email: Optional[str]
    telegram_chat_id: Optional[str]
```

## Core Services

### 1. Position Manager Service
```python
class PositionManager:
    """Central service for position lifecycle management"""
    
    async def enter_position(
        wallet: str,
        pool_address: str,
        amounts: Dict[str, float],
        tx_hash: str
    ) -> Position:
        """Record new position entry"""
        
    async def sync_position(position_id: str) -> Position:
        """Sync position with on-chain data"""
        
    async def exit_position(
        position_id: str,
        tx_hash: str
    ) -> Position:
        """Mark position as exited"""
        
    async def get_user_positions(
        wallet: str,
        status: Optional[PositionStatus] = None
    ) -> List[Position]:
        """Get all positions for a wallet"""
```

### 2. P&L Calculator Service
```python
class PnLCalculator:
    """Calculate profit/loss including impermanent loss"""
    
    def calculate_impermanent_loss(
        entry_price_a: float,
        entry_price_b: float,
        current_price_a: float,
        current_price_b: float,
        entry_amount_a: float,
        entry_amount_b: float
    ) -> ImpermanentLossResult:
        """Calculate IL using standard formula"""
        
    def calculate_fees_earned(
        position: Position,
        pool_data: PoolData
    ) -> FeesEarnedResult:
        """Calculate fees based on pool volume and share"""
        
    def calculate_net_pnl(
        position: Position,
        current_prices: Dict[str, float]
    ) -> PnLResult:
        """Calculate total P&L including fees minus IL"""
        
    def calculate_break_even_time(
        position: Position,
        current_apy: float
    ) -> BreakEvenResult:
        """Calculate time to recover IL through fees"""
```

### 3. Position Monitor Agent
```python
class PositionMonitorAgent(BaseAgent):
    """LangChain agent for intelligent position monitoring"""
    
    async def analyze_position_health(
        position: Position
    ) -> PositionAnalysis:
        """Comprehensive position analysis"""
        
    async def generate_exit_recommendation(
        position: Position,
        market_data: MarketData
    ) -> ExitRecommendation:
        """AI-powered exit recommendations"""
        
    async def monitor_all_positions(self):
        """Continuous monitoring loop"""
```

### 4. Price Oracle Service
```python
class PriceOracle:
    """Real-time price feeds from multiple sources"""
    
    async def get_token_price(
        mint: str,
        source: PriceSource = "jupiter"
    ) -> float:
        """Get current token price in USD"""
        
    async def subscribe_price_updates(
        mints: List[str],
        callback: Callable
    ):
        """WebSocket subscription for real-time updates"""
        
    async def get_historical_prices(
        mint: str,
        start: datetime,
        end: datetime
    ) -> List[PricePoint]:
        """Historical price data for backtesting"""
```

## Data Flow

### 1. Position Entry Flow
```
User enters pool → Frontend captures TX → Backend:
1. Parse transaction for pool & amounts
2. Fetch current prices from oracle
3. Create Position record
4. Start monitoring
5. Return position details to frontend
```

### 2. Real-Time Monitoring Flow
```
Every 30 seconds:
1. Fetch all active positions
2. Get current prices for all tokens
3. Calculate current P&L for each position
4. Check alert thresholds
5. Store snapshot for history
6. Send alerts if triggered
```

### 3. Position Sync Flow
```
Every 5 minutes (or on-demand):
1. Query on-chain data via Helius
2. Update position balances
3. Calculate fees earned
4. Update position record
5. Trigger recalculation
```

## API Endpoints

### Position Management
```typescript
POST   /api/positions/enter
GET    /api/positions
GET    /api/positions/:id
POST   /api/positions/:id/exit
POST   /api/positions/:id/sync
DELETE /api/positions/:id

// Bulk operations
POST   /api/positions/sync-all
GET    /api/positions/export
```

### P&L Analytics
```typescript
GET    /api/positions/:id/pnl
GET    /api/positions/:id/history
GET    /api/positions/:id/forecast
GET    /api/portfolio/summary
GET    /api/portfolio/performance
```

### Alerts & Monitoring
```typescript
GET    /api/alerts
POST   /api/alerts
PUT    /api/alerts/:id
DELETE /api/alerts/:id
GET    /api/positions/:id/recommendations
```

## Frontend Components

### 1. Position Dashboard
```tsx
<PositionDashboard>
  <PortfolioSummary>
    - Total Value Locked
    - Total P&L (USD & %)
    - Active Positions Count
    - 24h Performance
  </PortfolioSummary>
  
  <PositionGrid>
    <PositionCard>
      - Pool Name & Protocol
      - Current Value
      - P&L with IL breakdown
      - APY (current vs entry)
      - Time in Position
      - Quick Actions (Exit, Sync)
    </PositionCard>
  </PositionGrid>
  
  <PerformanceChart>
    - Portfolio value over time
    - P&L breakdown by position
  </PerformanceChart>
</PositionDashboard>
```

### 2. Position Detail View
```tsx
<PositionDetail>
  <PnLBreakdown>
    - Entry Value vs Current Value
    - Fees Earned
    - Impermanent Loss
    - Net P&L
  </PnLBreakdown>
  
  <ILCalculator>
    - Visual IL curve
    - Break-even calculator
    - "What-if" scenarios
  </ILCalculator>
  
  <ExitAnalysis>
    - AI recommendations
    - Optimal exit timing
    - Tax implications
  </ExitAnalysis>
  
  <HistoricalChart>
    - Position value over time
    - APY trends
    - Volume & TVL
  </HistoricalChart>
</PositionDetail>
```

## Integration Points

### 1. Wallet Integration
- Connect via Phantom/Solflare
- Read LP token balances
- Sign transactions for entry/exit
- Auto-discover existing positions

### 2. DEX Protocol Integration
```python
# Protocol adapters for each DEX
class ProtocolAdapter:
    async def get_pool_info(pool_address: str) -> PoolInfo
    async def get_user_position(wallet: str, pool: str) -> UserPosition
    async def calculate_fees_earned(position: Position) -> float
```

### 3. Helius Integration
- WebSocket for real-time updates
- Enhanced transaction parsing
- Historical data for backtesting
- Webhook for position changes

## Storage Strategy

### 1. Real-Time Data (Redis)
```python
# Fast access for active monitoring
positions:{wallet}:{position_id}  # Current position state
snapshots:{position_id}:latest    # Latest snapshot
prices:{token_mint}               # Current prices with TTL
alerts:pending                    # Pending alerts queue
```

### 2. Historical Data (PostgreSQL)
```sql
-- Core tables
positions              -- All positions (active & closed)
position_snapshots     -- Historical snapshots
position_transactions  -- Entry/exit transactions
alert_configurations   -- User alert settings
alert_history         -- Sent alerts log
```

### 3. Cache Strategy
- Position data: 30-second cache
- Price data: 5-second cache
- Pool data: 60-second cache
- Historical data: 1-hour cache

## Security Considerations

### 1. Data Privacy
- Never store private keys
- Wallet addresses are hashed for storage
- Position data encrypted at rest
- API requires authentication

### 2. Read-Only Access
- Only read blockchain data
- No transaction signing in backend
- Position entry via TX hash only
- Manual user confirmation for exits

### 3. Data Validation
- Verify TX signatures
- Validate pool addresses
- Confirm token mints
- Sanity check calculations

## Performance Optimization

### 1. Batch Processing
- Batch price queries
- Bulk position updates
- Grouped alert sending
- Efficient snapshot storage

### 2. Caching Strategy
- Multi-level caching
- Smart invalidation
- Precomputed aggregates
- CDN for static data

### 3. Database Optimization
- Indexed queries
- Partitioned tables
- Materialized views
- Query optimization

## Testing Strategy

### 1. Unit Tests
- P&L calculations
- IL formulas
- Alert logic
- Data models

### 2. Integration Tests
- DEX adapters
- Price oracles
- Database operations
- API endpoints

### 3. E2E Tests
- Position lifecycle
- Alert delivery
- Performance under load
- Edge cases

## Deployment Considerations

### 1. Infrastructure
- API: Vercel/Railway
- Database: Supabase/Neon
- Cache: Upstash Redis
- Monitoring: Datadog

### 2. Scaling Strategy
- Horizontal API scaling
- Read replicas for DB
- Queue for heavy tasks
- Rate limiting

### 3. Monitoring
- Position sync health
- Alert delivery status
- API performance
- Error tracking

## Future Enhancements

### Phase 1 (Current)
- Basic position tracking
- Simple P&L calculation
- Manual position entry
- Basic alerts

### Phase 2
- Auto-discovery of positions
- Advanced IL strategies
- Portfolio optimization
- Tax reporting

### Phase 3
- Cross-chain positions
- Automated rebalancing
- Social features
- Advanced analytics

## Success Metrics

### Technical Metrics
- Position sync accuracy: >99.9%
- P&L calculation time: <100ms
- Alert delivery time: <5s
- API uptime: >99.5%

### User Metrics
- Positions tracked per user
- Alert engagement rate
- Exit recommendation accuracy
- User retention rate

## Risk Mitigation

### 1. Data Accuracy
- Multiple price sources
- On-chain verification
- Calculation validation
- User confirmation

### 2. System Reliability
- Graceful degradation
- Backup data sources
- Error recovery
- Manual overrides

### 3. User Protection
- Clear risk warnings
- Conservative calculations
- Transparent methodology
- Educational content

---

This design document serves as the single source of truth for the Position Tracking system. All implementation decisions should reference and align with this specification.