'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'
import { 
  TrendingUpIcon, 
  TrendingDownIcon, 
  DollarSignIcon,
  ClockIcon,
  AlertTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  RefreshCwIcon,
  ActivityIcon
} from './icons/Icons'

interface Position {
  id: string
  pool_data: any
  entry_amount: number
  current_value: number
  pnl_amount: number
  pnl_percent: number
  entry_apy: number
  current_apy: number
  status: string
  entry_time: string
  exit_time?: string
  exit_reason?: string
}

interface PositionSummary {
  total_positions: number
  active_positions: number
  total_invested: number
  current_value: number
  total_pnl: number
  total_pnl_percent: number
  total_rewards: number
  average_apy: number
}

export default function PositionDashboard() {
  const [positions, setPositions] = useState<Position[]>([])
  const [history, setHistory] = useState<Position[]>([])
  const [summary, setSummary] = useState<PositionSummary | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [selectedTab, setSelectedTab] = useState<'active' | 'history'>('active')

  useEffect(() => {
    fetchPositions()
    const interval = setInterval(fetchPositions, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  const fetchPositions = async () => {
    try {
      setIsRefreshing(true)
      const response = await fetch(`${apiClient.baseUrl}/positions`)
      const data = await response.json()
      
      setPositions(data.active_positions || [])
      setHistory(data.position_history || [])
      setSummary(data.summary || null)
    } catch (error) {
      console.error('Failed to fetch positions:', error)
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }

  const handleExitPosition = async (positionId: string) => {
    if (!confirm('Are you sure you want to exit this position?')) return
    
    try {
      const response = await fetch(`${apiClient.baseUrl}/position/exit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ position_id: positionId, reason: 'manual' })
      })
      
      if (response.ok) {
        const result = await response.json()
        alert(`Position exited! P&L: ${result.final_pnl_percent.toFixed(1)}%`)
        fetchPositions()
      }
    } catch (error) {
      console.error('Failed to exit position:', error)
      alert('Failed to exit position')
    }
  }

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const hours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)
    
    if (hours < 1) return '< 1h ago'
    if (hours < 24) return `${Math.floor(hours)}h ago`
    return `${Math.floor(hours / 24)}d ago`
  }

  const getPnLColor = (pnl: number) => {
    if (pnl > 0) return 'text-green-500'
    if (pnl < 0) return 'text-red-500'
    return 'text-text-secondary'
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircleIcon className="w-4 h-4 text-green-500" />
      case 'exited':
        return <XCircleIcon className="w-4 h-4 text-text-tertiary" />
      default:
        return <AlertTriangleIcon className="w-4 h-4 text-yellow-500" />
    }
  }

  if (isLoading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-12">
          <div className="loading-spinner w-8 h-8" />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Portfolio Summary */}
      {summary && (
        <div className="card-gradient">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-text-primary">Portfolio Overview</h2>
            <button
              onClick={fetchPositions}
              className={`btn-ghost btn-sm ${isRefreshing ? 'animate-spin' : ''}`}
              disabled={isRefreshing}
            >
              <RefreshCwIcon className="w-4 h-4" />
            </button>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-terminal-surface/50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <DollarSignIcon className="w-4 h-4 text-text-tertiary" />
                <span className="text-xs text-text-tertiary uppercase">Total Invested</span>
              </div>
              <p className="text-xl font-bold text-text-primary">
                ${summary.total_invested.toFixed(2)}
              </p>
            </div>
            
            <div className="bg-terminal-surface/50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUpIcon className="w-4 h-4 text-text-tertiary" />
                <span className="text-xs text-text-tertiary uppercase">Current Value</span>
              </div>
              <p className="text-xl font-bold text-text-primary">
                ${summary.current_value.toFixed(2)}
              </p>
            </div>
            
            <div className="bg-terminal-surface/50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                {summary.total_pnl >= 0 ? (
                  <TrendingUpIcon className="w-4 h-4 text-green-500" />
                ) : (
                  <TrendingDownIcon className="w-4 h-4 text-red-500" />
                )}
                <span className="text-xs text-text-tertiary uppercase">Total P&L</span>
              </div>
              <p className={`text-xl font-bold ${getPnLColor(summary.total_pnl)}`}>
                ${summary.total_pnl.toFixed(2)} ({summary.total_pnl_percent.toFixed(1)}%)
              </p>
            </div>
            
            <div className="bg-terminal-surface/50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <ActivityIcon className="w-4 h-4 text-text-tertiary" />
                <span className="text-xs text-text-tertiary uppercase">Avg APY</span>
              </div>
              <p className="text-xl font-bold text-cyber-primary">
                {summary.average_apy.toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-4 border-b border-terminal-border">
        <button
          onClick={() => setSelectedTab('active')}
          className={`pb-2 px-4 font-semibold transition-colors ${
            selectedTab === 'active' 
              ? 'text-cyber-primary border-b-2 border-cyber-primary' 
              : 'text-text-tertiary hover:text-text-primary'
          }`}
        >
          Active Positions ({positions.length})
        </button>
        <button
          onClick={() => setSelectedTab('history')}
          className={`pb-2 px-4 font-semibold transition-colors ${
            selectedTab === 'history' 
              ? 'text-cyber-primary border-b-2 border-cyber-primary' 
              : 'text-text-tertiary hover:text-text-primary'
          }`}
        >
          History ({history.length})
        </button>
      </div>

      {/* Positions List */}
      <div className="space-y-4">
        {selectedTab === 'active' && positions.length === 0 && (
          <div className="card text-center py-8">
            <p className="text-text-tertiary">No active positions</p>
          </div>
        )}
        
        {selectedTab === 'history' && history.length === 0 && (
          <div className="card text-center py-8">
            <p className="text-text-tertiary">No position history</p>
          </div>
        )}

        {(selectedTab === 'active' ? positions : history).map((position) => (
          <div key={position.id} className="card hover-lift">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold text-text-primary">
                    {position.pool_data?.token_symbols || 'Unknown Pool'}
                  </h3>
                  {getStatusIcon(position.status)}
                  <span className="text-sm text-text-tertiary">
                    {formatTimeAgo(position.entry_time)}
                  </span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div>
                    <p className="text-xs text-text-tertiary">Entry</p>
                    <p className="text-sm font-semibold">${position.entry_amount.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-text-tertiary">Current</p>
                    <p className="text-sm font-semibold">${position.current_value.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-text-tertiary">P&L</p>
                    <p className={`text-sm font-semibold ${getPnLColor(position.pnl_percent)}`}>
                      ${position.pnl_amount.toFixed(2)} ({position.pnl_percent.toFixed(1)}%)
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-text-tertiary">APY</p>
                    <p className="text-sm font-semibold text-cyber-primary">
                      {position.current_apy.toFixed(1)}%
                      <span className="text-xs text-text-tertiary ml-1">
                        ({position.current_apy - position.entry_apy > 0 ? '+' : ''}
                        {(position.current_apy - position.entry_apy).toFixed(1)}%)
                      </span>
                    </p>
                  </div>
                </div>

                {position.exit_reason && (
                  <div className="bg-terminal-surface/50 rounded px-3 py-1 inline-block">
                    <span className="text-xs text-text-tertiary">
                      Exit: {position.exit_reason.replace('_', ' ')}
                    </span>
                  </div>
                )}
              </div>

              {position.status === 'active' && (
                <button
                  onClick={() => handleExitPosition(position.id)}
                  className="btn-secondary btn-sm ml-4"
                >
                  Exit
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}