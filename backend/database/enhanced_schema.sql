-- Enhanced Analytics Database Schema for Solana Degen Hunter
-- Complete portfolio tracking, risk analysis, and P&L monitoring

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search

-- Drop existing tables if needed (comment out in production)
-- DROP TABLE IF EXISTS pool_risk_analysis CASCADE;
-- DROP TABLE IF EXISTS portfolio_history CASCADE;

-- Enhanced pools table with risk metrics
CREATE TABLE IF NOT EXISTS pools_enhanced (
    pool_address VARCHAR(44) PRIMARY KEY,
    protocol VARCHAR(50) NOT NULL,
    token_a_mint VARCHAR(44) NOT NULL,
    token_b_mint VARCHAR(44) NOT NULL,
    token_a_symbol VARCHAR(20),
    token_b_symbol VARCHAR(20),
    token_pair VARCHAR(50) GENERATED ALWAYS AS (token_a_symbol || '-' || token_b_symbol) STORED,
    fee_tier DECIMAL(5, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_analyzed TIMESTAMP WITH TIME ZONE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_flagged BOOLEAN DEFAULT FALSE,
    flag_reason TEXT
);

-- Real-time pool risk analysis (auto-populated for ALL pools)
CREATE TABLE IF NOT EXISTS pool_risk_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pool_address VARCHAR(44) REFERENCES pools_enhanced(pool_address),
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Current metrics
    apy DECIMAL(10, 2),
    tvl DECIMAL(20, 2),
    volume_24h DECIMAL(20, 2),
    volume_7d DECIMAL(20, 2),
    
    -- Risk scores (0-100, 100 = highest risk)
    overall_risk_score INTEGER CHECK (overall_risk_score >= 0 AND overall_risk_score <= 100),
    degen_score INTEGER CHECK (degen_score >= 0 AND degen_score <= 100),
    rug_risk_score INTEGER CHECK (rug_risk_score >= 0 AND rug_risk_score <= 100),
    
    -- Quality scores (0-10, 10 = best)
    sustainability_score DECIMAL(3, 1) CHECK (sustainability_score >= 0 AND sustainability_score <= 10),
    liquidity_score DECIMAL(3, 1) CHECK (liquidity_score >= 0 AND liquidity_score <= 10),
    volume_score DECIMAL(3, 1) CHECK (volume_score >= 0 AND volume_score <= 10),
    
    -- Risk factors
    impermanent_loss_risk INTEGER CHECK (impermanent_loss_risk >= 0 AND impermanent_loss_risk <= 100),
    volatility_24h INTEGER CHECK (volatility_24h >= 0 AND volatility_24h <= 100),
    concentration_risk DECIMAL(5, 2), -- % held by top holder
    
    -- Additional analytics
    holder_count INTEGER,
    age_hours INTEGER,
    volume_to_tvl_ratio DECIMAL(10, 4),
    price_impact_1k DECIMAL(5, 2), -- Price impact for $1k trade
    
    -- Risk flags
    has_locked_liquidity BOOLEAN DEFAULT FALSE,
    is_honeypot BOOLEAN DEFAULT FALSE,
    has_mint_authority BOOLEAN DEFAULT TRUE,
    creator_holds_percentage DECIMAL(5, 2),
    
    -- Recommendation
    risk_rating VARCHAR(20) CHECK (risk_rating IN ('SAFE', 'LOW', 'MODERATE', 'HIGH', 'EXTREME', 'AVOID')),
    recommendation TEXT,
    
    -- Make it unique per pool per hour
    UNIQUE(pool_address, date_trunc('hour', analyzed_at))
);

