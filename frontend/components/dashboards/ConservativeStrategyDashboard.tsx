'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Shield, 
  TrendingDown, 
  AlertTriangle, 
  BarChart3,
  Activity,
  DollarSign,
  Clock,
  CheckCircle
} from 'lucide-react'
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  PieChart, 
  Pie, 
  Cell,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ResponsiveContainer,
  RadialBarChart,
  RadialBar
} from 'recharts'

interface ConservativeDashboardProps {
  strategyId: string
  performance: any
  isActive: boolean
}

export default function ConservativeStrategyDashboard({ 
  strategyId, 
  performance, 
  isActive 
}: ConservativeDashboardProps) {
  const [timeframe, setTimeframe] = useState<'24h' | '7d' | '30d'>('7d')
  const [riskData, setRiskData] = useState<any[]>([])
  const [allocationData, setAllocationData] = useState<any[]>([])
  const [returnData, setReturnData] = useState<any[]>([])

  // Mock data for visualization
  useEffect(() => {
    // Risk exposure over time
    const mockRiskData = Array.from({ length: 30 }, (_, i) => ({
      date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toLocaleDateString(),
      risk: Math.max(10, Math.min(30, 20 + Math.random() * 10 - 5)),
      volatility: Math.max(5, Math.min(15, 10 + Math.random() * 5 - 2.5))
    }))
    setRiskData(mockRiskData)

    // Asset allocation
    const mockAllocation = [
      { name: 'Stable Pools', value: 60, color: '#3B82F6' },
      { name: 'Blue Chip', value: 30, color: '#10B981' },
      { name: 'Cash Reserve', value: 10, color: '#6B7280' }
    ]
    setAllocationData(mockAllocation)

    // Returns data
    const mockReturns = Array.from({ length: 30 }, (_, i) => ({
      date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toLocaleDateString(),
      returns: 100 + i * 0.3 + Math.random() * 2,
      benchmark: 100 + i * 0.2
    }))
    setReturnData(mockReturns)
  }, [timeframe])

  const formatPercent = (value: number) => `${value.toFixed(1)}%`
  const formatCurrency = (value: number) => `$${value.toLocaleString()}`

  // Risk gauge data
  const riskGaugeData = [{
    name: 'Risk Level',
    value: 25,
    fill: '#3B82F6'
  }]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Shield className="w-8 h-8 text-blue-500" />
          <div>
            <h2 className="text-2xl font-bold text-white">Conservative Strategy</h2>
            <p className="text-gray-400">Low risk, steady returns focus</p>
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
          value={formatPercent(performance?.total_pnl || 12.5)}
          icon={<TrendingDown className="w-5 h-5" />}
          trend="up"
          color="blue"
        />
        <MetricCard
          title="Risk Exposure"
          value={formatPercent(25)}
          icon={<AlertTriangle className="w-5 h-5" />}
          trend="stable"
          color="green"
        />
        <MetricCard
          title="Sharpe Ratio"
          value="1.85"
          icon={<BarChart3 className="w-5 h-5" />}
          trend="up"
          color="blue"
        />
        <MetricCard
          title="Max Drawdown"
          value={formatPercent(3.2)}
          icon={<Activity className="w-5 h-5" />}
          trend="stable"
          color="yellow"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Level Gauge */}
        <div className="bg-gray-900 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Current Risk Level</h3>
          <ResponsiveContainer width="100%" height={200}>
            <RadialBarChart 
              cx="50%" 
              cy="50%" 
              innerRadius="60%" 
              outerRadius="90%" 
              data={riskGaugeData}
              startAngle={180} 
              endAngle={0}
            >
              <RadialBar dataKey="value" cornerRadius={10} fill="#3B82F6" />
              <text 
                x="50%" 
                y="50%" 
                textAnchor="middle" 
                dominantBaseline="middle" 
                className="fill-white text-3xl font-bold"
              >
                LOW
              </text>
              <text 
                x="50%" 
                y="65%" 
                textAnchor="middle" 
                dominantBaseline="middle" 
                className="fill-gray-400 text-sm"
              >
                25% exposure
              </text>
            </RadialBarChart>
          </ResponsiveContainer>
        </div>

        {/* Asset Allocation */}
        <div className="bg-gray-900 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Asset Allocation</h3>
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
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 space-y-2">
            {allocationData.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-gray-400">{item.name}</span>
                </div>
                <span className="text-white font-medium">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Returns vs Benchmark */}
        <div className="bg-gray-900 rounded-lg p-6 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Cumulative Returns</h3>
            <div className="flex gap-2">
              {(['24h', '7d', '30d'] as const).map((tf) => (
                <button
                  key={tf}
                  onClick={() => setTimeframe(tf)}
                  className={`px-3 py-1 rounded text-sm ${
                    timeframe === tf 
                      ? 'bg-blue-500/20 text-blue-400' 
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  {tf}
                </button>
              ))}
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={returnData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="date" 
                stroke="#9CA3AF"
                fontSize={12}
              />
              <YAxis 
                stroke="#9CA3AF"
                fontSize={12}
                domain={['dataMin - 5', 'dataMax + 5']}
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
                dataKey="returns" 
                stroke="#3B82F6" 
                strokeWidth={2}
                name="Strategy Returns"
                dot={false}
              />
              <Line 
                type="monotone" 
                dataKey="benchmark" 
                stroke="#6B7280" 
                strokeWidth={2}
                name="Benchmark"
                strokeDasharray="5 5"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Risk & Volatility */}
        <div className="bg-gray-900 rounded-lg p-6 lg:col-span-2">
          <h3 className="text-lg font-semibold text-white mb-4">Risk & Volatility Tracking</h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={riskData}>
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
              <Area 
                type="monotone" 
                dataKey="risk" 
                stroke="#3B82F6" 
                fill="#3B82F6"
                fillOpacity={0.3}
                name="Risk Exposure %"
              />
              <Area 
                type="monotone" 
                dataKey="volatility" 
                stroke="#10B981" 
                fill="#10B981"
                fillOpacity={0.3}
                name="Volatility %"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Safety Checklist */}
      <div className="bg-gray-900 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Safety Checklist</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            { label: 'Risk within limits', status: true },
            { label: 'Diversification target met', status: true },
            { label: 'Drawdown acceptable', status: true },
            { label: 'Volatility controlled', status: true },
            { label: 'Liquidity adequate', status: true },
            { label: 'Position sizes optimal', status: false }
          ].map((item, index) => (
            <div key={index} className="flex items-center gap-3">
              <CheckCircle className={`w-5 h-5 ${
                item.status ? 'text-green-500' : 'text-gray-500'
              }`} />
              <span className={`text-sm ${
                item.status ? 'text-gray-300' : 'text-gray-500'
              }`}>
                {item.label}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Metric Card Component
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