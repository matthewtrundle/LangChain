# Executive AI Context

## Project Vision
Build a production-ready Solana yield hunting system that:
1. Discovers high-yield opportunities in real-time
2. Assesses risk using sophisticated scoring algorithms
3. Monitors positions with P&L tracking
4. Operates safely on testnet with mainnet-ready architecture

## Key Requirements from GPT-4o Dialog
*Note: Awaiting actual GPT-4o dialog file. This placeholder contains inferred requirements from existing codebase.*

### Architecture Decisions
- Multi-agent system with specialized roles (Scanner, Analyzer, Monitor, Coordinator)
- Python backend with FastAPI and LangChain
- Next.js frontend with real-time updates
- Helius RPC as primary data source

### Priority Features
1. **Real-time Discovery**: WebSocket connections for instant updates
2. **Risk Assessment**: "Degen Score" algorithm considering:
   - Liquidity depth
   - Historical volatility
   - Smart contract risk
   - Team/project reputation
3. **Position Tracking**: 
   - Entry/exit tracking
   - P&L calculations including fees
   - Impermanent loss monitoring
4. **Safety First**: Testnet default, dry-run mode, explicit confirmations

### Quality Standards
- Production-ready code suitable for portfolio/interviews
- Comprehensive testing (unit, integration, e2e)
- Observability with structured logging
- Security-first approach with no hardcoded secrets

### Success Metrics
- Discovers opportunities within 30 seconds of creation
- Accurate P&L tracking within 0.1% margin
- Zero security incidents
- 99.9% uptime for monitoring service