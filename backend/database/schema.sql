-- Position Tracking Database Schema
-- For Railway PostgreSQL

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Positions table - Core position data
CREATE TABLE positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_wallet VARCHAR(44) NOT NULL,
    pool_address VARCHAR(44) NOT NULL,
    protocol VARCHAR(20) NOT NULL CHECK (protocol IN ('raydium', 'orca', 'meteora')),
    
    -- Entry data
    entry_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    entry_price_a DECIMAL(20, 8) NOT NULL,
    entry_price_b DECIMAL(20, 8) NOT NULL,
    entry_amount_a DECIMAL(20, 8) NOT NULL,
    entry_amount_b DECIMAL(20, 8) NOT NULL,
    entry_lp_tokens DECIMAL(20, 8) NOT NULL,
    entry_tx_hash VARCHAR(88) NOT NULL,
    entry_value_usd DECIMAL(20, 2) NOT NULL,
    
    -- Current state
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'CLOSED', 'PENDING')),
    current_amount_a DECIMAL(20, 8),
    current_amount_b DECIMAL(20, 8),
    fees_earned_a DECIMAL(20, 8) DEFAULT 0,
    fees_earned_b DECIMAL(20, 8) DEFAULT 0,
    
    -- Exit data (nullable)
    exit_timestamp TIMESTAMP WITH TIME ZONE,
    exit_price_a DECIMAL(20, 8),
    exit_price_b DECIMAL(20, 8),
    exit_amount_a DECIMAL(20, 8),
    exit_amount_b DECIMAL(20, 8),
    exit_tx_hash VARCHAR(88),
    exit_value_usd DECIMAL(20, 2),
    
    -- Pool metadata
    token_a_symbol VARCHAR(20) NOT NULL,
    token_b_symbol VARCHAR(20) NOT NULL,
    token_a_mint VARCHAR(44) NOT NULL,
    token_b_mint VARCHAR(44) NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_sync TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Position snapshots - Historical tracking
CREATE TABLE position_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    position_id UUID NOT NULL REFERENCES positions(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Prices at snapshot time
    price_a DECIMAL(20, 8) NOT NULL,
    price_b DECIMAL(20, 8) NOT NULL,
    
    -- Calculated values
    value_usd DECIMAL(20, 2) NOT NULL,
    fees_earned_usd DECIMAL(20, 2) NOT NULL,
    impermanent_loss_usd DECIMAL(20, 2) NOT NULL,
    impermanent_loss_percent DECIMAL(10, 4) NOT NULL,
    net_pnl_usd DECIMAL(20, 2) NOT NULL,
    net_pnl_percent DECIMAL(10, 4) NOT NULL,
    
    -- Pool metrics at time
    pool_tvl DECIMAL(20, 2),
    pool_apy DECIMAL(10, 2),
    pool_volume_24h DECIMAL(20, 2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Alert configurations
CREATE TABLE alert_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_wallet VARCHAR(44) NOT NULL,
    position_id UUID REFERENCES positions(id) ON DELETE CASCADE,
    
    -- Alert thresholds
    apy_drop_threshold DECIMAL(10, 2),      -- Alert if APY drops by X%
    il_threshold DECIMAL(10, 2),            -- Alert if IL exceeds X%
    profit_target DECIMAL(10, 2),           -- Alert when profit hits X%
    stop_loss DECIMAL(10, 2),               -- Alert when loss hits X%
    
    -- Delivery preferences
    webhook_url TEXT,
    email VARCHAR(255),
    telegram_chat_id VARCHAR(100),
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Alert history
CREATE TABLE alert_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_config_id UUID REFERENCES alert_configs(id) ON DELETE SET NULL,
    position_id UUID REFERENCES positions(id) ON DELETE CASCADE,
    
    alert_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    trigger_value DECIMAL(20, 4),
    threshold_value DECIMAL(20, 4),
    
    delivered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    delivery_method VARCHAR(50),
    delivery_status VARCHAR(20) DEFAULT 'SENT'
);

-- Price cache table (for historical data)
CREATE TABLE price_history (
    token_mint VARCHAR(44) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    price_usd DECIMAL(20, 8) NOT NULL,
    source VARCHAR(20) DEFAULT 'helius',
    
    PRIMARY KEY (token_mint, timestamp)
);

-- Indexes for performance
CREATE INDEX idx_positions_user_wallet ON positions(user_wallet);
CREATE INDEX idx_positions_status ON positions(status);
CREATE INDEX idx_positions_pool_protocol ON positions(pool_address, protocol);
CREATE INDEX idx_positions_updated_at ON positions(updated_at);

CREATE INDEX idx_snapshots_position_timestamp ON position_snapshots(position_id, timestamp DESC);
CREATE INDEX idx_snapshots_timestamp ON position_snapshots(timestamp DESC);

CREATE INDEX idx_alerts_user_active ON alert_configs(user_wallet, is_active);
CREATE INDEX idx_alerts_position ON alert_configs(position_id);

CREATE INDEX idx_alert_history_position ON alert_history(position_id, delivered_at DESC);

CREATE INDEX idx_price_history_token_time ON price_history(token_mint, timestamp DESC);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_positions_updated_at BEFORE UPDATE ON positions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alert_configs_updated_at BEFORE UPDATE ON alert_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE VIEW active_positions_summary AS
SELECT 
    p.*,
    ps.value_usd as current_value_usd,
    ps.net_pnl_usd,
    ps.net_pnl_percent,
    ps.impermanent_loss_percent,
    ps.pool_apy as current_apy
FROM positions p
LEFT JOIN LATERAL (
    SELECT * FROM position_snapshots 
    WHERE position_id = p.id 
    ORDER BY timestamp DESC 
    LIMIT 1
) ps ON true
WHERE p.status = 'ACTIVE';

-- Sample data for testing (commented out for production)
/*
INSERT INTO positions (
    user_wallet, pool_address, protocol,
    entry_timestamp, entry_price_a, entry_price_b,
    entry_amount_a, entry_amount_b, entry_lp_tokens,
    entry_tx_hash, entry_value_usd,
    token_a_symbol, token_b_symbol,
    token_a_mint, token_b_mint
) VALUES (
    'DemoWallet111111111111111111111111111111111',
    '7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU',
    'raydium',
    NOW() - INTERVAL '2 days',
    0.00001234, 1.00,
    1000000, 12.34,
    100.5,
    'DemoTxHash111111111111111111111111111111111111111111111111111111111111111111',
    24.68,
    'BONK', 'USDC',
    'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
    'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
);
*/