-- Enhanced positions table with better tracking
CREATE TABLE IF NOT EXISTS positions_enhanced (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_wallet VARCHAR(44) NOT NULL,
    pool_address VARCHAR(44) REFERENCES pools_enhanced(pool_address),
    position_key VARCHAR(100) UNIQUE,
    
    -- Entry data
    entry_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    entry_amount_usd DECIMAL(20, 2) NOT NULL,
    entry_amount_a DECIMAL(20, 8) NOT NULL,
    entry_amount_b DECIMAL(20, 8) NOT NULL,
    entry_price_a DECIMAL(20, 8) NOT NULL,
    entry_price_b DECIMAL(20, 8) NOT NULL,
    entry_tx_hash VARCHAR(88) NOT NULL,
    entry_gas_sol DECIMAL(10, 8),
    entry_gas_usd DECIMAL(10, 2),
    
    -- Risk snapshot at entry
    entry_risk_score INTEGER,
    entry_apy DECIMAL(10, 2),
    entry_tvl DECIMAL(20, 2),
    
    -- Current state
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'CLOSED', 'LIQUIDATED')),
    current_value_usd DECIMAL(20, 2),
    unrealized_pnl_usd DECIMAL(20, 2),
    unrealized_pnl_percent DECIMAL(10, 2),
    
    -- Accumulated earnings
    total_fees_earned_usd DECIMAL(20, 2) DEFAULT 0,
    total_rewards_earned_usd DECIMAL(20, 2) DEFAULT 0,
    
    -- Exit data
    exit_timestamp TIMESTAMP WITH TIME ZONE,
    exit_amount_usd DECIMAL(20, 2),
    exit_amount_a DECIMAL(20, 8),
    exit_amount_b DECIMAL(20, 8),
    exit_price_a DECIMAL(20, 8),
    exit_price_b DECIMAL(20, 8),
    exit_tx_hash VARCHAR(88),
    exit_gas_sol DECIMAL(10, 8),
    exit_gas_usd DECIMAL(10, 2),
    
    -- Final P&L (calculated on exit)
    realized_pnl_usd DECIMAL(20, 2),
    realized_pnl_percent DECIMAL(10, 2),
    total_gas_spent_usd DECIMAL(10, 2),
    net_pnl_usd DECIMAL(20, 2),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_snapshot TIMESTAMP WITH TIME ZONE
);

-- High-frequency position snapshots for charts
CREATE TABLE IF NOT EXISTS position_snapshots_hf (
    position_id UUID REFERENCES positions_enhanced(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Values
    value_usd DECIMAL(20, 2) NOT NULL,
    pnl_usd DECIMAL(20, 2) NOT NULL,
    pnl_percent DECIMAL(10, 2) NOT NULL,
    
    -- Components
    fees_earned_usd DECIMAL(20, 2),
    il_usd DECIMAL(20, 2),
    il_percent DECIMAL(10, 2),
    
    -- Pool state
    pool_apy DECIMAL(10, 2),
    pool_tvl DECIMAL(20, 2),
    
    PRIMARY KEY (position_id, timestamp)
);

-- Portfolio history for overall tracking
CREATE TABLE IF NOT EXISTS portfolio_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_wallet VARCHAR(44) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Portfolio value
    total_value_usd DECIMAL(20, 2) NOT NULL,
    total_invested_usd DECIMAL(20, 2) NOT NULL,
    total_pnl_usd DECIMAL(20, 2) NOT NULL,
    total_pnl_percent DECIMAL(10, 2) NOT NULL,
    
    -- Breakdown
    active_positions_count INTEGER DEFAULT 0,
    closed_positions_count INTEGER DEFAULT 0,
    total_fees_earned_usd DECIMAL(20, 2) DEFAULT 0,
    total_rewards_earned_usd DECIMAL(20, 2) DEFAULT 0,
    total_il_usd DECIMAL(20, 2) DEFAULT 0,
    total_gas_spent_usd DECIMAL(20, 2) DEFAULT 0,
    
    -- Win rate
    winning_positions INTEGER DEFAULT 0,
    losing_positions INTEGER DEFAULT 0,
    win_rate DECIMAL(5, 2) GENERATED ALWAYS AS (
        CASE 
            WHEN (winning_positions + losing_positions) > 0 
            THEN (winning_positions::DECIMAL / (winning_positions + losing_positions)) * 100
            ELSE 0
        END
    ) STORED,
    
    -- Best/worst
    best_position_pnl_usd DECIMAL(20, 2),
    worst_position_pnl_usd DECIMAL(20, 2),
    
    -- Token balances
    sol_balance DECIMAL(20, 8),
    usdc_balance DECIMAL(20, 8),
    
    UNIQUE(user_wallet, timestamp)
);

