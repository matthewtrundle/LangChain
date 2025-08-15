# 🚀 Solana Degen Yield Hunter

An intelligent yield farming assistant for Solana that uses AI agents to discover high-APY opportunities, analyze risk, and execute automated trading strategies.

## 🌟 Overview

This project combines:
- **Multi-Agent AI System** using LangChain for intelligent pool discovery
- **Automated Trading Bot** with configurable strategies
- **Real-time Risk Analysis** for all discovered pools
- **Beautiful Next.js Frontend** with live updates
- **Paper Trading Mode** for risk-free testing

## 🏗️ Architecture

### Backend (Python/FastAPI)
```
backend/
├── agents/           # AI agents for different tasks
├── services/         # Core services (trading bot, risk analysis, etc.)
├── models/           # Data models and strategies
├── tools/            # External integrations (Helius, Raydium, etc.)
├── database/         # PostgreSQL schemas and connections
└── main.py          # FastAPI application
```

### Frontend (Next.js/TypeScript)
```
frontend/
├── app/             # Next.js app router
├── components/      # React components
├── lib/             # Utilities and API clients
└── styles/          # Tailwind CSS
```

## 🎯 Key Features

### 1. **Pool Discovery**
- Scans Solana DEXs (Raydium, Orca, etc.) for high-yield pools
- Filters by APY, TVL, and risk parameters
- Real-time WebSocket updates for new opportunities

### 2. **Risk Analysis**
- Automatic risk scoring for ALL discovered pools
- Analyzes:
  - Rug pull risk
  - Impermanent loss potential
  - Sustainability metrics
  - Liquidity depth
  - Volume patterns

### 3. **Automated Trading Bot**
Three preset strategies:
- **Conservative**: Low risk, 5% stop loss, 15% take profit
- **Balanced**: Moderate risk, 10% stop loss, 30% take profit  
- **Degen**: High risk, 20% stop loss, 100% take profit

Features:
- Smart position sizing
- Automatic entry/exit based on rules
- Portfolio rebalancing
- Daily loss limits
- Rug pull detection

### 4. **Portfolio Analytics**
- Real-time P&L tracking
- Performance metrics and charts
- Position history with detailed analysis
- Win rate visualization
- Fee and impermanent loss breakdown

### 5. **Paper Trading**
- Test strategies with virtual $10,000
- Realistic simulation including slippage and gas
- Track performance before risking real funds

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- PostgreSQL
- Helius API key
- OpenAI API key (for LangChain agents)

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export HELIUS_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export DATABASE_URL="postgresql://user:pass@localhost/solana_hunter"

# Run database migrations
python setup_database.py

# Start the backend
python main.py
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

### Deploy to Production
```bash
# Frontend (Railway/Vercel)
npm run build

# Backend (Railway)
# Dockerfile included for deployment
```

## 📊 API Usage & Costs

### Helius API Usage
- **Daily**: ~21,600 calls (with 5 active positions)
- **Monthly**: ~650,000 calls
- **Recommendation**: Paid Helius plan required

### OpenAI Usage
- Minimal - only for complex analysis tasks
- Approximately $5-10/month for moderate usage

## 🎮 How to Use

### 1. **Discover Pools**
- Use the search bar to find pools (e.g., "Find SOL pools with 500%+ APY")
- Or use quick scan buttons for preset searches
- Risk analysis runs automatically for all pools

### 2. **Manual Trading**
- Click "Enter Position" on any pool card
- Monitor positions in the Active Positions tab
- View analytics in Portfolio Dashboard

### 3. **Automated Trading**
1. Enable Paper Trading (recommended for testing)
2. Select a strategy (Conservative/Balanced/Degen)
3. Click "Start Bot"
4. Monitor performance in real-time

### 4. **Risk Management**
- Each pool shows risk scores automatically
- Red = High Risk, Yellow = Moderate, Green = Low
- Bot respects risk limits based on strategy

## 🔧 Configuration

### Trading Strategies (`backend/models/trading_strategy.py`)
Customize entry/exit rules, position sizing, and risk limits.

### Risk Analysis (`backend/services/risk_analysis_service.py`)
Adjust risk scoring algorithms and thresholds.

### API Endpoints
- `/bot/start` - Start trading bot
- `/bot/stop` - Stop trading bot
- `/bot/strategies` - Get available strategies
- `/risk/pool/{address}` - Get risk analysis
- `/paper-trading/enable` - Enable paper trading
- `/backtest/run` - Run strategy backtest

## 🛡️ Safety Features

1. **Position Limits**: Max positions per protocol/token
2. **Stop Losses**: Automatic exit on losses
3. **Daily Loss Limits**: Circuit breaker for bad days
4. **Rug Detection**: Monitors for sudden TVL/volume drops
5. **Gas Optimization**: Considers transaction costs
6. **Manual Override**: Stop bot anytime

## 📈 Performance Tracking

The system tracks:
- Win rate and profit factor
- Sharpe ratio and max drawdown
- Best/worst trades
- Fee efficiency
- Impermanent loss impact

## 🧪 Testing

### Paper Trading
Best way to test strategies:
```
1. Enable paper trading in UI
2. Start bot with chosen strategy
3. Monitor virtual trades
4. Analyze results before going live
```

### Backtesting
Test strategies on historical data:
```bash
curl -X POST http://localhost:8000/backtest/run \
  -H "Content-Type: application/json" \
  -d '{"strategy_type": "balanced", "days_back": 30}'
```

## ⚠️ Disclaimers

1. **High Risk**: DeFi yield farming is extremely risky
2. **No Guarantees**: Past performance doesn't predict future results
3. **DYOR**: Always do your own research
4. **Start Small**: Test with small amounts first
5. **Monitor Closely**: Bot requires supervision

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📝 License

MIT License - see LICENSE file for details

---

Built with ❤️ for the Solana degen community