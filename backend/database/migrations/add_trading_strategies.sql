-- Add trading_strategies table for multi-strategy support
CREATE TABLE IF NOT EXISTS trading_strategies (
    id UUID PRIMARY KEY,
    strategy_type VARCHAR(50) NOT NULL,
    capital_allocation NUMERIC(5, 2) CHECK (capital_allocation >= 0 AND capital_allocation <= 100),
    is_active BOOLEAN DEFAULT FALSE,
    performance_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP NULL
);

-- Add indexes
CREATE INDEX idx_strategies_active ON trading_strategies(is_active) WHERE deleted_at IS NULL;
CREATE INDEX idx_strategies_type ON trading_strategies(strategy_type);

-- Add strategy_executions enhancements for multi-strategy
ALTER TABLE strategy_executions 
ADD COLUMN IF NOT EXISTS strategy_instance_id UUID REFERENCES trading_strategies(id);

-- Create view for active strategies
CREATE OR REPLACE VIEW active_strategies AS
SELECT 
    id,
    strategy_type,
    capital_allocation,
    performance_data->>'total_pnl' as total_pnl,
    performance_data->>'win_rate' as win_rate,
    performance_data->>'total_trades' as total_trades,
    created_at
FROM trading_strategies
WHERE is_active = TRUE AND deleted_at IS NULL;