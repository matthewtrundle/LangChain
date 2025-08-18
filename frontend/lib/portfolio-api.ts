import { apiClient } from './api'

export interface PortfolioSnapshot {
  timestamp: string
  value: number
  pnl: number
  pnlPercent: number
  feesEarned: number
  impermanentLoss: number
  gasCosts: number
}

export interface PortfolioMetrics {
  totalValue: number
  totalInvested: number
  totalPnL: number
  totalPnLPercent: number
  winningPositions: number
  losingPositions: number
  winRate: number
  totalFeesEarned: number
  totalImpermanentLoss: number
  totalGasCosts: number
  activePositions: number
  closedPositions: number
}

export interface PortfolioPosition {
  id: string
  poolName: string
  poolAddress: string
  entryDate: string
  exitDate?: string
  duration: string
  entryValue: number
  exitValue?: number
  currentValue?: number
  pnl: number
  pnlPercent: number
  fees: number
  apy: number
  status: 'active' | 'closed' | 'liquidated'
  riskRating?: string
}

class PortfolioApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  async getPortfolioHistory(walletAddress: string, timeframe: '24h' | '7d' | '30d' | 'all' = '7d'): Promise<PortfolioSnapshot[]> {
    try {
      const response = await fetch(`${this.baseUrl}/portfolio/history/${walletAddress}?timeframe=${timeframe}`)
      if (!response.ok) throw new Error('Failed to fetch portfolio history')
      const data = await response.json()
      return data.history || []
    } catch (error) {
      console.error('Error fetching portfolio history:', error)
      // Return empty array if API fails
      return []
    }
  }

  async getPortfolioMetrics(walletAddress: string): Promise<PortfolioMetrics> {
    try {
      const response = await fetch(`${this.baseUrl}/portfolio/metrics/${walletAddress}`)
      if (!response.ok) throw new Error('Failed to fetch portfolio metrics')
      const data = await response.json()
      return data.metrics
    } catch (error) {
      console.error('Error fetching portfolio metrics:', error)
      // Return zero metrics if API fails
      return {
        totalValue: 0,
        totalInvested: 0,
        totalPnL: 0,
        totalPnLPercent: 0,
        winningPositions: 0,
        losingPositions: 0,
        winRate: 0,
        totalFeesEarned: 0,
        totalImpermanentLoss: 0,
        totalGasCosts: 0,
        activePositions: 0,
        closedPositions: 0
      }
    }
  }

  async getPositions(walletAddress: string, status?: 'active' | 'closed' | 'all'): Promise<PortfolioPosition[]> {
    try {
      const url = status 
        ? `${this.baseUrl}/portfolio/positions/${walletAddress}?status=${status}`
        : `${this.baseUrl}/portfolio/positions/${walletAddress}`
      const response = await fetch(url)
      if (!response.ok) throw new Error('Failed to fetch positions')
      const data = await response.json()
      return data.positions || []
    } catch (error) {
      console.error('Error fetching positions:', error)
      // Return empty array if API fails
      return []
    }
  }
}

export const portfolioApi = new PortfolioApiClient(apiClient.baseUrl)