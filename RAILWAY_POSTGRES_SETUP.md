# PostgreSQL Setup Guide for Railway

## Step 1: Add PostgreSQL to Your Railway Project

1. Go to your Railway project dashboard
2. Click "New Service" or "+" button
3. Select "Database" → "Add PostgreSQL"
4. Railway will automatically provision a PostgreSQL database

## Step 2: Connect Backend to PostgreSQL

1. In your Railway dashboard, click on your backend service
2. Go to the "Variables" tab
3. Click "Add Reference Variable"
4. Select your PostgreSQL service
5. Choose `DATABASE_URL` from the dropdown
6. This will automatically inject the PostgreSQL connection string

## Step 3: Run Database Migrations

Once PostgreSQL is connected, you need to create all the tables. Here's how:

### Option A: Using Railway's Run Command (Recommended)

1. In your backend service settings on Railway
2. Add this to your "Deploy" settings under "Start Command":
   ```
   python -c "import asyncio; from database.setup import run_migrations; asyncio.run(run_migrations())" && python main.py
   ```

### Option B: Manual Migration via Railway Shell

1. Click on your backend service in Railway
2. Click "Connect" → "Railway Shell"
3. Run these commands:
   ```bash
   cd backend
   python
   ```
4. Then in Python:
   ```python
   import asyncio
   from database.setup import run_migrations
   asyncio.run(run_migrations())
   exit()
   ```

### Option C: Using SQL directly

1. In Railway, click on your PostgreSQL service
2. Click "Connect" → "Postgres Connection URL"
3. Use a PostgreSQL client (like pgAdmin or TablePlus) to connect
4. Run the SQL from `/backend/database/enhanced_schema.sql`

## Step 4: Verify Setup

After running migrations, your backend logs should show:
```
[DB] Connected to PostgreSQL: PostgreSQL 15.x on x86_64...
✅ Database tables created successfully!
```

## Database Tables Created

The full schema includes:

1. **pools_enhanced** - Discovered yield pools
2. **pool_risk_analysis** - Risk scores and analysis
3. **portfolio_positions** - Active positions
4. **position_snapshots** - Historical P&L tracking
5. **position_transactions** - Entry/exit transactions
6. **alerts** - Price and APY alerts
7. **alert_history** - Alert trigger history
8. **yield_opportunities** - High-yield opportunities
9. **pool_apy_history** - APY tracking over time
10. **wallet_connections** - Connected wallets
11. **trading_strategies** - Bot trading strategies
12. **strategy_executions** - Strategy execution history

## Environment Variables

Your backend will automatically have:
- `DATABASE_URL` - PostgreSQL connection string (auto-injected by Railway)

## Troubleshooting

1. **"Using local database URL" warning**
   - This means DATABASE_URL is not set
   - Check that you've added the reference variable in Railway

2. **Connection refused errors**
   - Ensure PostgreSQL service is running in Railway
   - Check that the reference variable is properly set

3. **Table not found errors**
   - Run the migrations as described above
   - Check backend logs for migration success

## Next Steps

Once PostgreSQL is set up:
1. Your risk analysis will persist across restarts
2. Position tracking will work properly
3. Historical data will be maintained
4. Analytics will show real trends

The backend will automatically use PostgreSQL for all database operations.