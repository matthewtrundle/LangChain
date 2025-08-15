# AI-to-AI Collaboration Workflow

## Overview
Claude CLI (Orchestrator) collaborates with GPT-4o through the `gpt5` CLI tool, with GPT-4o assuming different role perspectives to provide specialized expertise.

## Collaboration Model

### 1. Claude CLI as Orchestrator
- Manages overall project flow
- Executes code changes
- Runs tests and validations
- Consults GPT-4o for decisions and expertise

### 2. GPT-4o via gpt5 Tool
Assumes different roles based on context:
- **Executive AI**: Strategic decisions, priorities, quality standards
- **DeFi Strategist**: Yield strategies, risk assessment, DeFi expertise
- **Builder**: Technical implementation advice, architecture decisions
- **Auditor/SecOps**: Security reviews, vulnerability assessments
- **SRE/Observer**: Observability, monitoring, operational excellence

## Workflow Examples

### Example 1: Implementing a New Yield Strategy
```bash
# Claude consults DeFi Strategist role
gpt5 "As DeFi Strategist: We're implementing perps funding rate arbitrage. What key metrics should we track and what risk parameters should we set for Solana perpetual futures?"

# Claude receives strategy advice, then consults Builder
gpt5 "As Builder: Given these DeFi requirements [details], how should we structure the TypeScript monitoring service to track funding rates across multiple perps exchanges?"

# Claude implements based on guidance, then consults Auditor
gpt5 "As Auditor/SecOps: Review this wallet interaction code for perpetual positions. Are there any security concerns? [code snippet]"
```

### Example 2: Debugging Production Issue
```bash
# Claude detects issue, consults SRE
gpt5 "As SRE/Observer: Our position monitor is missing 30% of transactions. Trace IDs show gaps. What observability improvements would help diagnose this?"

# After implementing suggestions, consult Executive
gpt5 "As Executive AI: We've identified a WebSocket reliability issue affecting 30% of transactions. Should we prioritize fixing this over new feature development?"
```

### Example 3: Architecture Decision
```bash
# Claude needs architectural guidance
gpt5 "As Builder: We need to choose between Redis pub/sub vs Kafka for real-time position updates. Given our scale (1000 positions, 100 updates/sec), what's your recommendation?"

# Follow up with security check
gpt5 "As Auditor/SecOps: If we use Redis pub/sub for position updates, what security considerations should we implement?"
```

## Communication Patterns

### 1. Decision Requests
```
Claude: "As [Role]: We need to decide [specific decision]. Context: [relevant details]. What's your recommendation?"
GPT-4o: Provides role-specific analysis and recommendation
```

### 2. Review Requests
```
Claude: "As [Role]: Please review [code/design/approach]. Specific concerns: [areas to focus on]"
GPT-4o: Provides role-specific review and suggestions
```

### 3. Problem Solving
```
Claude: "As [Role]: We're facing [specific problem]. Attempted solutions: [what we tried]. What alternative approaches should we consider?"
GPT-4o: Provides role-specific solutions and trade-offs
```

### 4. Progress Updates
```
Claude: "As Executive AI: Status update - [completed items], [blockers], [next steps]. Should we adjust priorities?"
GPT-4o: Provides strategic guidance on priorities
```

## Role-Specific Consultation Guidelines

### Executive AI Consultations
- Strategic decisions and trade-offs
- Priority adjustments based on progress
- Quality gates and acceptance criteria
- Resource allocation decisions

### DeFi Strategist Consultations
- Yield strategy evaluation
- Risk parameter tuning
- Market condition assessments
- Protocol-specific optimizations

### Builder Consultations
- Technical architecture decisions
- Implementation approach
- Performance optimization
- Integration strategies

### Auditor/SecOps Consultations
- Security reviews
- Vulnerability assessments
- Key management strategies
- Compliance checks

### SRE/Observer Consultations
- Monitoring strategy
- Alert thresholds
- Performance baselines
- Incident response planning

## Best Practices

1. **Context Preservation**: Always include relevant context when switching roles
2. **Clear Role Declaration**: Start each consultation with "As [Role]:"
3. **Specific Questions**: Ask focused questions rather than open-ended ones
4. **Implementation Verification**: After implementing GPT-4o suggestions, verify with appropriate role
5. **Decision Documentation**: Record key decisions in project documentation

## Integration with Development Flow

1. **Planning Phase**: Consult Executive AI for priorities
2. **Design Phase**: Consult DeFi Strategist and Builder for approach
3. **Implementation Phase**: Regular Builder consultations
4. **Review Phase**: Auditor/SecOps review before deployment
5. **Monitoring Phase**: SRE/Observer for operational excellence

This collaborative approach ensures comprehensive expertise across all aspects of the project while maintaining clear separation of concerns.