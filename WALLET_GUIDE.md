# Wallet & Position Management Guide

## Overview

The Solana Degen Hunter includes a fully-featured mock wallet system for testing yield farming strategies without using real funds. The wallet starts with $10,000 and tracks all your positions, transactions, and performance metrics.

## Features

### 🏦 Mock Wallet
- **Starting Balance**: $10,000 (customizable)
- **Transaction Tracking**: Every action is recorded
- **Performance Metrics**: Win rate, P&L, best/worst positions
- **Gas Fee Simulation**: Realistic transaction costs
- **Development Reset**: Reset wallet for testing

### 📊 Position Management
- **Risk Limits**:
  - Maximum 5 positions at once
  - Maximum $1,000 per position
  - Maximum $5,000 total exposure
- **Automated Exit Rules**:
  - Stop Loss: -10%
  - Take Profit: +50%
  - APY Drop: -50% from entry
  - Low Liquidity: TVL < $10k
  - Rug Risk Detection

### 📈 Performance Tracking
- Real-time P&L calculation
- Position-by-position performance
- Win rate statistics
- Transaction history
- Fee tracking

## How to Use

### 1. Access Portfolio
Click the **POSITIONS** button in the header to open the Portfolio Management view.

### 2. Enter a Position
1. Find a pool you want to enter
2. Click **"Enter $100"** (or custom amount)
3. The position entry modal will show:
   - Available wallet balance
   - Custom amount input
   - Quick amount buttons ($100, $250, $500, $1000)
   - Estimated daily returns

### 3. Monitor Positions
The Position Dashboard shows:
- **Portfolio Overview**: Total invested, current value, P&L
- **Active Positions**: Live positions with current performance
- **Position History**: Closed positions with exit reasons

### 4. Exit Positions
Positions can exit in two ways:
- **Manual Exit**: Click "Exit" button on any active position
- **Automatic Exit**: System exits based on predefined rules

### 5. Track Performance
The Wallet Dashboard displays:
- Current balance with P&L
- Performance metrics (win rate, average P&L)
- Recent transactions
- Total fees paid

## API Endpoints

### Wallet Endpoints
```bash
# Get wallet balance and summary
GET /wallet

# Get transaction history
GET /wallet/transactions?limit=10

# Get performance metrics
GET /wallet/performance

# Reset wallet (dev only)
POST /wallet/reset
```

### Position Endpoints
```bash
# Enter a new position
POST /position/enter
{
  "pool_address": "...",
  "pool_data": {...},
  "amount": 100
}

# Exit a position
POST /position/exit
{
  "position_id": "...",
  "reason": "manual"
}

# Get all positions
GET /positions

# Get specific position
GET /position/{position_id}

# Check positions (triggers monitor)
GET /monitor/check
```

## Testing

### Run the Wallet Demo
```bash
cd backend
python test_wallet.py
```

This will simulate:
- Entering multiple positions
- Position value changes
- Automatic and manual exits
- Final performance summary

### Reset for Testing
In development mode, you can reset the wallet:
1. Click "Reset Wallet" in the Wallet Dashboard
2. Or call `POST /wallet/reset`

## Position Exit Rules

### Stop Loss (-10%)
Automatically exits when position loses 10% of value

### Take Profit (+50%)
Automatically exits when position gains 50%

### APY Degradation
Exits if APY drops more than 50% from entry

### Low Liquidity
Exits if pool TVL drops below $10,000

### Rug Risk
Exits immediately if rug pull indicators detected

## Best Practices

1. **Start Small**: Test with $100 positions first
2. **Diversify**: Don't put all funds in one pool
3. **Monitor APY**: High APYs often degrade quickly
4. **Check Liquidity**: Ensure pools have sufficient TVL
5. **Review History**: Learn from past trades

## Example Workflow

1. **Scan for Opportunities**
   ```
   Quick Scan 500%+ → Find 10 pools
   ```

2. **Analyze Top Pools**
   ```
   Analyze BONK/SOL → Degen Score: 7.5/10
   ```

3. **Enter Position**
   ```
   Enter $250 → Position created
   ```

4. **Monitor Performance**
   ```
   +15% after 6 hours → Still holding
   ```

5. **Exit Strategy**
   ```
   Auto-exit at +50% → Profit locked in
   ```

## Troubleshooting

### "Insufficient Balance"
- Check wallet balance in dashboard
- Ensure you have funds after fees
- Consider smaller position size

### "Maximum Positions Reached"
- Exit some positions first
- System limits to 5 active positions

### "Position Size Too Large"
- Maximum $1,000 per position
- Split into multiple smaller positions

### Position Not Updating
- Refresh the dashboard
- Check `/monitor/check` endpoint
- Positions update every 30 seconds

## Development

The wallet system uses:
- In-memory storage (resets on restart)
- Simulated price movements
- Mock gas fees (0.01 SOL per transaction)
- Configurable parameters in `config.py`

For production, you would:
- Use a real database
- Integrate with actual wallets
- Fetch real-time prices
- Calculate actual gas fees