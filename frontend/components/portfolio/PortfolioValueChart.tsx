'use client'

import { motion } from 'framer-motion'
import { useEffect, useState, useRef } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts'

interface PortfolioValueChartProps {
  data: {
    timestamp: string
    value: number
    pnl: number
  }[]
  isLoading?: boolean
}

export default function PortfolioValueChart({ data, isLoading = false }: PortfolioValueChartProps) {
  const [animatedData, setAnimatedData] = useState<typeof data>([])
  const chartRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Animate data points appearing
    const timer = setTimeout(() => {
      setAnimatedData(data)
    }, 100)
    return () => clearTimeout(timer)
  }, [data])

  const formatValue = (value: number) => `$${value.toLocaleString()}`
  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      const isProfit = data.pnl >= 0
      
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-terminal-card border border-cyber-primary/30 rounded-lg p-4 shadow-xl"
          style={{
            boxShadow: '0 0 20px rgba(0, 255, 170, 0.3)',
          }}
        >
          <div className="text-text-tertiary text-xs mb-1">{formatDate(label)}</div>
          <div className="text-text-primary text-lg font-bold">{formatValue(data.value)}</div>
          <div className={`text-sm font-semibold ${isProfit ? 'text-cyber-primary' : 'text-red-500'}`}>
            {isProfit ? '+' : ''}{formatValue(data.pnl)} ({((data.pnl / (data.value - data.pnl)) * 100).toFixed(2)}%)
          </div>
        </motion.div>
      )
    }
    return null
  }

  if (isLoading) {
    return (
      <div className="h-96 flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="w-16 h-16 border-4 border-cyber-primary border-t-transparent rounded-full"
        />
      </div>
    )
  }

  return (
    <motion.div
      ref={chartRef}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="relative"
    >
      {/* Glow effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-cyber-primary/10 to-cyber-secondary/10 blur-3xl -z-10" />
      
      <ResponsiveContainer width="100%" height={400}>
        <AreaChart data={animatedData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="portfolioGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00ffaa" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#00ffaa" stopOpacity={0.1}/>
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="rgba(255, 255, 255, 0.1)" 
            vertical={false}
          />
          
          <XAxis 
            dataKey="timestamp"
            tickFormatter={formatDate}
            stroke="#666"
            tick={{ fill: '#999', fontSize: 12 }}
          />
          
          <YAxis 
            tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
            stroke="#666"
            tick={{ fill: '#999', fontSize: 12 }}
          />
          
          <Tooltip content={<CustomTooltip />} />
          
          <Area
            type="monotone"
            dataKey="value"
            stroke="#00ffaa"
            strokeWidth={3}
            fillOpacity={1}
            fill="url(#portfolioGradient)"
            filter="url(#glow)"
            animationDuration={1500}
            animationEasing="ease-out"
          />
        </AreaChart>
      </ResponsiveContainer>
      
      {/* Stats overlay */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="absolute top-4 left-4 bg-terminal-card/80 backdrop-blur-sm rounded-lg p-3 border border-terminal-border"
      >
        <div className="text-text-tertiary text-xs mb-1">Portfolio Value</div>
        <div className="text-text-primary text-2xl font-bold">
          {data.length > 0 ? formatValue(data[data.length - 1].value) : '$0'}
        </div>
        {data.length > 0 && data[data.length - 1].pnl !== 0 && (
          <div className={`text-sm font-semibold ${data[data.length - 1].pnl >= 0 ? 'text-cyber-primary' : 'text-red-500'}`}>
            {data[data.length - 1].pnl >= 0 ? '+' : ''}{formatValue(data[data.length - 1].pnl)}
          </div>
        )}
      </motion.div>
    </motion.div>
  )
}