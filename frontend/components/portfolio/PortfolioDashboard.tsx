'use client'

import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'
import PortfolioValueChart from './PortfolioValueChart'
import PnLBreakdown from './PnLBreakdown'
import WinRateMeter from './WinRateMeter'
import PositionHistoryTable from './PositionHistoryTable'
import BestWorstPositionCards from './BestWorstPositionCards'
import { Wallet, TrendingUp, Activity, BarChart3 } from 'lucide-react'
import { portfolioApi } from '@/lib/portfolio-api'

interface PortfolioDashboardProps {
  walletAddress?: string
}

export default function PortfolioDashboard({ walletAddress }: PortfolioDashboardProps) {
  const [portfolioData, setPortfolioData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [timeframe, setTimeframe] = useState<'24h' | '7d' | '30d' | 'all'>('7d')
  
  useEffect(() => {
    if (!walletAddress) {
      setIsLoading(false)
      return
    }

    const fetchPortfolioData = async () => {
      setIsLoading(true)
      try {
        // Fetch all data in parallel
        const [history, metrics, positions] = await Promise.all([
          portfolioApi.getPortfolioHistory(walletAddress, timeframe),
          portfolioApi.getPortfolioMetrics(walletAddress),
          portfolioApi.getPositions(walletAddress)
        ])

        // Find best and worst positions
        const sortedByPnL = [...positions].sort((a, b) => b.pnl - a.pnl)
        const bestPosition = sortedByPnL[0]
        const worstPosition = sortedByPnL[sortedByPnL.length - 1]

        setPortfolioData({
          chartData: history,
          breakdown: {
            feesEarned: metrics.totalFeesEarned,
            impermanentLoss: metrics.totalImpermanentLoss,
            gasCosts: metrics.totalGasCosts,
            totalValue: metrics.totalValue,
          },
          winRate: {
            winningPositions: metrics.winningPositions,
            losingPositions: metrics.losingPositions,
          },
          positions,
          metrics,
          bestPosition: bestPosition ? {
            poolName: bestPosition.poolName,
            pnl: bestPosition.pnl,
            pnlPercent: bestPosition.pnlPercent,
            duration: bestPosition.duration,
            apy: bestPosition.apy,
            entryValue: bestPosition.entryValue,
            exitValue: bestPosition.exitValue,
            date: bestPosition.entryDate + (bestPosition.exitDate ? ` - ${bestPosition.exitDate}` : ''),
          } : null,
          worstPosition: worstPosition && worstPosition.pnl < 0 ? {
            poolName: worstPosition.poolName,
            pnl: worstPosition.pnl,
            pnlPercent: worstPosition.pnlPercent,
            duration: worstPosition.duration,
            apy: worstPosition.apy,
            entryValue: worstPosition.entryValue,
            exitValue: worstPosition.exitValue,
            date: worstPosition.entryDate + (worstPosition.exitDate ? ` - ${worstPosition.exitDate}` : ''),
          } : null,
        })
      } catch (error) {
        console.error('Error fetching portfolio data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchPortfolioData()
  }, [walletAddress, timeframe])
  
  if (!walletAddress) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="bg-terminal-surface/50 rounded-xl border border-terminal-border p-12 text-center"
      >
        <Wallet className="w-16 h-16 text-text-tertiary mx-auto mb-4" />
        <h3 className="text-xl font-bold text-text-primary mb-2">Connect Your Wallet</h3>
        <p className="text-text-secondary">
          Connect your wallet to view portfolio analytics and track your positions
        </p>
      </motion.div>
    )
  }
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-text-primary">Portfolio Analytics</h2>
          <p className="text-text-secondary">Track your yield farming performance</p>
        </div>
        
        {/* Timeframe selector */}
        <div className="flex items-center gap-2 bg-terminal-surface/50 rounded-lg p-1 border border-terminal-border">
          {(['24h', '7d', '30d', 'all'] as const).map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                timeframe === tf
                  ? 'bg-cyber-primary text-black'
                  : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              {tf === 'all' ? 'All Time' : tf.toUpperCase()}
            </button>
          ))}
        </div>
      </div>
      
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          {
            label: 'Total Value',
            value: portfolioData?.metrics ? `$${portfolioData.metrics.totalValue.toLocaleString()}` : '$0',
            change: portfolioData?.metrics ? `${portfolioData.metrics.totalPnLPercent >= 0 ? '+' : ''}${portfolioData.metrics.totalPnLPercent.toFixed(1)}%` : '0%',
            icon: Wallet,
            color: 'text-cyber-primary',
          },
          {
            label: 'Total P&L',
            value: portfolioData?.metrics ? `${portfolioData.metrics.totalPnL >= 0 ? '+' : ''}$${portfolioData.metrics.totalPnL.toLocaleString()}` : '$0',
            change: portfolioData?.metrics ? `${portfolioData.metrics.totalPnLPercent >= 0 ? '+' : ''}${portfolioData.metrics.totalPnLPercent.toFixed(1)}%` : '0%',
            icon: TrendingUp,
            color: portfolioData?.metrics?.totalPnL >= 0 ? 'text-green-500' : 'text-red-500',
          },
          {
            label: 'Active Positions',
            value: portfolioData?.metrics?.activePositions?.toString() || '0',
            change: portfolioData?.positions ? `${Math.round(portfolioData.positions.filter((p: any) => p.status === 'active').reduce((sum: number, p: any) => sum + p.apy, 0) / Math.max(1, portfolioData.metrics.activePositions))}% Avg APY` : '0% APY',
            icon: Activity,
            color: 'text-blue-500',
          },
          {
            label: 'Total Positions',
            value: portfolioData?.metrics ? (portfolioData.metrics.activePositions + portfolioData.metrics.closedPositions).toString() : '0',
            change: portfolioData?.metrics ? `${portfolioData.metrics.winRate.toFixed(0)}% Win Rate` : '0% Win Rate',
            icon: BarChart3,
            color: 'text-purple-500',
          },
        ].map((stat, index) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-terminal-surface/50 rounded-xl border border-terminal-border p-4"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-text-tertiary text-sm">{stat.label}</span>
                <Icon className={`w-5 h-5 ${stat.color}`} />
              </div>
              <div className="text-2xl font-bold text-text-primary">{stat.value}</div>
              <div className={`text-sm ${stat.color}`}>{stat.change}</div>
            </motion.div>
          )
        })}
      </div>
      
      {/* Main Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-terminal-surface/50 rounded-xl border border-terminal-border p-6"
      >
        <h3 className="text-lg font-bold text-text-primary mb-4">Portfolio Value Over Time</h3>
        <PortfolioValueChart 
          data={portfolioData?.chartData || []} 
          isLoading={isLoading}
        />
      </motion.div>
      
      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* P&L Breakdown */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-terminal-surface/50 rounded-xl border border-terminal-border p-6"
        >
          <h3 className="text-lg font-bold text-text-primary mb-4">P&L Breakdown</h3>
          {portfolioData && (
            <PnLBreakdown {...portfolioData.breakdown} />
          )}
        </motion.div>
        
        {/* Win Rate */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-terminal-surface/50 rounded-xl border border-terminal-border p-6"
        >
          <h3 className="text-lg font-bold text-text-primary mb-4">Win Rate Analysis</h3>
          {portfolioData && (
            <WinRateMeter {...portfolioData.winRate} />
          )}
        </motion.div>
        
        {/* Quick Stats */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-terminal-surface/50 rounded-xl border border-terminal-border p-6 space-y-4"
        >
          <h3 className="text-lg font-bold text-text-primary mb-4">Performance Metrics</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-text-tertiary">Avg Position Size</span>
              <span className="text-text-primary font-medium">$3,200</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-text-tertiary">Avg Hold Time</span>
              <span className="text-text-primary font-medium">3.5 days</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-text-tertiary">Best Day</span>
              <span className="text-cyber-primary font-medium">+$2,100</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-text-tertiary">Worst Day</span>
              <span className="text-red-500 font-medium">-$450</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-text-tertiary">Total Fees Earned</span>
              <span className="text-green-500 font-medium">$3,200</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-text-tertiary">Gas Efficiency</span>
              <span className="text-text-primary font-medium">98.5%</span>
            </div>
          </div>
        </motion.div>
      </div>
      
      {/* Best/Worst Positions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <h3 className="text-lg font-bold text-text-primary mb-4">Notable Positions</h3>
        <BestWorstPositionCards
          bestPosition={portfolioData?.bestPosition}
          worstPosition={portfolioData?.worstPosition}
        />
      </motion.div>
      
      {/* Position History */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
      >
        <h3 className="text-lg font-bold text-text-primary mb-4">Position History</h3>
        <PositionHistoryTable positions={portfolioData?.positions || []} />
      </motion.div>
    </motion.div>
  )
}