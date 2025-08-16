'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Activity,
  DollarSign,
  PieChart as PieChartIcon,
  Shuffle,
  Target
} from 'lucide-react'
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  ScatterChart,
  Scatter,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ResponsiveContainer,
  Cell,
  ZAxis
} from 'recharts'

interface BalancedDashboardProps {
  strategyId: string
  performance: any
  isActive: boolean
}

export default function BalancedStrategyDashboard({ 
  strategyId, 
  performance, 
  isActive 
}: BalancedDashboardProps) {
  const [timeframe, setTimeframe] = useState<'24h' | '7d' | '30d'>('7d')
  const [sharpeData, setSharpeData] = useState<any[]>([])
  const [riskRewardData, setRiskRewardData] = useState<any[]>([])
  const [correlationData, setCorrelationData] = useState<any[]>([])
  const [allocationHistory, setAllocationHistory] = useState<any[]>([])

  // Mock data generation
  useEffect(() => {
    // Sharpe ratio trend
    const mockSharpe = Array.from({ length: 30 }, (_, i) => ({
      date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toLocaleDateString(),
      sharpe: 1.2 + Math.sin(i / 5) * 0.5 + Math.random() * 0.2,
      benchmark: 0.8
    }))
    setSharpeData(mockSharpe)

    // Risk/Reward scatter
    const mockRiskReward = [
      { name: 'SOL-USDC', risk: 15, reward: 18, size: 2000 },
      { name: 'RAY-USDC', risk: 25, reward: 35, size: 1500 },
      { name: 'ORCA-USDC', risk: 30, reward: 45, size: 1000 },
      { name: 'SRM-USDC', risk: 35, reward: 40, size: 800 },
      { name: 'MNGO-USDC', risk: 40, reward: 55, size: 1200 },
      { name: 'STEP-USDC', risk: 45, reward: 60, size: 600 }
    ]
    setRiskRewardData(mockRiskReward)

    // Correlation matrix data
    const assets = ['SOL', 'RAY', 'ORCA', 'SRM', 'MNGO']
    const correlations = []
    for (let i = 0; i < assets.length; i++) {
      for (let j = 0; j < assets.length; j++) {
        correlations.push({
          x: assets[i],
          y: assets[j],
          value: i === j ? 1 : Math.random() * 0.8 - 0.2
        })
      }
    }
    setCorrelationData(correlations)

    // Allocation history
    const mockAllocation = Array.from({ length: 30 }, (_, i) => ({
      date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toLocaleDateString(),
      'Stable Pools': 40 + Math.sin(i / 10) * 5,
      'Blue Chip': 35 - Math.sin(i / 10) * 5,
      'Mid Cap': 20 + Math.random() * 5,
      'High Risk': 5
    }))
    setAllocationHistory(mockAllocation)
  }, [timeframe])

  const formatPercent = (value: number) => `${value.toFixed(1)}%`
  const formatValue = (value: number) => value.toFixed(2)

  // Color scale for correlation heatmap
  const getCorrelationColor = (value: number) => {
    if (value > 0.7) return '#10B981'
    if (value > 0.3) return '#3B82F6'
    if (value > -0.3) return '#6B7280'
    if (value > -0.7) return '#F59E0B'
    return '#EF4444'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <BarChart3 className="w-8 h-8 text-yellow-500" />
          <div>
            <h2 className="text-2xl font-bold text-white">Balanced Strategy</h2>
            <p className="text-gray-400">Optimized risk-reward balance</p>
          </div>
        </div>
        <div className={`px-4 py-2 rounded-lg font-medium ${
          isActive 
            ? 'bg-green-500/20 text-green-400' 
            : 'bg-gray-500/20 text-gray-400'
        }`}>
          {isActive ? 'Active' : 'Inactive'}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="Total Return"
          value={formatPercent(performance?.total_pnl || 28.5)}
          icon={<TrendingUp className="w-5 h-5" />}
          trend="up"
          color="yellow"
        />
        <MetricCard
          title="Sharpe Ratio"
          value="1.42"
          icon={<Target className="w-5 h-5" />}
          trend="up"
          color="green"
        />
        <MetricCard
          title="Max Drawdown"
          value={formatPercent(8.3)}
          icon={<TrendingDown className="w-5 h-5" />}
          trend="stable"
          color="yellow"
        />
        <MetricCard
          title="Active Positions"
          value="12"
          icon={<Shuffle className="w-5 h-5" />}
          trend="stable"
          color="blue"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk/Reward Scatter */}
        <div className="bg-gray-900 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Risk/Reward Analysis</h3>
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                type="number" 
                dataKey="risk" 
                name="Risk %" 
                stroke="#9CA3AF"
                label={{ value: 'Risk %', position: 'insideBottom', offset: -10 }}
              />
              <YAxis 
                type="number" 
                dataKey="reward" 
                name="Reward %" 
                stroke="#9CA3AF"
                label={{ value: 'Reward %', position: 'insideLeft', angle: -90 }}
              />
              <ZAxis type="number" dataKey="size" range={[50, 400]} />
              <Tooltip 
                cursor={{ strokeDasharray: '3 3' }}
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }}
                formatter={(value: any, name: string) => [
                  name === 'size' ? `$${value}K` : `${value}%`, 
                  name
                ]}
              />
              <Scatter 
                name="Pools" 
                data={riskRewardData} 
                fill="#F59E0B"
              >
                {riskRewardData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.reward > entry.risk * 1.5 ? '#10B981' : '#F59E0B'} 
                  />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
          <div className="mt-4 text-xs text-gray-400">
            <p>Bubble size represents position size</p>
            <p className="text-green-400">Green: High reward/risk ratio</p>
          </div>
        </div>

        {/* Sharpe Ratio Trend */}
        <div className="bg-gray-900 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Sharpe Ratio Trend</h3>
            <div className="flex gap-2">
              {(['24h', '7d', '30d'] as const).map((tf) => (
                <button
                  key={tf}
                  onClick={() => setTimeframe(tf)}
                  className={`px-3 py-1 rounded text-sm ${
                    timeframe === tf 
                      ? 'bg-yellow-500/20 text-yellow-400' 
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  {tf}
                </button>
              ))}
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={sharpeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="date" 
                stroke="#9CA3AF"
                fontSize={12}
              />
              <YAxis 
                stroke="#9CA3AF"
                fontSize={12}
                domain={[0, 'dataMax + 0.5']}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="sharpe" 
                stroke="#F59E0B" 
                strokeWidth={2}
                name="Strategy Sharpe"
                dot={false}
              />
              <Line 
                type="monotone" 
                dataKey="benchmark" 
                stroke="#6B7280" 
                strokeWidth={2}
                name="Market Benchmark"
                strokeDasharray="5 5"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Allocation History */}
        <div className="bg-gray-900 rounded-lg p-6 lg:col-span-2">
          <h3 className="text-lg font-semibold text-white mb-4">Allocation Over Time</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={allocationHistory}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="date" 
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
              />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="Stable Pools" 
                stackId="1" 
                stroke="#3B82F6" 
                fill="#3B82F6"
                fillOpacity={0.6}
              />
              <Area 
                type="monotone" 
                dataKey="Blue Chip" 
                stackId="1" 
                stroke="#10B981" 
                fill="#10B981"
                fillOpacity={0.6}
              />
              <Area 
                type="monotone" 
                dataKey="Mid Cap" 
                stackId="1" 
                stroke="#F59E0B" 
                fill="#F59E0B"
                fillOpacity={0.6}
              />
              <Area 
                type="monotone" 
                dataKey="High Risk" 
                stackId="1" 
                stroke="#EF4444" 
                fill="#EF4444"
                fillOpacity={0.6}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Correlation Matrix */}
        <div className="bg-gray-900 rounded-lg p-6 lg:col-span-2">
          <h3 className="text-lg font-semibold text-white mb-4">Asset Correlation Matrix</h3>
          <div className="grid grid-cols-6 gap-1">
            <div></div>
            {['SOL', 'RAY', 'ORCA', 'SRM', 'MNGO'].map(asset => (
              <div key={asset} className="text-center text-xs text-gray-400 font-medium">
                {asset}
              </div>
            ))}
            
            {['SOL', 'RAY', 'ORCA', 'SRM', 'MNGO'].map(asset1 => (
              <>
                <div key={`label-${asset1}`} className="text-right text-xs text-gray-400 font-medium pr-2">
                  {asset1}
                </div>
                {['SOL', 'RAY', 'ORCA', 'SRM', 'MNGO'].map(asset2 => {
                  const correlation = correlationData.find(
                    d => d.x === asset1 && d.y === asset2
                  )?.value || 0
                  return (
                    <div
                      key={`${asset1}-${asset2}`}
                      className="aspect-square rounded flex items-center justify-center text-xs font-medium"
                      style={{
                        backgroundColor: getCorrelationColor(correlation),
                        opacity: 0.8
                      }}
                    >
                      {correlation.toFixed(2)}
                    </div>
                  )
                })}
              </>
            ))}
          </div>
          <div className="mt-4 flex items-center justify-center gap-4 text-xs text-gray-400">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-red-500 rounded"></div>
              <span>Strong Negative</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-gray-500 rounded"></div>
              <span>Neutral</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-green-500 rounded"></div>
              <span>Strong Positive</span>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Summary */}
      <div className="bg-gray-900 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Strategy Performance Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div>
            <p className="text-sm text-gray-400">Win Rate</p>
            <p className="text-xl font-bold text-white">68.5%</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Avg Position Size</p>
            <p className="text-xl font-bold text-white">$2,450</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Risk-Adjusted Return</p>
            <p className="text-xl font-bold text-green-400">+1.42</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Correlation to Market</p>
            <p className="text-xl font-bold text-white">0.65</p>
          </div>
        </div>
      </div>
    </div>
  )
}

// Reuse MetricCard component
function MetricCard({ 
  title, 
  value, 
  icon, 
  trend, 
  color 
}: {
  title: string
  value: string
  icon: React.ReactNode
  trend: 'up' | 'down' | 'stable'
  color: 'blue' | 'green' | 'yellow' | 'red'
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
      className={`p-4 rounded-lg border ${colors[color]}`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-400">{title}</span>
        {icon}
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
    </motion.div>
  )
}