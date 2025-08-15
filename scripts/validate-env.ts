#!/usr/bin/env ts-node

import { config } from 'dotenv';
import { z } from 'zod';
import { existsSync } from 'fs';
import { resolve } from 'path';

// Load environment variables
config();

// Define environment schema
const envSchema = z.object({
  // Network configuration
  NETWORK: z.enum(['TESTNET', 'MAINNET']).default('TESTNET'),
  RPC_URL: z.string().url().default('https://api.testnet.solana.com'),
  HELIUS_API_KEY: z.string().min(1),
  
  // Wallet configuration (one required)
  WALLET_KEY_B64: z.string().optional(),
  WALLET_KEY_PATH: z.string().optional(),
  
  // Operation mode
  DRY_RUN: z.string().transform(v => v !== 'false').default('true'),
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
  
  // API keys
  OPENROUTER_API_KEY: z.string().min(1),
  
  // Optional performance tuning
  POSITION_POLL_INTERVAL: z.string().transform(Number).default('30'),
  MAX_CONCURRENT_RPC_CALLS: z.string().transform(Number).default('5'),
  CACHE_TTL_SECONDS: z.string().transform(Number).default('300'),
}).refine(
  (data) => data.WALLET_KEY_B64 || data.WALLET_KEY_PATH,
  { message: "Either WALLET_KEY_B64 or WALLET_KEY_PATH must be provided" }
).refine(
  (data) => {
    if (data.WALLET_KEY_PATH) {
      const fullPath = resolve(process.cwd(), data.WALLET_KEY_PATH);
      return existsSync(fullPath);
    }
    return true;
  },
  { message: "WALLET_KEY_PATH file does not exist" }
).refine(
  (data) => {
    if (data.NETWORK === 'MAINNET' && data.DRY_RUN === false) {
      console.warn('⚠️  WARNING: Mainnet writes enabled! Use with extreme caution.');
      return true;
    }
    return true;
  }
);

// Validate environment
try {
  const env = envSchema.parse(process.env);
  
  console.log('✅ Environment validation successful!');
  console.log('\nConfiguration:');
  console.log(`  Network: ${env.NETWORK}`);
  console.log(`  RPC URL: ${env.RPC_URL}`);
  console.log(`  Dry Run: ${env.DRY_RUN}`);
  console.log(`  Log Level: ${env.LOG_LEVEL}`);
  console.log(`  Wallet: ${env.WALLET_KEY_B64 ? 'Base64 key' : `File at ${env.WALLET_KEY_PATH}`}`);
  
  if (env.NETWORK === 'TESTNET') {
    console.log('\n🧪 Running on testnet - safe for testing');
  } else if (env.DRY_RUN) {
    console.log('\n🔒 Mainnet in dry-run mode - no transactions will be sent');
  } else {
    console.log('\n🚨 MAINNET WITH WRITES ENABLED - BE VERY CAREFUL! 🚨');
  }
  
  process.exit(0);
} catch (error) {
  console.error('❌ Environment validation failed!\n');
  
  if (error instanceof z.ZodError) {
    error.errors.forEach(err => {
      console.error(`  ${err.path.join('.')}: ${err.message}`);
    });
    console.error('\nPlease check your .env file against .env.example');
  } else {
    console.error(error);
  }
  
  process.exit(1);
}