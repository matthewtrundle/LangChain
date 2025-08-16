#!/usr/bin/env python3
"""
Check which tables exist and run the full enhanced schema
"""

import subprocess
from pathlib import Path

def check_and_complete_setup():
    db_url = "postgresql://postgres:PTsgRXKJImryLugsgsXfeMoTpBdFaWhv@mainline.proxy.rlwy.net:54694/railway"
    
    print("🔍 Checking database setup...")
    print("=" * 60)
    
    # SQL to check existing tables and run missing ones
    check_sql = """
-- List current tables
\\echo '📊 Current tables in database:'
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Check for missing tables
\\echo ''
\\echo '🔍 Checking for missing tables...'

-- Create pool_risk_analysis if missing
CREATE TABLE IF NOT EXISTS pool_risk_analysis (
    pool_address VARCHAR(100) PRIMARY KEY,
    analyzed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    overall_risk_score INTEGER,
    degen_score INTEGER,
    rug_risk_score INTEGER,
    sustainability_score NUMERIC(3, 1),
    liquidity_score NUMERIC(3, 1),
    volume_score NUMERIC(3, 1),
    impermanent_loss_risk INTEGER,
    volatility_24h NUMERIC(10, 2),
    risk_rating VARCHAR(20),
    recommendation TEXT,
    apy NUMERIC(10, 2),
    tvl NUMERIC(20, 2),
    volume_24h NUMERIC(20, 2),
    volume_7d NUMERIC(20, 2),
    volume_to_tvl_ratio NUMERIC(10, 4),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create portfolio_positions if missing
CREATE TABLE IF NOT EXISTS portfolio_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_address VARCHAR(100) NOT NULL,
    entry_price NUMERIC(20, 8),
    entry_amount NUMERIC(20, 8),
    entry_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    exit_price NUMERIC(20, 8),
    exit_amount NUMERIC(20, 8),
    exit_timestamp TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    realized_pnl NUMERIC(20, 8),
    unrealized_pnl NUMERIC(20, 8),
    fees_paid NUMERIC(20, 8),
    gas_costs NUMERIC(20, 8),
    impermanent_loss NUMERIC(20, 8),
    notes TEXT,
    wallet_address VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create position_transactions if missing
CREATE TABLE IF NOT EXISTS position_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    position_id UUID REFERENCES portfolio_positions(id),
    transaction_type VARCHAR(20) NOT NULL,
    transaction_hash VARCHAR(100),
    amount NUMERIC(20, 8),
    price NUMERIC(20, 8),
    fees NUMERIC(20, 8),
    gas_cost NUMERIC(20, 8),
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create alerts if missing
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_address VARCHAR(100) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    condition VARCHAR(20) NOT NULL,
    threshold_value NUMERIC(20, 8),
    current_value NUMERIC(20, 8),
    is_active BOOLEAN DEFAULT true,
    last_triggered TIMESTAMP,
    notification_channel VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create alert_history if missing
CREATE TABLE IF NOT EXISTS alert_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID REFERENCES alerts(id),
    triggered_at TIMESTAMP NOT NULL DEFAULT NOW(),
    triggered_value NUMERIC(20, 8),
    message TEXT,
    acknowledged BOOLEAN DEFAULT false,
    acknowledged_at TIMESTAMP
);

-- Create yield_opportunities if missing
CREATE TABLE IF NOT EXISTS yield_opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pool_address VARCHAR(100) NOT NULL,
    protocol VARCHAR(50),
    token_pair VARCHAR(100),
    apy NUMERIC(10, 2),
    tvl NUMERIC(20, 2),
    risk_score INTEGER,
    discovered_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB
);

-- Create pool_apy_history if missing
CREATE TABLE IF NOT EXISTS pool_apy_history (
    pool_address VARCHAR(100),
    timestamp TIMESTAMP NOT NULL,
    apy NUMERIC(10, 2),
    tvl NUMERIC(20, 2),
    volume_24h NUMERIC(20, 2),
    PRIMARY KEY (pool_address, timestamp)
);

-- Create wallet_connections if missing
CREATE TABLE IF NOT EXISTS wallet_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_address VARCHAR(100) UNIQUE NOT NULL,
    wallet_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    last_sync TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create trading_strategies if missing
CREATE TABLE IF NOT EXISTS trading_strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    strategy_type VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT false,
    parameters JSONB,
    performance_metrics JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create strategy_executions if missing
CREATE TABLE IF NOT EXISTS strategy_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id UUID REFERENCES trading_strategies(id),
    pool_address VARCHAR(100),
    action VARCHAR(20) NOT NULL,
    amount NUMERIC(20, 8),
    price NUMERIC(20, 8),
    reason TEXT,
    executed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    transaction_hash VARCHAR(100),
    status VARCHAR(20) DEFAULT 'completed',
    pnl NUMERIC(20, 8)
);

-- Create indexes if missing
CREATE INDEX IF NOT EXISTS idx_positions_status ON portfolio_positions(status);
CREATE INDEX IF NOT EXISTS idx_positions_wallet ON portfolio_positions(wallet_address);
CREATE INDEX IF NOT EXISTS idx_alerts_active ON alerts(is_active);
CREATE INDEX IF NOT EXISTS idx_alerts_pool ON alerts(pool_address);
CREATE INDEX IF NOT EXISTS idx_risk_analysis_rating ON pool_risk_analysis(risk_rating);
CREATE INDEX IF NOT EXISTS idx_opportunities_apy ON yield_opportunities(apy DESC);

-- Show final table count
\\echo ''
\\echo '✅ Setup complete! Final table list:'
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
"""
    
    # Write SQL file
    temp_file = Path(__file__).parent / "complete_setup.sql"
    with open(temp_file, 'w') as f:
        f.write(check_sql)
    
    try:
        # Run psql
        result = subprocess.run([
            'psql',
            db_url,
            '-f', str(temp_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database setup verification complete!")
            print("\nOutput:")
            print(result.stdout)
            return True
        else:
            print("❌ Error:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if temp_file.exists():
            temp_file.unlink()

if __name__ == "__main__":
    check_and_complete_setup()