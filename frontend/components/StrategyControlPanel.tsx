'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Plus, 
  Play, 
  Pause, 
  Trash2, 
  TrendingUp, 
  Shield, 
  Zap,
  DollarSign,
  BarChart3,
  AlertCircle
} from 'lucide-react'
import { fetchWithConfig } from '@/lib/api'

interface Strategy {
  id: string
  type: 'conservative' | 'balanced' | 'degen'
  capital_allocation: number
  is_active: boolean
  created_at: string
  performance: {
    total_pnl: number
    win_rate: number
    total_trades: number
    active_positions: number
  }
}

interface StrategyControlPanelProps {
  onStrategyChange?: () => void
}

export default function StrategyControlPanel({ onStrategyChange }: StrategyControlPanelProps) {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [totalAllocation, setTotalAllocation] = useState(0)

  useEffect(() => {
    fetchStrategies()
    const interval = setInterval(fetchStrategies, 5000) // Refresh every 5s
    return () => clearInterval(interval)
  }, [])

  const fetchStrategies = async () => {
    try {
      const response = await fetchWithConfig('/strategies')
      const data = await response.json()
      setStrategies(data.strategies || [])
      
      // Calculate total allocation
      const total = data.strategies?.reduce((sum: number, s: Strategy) => sum + s.capital_allocation, 0) || 0
      setTotalAllocation(total)
    } catch (error) {
      console.error('Failed to fetch strategies:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStartStrategy = async (strategyId: string) => {
    try {
      await fetchWithConfig(`/strategies/${strategyId}/start`, { method: 'POST' })
      await fetchStrategies()
      onStrategyChange?.()
    } catch (error) {
      console.error('Failed to start strategy:', error)
    }
  }

  const handleStopStrategy = async (strategyId: string) => {
    try {
      await fetchWithConfig(`/strategies/${strategyId}/stop`, { method: 'POST' })
      await fetchStrategies()
      onStrategyChange?.()
    } catch (error) {
      console.error('Failed to stop strategy:', error)
    }
  }

  const getStrategyIcon = (type: string) => {
    switch (type) {
      case 'conservative':
        return <Shield className="w-5 h-5 text-blue-500" />
      case 'balanced':
        return <BarChart3 className="w-5 h-5 text-yellow-500" />
      case 'degen':
        return <Zap className="w-5 h-5 text-red-500" />
      default:
        return <TrendingUp className="w-5 h-5 text-gray-500" />
    }
  }

  const getStrategyColor = (type: string) => {
    switch (type) {
      case 'conservative':
        return 'bg-blue-500/10 border-blue-500/20 hover:border-blue-500/40'
      case 'balanced':
        return 'bg-yellow-500/10 border-yellow-500/20 hover:border-yellow-500/40'
      case 'degen':
        return 'bg-red-500/10 border-red-500/20 hover:border-red-500/40'
      default:
        return 'bg-gray-500/10 border-gray-500/20'
    }
  }

  const formatPnL = (pnl: number) => {
    const isPositive = pnl >= 0
    return (
      <span className={isPositive ? 'text-green-500' : 'text-red-500'}>
        {isPositive ? '+' : ''}{pnl.toFixed(2)}%
      </span>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Strategy Control Panel</h2>
          <p className="text-gray-400 mt-1">Manage your trading strategies</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="btn-primary flex items-center gap-2"
          disabled={totalAllocation >= 100}
        >
          <Plus className="w-4 h-4" />
          Add Strategy
        </button>
      </div>

      {/* Allocation Progress */}
      <div className="bg-gray-900 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400">Total Capital Allocation</span>
          <span className="text-sm font-medium text-white">{totalAllocation.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-gray-800 rounded-full h-2">
          <motion.div
            className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${totalAllocation}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
        {totalAllocation >= 100 && (
          <p className="text-xs text-yellow-500 mt-2 flex items-center gap-1">
            <AlertCircle className="w-3 h-3" />
            Maximum allocation reached
          </p>
        )}
      </div>

      {/* Strategy Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <AnimatePresence>
          {strategies.map((strategy) => (
            <motion.div
              key={strategy.id}
              layout
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className={`rounded-lg border p-6 transition-all ${getStrategyColor(strategy.type)}`}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  {getStrategyIcon(strategy.type)}
                  <div>
                    <h3 className="font-semibold text-white capitalize">{strategy.type}</h3>
                    <p className="text-xs text-gray-400">{strategy.capital_allocation}% allocation</p>
                  </div>
                </div>
                <div className={`px-2 py-1 rounded text-xs font-medium ${
                  strategy.is_active 
                    ? 'bg-green-500/20 text-green-400' 
                    : 'bg-gray-500/20 text-gray-400'
                }`}>
                  {strategy.is_active ? 'Active' : 'Stopped'}
                </div>
              </div>

              {/* Performance Stats */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div>
                  <p className="text-xs text-gray-400">Total P&L</p>
                  <p className="text-sm font-medium">{formatPnL(strategy.performance.total_pnl)}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Win Rate</p>
                  <p className="text-sm font-medium text-white">{strategy.performance.win_rate.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Trades</p>
                  <p className="text-sm font-medium text-white">{strategy.performance.total_trades}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Positions</p>
                  <p className="text-sm font-medium text-white">{strategy.performance.active_positions}</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                {strategy.is_active ? (
                  <button
                    onClick={() => handleStopStrategy(strategy.id)}
                    className="flex-1 btn-secondary flex items-center justify-center gap-2"
                  >
                    <Pause className="w-4 h-4" />
                    Stop
                  </button>
                ) : (
                  <button
                    onClick={() => handleStartStrategy(strategy.id)}
                    className="flex-1 btn-primary flex items-center justify-center gap-2"
                  >
                    <Play className="w-4 h-4" />
                    Start
                  </button>
                )}
                <button
                  className="btn-ghost p-2"
                  onClick={() => {/* TODO: Remove strategy */}}
                >
                  <Trash2 className="w-4 h-4 text-red-400" />
                </button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Add Strategy Modal */}
      <AddStrategyModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onAdd={async () => {
          await fetchStrategies()
          onStrategyChange?.()
        }}
        remainingAllocation={100 - totalAllocation}
      />
    </div>
  )
}

// Add Strategy Modal Component
function AddStrategyModal({ 
  isOpen, 
  onClose, 
  onAdd, 
  remainingAllocation 
}: {
  isOpen: boolean
  onClose: () => void
  onAdd: () => void
  remainingAllocation: number
}) {
  const [selectedType, setSelectedType] = useState<string>('balanced')
  const [allocation, setAllocation] = useState(Math.min(33.33, remainingAllocation))
  const [loading, setLoading] = useState(false)

  const handleAdd = async () => {
    setLoading(true)
    try {
      const response = await fetchWithConfig('/strategies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          strategy_type: selectedType,
          capital_allocation: allocation
        })
      })
      
      if (response.ok) {
        onAdd()
        onClose()
      }
    } catch (error) {
      console.error('Failed to add strategy:', error)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9 }}
        animate={{ scale: 1 }}
        className="bg-gray-900 rounded-lg p-6 max-w-md w-full"
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="text-xl font-bold text-white mb-4">Add New Strategy</h3>
        
        {/* Strategy Type Selection */}
        <div className="space-y-4 mb-6">
          <label className="text-sm text-gray-400">Strategy Type</label>
          <div className="grid grid-cols-3 gap-3">
            {['conservative', 'balanced', 'degen'].map((type) => (
              <button
                key={type}
                onClick={() => setSelectedType(type)}
                className={`p-3 rounded-lg border transition-all ${
                  selectedType === type
                    ? 'border-purple-500 bg-purple-500/20'
                    : 'border-gray-700 hover:border-gray-600'
                }`}
              >
                <div className="text-center">
                  {type === 'conservative' && <Shield className="w-6 h-6 mx-auto mb-1 text-blue-500" />}
                  {type === 'balanced' && <BarChart3 className="w-6 h-6 mx-auto mb-1 text-yellow-500" />}
                  {type === 'degen' && <Zap className="w-6 h-6 mx-auto mb-1 text-red-500" />}
                  <p className="text-sm capitalize">{type}</p>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Capital Allocation */}
        <div className="space-y-4 mb-6">
          <label className="text-sm text-gray-400">Capital Allocation</label>
          <div className="flex items-center gap-4">
            <input
              type="range"
              min="1"
              max={remainingAllocation}
              value={allocation}
              onChange={(e) => setAllocation(parseFloat(e.target.value))}
              className="flex-1"
            />
            <span className="text-white font-medium w-16 text-right">{allocation.toFixed(1)}%</span>
          </div>
          <p className="text-xs text-gray-500">
            Remaining allocation: {remainingAllocation.toFixed(1)}%
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 btn-secondary"
          >
            Cancel
          </button>
          <button
            onClick={handleAdd}
            disabled={loading}
            className="flex-1 btn-primary"
          >
            {loading ? 'Adding...' : 'Add Strategy'}
          </button>
        </div>
      </motion.div>
    </motion.div>
  )
}