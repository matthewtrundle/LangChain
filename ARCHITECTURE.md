# 🏗️ Solana Degen Hunter - Architecture Overview

## System Components

### 1. **Multi-Agent AI System**

#### Coordinator Agent (`agents/coordinator_agent.py`)
- Orchestrates all other agents
- Processes natural language queries
- Delegates tasks to specialized agents
- Aggregates results

#### Scanner Agent (`agents/scanner_agent.py`)
- Discovers new pools from multiple sources
- Integrates with Raydium, Orca, Jupiter APIs
- Filters by APY, TVL, age criteria
- Real-time WebSocket monitoring

#### Analyzer Agent (`agents/analyzer_agent.py`)
- Deep risk analysis of pools
- Calculates degen scores
- Evaluates sustainability
- Detects potential rug pulls

#### Monitor Agent (`agents/monitor_agent.py`)
- Tracks active positions
- Monitors P&L in real-time
- Sends alerts for significant changes
- Manages exit signals

### 2. **Automated Trading Bot**

#### Trading Bot Service (`services/trading_bot.py`)
- Executes automated trading strategies
- Entry/exit logic based on rules
- Position sizing algorithms
- Risk management enforcement

#### Strategy System (`models/trading_strategy.py`)
- Configurable strategy presets
- Entry rules (APY, TVL, risk thresholds)
- Exit rules (stop loss, take profit, time limits)
- Position sizing methods
- Portfolio risk limits

#### Paper Trading (`services/paper_trading.py`)
- Virtual wallet simulation
- Realistic slippage modeling
- Performance tracking
- Risk-free testing environment

### 3. **Risk Analysis Engine**

#### Risk Analysis Service (`services/risk_analysis_service.py`)
- Runs every 5 minutes automatically
- Analyzes ALL discovered pools
- Calculates multiple risk metrics:
  - Overall risk score (0-100)
  - Degen score
  - Rug risk score
  - Sustainability score
  - Impermanent loss risk
  - Volatility metrics

#### Pool Validator (`tools/enhanced_pool_validator.py`)
- Validates pool data integrity
- Checks for suspicious patterns
- Filters out scam pools

### 4. **Data Layer**

#### Database Schema (`database/enhanced_schema.sql`)
```sql
pools_enhanced          -- Pool metadata and info
pool_risk_analysis      -- Risk scores and metrics
positions_enhanced      -- Active/closed positions
position_snapshots_hf   -- High-frequency P&L data
portfolio_history       -- Overall portfolio tracking
```

#### Caching Layer (`utils/cache.py`)
- Redis-like in-memory cache
- Reduces API calls
- TTL-based expiration
- Performance optimization

### 5. **External Integrations**

#### Helius Client (`tools/helius_client.py`)
- Solana RPC calls
- Token balance queries
- Transaction history
- WebSocket subscriptions

#### Raydium Scanner (`tools/raydium_scanner.py`)
- Direct Raydium API integration
- Real-time pool discovery
- APY calculations
- Volume/TVL data

#### Price Oracle (`services/price_oracle.py`)
- Multi-source price feeds
- Token price caching
- Slippage calculations

### 6. **Frontend Architecture**

#### Main Application (`app/page.tsx`)
- Tab-based navigation
- Real-time WebSocket updates
- Responsive design
- Dark theme with cyber aesthetics

#### Component Library
```
components/
├── OpportunityCard       -- Pool display cards
├── TradingBotControl     -- Bot management UI
├── portfolio/            -- Portfolio analytics
│   ├── PortfolioValueChart
│   ├── PnLBreakdown
│   ├── WinRateMeter
│   ├── PositionHistoryTable
│   └── BestWorstPositionCards
├── AnimatedHero          -- Landing animations
├── RiskVisualization     -- Risk score display
└── WalletDashboard       -- Wallet integration
```

#### State Management
- React hooks for local state
- WebSocket for real-time updates
- API client for data fetching
- No heavy state library needed

### 7. **API Architecture**

#### FastAPI Backend (`main.py`)
- RESTful endpoints
- WebSocket support
- CORS enabled
- Rate limiting
- Performance monitoring

#### Key Endpoints
```
/hunt                   -- Natural language search
/scan                   -- Direct pool scanning
/analyze                -- Risk analysis
/bot/*                  -- Trading bot control
/risk/*                 -- Risk data access
/paper-trading/*        -- Paper trading control
/backtest/*             -- Strategy backtesting
/ws                     -- WebSocket connection
```

### 8. **Security & Safety**

#### Rate Limiting (`middleware/rate_limiter.py`)
- API call limits
- Caching to reduce load
- Graceful degradation

#### Position Limits
- Max positions per protocol
- Concentration limits
- Daily loss limits
- Emergency stop functionality

#### Wallet Safety
- Paper trading mode
- Position size limits
- No private key storage
- Manual approval required

## Data Flow

```
User Query → Coordinator Agent
                ↓
         Task Distribution
         ↙      ↓      ↘
    Scanner  Analyzer  Monitor
       ↓        ↓        ↓
    Helius   Risk DB  Positions
       ↓        ↓        ↓
         Pool Results
              ↓
         Risk Analysis Service
              ↓
         Trading Bot (if enabled)
              ↓
         Position Entry/Exit
              ↓
         Portfolio Tracking
```

## Performance Considerations

### API Usage
- Helius: ~21,600 calls/day
- Caching reduces redundant calls
- WebSocket for real-time data
- Batch processing where possible

### Database
- Indexes on frequently queried fields
- Materialized views for analytics
- Hourly aggregations for charts
- Efficient time-series storage

### Frontend
- Lazy loading components
- Debounced search
- Optimistic UI updates
- Efficient re-renders

## Deployment

### Backend (Railway)
- Dockerfile provided
- Environment variables
- PostgreSQL addon
- Auto-scaling capable

### Frontend (Railway/Vercel)
- Next.js optimizations
- Static generation where possible
- API route proxying
- CDN distribution

## Monitoring

### Observability (`observability/`)
- Custom metrics collection
- Performance tracking
- Error logging
- Usage analytics

### Health Checks
- `/health` endpoint
- Service status monitoring
- Dependency checks
- Uptime tracking