-- Analytics aggregations (materialized views for performance)
CREATE MATERIALIZED VIEW IF NOT EXISTS top_pools_by_risk AS
SELECT 
    p.pool_address,
    p.token_pair,
    p.protocol,
    r.apy,
    r.tvl,
    r.volume_24h,
    r.overall_risk_score,
    r.risk_rating,
    r.sustainability_score,
    r.recommendation,
    r.analyzed_at
FROM pools_enhanced p
JOIN LATERAL (
    SELECT * FROM pool_risk_analysis 
    WHERE pool_address = p.pool_address 
    ORDER BY analyzed_at DESC 
    LIMIT 1
) r ON true
WHERE r.risk_rating IN ('SAFE', 'LOW', 'MODERATE')
  AND r.tvl > 10000
  AND NOT p.is_flagged
ORDER BY r.apy DESC;

-- User position performance view
CREATE OR REPLACE VIEW user_position_performance AS
SELECT 
    p.user_wallet,
    p.id as position_id,
    pe.token_pair,
    p.entry_timestamp,
    p.entry_amount_usd,
    p.current_value_usd,
    p.unrealized_pnl_usd,
    p.unrealized_pnl_percent,
    p.total_fees_earned_usd,
    p.status,
    r.risk_rating as current_risk_rating,
    r.apy as current_apy
FROM positions_enhanced p
JOIN pools_enhanced pe ON p.pool_address = pe.pool_address
LEFT JOIN LATERAL (
    SELECT risk_rating, apy 
    FROM pool_risk_analysis 
    WHERE pool_address = p.pool_address 
    ORDER BY analyzed_at DESC 
    LIMIT 1
) r ON true;

-- Indexes for performance
CREATE INDEX idx_pools_enhanced_pair ON pools_enhanced(token_pair);
CREATE INDEX idx_pools_enhanced_protocol ON pools_enhanced(protocol);
CREATE INDEX idx_risk_analysis_pool_time ON pool_risk_analysis(pool_address, analyzed_at DESC);
CREATE INDEX idx_risk_analysis_rating ON pool_risk_analysis(risk_rating) WHERE risk_rating IN ('SAFE', 'LOW', 'MODERATE');
CREATE INDEX idx_positions_enhanced_user_status ON positions_enhanced(user_wallet, status);
CREATE INDEX idx_positions_enhanced_updated ON positions_enhanced(updated_at DESC);
CREATE INDEX idx_snapshots_hf_position_time ON position_snapshots_hf(position_id, timestamp DESC);
CREATE INDEX idx_portfolio_history_user_time ON portfolio_history(user_wallet, timestamp DESC);

-- Triggers
CREATE TRIGGER update_positions_enhanced_updated_at 
BEFORE UPDATE ON positions_enhanced
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Functions for analytics
CREATE OR REPLACE FUNCTION calculate_position_pnl(
    entry_value DECIMAL,
    current_value DECIMAL,
    fees_earned DECIMAL,
    gas_spent DECIMAL
) RETURNS TABLE (
    gross_pnl DECIMAL,
    net_pnl DECIMAL,
    pnl_percent DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        current_value - entry_value + fees_earned AS gross_pnl,
        current_value - entry_value + fees_earned - gas_spent AS net_pnl,
        ((current_value - entry_value + fees_earned - gas_spent) / entry_value) * 100 AS pnl_percent;
END;
$$ LANGUAGE plpgsql;

-- Auto-refresh materialized views (run as scheduled job)
CREATE OR REPLACE FUNCTION refresh_analytics_views() RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY top_pools_by_risk;
END;
$$ LANGUAGE plpgsql;