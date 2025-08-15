Stack: TypeScript/Node, pnpm, ts-node, Zod, viem/solana web3 (or helius/validator RPC), jest, tsup.
Produce: 
- `src/config/index.ts` (zod-validated, supports TESTNET/MAINNET; no keys inside code)
- `src/wallet/testnetWallet.ts` (keypair from env or file ref; sign disabled unless DRY_RUN=false and confirm)
- `src/strategies/registry.ts` (pluggable strategy descriptors)
- `src/monitor/index.ts` (poll loop + adapters + PnL/health calculators)
- `src/cli.ts` (yargs or commander: `scan`, `monitor`, `report`)
- `scripts/validate-env.ts` (fast fail)