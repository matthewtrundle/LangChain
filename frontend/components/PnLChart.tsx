'use client'

import { motion } from 'framer-motion'
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  ReferenceLine
} from 'recharts'
import { useState, useEffect } from 'react'

interface PnLDataPoint {
  timestamp: string
  value: number
  pnl: number
  fees: number
  il: number
}

interface PnLChartProps {
  data: PnLDataPoint[]
  initialValue: number
  className?: string
}

export default function PnLChart({ data, initialValue, className = '' }: PnLChartProps) {
  const [selectedTimeframe, setSelectedTimeframe] = useState<'1H' | '24H' | '7D' | 'ALL'>('24H')
  const [isAnimated, setIsAnimated] = useState(false)
  
  useEffect(() => {
    // Trigger animation on mount
    setTimeout(() => setIsAnimated(true), 100)
  }, [])
  
  // Calculate current P&L
  const currentValue = data[data.length - 1]?.value || initialValue
  const totalPnL = currentValue - initialValue
  const pnlPercent = ((currentValue - initialValue) / initialValue) * 100
  const isProfit = totalPnL >= 0
  
  // Calculate max drawdown
  const maxDrawdown = Math.min(...data.map(d => d.pnl))
  const maxProfit = Math.max(...data.map(d => d.pnl))
  
  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload[0]) {
      const data = payload[0].payload
      return (
        <div className="bg-terminal-card border border-terminal-border rounded-lg p-3 shadow-xl">
          <p className="text-xs text-text-tertiary mb-1">
            {new Date(data.timestamp).toLocaleString()}
          </p>
          <div className="space-y-1">
            <div className="flex justify-between gap-4">
              <span className="text-xs text-text-tertiary">Value:</span>
              <span className="text-sm font-semibold text-text-primary">
                ${data.value.toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-xs text-text-tertiary">P&L:</span>
              <span className={`text-sm font-semibold ${data.pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {data.pnl >= 0 ? '+' : ''}{data.pnl.toFixed(2)}%
              </span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-xs text-text-tertiary">Fees:</span>
              <span className="text-sm text-cyber-primary">
                +${data.fees.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-xs text-text-tertiary">IL:</span>
              <span className="text-sm text-orange-500">
                -${Math.abs(data.il).toFixed(2)}
              </span>
            </div>
          </div>
        </div>
      )
    }
    return null
  }
  
  return (
    <div className={`bg-terminal-card border border-terminal-border rounded-lg p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-text-primary mb-1">Position Performance</h3>
          <div className="flex items-baseline gap-3">
            <span className={`text-3xl font-bold ${isProfit ? 'text-green-500' : 'text-red-500'}`}>
              {isProfit ? '+' : ''}{pnlPercent.toFixed(2)}%
            </span>
            <span className="text-sm text-text-tertiary">
              ${currentValue.toLocaleString()}
            </span>
          </div>
        </div>
        
        {/* Timeframe selector */}
        <div className="flex gap-1 bg-terminal-surface rounded-lg p-1">
          {(['1H', '24H', '7D', 'ALL'] as const).map((tf) => (
            <button
              key={tf}
              onClick={() => setSelectedTimeframe(tf)}
              className={`px-3 py-1 text-xs font-medium rounded transition-all ${
                selectedTimeframe === tf
                  ? 'bg-cyber-primary text-black'
                  : 'text-text-tertiary hover:text-text-primary'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>
      
      {/* Key metrics */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-center"
        >
          <div className="text-xs text-text-tertiary mb-1">Total Fees</div>
          <div className="text-lg font-semibold text-cyber-primary">
            ${data[data.length - 1]?.fees.toFixed(2) || '0.00'}
          </div>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-center"
        >
          <div className="text-xs text-text-tertiary mb-1">IL Impact</div>
          <div className="text-lg font-semibold text-orange-500">
            -${Math.abs(data[data.length - 1]?.il || 0).toFixed(2)}
          </div>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="text-center"
        >
          <div className="text-xs text-text-tertiary mb-1">Max Profit</div>
          <div className="text-lg font-semibold text-green-500">
            +{maxProfit.toFixed(2)}%
          </div>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="text-center"
        >
          <div className="text-xs text-text-tertiary mb-1">Max Drawdown</div>
          <div className="text-lg font-semibold text-red-500">
            {maxDrawdown.toFixed(2)}%
          </div>
        </motion.div>
      </div>
      
      {/* Chart */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: isAnimated ? 1 : 0 }}
        transition={{ duration: 0.5 }}
        className="h-64"
      >
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorPnL" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={isProfit ? '#10b981' : '#ef4444'} stopOpacity={0.3}/>
                <stop offset="95%" stopColor={isProfit ? '#10b981' : '#ef4444'} stopOpacity={0}/>
              </linearGradient>
            </defs>
            
            <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
            
            <XAxis 
              dataKey="timestamp" 
              stroke="#666"
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => {
                const date = new Date(value)
                return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
              }}
            />
            
            <YAxis 
              stroke="#666"
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => `${value}%`}
            />
            
            <Tooltip content={<CustomTooltip />} />
            
            <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
            
            <Area
              type="monotone"
              dataKey="pnl"
              stroke={isProfit ? '#10b981' : '#ef4444'}
              strokeWidth={2}
              fill="url(#colorPnL)"
              animationDuration={1500}
              animationBegin={0}
            />
          </AreaChart>
        </ResponsiveContainer>
      </motion.div>
      
      {/* IL Warning */}
      {Math.abs(data[data.length - 1]?.il || 0) > 50 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="mt-4 p-3 bg-orange-500/10 border border-orange-500/30 rounded-lg"
        >
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse" />
            <span className="text-sm text-orange-500">
              High impermanent loss detected. Consider rebalancing your position.
            </span>
          </div>
        </motion.div>
      )}
    </div>
  )
}