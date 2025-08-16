'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Play, Pause, Settings, TrendingUp, AlertTriangle, DollarSign, Activity, BarChart } from 'lucide-react'
import { apiClient } from '@/lib/api'
import { useWebSocket } from '@/lib/websocket'

interface BotStatus {
  enabled: boolean
  strategy: {
    name: string
    type: string
    description: string
  }
  performance: {
    win_rate: number
    total_pnl: number
    best_trade: number
    worst_trade: number
  }
  limits: {
    active_positions: number
    max_positions: number
    available_capital: number
  }
}

interface Strategy {
  type: string
  name: string
  description: string
  entry_rules: {
    max_risk_score: number
    min_apy: number
    min_tvl: number
  }
  exit_rules: {
    stop_loss: number
    take_profit: number
  }
  risk_limits: {
    max_positions: number
    max_portfolio_percent: number
  }
}

export default function TradingBotControl() {
  const [botStatus, setBotStatus] = useState<BotStatus | null>(null)
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [selectedStrategy, setSelectedStrategy] = useState<string>('balanced')
  const [isLoading, setIsLoading] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [paperTradingEnabled, setPaperTradingEnabled] = useState(false)
  const [paperTradingStats, setPaperTradingStats] = useState<any>(null)
  const { subscribe, isConnected } = useWebSocket()

  // Fetch bot status
  useEffect(() => {
    fetchBotStatus()
    fetchStrategies()
    fetchPaperTradingStatus()
    
    // Poll status every 5 seconds
    const interval = setInterval(() => {
      fetchBotStatus()
      fetchPaperTradingStatus()
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  // Handle WebSocket updates
  useEffect(() => {
    const unsubscribe = subscribe('bot_status', (message) => {
      if (message.data) {
        setBotStatus(prev => ({
          ...prev!,
          enabled: message.data.enabled,
          performance: message.data.performance,
          limits: {
            active_positions: message.data.active_positions,
            max_positions: prev?.limits.max_positions || 10,
            available_capital: message.data.available_capital
          }
        }))
      }
    })

    return unsubscribe
  }, [subscribe])

  const fetchBotStatus = async () => {
    try {
      const response = await fetch(`${apiClient.baseUrl}/bot/status`)
      const data = await response.json()
      setBotStatus(data)
      setSelectedStrategy(data.strategy?.type || 'balanced')
    } catch (error) {
      console.error('Failed to fetch bot status:', error)
    }
  }

  const fetchStrategies = async () => {
    try {
      const response = await fetch(`${apiClient.baseUrl}/bot/strategies`)
      const data = await response.json()
      setStrategies(data.strategies)
    } catch (error) {
      console.error('Failed to fetch strategies:', error)
    }
  }

  const fetchPaperTradingStatus = async () => {
    try {
      const response = await fetch(`${apiClient.baseUrl}/paper-trading/status`)
      const data = await response.json()
      setPaperTradingEnabled(data.enabled)
      setPaperTradingStats(data.performance)
    } catch (error) {
      console.error('Failed to fetch paper trading status:', error)
    }
  }

  const togglePaperTrading = async () => {
    setIsLoading(true)
    try {
      const endpoint = paperTradingEnabled ? '/paper-trading/disable' : '/paper-trading/enable'
      const response = await fetch(`${apiClient.baseUrl}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ initial_balance: 10000 })
      })
      
      if (response.ok) {
        await fetchPaperTradingStatus()
      }
    } catch (error) {
      console.error('Failed to toggle paper trading:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const toggleBot = async () => {
    setIsLoading(true)
    try {
      const endpoint = botStatus?.enabled ? '/bot/stop' : '/bot/start'
      const body = !botStatus?.enabled ? { strategy_type: selectedStrategy } : {}
      
      const response = await fetch(`${apiClient.baseUrl}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      
      if (response.ok) {
        await fetchBotStatus()
      }
    } catch (error) {
      console.error('Failed to toggle bot:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const updateStrategy = async (strategyType: string) => {
    setIsLoading(true)
    try {
      const response = await fetch(`${apiClient.baseUrl}/bot/strategy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strategy_type: strategyType })
      })
      
      if (response.ok) {
        setSelectedStrategy(strategyType)
        await fetchBotStatus()
      }
    } catch (error) {
      console.error('Failed to update strategy:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getStrategyColor = (type: string) => {
    switch (type) {
      case 'conservative': return 'text-green-500'
      case 'balanced': return 'text-blue-500'
      case 'degen': return 'text-red-500'
      default: return 'text-text-secondary'
    }
  }

  const getStrategyIcon = (type: string) => {
    switch (type) {
      case 'conservative': return '🛡️'
      case 'balanced': return '⚖️'
      case 'degen': return '🎰'
      default: return '🤖'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-terminal-surface/80 backdrop-blur-sm rounded-xl border border-terminal-border p-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className={`p-3 rounded-lg ${botStatus?.enabled ? 'bg-green-500/20' : 'bg-terminal-surface'} border ${botStatus?.enabled ? 'border-green-500' : 'border-terminal-border'}`}>
            <Activity className={`w-6 h-6 ${botStatus?.enabled ? 'text-green-500' : 'text-text-tertiary'}`} />
          </div>
          <div>
            <h3 className="text-xl font-bold text-text-primary">Trading Bot</h3>
            <p className="text-sm text-text-secondary">
              {botStatus?.enabled ? 'Actively trading' : 'Stopped'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 rounded-lg bg-terminal-surface border border-terminal-border hover:border-cyber-primary/50 transition-colors"
          >
            <Settings className="w-5 h-5 text-text-secondary" />
          </button>
          
          <button
            onClick={toggleBot}
            disabled={isLoading}
            className={`px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition-all ${
              botStatus?.enabled 
                ? 'bg-red-500/20 text-red-500 border border-red-500 hover:bg-red-500/30'
                : 'bg-cyber-primary text-black hover:bg-cyber-secondary'
            } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {botStatus?.enabled ? (
              <>
                <Pause className="w-4 h-4" />
                Stop Bot
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Start Bot
              </>
            )}
          </button>
        </div>
      </div>

      {/* Current Strategy */}
      <div className="bg-terminal-surface/50 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{getStrategyIcon(botStatus?.strategy?.type || 'balanced')}</span>
            <div>
              <div className="text-sm text-text-tertiary">Active Strategy</div>
              <div className={`text-lg font-bold ${getStrategyColor(botStatus?.strategy?.type || 'balanced')}`}>
                {botStatus?.strategy?.name || 'None'}
              </div>
            </div>
          </div>
          
          {botStatus?.strategy && (
            <div className="text-right">
              <div className="text-xs text-text-tertiary">Risk Profile</div>
              <div className="flex items-center gap-1 mt-1">
                {[...Array(3)].map((_, i) => (
                  <div
                    key={i}
                    className={`w-2 h-2 rounded-full ${
                      i < (botStatus.strategy.type === 'conservative' ? 1 : botStatus.strategy.type === 'balanced' ? 2 : 3)
                        ? getStrategyColor(botStatus.strategy.type) === 'text-green-500' ? 'bg-green-500' :
                          getStrategyColor(botStatus.strategy.type) === 'text-blue-500' ? 'bg-blue-500' : 'bg-red-500'
                        : 'bg-terminal-surface'
                    }`}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Performance Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-terminal-surface/30 rounded-lg p-3 border border-terminal-border"
        >
          <div className="flex items-center gap-2 text-text-tertiary text-sm mb-1">
            <TrendingUp className="w-4 h-4" />
            Win Rate
          </div>
          <div className="text-xl font-bold text-text-primary">
            {botStatus?.performance ? `${(botStatus.performance.win_rate * 100).toFixed(1)}%` : '0%'}
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-terminal-surface/30 rounded-lg p-3 border border-terminal-border"
        >
          <div className="flex items-center gap-2 text-text-tertiary text-sm mb-1">
            <DollarSign className="w-4 h-4" />
            Total P&L
          </div>
          <div className={`text-xl font-bold ${
            (botStatus?.performance?.total_pnl || 0) >= 0 ? 'text-green-500' : 'text-red-500'
          }`}>
            ${botStatus?.performance?.total_pnl?.toFixed(2) || '0.00'}
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-terminal-surface/30 rounded-lg p-3 border border-terminal-border"
        >
          <div className="flex items-center gap-2 text-text-tertiary text-sm mb-1">
            <Activity className="w-4 h-4" />
            Positions
          </div>
          <div className="text-xl font-bold text-text-primary">
            {botStatus?.limits?.active_positions || 0}/{botStatus?.limits?.max_positions || 0}
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-terminal-surface/30 rounded-lg p-3 border border-terminal-border"
        >
          <div className="flex items-center gap-2 text-text-tertiary text-sm mb-1">
            <BarChart className="w-4 h-4" />
            Available
          </div>
          <div className="text-xl font-bold text-text-primary">
            ${botStatus?.limits?.available_capital?.toFixed(0) || '0'}
          </div>
        </motion.div>
      </div>

      {/* Strategy Settings */}
      <AnimatePresence>
        {showSettings && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="border-t border-terminal-border pt-6">
              <h4 className="text-lg font-semibold text-text-primary mb-4">Select Strategy</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {strategies.map((strategy) => (
                  <motion.div
                    key={strategy.type}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => !botStatus?.enabled && setSelectedStrategy(strategy.type)}
                    className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      selectedStrategy === strategy.type
                        ? 'border-cyber-primary bg-cyber-primary/10'
                        : 'border-terminal-border bg-terminal-surface/30 hover:border-terminal-border/80'
                    } ${botStatus?.enabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl">{getStrategyIcon(strategy.type)}</span>
                      <h5 className={`font-bold ${getStrategyColor(strategy.type)}`}>
                        {strategy.name}
                      </h5>
                    </div>
                    
                    <p className="text-xs text-text-secondary mb-3">
                      {strategy.description}
                    </p>
                    
                    <div className="space-y-2 text-xs">
                      <div className="flex justify-between">
                        <span className="text-text-tertiary">Risk Score</span>
                        <span className="text-text-primary">≤ {strategy.entry_rules.max_risk_score}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-text-tertiary">Min APY</span>
                        <span className="text-text-primary">{strategy.entry_rules.min_apy}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-text-tertiary">Stop Loss</span>
                        <span className="text-red-500">{strategy.exit_rules.stop_loss}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-text-tertiary">Take Profit</span>
                        <span className="text-green-500">+{strategy.exit_rules.take_profit}%</span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              {!botStatus?.enabled && (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => updateStrategy(selectedStrategy)}
                  disabled={isLoading || selectedStrategy === botStatus?.strategy?.type}
                  className="mt-4 w-full py-3 rounded-lg bg-terminal-surface border border-terminal-border hover:border-cyber-primary/50 text-text-primary font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  Apply Strategy
                </motion.button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Paper Trading Toggle */}
      <div className="mt-6 p-4 bg-terminal-surface/50 rounded-lg border border-terminal-border">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${paperTradingEnabled ? 'bg-blue-500' : 'bg-gray-500'} animate-pulse`} />
            <div>
              <div className="text-sm font-medium text-text-primary">Paper Trading Mode</div>
              <div className="text-xs text-text-secondary">
                {paperTradingEnabled ? 'Testing with virtual funds' : 'Trade with real funds'}
              </div>
            </div>
          </div>
          <button
            onClick={togglePaperTrading}
            disabled={isLoading || botStatus?.enabled}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              paperTradingEnabled 
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500'
                : 'bg-terminal-surface border border-terminal-border text-text-secondary hover:border-cyber-primary/50'
            } ${isLoading || botStatus?.enabled ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {paperTradingEnabled ? 'Disable' : 'Enable'} Paper Trading
          </button>
        </div>

        {/* Paper Trading Stats */}
        {paperTradingEnabled && paperTradingStats && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-3 pt-3 border-t border-terminal-border"
          >
            <div className="grid grid-cols-3 gap-3 text-xs">
              <div>
                <div className="text-text-tertiary">Balance</div>
                <div className="text-text-primary font-medium">
                  ${paperTradingStats.current_balance?.toFixed(2) || '10,000'}
                </div>
              </div>
              <div>
                <div className="text-text-tertiary">P&L</div>
                <div className={`font-medium ${(paperTradingStats.total_pnl || 0) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  ${paperTradingStats.total_pnl?.toFixed(2) || '0.00'}
                </div>
              </div>
              <div>
                <div className="text-text-tertiary">Win Rate</div>
                <div className="text-text-primary font-medium">
                  {((paperTradingStats.win_rate || 0) * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Warning */}
      {botStatus?.enabled && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/30 flex items-start gap-2"
        >
          <AlertTriangle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-yellow-200">
            <strong>Bot is actively trading{paperTradingEnabled ? ' (Paper Mode)' : ''}.</strong> All positions are entered and exited automatically based on the {botStatus.strategy.name} strategy rules.
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}