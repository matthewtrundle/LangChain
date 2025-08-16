'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Zap, 
  TrendingUp, 
  TrendingDown, 
  Activity,
  DollarSign,
  AlertTriangle,
  Flame,
  Timer,
  BarChart3,
  ArrowUp,
  ArrowDown
} from 'lucide-react'
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart,
  Bar,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ResponsiveContainer,
  Cell,
  RadialBarChart,
  RadialBar
} from 'recharts'

interface DegenDashboardProps {
  strategyId: string
  performance: any
  isActive: boolean
}

interface Trade {
  id: string
  time: string
  pool: string
  action: 'BUY' | 'SELL'
  amount: number
  pnl?: number
  leverage: number
}

export default function DegenStrategyDashboard({ 
  strategyId, 
  performance, 
  isActive 
}: DegenDashboardProps) {
  const [realtimePnL, setRealtimePnL] = useState(0)
  const [trades, setTrades] = useState<Trade[]>([])
  const [leverageData, setLeverageData] = useState<any[]>([])
  const [volatilityData, setVolatilityData] = useState<any[]>([])
  const [pnlHistory, setPnlHistory] = useState<any[]>([])
  const tickerRef = useRef<HTMLDivElement>(null)

  // Simulate real-time P&L updates
  useEffect(() => {
    if (!isActive) return
    
    const interval = setInterval(() => {
      setRealtimePnL(prev => {
        const change = (Math.random() - 0.48) * 500 // Slight negative bias for realism
        return prev + change
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [isActive])

  // Simulate trade activity
  useEffect(() => {
    if (!isActive) return

    const tradeInterval = setInterval(() => {
      const newTrade: Trade = {
        id: Date.now().toString(),
        time: new Date().toLocaleTimeString(),
        pool: ['SOL-BONK', 'DOGE-USDC', 'PEPE-SOL', 'WIF-USDC', 'MEME-SOL'][Math.floor(Math.random() * 5)],
        action: Math.random() > 0.5 ? 'BUY' : 'SELL',
        amount: Math.floor(Math.random() * 5000) + 500,
        pnl: Math.random() > 0.5 ? Math.random() * 200 : -Math.random() * 150,
        leverage: Math.floor(Math.random() * 10) + 1
      }
      
      setTrades(prev => [newTrade, ...prev.slice(0, 19)])
    }, 3000 + Math.random() * 5000) // Random interval 3-8 seconds

    return () => clearInterval(tradeInterval)
  }, [isActive])

  // Mock data generation
  useEffect(() => {
    // Leverage gauge data
    const currentLeverage = 7.5
    setLeverageData([{
      name: 'Leverage',
      value: (currentLeverage / 10) * 100,
      fill: currentLeverage > 8 ? '#EF4444' : currentLeverage > 5 ? '#F59E0B' : '#10B981'
    }])

    // Volatility history
    const mockVolatility = Array.from({ length: 24 }, (_, i) => ({
      hour: `${i}:00`,
      volatility: 20 + Math.random() * 60,
      trades: Math.floor(Math.random() * 50) + 10
    }))
    setVolatilityData(mockVolatility)

    // P&L history (last 100 trades)
    const mockPnL = Array.from({ length: 100 }, (_, i) => ({
      trade: i + 1,
      pnl: Math.random() > 0.45 ? Math.random() * 500 : -Math.random() * 400,
      cumulative: 0 // Will calculate below
    }))
    
    // Calculate cumulative P&L
    let cumulative = 0
    mockPnL.forEach(trade => {
      cumulative += trade.pnl
      trade.cumulative = cumulative
    })
    
    setPnlHistory(mockPnL)
  }, [])

  const formatPnL = (value: number) => {
    const isPositive = value >= 0
    return (
      <span className={isPositive ? 'text-green-500' : 'text-red-500'}>
        {isPositive ? '+' : ''}{value.toFixed(2)}
      </span>
    )
  }

  const formatCurrency = (value: number) => `$${value.toLocaleString()}`

  return (
    <div className="space-y-6">
      {/* Header with Live P&L Ticker */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Zap className="w-8 h-8 text-red-500" />
          <div>
            <h2 className="text-2xl font-bold text-white">Degen Strategy</h2>
            <p className="text-gray-400">High risk, high reward plays</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          {/* Live P&L Ticker */}
          <motion.div
            className={`px-6 py-3 rounded-lg font-mono text-2xl font-bold ${
              realtimePnL >= 0 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
            }`}
            animate={{
              scale: [1, 1.05, 1],
            }}
            transition={{
              duration: 0.5,
              repeat: Infinity,
              repeatDelay: 2
            }}
          >
            {realtimePnL >= 0 ? '+' : ''}{realtimePnL.toFixed(2)} USDC
          </motion.div>
          <div className={`px-4 py-2 rounded-lg font-medium ${
            isActive 
              ? 'bg-red-500/20 text-red-400 animate-pulse' 
              : 'bg-gray-500/20 text-gray-400'
          }`}>
            {isActive ? '🔥 LIVE' : 'Inactive'}
          </div>
        </div>
      </div>

      {/* Risk Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="24h P&L"
          value={formatCurrency(3250)}
          icon={<Flame className="w-5 h-5" />}
          trend="up"
          color="red"
          pulse={true}
        />
        <MetricCard
          title="Win Rate"
          value="45.2%"
          icon={<Activity className="w-5 h-5" />}
          trend="down"
          color="yellow"
        />
        <MetricCard
          title="Avg Leverage"
          value="7.5x"
          icon={<BarChart3 className="w-5 h-5" />}
          trend="up"
          color="red"
        />
        <MetricCard
          title="Active Trades"
          value="23"
          icon={<Timer className="w-5 h-5" />}
          trend="stable"
          color="blue"
          pulse={true}
        />
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Leverage Gauge */}
        <div className="bg-gray-900 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            Current Leverage
            <AlertTriangle className="w-4 h-4 text-yellow-500" />
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <RadialBarChart 
              cx="50%" 
              cy="50%" 
              innerRadius="60%" 
              outerRadius="90%" 
              data={leverageData}
              startAngle={180} 
              endAngle={0}
            >
              <RadialBar dataKey="value" cornerRadius={10} fill={leverageData[0]?.fill} />
              <text 
                x="50%" 
                y="50%" 
                textAnchor="middle" 
                dominantBaseline="middle" 
                className="fill-white text-3xl font-bold"
              >
                7.5x
              </text>
              <text 
                x="50%" 
                y="65%" 
                textAnchor="middle" 
                dominantBaseline="middle" 
                className="fill-gray-400 text-sm"
              >
                High Risk!
              </text>
            </RadialBarChart>
          </ResponsiveContainer>
          <div className="mt-4 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Max Allowed:</span>
              <span className="text-white">10x</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Liquidation Risk:</span>
              <span className="text-red-400 font-bold">HIGH</span>
            </div>
          </div>
        </div>

        {/* Real-time Trade Feed */}
        <div className="bg-gray-900 rounded-lg p-6 lg:col-span-2">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            Live Trade Activity
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
          </h3>
          <div className="space-y-2 max-h-[300px] overflow-y-auto custom-scrollbar">
            <AnimatePresence mode="popLayout">
              {trades.map(trade => (
                <motion.div
                  key={trade.id}
                  layout
                  initial={{ opacity: 0, x: -50 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 50 }}
                  className="flex items-center justify-between p-3 bg-gray-800 rounded-lg border border-gray-700"
                >
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded ${
                      trade.action === 'BUY' ? 'bg-green-500/20' : 'bg-red-500/20'
                    }`}>
                      {trade.action === 'BUY' ? 
                        <ArrowUp className="w-4 h-4 text-green-400" /> : 
                        <ArrowDown className="w-4 h-4 text-red-400" />
                      }
                    </div>
                    <div>
                      <div className="text-sm font-medium text-white">{trade.pool}</div>
                      <div className="text-xs text-gray-400">{trade.time} • {trade.leverage}x leverage</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-white">${trade.amount}</div>
                    {trade.pnl && (
                      <div className="text-xs">{formatPnL(trade.pnl)}</div>
                    )}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>

        {/* P&L Chart */}
        <div className="bg-gray-900 rounded-lg p-6 lg:col-span-3">
          <h3 className="text-lg font-semibold text-white mb-4">Cumulative P&L (Last 100 Trades)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={pnlHistory}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="trade" 
                stroke="#9CA3AF"
                fontSize={12}
              />
              <YAxis 
                stroke="#9CA3AF"
                fontSize={12}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }}
                formatter={(value: any) => [`$${value.toFixed(2)}`, 'P&L']}
              />
              <defs>
                <linearGradient id="colorPnL" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10B981" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#10B981" stopOpacity={0.1}/>
                </linearGradient>
                <linearGradient id="colorLoss" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#EF4444" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#EF4444" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <Area 
                type="monotone" 
                dataKey="cumulative" 
                stroke="#10B981" 
                fill="url(#colorPnL)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Volatility Index */}
        <div className="bg-gray-900 rounded-lg p-6 lg:col-span-3">
          <h3 className="text-lg font-semibold text-white mb-4">24h Volatility & Trade Frequency</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={volatilityData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="hour" 
                stroke="#9CA3AF"
                fontSize={12}
              />
              <YAxis 
                yAxisId="left"
                stroke="#9CA3AF"
                fontSize={12}
              />
              <YAxis 
                yAxisId="right"
                orientation="right"
                stroke="#9CA3AF"
                fontSize={12}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }}
              />
              <Bar 
                yAxisId="left"
                dataKey="volatility" 
                fill="#EF4444"
                fillOpacity={0.6}
                name="Volatility %"
              />
              <Line 
                yAxisId="right"
                type="monotone" 
                dataKey="trades" 
                stroke="#F59E0B" 
                strokeWidth={2}
                name="Trade Count"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Risk Warnings */}
      <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-red-500" />
          Active Risk Alerts
        </h3>
        <div className="space-y-3">
          {[
            { level: 'HIGH', message: 'Leverage exceeds 5x on 3 positions', time: '2 min ago' },
            { level: 'MEDIUM', message: 'Volatility spike detected in BONK pool', time: '5 min ago' },
            { level: 'HIGH', message: 'Position size exceeds 15% of portfolio', time: '12 min ago' }
          ].map((alert, index) => (
            <div key={index} className="flex items-start gap-3">
              <div className={`px-2 py-1 rounded text-xs font-bold ${
                alert.level === 'HIGH' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'
              }`}>
                {alert.level}
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-300">{alert.message}</p>
                <p className="text-xs text-gray-500">{alert.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Enhanced MetricCard with pulse animation
function MetricCard({ 
  title, 
  value, 
  icon, 
  trend, 
  color,
  pulse = false
}: {
  title: string
  value: string
  icon: React.ReactNode
  trend: 'up' | 'down' | 'stable'
  color: 'blue' | 'green' | 'yellow' | 'red'
  pulse?: boolean
}) {
  const colors = {
    blue: 'bg-blue-500/10 border-blue-500/20 text-blue-400',
    green: 'bg-green-500/10 border-green-500/20 text-green-400',
    yellow: 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400',
    red: 'bg-red-500/10 border-red-500/20 text-red-400'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`p-4 rounded-lg border ${colors[color]} ${pulse ? 'animate-pulse-slow' : ''}`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-400">{title}</span>
        {icon}
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
    </motion.div>
  )
}