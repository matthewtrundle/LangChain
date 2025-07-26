export interface Pool {
  pool_address: string
  protocol: string
  token_symbols: string
  token_a?: string
  token_b?: string
  token_a_mint?: string
  token_b_mint?: string
  apy: number
  estimated_apy?: number
  apy_24h?: number
  apy_7d?: number
  apy_1h?: number
  tvl: number
  volume_24h: number
  volume_7d?: number
  volume_1h?: number
  age_days?: number
  age_hours?: number
  creator?: string
  liquidity_locked?: boolean
  source: string
  real_data: boolean
  degen_score?: number
  risk_level?: 'LOW' | 'MEDIUM' | 'HIGH' | 'EXTREME'
  recommendation?: string
  sustainability_score?: number
  jupiter_pricing?: any
  coingecko_data?: any
  real_address?: boolean
  solscan_url?: string
  fee_tier?: string
  volume_7d?: number
}

export interface ScanResult {
  source: string
  found_pools: number
  pools: Pool[]
  scan_time: string
  data_sources: string[]
}

export interface AgentResponse {
  agent: string
  success: boolean
  result?: string
  error?: string
  task?: string
  score_data?: {
    degen_score: number
    risk_level: string
    score_breakdown?: {
      liquidity_score: number
      age_score: number
      volume_score: number
      creator_score: number
      token_score: number
    }
    red_flags?: string[]
  }
}

export interface CoordinatorResponse {
  workflow_id: string
  coordination_complete: boolean
  user_query: string
  intent: any
  results: any
  coordination_summary: string
  execution_time: string
  success: boolean
  error?: string
}

export interface DegenScore {
  pool_address: string
  degen_score: number
  risk_level: string
  score_breakdown: {
    liquidity_score: number
    age_score: number
    volume_score: number
    creator_score: number
    token_score: number
  }
  recommendation: string
}