# Direct PostgreSQL Setup Instructions

Since I can't run Python scripts directly on your machine, here's how to set up your database:

## Method 1: Using psql Command Line

```bash
# Connect to your Railway PostgreSQL
psql "postgresql://postgres:PTsgRXKJImryLugsgsXfeMoTpBdFaWhv@mainline.proxy.rlwy.net:54694/railway"

# Once connected, run:
\i backend/database/enhanced_schema.sql

# Or copy and paste the contents of enhanced_schema.sql
```

## Method 2: Using a PostgreSQL GUI Client

1. Download a PostgreSQL client like:
   - **TablePlus** (recommended): https://tableplus.com/
   - **pgAdmin**: https://www.pgadmin.org/
   - **DBeaver**: https://dbeaver.io/

2. Create a new connection with these details:
   - **Host**: mainline.proxy.rlwy.net
   - **Port**: 54694
   - **Database**: railway
   - **Username**: postgres
   - **Password**: PTsgRXKJImryLugsgsXfeMoTpBdFaWhv

3. Once connected, open and run the SQL file:
   `backend/database/enhanced_schema.sql`

## Method 3: Using Railway CLI

If you have Railway CLI installed:

```bash
cd backend
railway run python run_migrations.py
```

## Method 4: Update Your Backend Start Command

In your Railway backend service settings, update the start command to:

```bash
cd backend && python run_migrations.py && python main.py
```

This will run migrations automatically when your backend deploys.

## What Gets Created

The migration will create these 12 tables:

1. **pools_enhanced** - Discovered yield farming pools
2. **pool_risk_analysis** - Risk analysis results
3. **portfolio_positions** - Your active positions
4. **position_snapshots** - P&L tracking snapshots
5. **position_transactions** - Entry/exit transactions
6. **alerts** - Price and APY alerts
7. **alert_history** - Alert trigger history
8. **yield_opportunities** - High-yield opportunities
9. **pool_apy_history** - Historical APY data
10. **wallet_connections** - Connected wallets
11. **trading_strategies** - Trading bot strategies
12. **strategy_executions** - Strategy execution logs

## Verify Setup

After running the migration, you should be able to:
1. See all tables in your PostgreSQL client
2. Your backend logs should show "Connected to PostgreSQL"
3. Risk analysis data will persist
4. Position tracking will work properly