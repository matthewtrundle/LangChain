# Security Policy

## Key Management

### Private Keys
- **NEVER** commit private keys to the repository
- Use environment variables or secure file references
- Two supported methods:
  1. Base64 encoded in `WALLET_KEY_B64` env var
  2. File path reference in `WALLET_KEY_PATH` pointing to gitignored location

### API Keys
- All API keys must be stored in environment variables
- Use `.env` file locally (gitignored)
- Reference `.env.example` for required keys

## Network Safety

### Default Configuration
- Default network is TESTNET
- Mainnet operations are disabled by default
- Write operations require both:
  - `DRY_RUN=false` in environment
  - `--confirm` flag on CLI

### Transaction Safety
- All transactions go through `WalletPort` interface
- Dry-run mode simulates but doesn't execute
- Confirmation required for all write operations

## Logging & Monitoring

### Secret Redaction
- Logs automatically redact sensitive data
- Never log full private keys or API keys
- Use structured logging with redaction filters

### Audit Trail
- All operations logged with trace IDs
- Reports generated in `reports/<timestamp>/`
- Summary includes redacted config snapshot

## Development Practices

### Code Review
- Security-sensitive changes require extra review
- Check for hardcoded values in PRs
- Validate all external inputs with Zod schemas

### Testing
- Use deterministic test seeds
- Mock external services in tests
- Never use real private keys in tests

### CI/CD
- Secret scanning enabled
- No production keys in CI environment
- Integration tests use testnet only

## Incident Response

If you discover a security issue:
1. Do NOT create a public issue
2. Contact maintainers directly
3. Use responsible disclosure timeline

## Key Rotation

Recommended rotation schedule:
- API keys: Every 90 days
- Wallet keys: Based on value at risk
- Test keys: Regenerate frequently

## Dependencies

- Regular dependency audits with `npm audit`
- Keep dependencies up to date
- Review new dependencies for security