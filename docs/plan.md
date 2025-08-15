# Sol Degen Yield Hunter - Initial PR Plan

## Scope
Establish the foundational orchestration system for the Solana Degen Yield Hunter project, enabling Claude CLI to manage the multi-agent development process.

## Decisions
1. **Architecture**: TypeScript/Node.js with Zod validation for all configurations
2. **Security**: Environment-based secrets, testnet default, dry-run safety
3. **Observability**: Structured logging with pino, trace IDs, report generation
4. **Testing**: Jest for unit tests, deterministic seeds, 95% coverage target

## Implementation Phases

### Phase 1: Core Infrastructure ✅
- [x] Orchestration directory structure
- [x] Master system prompt for Claude CLI
- [x] Task contract JSON
- [x] Role cards for 5 AI personas
- [x] Security policy and .env.example
- [x] Environment validation script

### Phase 2: Wallet & Config System (Next)
- [ ] Zod-validated configuration module
- [ ] WalletPort interface and implementations
- [ ] Testnet wallet with safety guards
- [ ] Config loader with environment merging

### Phase 3: Monitoring & Logging
- [ ] Structured logging with pino
- [ ] Trace ID generation and propagation
- [ ] Report generation system
- [ ] Health check endpoint

### Phase 4: Strategy & Position System
- [ ] Strategy registry with pluggable adapters
- [ ] Position monitor skeleton
- [ ] Mock data adapters for testing
- [ ] P&L calculation engine

## Acceptance Tests
1. ✅ No hardcoded keys in codebase
2. ✅ .env.example documents all required variables
3. ✅ validate-env.ts catches missing/invalid config
4. ⏳ Unit tests pass for all core modules
5. ⏳ CI pipeline runs successfully
6. ⏳ Can generate position report on testnet

## How to Run
```bash
# Install dependencies
pnpm install

# Set up environment
cp .env.example .env
# Edit .env with your keys

# Validate environment
pnpm run validate-env

# Run the orchestrator
claude -p prompts/system.md \
       -J tasks/degen_hunter.bootstrap.json \
       -a prompts/roles/*.md

# Run tests (when implemented)
pnpm test
```

## Next Steps
1. Create the TypeScript package.json and dependencies
2. Implement core configuration module with Zod
3. Build wallet abstraction layer
4. Set up CI pipeline