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
      // Return mock data for demo
      return this.generateMockHistory(timeframe)
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
      // Return mock data for demo
      return this.generateMockMetrics()
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
      // Return mock data for demo
      return this.generateMockPositions()
    }
  }

  // Mock data generators for demo
  private generateMockHistory(timeframe: string): PortfolioSnapshot[] {
    const now = Date.now()
    const points = timeframe === '24h' ? 24 : timeframe === '7d' ? 168 : timeframe === '30d' ? 720 : 1000
    const interval = timeframe === '24h' ? 3600000 : timeframe === '7d' ? 3600000 : timeframe === '30d' ? 3600000 : 86400000
    
    const history: PortfolioSnapshot[] = []
    let value = 10000
    let totalFees = 0
    let totalIL = 0
    let totalGas = 0

    for (let i = 0; i < points; i++) {
      const timestamp = new Date(now - (points - i) * interval).toISOString()
      
      // Simulate value changes
      const change = (Math.random() - 0.48) * 500 // Slight upward bias
      value = Math.max(5000, value + change)
      
      // Accumulate fees and costs
      totalFees += Math.random() * 20
      totalIL += Math.random() * 10
      totalGas += Math.random() * 2
      
      const pnl = value - 10000 + totalFees - totalIL - totalGas
      const pnlPercent = (pnl / 10000) * 100

      history.push({
        timestamp,
        value: Math.round(value * 100) / 100,
        pnl: Math.round(pnl * 100) / 100,
        pnlPercent: Math.round(pnlPercent * 100) / 100,
        feesEarned: Math.round(totalFees * 100) / 100,
        impermanentLoss: Math.round(totalIL * 100) / 100,
        gasCosts: Math.round(totalGas * 100) / 100
      })
    }

    return history
  }

  private generateMockMetrics(): PortfolioMetrics {
    return {
      totalValue: 15000,
      totalInvested: 10000,
      totalPnL: 5000,
      totalPnLPercent: 50,
      winningPositions: 18,
      losingPositions: 7,
      winRate: 72,
      totalFeesEarned: 3200,
      totalImpermanentLoss: 800,
      totalGasCosts: 150,
      activePositions: 3,
      closedPositions: 22
    }
  }

  private generateMockPositions(): PortfolioPosition[] {
    const pools = ['SOL-USDC', 'BONK-SOL', 'JUP-USDC', 'RAY-SOL', 'ORCA-USDC']
    const positions: PortfolioPosition[] = []

    for (let i = 0; i < 25; i++) {
      const entryDate = new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000)
      const isActive = i < 3
      const exitDate = isActive ? undefined : new Date(entryDate.getTime() + Math.random() * 7 * 24 * 60 * 60 * 1000)
      const duration = isActive 
        ? `${Math.floor((Date.now() - entryDate.getTime()) / (1000 * 60 * 60 * 24))} days`
        : `${Math.floor((exitDate!.getTime() - entryDate.getTime()) / (1000 * 60 * 60 * 24))} days`
      
      const entryValue = Math.round((1000 + Math.random() * 9000) * 100) / 100
      const pnlPercent = (Math.random() - 0.3) * 100 // 70% win rate
      const pnl = (entryValue * pnlPercent) / 100
      const exitValue = isActive ? undefined : entryValue + pnl
      const currentValue = isActive ? entryValue + pnl : undefined

      positions.push({
        id: `pos-${i}`,
        poolName: pools[Math.floor(Math.random() * pools.length)],
        poolAddress: `pool-${i}`,
        entryDate: entryDate.toISOString().split('T')[0],
        exitDate: exitDate?.toISOString().split('T')[0],
        duration,
        entryValue,
        exitValue,
        currentValue,
        pnl: Math.round(pnl * 100) / 100,
        pnlPercent: Math.round(pnlPercent * 100) / 100,
        fees: Math.round(Math.random() * 200 * 100) / 100,
        apy: Math.round(500 + Math.random() * 3500),
        status: isActive ? 'active' : pnl > 0 ? 'closed' : 'closed',
        riskRating: ['LOW', 'MODERATE', 'HIGH'][Math.floor(Math.random() * 3)]
      })
    }

    return positions.sort((a, b) => new Date(b.entryDate).getTime() - new Date(a.entryDate).getTime())
  }
}

export const portfolioApi = new PortfolioApiClient(apiClient.baseUrl)