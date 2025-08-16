'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  PieChart as PieChartIcon, 
  TrendingUp, 
  TrendingDown, 
  Activity,
  DollarSign,
  AlertTriangle,
  BarChart3,
  Target,
  Layers,
  RefreshCw
} from 'lucide-react'
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  ComposedChart,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ResponsiveContainer,
  Treemap
} from 'recharts'
import { usePaperTrading } from '@/contexts/PaperTradingContext'

interface Strategy {
  id: string
  type: string
  allocation: number
  performance: {
    total_pnl: number
    risk_contribution: number
    sharpe_ratio: number
  }
}

export default function AggregatePortfolioView() {
  const { isPaperMode } = usePaperTrading()
  const [timeframe, setTimeframe] = useState<'24h' | '7d' | '30d' | 'all'>('7d')
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [performanceData, setPerformanceData] = useState<any[]>([])
  const [allocationData, setAllocationData] = useState<any[]>([])
  const [riskData, setRiskData] = useState<any[]>([])
  const [attributionData, setAttributionData] = useState<any[]>([])

  // Mock data generation
  useEffect(() => {
    // Mock strategies
    const mockStrategies: Strategy[] = [
      {
        id: '1',
        type: 'Conservative',
        allocation: 40,
        performance: {
          total_pnl: 12.5,
          risk_contribution: 15,
          sharpe_ratio: 1.85
        }
      },
      {
        id: '2',
        type: 'Balanced',
        allocation: 35,
        performance: {
          total_pnl: 28.5,
          risk_contribution: 35,
          sharpe_ratio: 1.42
        }
      },
      {
        id: '3',
        type: 'Degen',
        allocation: 25,
        performance: {
          total_pnl: 45.2,
          risk_contribution: 50,
          sharpe_ratio: 0.95
        }
      }
    ]
    setStrategies(mockStrategies)

    // Combined performance over time
    const days = timeframe === '24h' ? 24 : timeframe === '7d' ? 7 : timeframe === '30d' ? 30 : 90
    const mockPerformance = Array.from({ length: days }, (_, i) => {
      const date = new Date(Date.now() - (days - i - 1) * 24 * 60 * 60 * 1000)
      return {
        date: timeframe === '24h' ? `${date.getHours()}:00` : date.toLocaleDateString(),
        Conservative: 100 + i * 0.5 + Math.random() * 2,
        Balanced: 100 + i * 1.0 + Math.random() * 5,
        Degen: 100 + i * 1.5 + Math.random() * 10 - 5,
        Total: 100 + i * 1.0 + Math.random() * 3
      }
    })
    setPerformanceData(mockPerformance)

    // Allocation data for pie chart
    const allocData = mockStrategies.map(s => ({
      name: s.type,
      value: s.allocation,
      color: s.type === 'Conservative' ? '#3B82F6' : s.type === 'Balanced' ? '#F59E0B' : '#EF4444'
    }))
    setAllocationData(allocData)

    // Risk contribution
    const riskContribution = mockStrategies.map(s => ({
      strategy: s.type,
      risk: s.performance.risk_contribution,
      return: s.performance.total_pnl,
      sharpe: s.performance.sharpe_ratio
    }))
    setRiskData(riskContribution)

    // Performance attribution (waterfall)
    const attribution = [
      { name: 'Starting Value', value: 10000, type: 'start' },
      { name: 'Conservative (+12.5%)', value: 500, type: 'positive' },
      { name: 'Balanced (+28.5%)', value: 997, type: 'positive' },
      { name: 'Degen (+45.2%)', value: 1130, type: 'positive' },
      { name: 'Fees & Costs', value: -127, type: 'negative' },
      { name: 'Final Value', value: 12500, type: 'end' }
    ]
    setAttributionData(attribution)
  }, [timeframe])

  const totalPnL = strategies.reduce((sum, s) => sum + s.performance.total_pnl * s.allocation / 100, 0)
  const avgSharpe = strategies.reduce((sum, s) => sum + s.performance.sharpe_ratio * s.allocation / 100, 0)

  const COLORS = {
    Conservative: '#3B82F6',
    Balanced: '#F59E0B',
    Degen: '#EF4444'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white">Portfolio Overview</h2>
          <p className="text-gray-400 mt-1">
            Combined performance across all strategies
            {isPaperMode && <span className="text-yellow-500 ml-2">(Paper Trading)</span>}
          </p>
        </div>
        <div className="flex gap-2">
          {(['24h', '7d', '30d', 'all'] as const).map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-4 py-2 rounded text-sm font-medium transition-all ${
                timeframe === tf 
                  ? 'bg-purple-500/20 text-purple-400 border border-purple-500/40' 
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {tf === 'all' ? 'All Time' : tf}
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <MetricCard
          title="Total Portfolio Value"
          value="$12,500"
          subtitle="+25.0%"
          icon={<DollarSign className="w-5 h-5" />}
          trend="up"
          color="purple"
        />
        <MetricCard
          title="Total Return"
          value={`${totalPnL.toFixed(1)}%`}
          subtitle="Weighted avg"
          icon={<TrendingUp className="w-5 h-5" />}
          trend="up"
          color="green"
        />
        <MetricCard
          title="Portfolio Sharpe"
          value={avgSharpe.toFixed(2)}
          subtitle="Risk-adjusted"
          icon={<Target className="w-5 h-5" />}
          trend="stable"
          color="blue"
        />
        <MetricCard
          title="Active Strategies"
          value="3"
          subtitle="All running"
          icon={<Layers className="w-5 h-5" />}
          trend="stable"
          color="yellow"
        />
        <MetricCard
          title="Total Positions"
          value="47"
          subtitle="Across strategies"
          icon={<Activity className="w-5 h-5" />}
          trend="up"
          color="purple"
        />
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Portfolio Performance Chart */}
        <div className="bg-gray-900 rounded-lg p-6 lg:col-span-2">
          <h3 className="text-lg font-semibold text-white mb-4">Portfolio Performance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="date" 
                stroke="#9CA3AF"
                fontSize={12}
              />
              <YAxis 
                stroke="#9CA3AF"
                fontSize={12}
                domain={[95, 'dataMax + 5']}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }}
                formatter={(value: any) => [`${value.toFixed(2)}%`, '']}
              />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="Conservative" 
                stackId="1"
                stroke={COLORS.Conservative} 
                fill={COLORS.Conservative}
                fillOpacity={0.6}
              />
              <Area 
                type="monotone" 
                dataKey="Balanced" 
                stackId="1"
                stroke={COLORS.Balanced} 
                fill={COLORS.Balanced}
                fillOpacity={0.6}
              />
              <Area 
                type="monotone" 
                dataKey="Degen" 
                stackId="1"
                stroke={COLORS.Degen} 
                fill={COLORS.Degen}
                fillOpacity={0.6}
              />
              <Line 
                type="monotone" 
                dataKey="Total" 
                stroke="#A855F7" 
                strokeWidth={3}
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Capital Allocation */}
        <div className="bg-gray-900 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Capital Allocation</h3>
            <button className="text-sm text-purple-400 hover:text-purple-300 flex items-center gap-1">
              <RefreshCw className="w-4 h-4" />
              Rebalance
            </button>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={allocationData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {allocationData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }}
                formatter={(value: any) => `${value}%`}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 space-y-3">
            {strategies.map((strategy) => (
              <div key={strategy.id} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: COLORS[strategy.type as keyof typeof COLORS] }}
                    />
                    <span className="text-gray-400">{strategy.type}</span>
                  </div>
                  <span className="text-white font-medium">{strategy.allocation}%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-1.5">
                  <div 
                    className="h-1.5 rounded-full transition-all duration-500"
                    style={{ 
                      width: `${strategy.allocation}%`,
                      backgroundColor: COLORS[strategy.type as keyof typeof COLORS]
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Risk Contribution */}
        <div className="bg-gray-900 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Risk Contribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <ComposedChart data={riskData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="strategy" 
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
                dataKey="risk" 
                fill="#EF4444"
                fillOpacity={0.6}
                name="Risk %"
              />
              <Line 
                yAxisId="right"
                type="monotone" 
                dataKey="sharpe" 
                stroke="#10B981" 
                strokeWidth={2}
                name="Sharpe Ratio"
                dot={{ fill: '#10B981' }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Performance Attribution */}
        <div className="bg-gray-900 rounded-lg p-6 lg:col-span-2">
          <h3 className="text-lg font-semibold text-white mb-4">Performance Attribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={attributionData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis type="number" stroke="#9CA3AF" fontSize={12} />
              <YAxis type="category" dataKey="name" stroke="#9CA3AF" fontSize={12} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }}
                formatter={(value: any) => `$${value.toLocaleString()}`}
              />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {attributionData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={
                      entry.type === 'positive' ? '#10B981' : 
                      entry.type === 'negative' ? '#EF4444' : 
                      entry.type === 'start' ? '#6B7280' : '#A855F7'
                    }
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Strategy Comparison Table */}
        <div className="bg-gray-900 rounded-lg p-6 lg:col-span-3">
          <h3 className="text-lg font-semibold text-white mb-4">Strategy Comparison</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Strategy</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Allocation</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Return</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Sharpe</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Risk Contrib.</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Positions</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Win Rate</th>
                </tr>
              </thead>
              <tbody>
                {strategies.map((strategy) => (
                  <tr key={strategy.id} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div 
                          className="w-3 h-3 rounded-full" 
                          style={{ backgroundColor: COLORS[strategy.type as keyof typeof COLORS] }}
                        />
                        <span className="text-white font-medium">{strategy.type}</span>
                      </div>
                    </td>
                    <td className="text-right py-3 px-4 text-gray-300">{strategy.allocation}%</td>
                    <td className="text-right py-3 px-4">
                      <span className={strategy.performance.total_pnl > 0 ? 'text-green-400' : 'text-red-400'}>
                        +{strategy.performance.total_pnl}%
                      </span>
                    </td>
                    <td className="text-right py-3 px-4 text-gray-300">{strategy.performance.sharpe_ratio}</td>
                    <td className="text-right py-3 px-4 text-gray-300">{strategy.performance.risk_contribution}%</td>
                    <td className="text-right py-3 px-4 text-gray-300">
                      {strategy.type === 'Conservative' ? '8' : strategy.type === 'Balanced' ? '12' : '23'}
                    </td>
                    <td className="text-right py-3 px-4 text-gray-300">
                      {strategy.type === 'Conservative' ? '72%' : strategy.type === 'Balanced' ? '65%' : '45%'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Rebalancing Suggestions */}
      <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <RefreshCw className="w-5 h-5 text-purple-500" />
          Rebalancing Suggestions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <p className="text-sm text-gray-400">Based on current performance:</p>
            <ul className="space-y-1 text-sm text-gray-300">
              <li>• Consider reducing Degen allocation by 5%</li>
              <li>• Increase Conservative allocation for stability</li>
              <li>• Balanced strategy performing well, maintain current allocation</li>
            </ul>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-gray-400">Risk optimization:</p>
            <ul className="space-y-1 text-sm text-gray-300">
              <li>• Current portfolio volatility: 18.5%</li>
              <li>• Suggested target: 15% for better risk-adjusted returns</li>
              <li>• Correlation between strategies is healthy (&lt; 0.6)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

// Metric Card Component
function MetricCard({ 
  title, 
  value, 
  subtitle,
  icon, 
  trend, 
  color 
}: {
  title: string
  value: string
  subtitle: string
  icon: React.ReactNode
  trend: 'up' | 'down' | 'stable'
  color: 'blue' | 'green' | 'yellow' | 'red' | 'purple'
}) {
  const colors = {
    blue: 'bg-blue-500/10 border-blue-500/20 text-blue-400',
    green: 'bg-green-500/10 border-green-500/20 text-green-400',
    yellow: 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400',
    red: 'bg-red-500/10 border-red-500/20 text-red-400',
    purple: 'bg-purple-500/10 border-purple-500/20 text-purple-400'
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
      <div className="text-xs text-gray-500 mt-1">{subtitle}</div>
    </motion.div>
  )
}