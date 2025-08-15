# Position Tracking Setup Guide

## Railway PostgreSQL Setup

### 1. Create PostgreSQL Database on Railway

1. Go to your Railway project
2. Click "New Service" → "Database" → "PostgreSQL"
3. Wait for deployment
4. Click on the PostgreSQL service
5. Go to "Variables" tab
6. Copy the `DATABASE_URL`

### 2. Set Environment Variables

Create or update your `.env` file:

```bash
# Railway PostgreSQL
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@YOUR_HOST.railway.app:PORT/railway

# Helius API
HELIUS_API_KEY=your_helius_api_key

# Optional: OpenAI for agents
OPENAI_API_KEY=your_openai_api_key
```

### 3. Initialize Database Schema

Run the setup script to create tables:

```bash
cd backend
python setup_database.py
```

Or manually connect and run:
```bash
psql $DATABASE_URL < database/schema.sql
```

### 4. Test Connection

```bash
python test_position_tracking.py
```

## API Endpoints

### Position Management

```bash
# Enter a position
POST /api/positions/enter
{
  "wallet": "your_wallet_address",
  "pool_address": "pool_address",
  "protocol": "raydium",
  "token_a_symbol": "SOL",
  "token_b_symbol": "USDC",
  "token_a_mint": "So11111111111111111111111111111111111111112",
  "token_b_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "amount_a": 1.5,
  "amount_b": 150,
  "lp_tokens": 15,
  "tx_hash": "your_transaction_hash"
}

# Get all positions
GET /api/positions?wallet=your_wallet_address

# Get single position
GET /api/positions/{position_id}

# Exit position
POST /api/positions/{position_id}/exit
{
  "tx_hash": "exit_transaction_hash"
}

# Sync position
POST /api/positions/{position_id}/sync

# Get P&L data
GET /api/positions/{position_id}/pnl

# Get portfolio summary
GET /api/portfolio/summary?wallet=your_wallet_address
```

## Testing with Mock Data

1. Run the test script to create sample positions:
```bash
python test_position_tracking.py --create-samples
```

2. Start the API server:
```bash
uvicorn main:app --reload
```

3. Test via API:
```bash
# Get portfolio summary
curl http://localhost:8000/api/portfolio/summary?wallet=DemoWallet111111111111111111111111111111111

# Enter a new position
curl -X POST http://localhost:8000/api/positions/enter \
  -H "Content-Type: application/json" \
  -d '{
    "wallet": "DemoWallet111111111111111111111111111111111",
    "pool_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
    "protocol": "raydium",
    "token_a_symbol": "BONK",
    "token_b_symbol": "USDC",
    "token_a_mint": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "token_b_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "amount_a": 1000000,
    "amount_b": 12.34,
    "lp_tokens": 100.5,
    "tx_hash": "TestTx123"
  }'
```

## Monitoring & Alerts

The position monitor runs every 30 seconds to:
- Update position values
- Calculate P&L and IL
- Check exit conditions
- Send alerts if configured

To start the monitor:
```bash
python run_monitor.py
```

## Frontend Integration

The position data is available via REST API and can be consumed by the Next.js frontend:

```typescript
// Get user positions
const positions = await fetch(`/api/positions?wallet=${walletAddress}`);

// Get position P&L
const pnl = await fetch(`/api/positions/${positionId}/pnl`);
```

## Troubleshooting

### Database Connection Issues
- Ensure DATABASE_URL is correctly formatted
- Check Railway service is running
- Verify network connectivity

### Price Oracle Issues
- Ensure HELIUS_API_KEY is set
- Check API rate limits
- Fallback prices are used if API fails

### Position Sync Issues
- Check Helius RPC endpoint
- Verify pool addresses are valid
- Check transaction hashes

## Next Steps

1. **Add WebSocket Support**: Real-time position updates
2. **Implement Alerts**: Email/Discord/Telegram notifications
3. **Add Historical Charts**: Position value over time
4. **Multi-wallet Support**: Track multiple wallets
5. **Export Features**: CSV/JSON export for taxes