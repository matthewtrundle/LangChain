import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'

export interface RiskAnalysis {
  pool_address: string
  analyzed_at: string
  apy: number
  tvl: number
  volume_24h: number
  volume_7d: number
  overall_risk_score: number
  degen_score: number
  rug_risk_score: number
  sustainability_score: number
  liquidity_score: number
  volume_score: number
  impermanent_loss_risk: number
  volatility_24h: number
  volume_to_tvl_ratio: number
  risk_rating: 'SAFE' | 'LOW' | 'MODERATE' | 'HIGH' | 'EXTREME' | 'AVOID'
  recommendation: string
}

export function useRiskAnalysis(poolAddress: string | null) {
  const [riskAnalysis, setRiskAnalysis] = useState<RiskAnalysis | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!poolAddress) {
      setRiskAnalysis(null)
      return
    }

    const fetchRiskAnalysis = async () => {
      setIsLoading(true)
      setError(null)
      
      try {
        const response = await fetch(`${apiClient.baseUrl}/risk/pool/${poolAddress}`)
        const data = await response.json()
        
        if (data.data) {
          setRiskAnalysis(data.data)
        } else {
          setError(data.error || 'No risk analysis available')
        }
      } catch (err) {
        console.error('Failed to fetch risk analysis:', err)
        setError('Failed to fetch risk analysis')
      } finally {
        setIsLoading(false)
      }
    }

    fetchRiskAnalysis()
  }, [poolAddress])

  return { riskAnalysis, isLoading, error }
}

export function useRiskAnalysisBatch(poolAddresses: string[]) {
  const [analyses, setAnalyses] = useState<Map<string, RiskAnalysis>>(new Map())
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (poolAddresses.length === 0) return

    const fetchBatchAnalyses = async () => {
      setIsLoading(true)
      
      // Fetch in parallel
      const promises = poolAddresses.map(async (address) => {
        try {
          const response = await fetch(`${apiClient.baseUrl}/risk/pool/${address}`)
          const data = await response.json()
          return { address, data: data.data }
        } catch (err) {
          console.error(`Failed to fetch risk for ${address}:`, err)
          return { address, data: null }
        }
      })

      const results = await Promise.all(promises)
      
      const newAnalyses = new Map<string, RiskAnalysis>()
      results.forEach(({ address, data }) => {
        if (data) {
          newAnalyses.set(address, data)
        }
      })
      
      setAnalyses(newAnalyses)
      setIsLoading(false)
    }

    fetchBatchAnalyses()
  }, [poolAddresses.join(',')])

  return { analyses, isLoading }
}