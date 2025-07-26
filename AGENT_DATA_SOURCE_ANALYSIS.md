# Agent Data Source Analysis

## Overview
This report analyzes each agent in the backend/agents folder to determine whether they're using real data or mock data.

## 1. Scanner Agent (`scanner_agent.py`)

### Data Sources Used:
- **PoolScannerTool**: Uses MOCK data (hardcoded pools)
- **RealPoolScannerTool**: Uses REAL data from DeFiLlama API
- **RadiumScannerTool**: Uses REAL data from Raydium API
- **WebSearchTool**: For web searches (real data)
- **HeliusClient**: Configured but not actively used for real data

### Current Implementation:
```python
# Line 15-17: Tools configured
PoolScannerTool(),           # Mock data for testing
RealPoolScannerTool(),       # Real DeFiLlama + Helius data
RadiumScannerTool(),         # Real Raydium pools with addresses
```

### Scan Method Behavior:
- Primary method `scan_new_opportunities()` tries to use real data first:
  1. First attempts RadiumScannerTool (REAL Raydium API data)
  2. Then attempts RealPoolScannerTool (REAL DeFiLlama data)
  3. Falls back to mock data if APIs fail

**Verdict: MIXED - Primarily uses REAL data, falls back to MOCK when APIs fail**

---

## 2. Analyzer Agent (`analyzer_agent.py`)

### Data Sources Used:
- **DegenScorerTool**: Uses algorithmic scoring based on input data
- **HeliusClient**: Configured but not actively used

### Current Implementation:
- Analyzes pool data passed to it (doesn't fetch new data)
- Uses mathematical calculations and heuristics for risk scoring
- Line 131-132: Mock APY and TVL changes for monitoring

```python
# Mock data used in _check_position_status
current_apy = entry_apy * 0.85  # Mock 15% APY decrease
current_tvl = pool_data.get("tvl", 0) * 0.9  # Mock 10% TVL decrease
```

**Verdict: MOCK - Processes data from other agents but uses mock calculations for changes**

---

## 3. Monitor Agent (`monitor_agent.py`)

### Data Sources Used:
- In-memory position tracking (not persistent)
- Mock position status updates

### Current Implementation:
```python
# Line 131-132: Simulates current pool data
current_apy = entry_apy * 0.85  # Mock 15% APY decrease
current_tvl = pool_data.get("tvl", 0) * 0.9  # Mock 10% TVL decrease
```

- Stores positions in memory: `self.tracked_positions = {}`
- Simulates monitoring with hardcoded percentage changes

**Verdict: MOCK - All monitoring data is simulated**

---

## 4. Coordinator Agent (`coordinator_agent.py`)

### Data Sources Used:
- Orchestrates other agents (doesn't fetch data directly)
- Relies on Scanner, Analyzer, and Monitor agents

### Current Implementation:
- Parses user queries to determine workflow
- Delegates to appropriate agents
- Synthesizes results from sub-agents

**Verdict: ORCHESTRATOR - Uses whatever data the sub-agents provide**

---

## Tool Analysis

### Real Data Tools:
1. **RealPoolScannerTool** (`real_pool_scanner.py`):
   - ✅ DeFiLlama API: `https://yields.llama.fi/pools` (REAL)
   - ❌ Helius: Configured but returns mock data
   - ❌ Jupiter prices: Returns mock data (TODO comment indicates future implementation)
   - ❌ CoinGecko: Returns mock data (TODO comment indicates future implementation)

2. **RadiumScannerTool** (`raydium_scanner.py`):
   - ✅ Raydium API: `https://api.raydium.io/v2/main/pairs` (REAL)
   - Calculates APY from actual volume and liquidity data
   - Provides real Solana addresses and Solscan links

### Mock Data Tools:
1. **PoolScannerTool** (`pool_scanner.py`):
   - Returns hardcoded mock pools for Raydium and Orca
   - Example pools with fake addresses and data

2. **DegenScorerTool** (`degen_scorer.py`):
   - Algorithmic scoring based on input
   - Mock creator whitelist/blacklist
   - Real calculations but based on whatever data is passed

---

## Summary

### Using Real Data:
- **Scanner Agent**: Primarily real (Raydium API, DeFiLlama API)
- **RadiumScannerTool**: Real Raydium pool data
- **RealPoolScannerTool**: Real DeFiLlama data

### Using Mock Data:
- **Monitor Agent**: All monitoring is simulated
- **Analyzer Agent**: Uses mock calculations for changes
- **PoolScannerTool**: Hardcoded mock pools

### Mixed/Partial:
- **Scanner Agent**: Has both real and mock tools
- **DegenScorerTool**: Real algorithms on potentially mock data
- **Coordinator Agent**: Depends on sub-agents

## Recommendations

To make the system fully use real data:

1. **Monitor Agent**: 
   - Implement real position tracking with database
   - Use Helius/Jupiter APIs for real-time price/APY updates

2. **Analyzer Agent**:
   - Fetch real current data instead of mock percentage changes
   - Integrate Helius for on-chain transaction analysis

3. **Complete TODOs**:
   - Implement Jupiter price fetching in RealPoolScannerTool
   - Implement CoinGecko market data fetching
   - Use Helius for real pool creation monitoring

4. **Add Persistence**:
   - Database for position tracking
   - Cache for API responses
   - Historical data storage