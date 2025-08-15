# GPT-4o Role Templates for gpt5 CLI

## How to Use
When Claude CLI needs specialized expertise, it will use these templates with the gpt5 tool:
```bash
gpt5 "As [Role]: [Specific question or request]"
```

## Executive AI Role

### Template
```
As Executive AI for the Solana Degen Yield Hunter project: 

Context: [Current project state, completed items, blockers]
Decision needed: [Specific strategic decision]
Constraints: [Time, resources, technical limitations]

Please provide strategic guidance considering:
- Project goals (demo-worthy, actually useful for DeFi)
- Quality standards (production-ready, interview-impressive)
- Risk vs. speed trade-offs
```

### Example Usage
```bash
gpt5 "As Executive AI: We've completed basic pool scanning but found performance issues with RPC calls (500ms latency). Should we: 1) Optimize current implementation, 2) Switch to WebSocket subscriptions, or 3) Implement caching layer? Timeline: 1 week remaining in sprint."
```

## DeFi Strategist Role

### Template
```
As DeFi Strategist for Solana yield hunting:

Strategy type: [AMM, lending, perps, staking, etc.]
Current market conditions: [Relevant metrics]
Risk tolerance: [Degen score threshold]

Please advise on:
- Yield calculation methodology
- Risk parameters and red flags
- Optimal entry/exit conditions
- Protocol-specific considerations
```

### Example Usage
```bash
gpt5 "As DeFi Strategist: Evaluating Raydium concentrated liquidity pools. Seeing 300% APR on SOL/USDC 0.05% fee tier. What risk factors should our Degen Score algorithm weight highest? Current factors: liquidity depth, volume, IL risk."
```

## Builder Role

### Template
```
As Builder (TypeScript/Node.js) for DeFi application:

Component: [What we're building]
Current stack: [Technologies in use]
Requirements: [Functional needs]
Constraints: [Performance, security, integration]

Please provide:
- Technical approach
- Code structure recommendations
- Potential pitfalls
- Testing strategy
```

### Example Usage
```bash
gpt5 "As Builder: Implementing WebSocket position monitor using Helius RPC. Need to track 1000+ positions across 10 protocols. Should we use: 1) Single WebSocket with filtering, 2) Multiple connections per protocol, or 3) Hybrid approach? Consider memory usage and reliability."
```

## Auditor/SecOps Role

### Template
```
As Auditor/SecOps for Solana DeFi application:

Component: [What needs review]
Operations: [What it does]
Current security measures: [Existing protections]

Please review for:
- Security vulnerabilities
- Key management issues
- Transaction safety
- Error handling gaps
```

### Example Usage
```bash
gpt5 "As Auditor/SecOps: Reviewing wallet transaction signing for auto-compound feature. Code uses Keypair from base64 env var, validates transaction before signing, uses compute budget. Any security concerns with this approach for testnet? Planning mainnet migration."
```

## SRE/Observer Role

### Template
```
As SRE/Observer for production DeFi system:

System component: [What needs monitoring]
Current metrics: [What we track]
SLOs: [Service level objectives]
Issues observed: [Any problems]

Please advise on:
- Monitoring strategy
- Alert thresholds
- Logging approach
- Performance optimization
```

### Example Usage
```bash
gpt5 "As SRE/Observer: Position monitor processes 100 updates/sec. Seeing memory growth (500MB/hour). Currently logging all position changes. How should we structure logging for debugging without memory bloat? Using pino with JSON output."
```

## Multi-Role Consultations

### Complex Decision Template
```
As [Primary Role] with input from [Secondary Role]:

Situation: [Complex scenario requiring multiple perspectives]
Primary concern: [Main role's focus]
Secondary concern: [Other role's focus]

Please provide integrated guidance.
```

### Example Usage
```bash
gpt5 "As Builder with Auditor/SecOps perspective: Implementing auto-rebalancing for concentrated liquidity. Need to handle private key access for transaction signing while maintaining security. How to structure code for both functionality and security?"
```

## Progress Check Templates

### Daily Standup
```bash
gpt5 "As Executive AI: Daily update - Completed: [list], In progress: [list], Blockers: [list]. Should we adjust today's priorities?"
```

### Sprint Review
```bash
gpt5 "As Executive AI: Sprint review - Delivered: [features], Missed: [items], Discovered: [new requirements]. How should we adjust next sprint?"
```

### Technical Decision Record
```bash
gpt5 "As Builder: Decided to use [technology] for [purpose] because [reasoning]. Any concerns or alternatives we should document?"
```

## Emergency Consultation

### Production Issue
```bash
gpt5 "As SRE/Observer: URGENT - [describe issue], Impact: [affected systems], Attempted fixes: [what tried]. What's the immediate mitigation?"
```

### Security Incident
```bash
gpt5 "As Auditor/SecOps: SECURITY - [describe potential breach/vulnerability], Affected: [components], Risk level: [assessment]. Immediate actions needed?"
```