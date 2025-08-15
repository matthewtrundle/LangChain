# Claude Orchestration System - Quick Start Guide

## Overview
This orchestration system enables Claude CLI to act as a sophisticated multi-agent development team for building the Solana Degen Yield Hunter.

## Setup Complete ✅
The following components have been created:

### 1. Master System Prompt
- Location: `prompts/system.md`
- Defines the Orchestrator role and execution rules

### 2. Task Contract
- Location: `tasks/degen_hunter.bootstrap.json`
- Specifies goals, inputs, and acceptance criteria

### 3. Role Cards
- `prompts/roles/executive.md` - Strategic decisions and quality control
- `prompts/roles/defi_strategist.md` - DeFi expertise and yield strategies
- `prompts/roles/builder.md` - TypeScript/Node implementation
- `prompts/roles/auditor_secops.md` - Security and compliance
- `prompts/roles/sre_observer.md` - Observability and operations

### 4. Security Setup
- `.env.example` - Environment variable template
- `SECURITY.md` - Security policies and practices
- `scripts/validate-env.ts` - Environment validation

### 5. Documentation
- `docs/plan.md` - Initial implementation plan
- `inputs/executive_context.md` - Placeholder for GPT-4o requirements

## How to Use

### Basic Invocation
```bash
claude -p prompts/system.md \
       -J tasks/degen_hunter.bootstrap.json
```

### With Role Cards (if CLI supports attachments)
```bash
claude -p prompts/system.md \
       -J tasks/degen_hunter.bootstrap.json \
       -a prompts/roles/executive.md \
       -a prompts/roles/defi_strategist.md \
       -a prompts/roles/builder.md \
       -a prompts/roles/auditor_secops.md \
       -a prompts/roles/sre_observer.md
```

### Alternative (if no attachment support)
Concatenate role cards into system prompt:
```bash
cat prompts/system.md prompts/roles/*.md > prompts/full-system.md
claude -p prompts/full-system.md -J tasks/degen_hunter.bootstrap.json
```

## What Claude Will Do

1. **Analyze Requirements**: Read executive context and existing codebase
2. **Plan Implementation**: Create detailed technical plans
3. **Generate Code**: Build TypeScript modules with tests
4. **Ensure Quality**: Apply security, testing, and observability standards
5. **Produce Artifacts**: Generate reports, documentation, and runbooks

## Key Features

- **No Hardcoded Secrets**: All sensitive data via environment variables
- **Testnet First**: Safe defaults with explicit mainnet enablement
- **Dry Run Mode**: Simulate operations without executing transactions
- **Structured Logging**: Full observability with trace IDs
- **Report Generation**: Automated summaries of each run

## Next Steps

1. **Add GPT-4o Dialog**: Place the actual dialog in `inputs/gpt4o_dialog.md`
2. **Run Validation**: `ts-node scripts/validate-env.ts`
3. **Execute Claude**: Use the invocation commands above
4. **Review Output**: Check `reports/` and `logs/` directories

## Important Notes

- The system defaults to testnet for safety
- All wallet operations require explicit confirmation
- Logs automatically redact sensitive information
- Each run produces a timestamped report

The orchestration system is now ready for use!