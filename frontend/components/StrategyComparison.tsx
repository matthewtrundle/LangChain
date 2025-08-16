'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Shield, 
  BarChart3, 
  Zap,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  DollarSign,
  Clock,
  Target,
  Layers
} from 'lucide-react'
import { 
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Cell
} from 'recharts'

interface Strategy {
  type: 'Conservative' | 'Balanced' | 'Degen'
  icon: React.ReactNode
  color: string
  description: string
  metrics: {
    expectedReturn: number
    riskLevel: number
    sharpeRatio: number
    maxDrawdown: number
    winRate: number
    avgLeverage: number
    volatility: number
    timeHorizon: string
  }
  characteristics: string[]
  suitableFor: string[]
}

export default function StrategyComparison() {
  const [selectedStrategy, setSelectedStrategy] = useState<'Conservative' | 'Balanced' | 'Degen' | null>(null)
  const [comparisonMode, setComparisonMode] = useState<'overview' | 'risk' | 'returns'>('overview')

  const strategies: Record<string, Strategy> = {
    Conservative: {
      type: 'Conservative',
      icon: <Shield className="w-6 h-6" />,
      color: '#3B82F6',
      description: 'Low-risk, stable returns through established pools',
      metrics: {
        expectedReturn: 12.5,
        riskLevel: 2,
        sharpeRatio: 1.85,
        maxDrawdown: 5,
        winRate: 72,
        avgLeverage: 1,
        volatility: 8,
        timeHorizon: 'Long-term (months)'
      },
      characteristics: [
        'Focus on blue-chip tokens',
        'No leverage usage',
        'Stable pool concentration',
        'Minimal impermanent loss',
        'Consistent daily returns'
      ],
      suitableFor: [
        'Risk-averse investors',
        'Long-term holders',
        'Passive income seekers',
        'Beginners to DeFi'
      ]
    },
    Balanced: {
      type: 'Balanced',
      icon: <BarChart3 className="w-6 h-6" />,
      color: '#F59E0B',
      description: 'Optimized risk-reward through diversified strategies',
      metrics: {
        expectedReturn: 28.5,
        riskLevel: 5,
        sharpeRatio: 1.42,
        maxDrawdown: 12,
        winRate: 65,
        avgLeverage: 2.5,
        volatility: 18,
        timeHorizon: 'Medium-term (weeks)'
      },
      characteristics: [
        'Mix of stable and volatile pools',
        'Moderate leverage (up to 3x)',
        'Dynamic rebalancing',
        'Correlation-based diversification',
        'Active risk management'
      ],
      suitableFor: [
        'Experienced DeFi users',
        'Growth-focused investors',
        'Active portfolio managers',
        'Risk-aware traders'
      ]
    },
    Degen: {
      type: 'Degen',
      icon: <Zap className="w-6 h-6" />,
      color: '#EF4444',
      description: 'High-risk, high-reward plays on volatile pools',
      metrics: {
        expectedReturn: 45.2,
        riskLevel: 9,
        sharpeRatio: 0.95,
        maxDrawdown: 35,
        winRate: 45,
        avgLeverage: 7.5,
        volatility: 45,
        timeHorizon: 'Short-term (hours/days)'
      },
      characteristics: [
        'Meme token focus',
        'High leverage (up to 10x)',
        'Rapid position turnover',
        'Momentum-based entries',
        'Accept high drawdowns'
      ],
      suitableFor: [
        'Risk seekers',
        'Active day traders',
        'Small allocation experiments',
        'Volatility lovers'
      ]
    }
  }

  // Prepare radar chart data
  const radarData = [
    { metric: 'Returns', Conservative: 25, Balanced: 60, Degen: 90 },
    { metric: 'Risk', Conservative: 20, Balanced: 50, Degen: 90 },
    { metric: 'Stability', Conservative: 90, Balanced: 65, Degen: 20 },
    { metric: 'Win Rate', Conservative: 72, Balanced: 65, Degen: 45 },
    { metric: 'Sharpe', Conservative: 90, Balanced: 70, Degen: 45 },
    { metric: 'Leverage', Conservative: 10, Balanced: 25, Degen: 75 }
  ]

  // Prepare comparison bar data
  const comparisonData = [
    {
      metric: 'Expected Return',
      Conservative: 12.5,
      Balanced: 28.5,
      Degen: 45.2
    },
    {
      metric: 'Max Drawdown',
      Conservative: -5,
      Balanced: -12,
      Degen: -35
    },
    {
      metric: 'Win Rate',
      Conservative: 72,
      Balanced: 65,
      Degen: 45
    },
    {
      metric: 'Avg Leverage',
      Conservative: 1,
      Balanced: 2.5,
      Degen: 7.5
    }
  ]

  const COLORS = {
    Conservative: '#3B82F6',
    Balanced: '#F59E0B',
    Degen: '#EF4444'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Strategy Comparison Tool</h2>
        <p className="text-gray-400">Compare different trading strategies to find the right fit for your risk profile</p>
      </div>

      {/* Strategy Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {Object.values(strategies).map((strategy) => (
          <motion.div
            key={strategy.type}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setSelectedStrategy(strategy.type)}
            className={`relative p-6 rounded-lg border-2 cursor-pointer transition-all ${
              selectedStrategy === strategy.type
                ? `border-${strategy.color} bg-${strategy.color}/10`
                : 'border-gray-700 bg-gray-900 hover:border-gray-600'
            }`}
            style={{
              borderColor: selectedStrategy === strategy.type ? strategy.color : undefined,
              backgroundColor: selectedStrategy === strategy.type ? `${strategy.color}20` : undefined
            }}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div 
                  className="p-3 rounded-lg"
                  style={{ backgroundColor: `${strategy.color}20`, color: strategy.color }}
                >
                  {strategy.icon}
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">{strategy.type}</h3>
                  <p className="text-sm text-gray-400">{strategy.metrics.timeHorizon}</p>
                </div>
              </div>
            </div>

            <p className="text-sm text-gray-300 mb-4">{strategy.description}</p>

            <div className="grid grid-cols-2 gap-3 mb-4">
              <div>
                <p className="text-xs text-gray-500">Expected Return</p>
                <p className="text-lg font-bold" style={{ color: strategy.color }}>
                  +{strategy.metrics.expectedReturn}%
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Risk Level</p>
                <div className="flex items-center gap-1 mt-1">
                  {[...Array(10)].map((_, i) => (
                    <div
                      key={i}
                      className="h-4 w-1 rounded-full"
                      style={{
                        backgroundColor: i < strategy.metrics.riskLevel ? strategy.color : '#374151'
                      }}
                    />
                  ))}
                </div>
              </div>
              <div>
                <p className="text-xs text-gray-500">Win Rate</p>
                <p className="text-lg font-bold text-white">{strategy.metrics.winRate}%</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Sharpe Ratio</p>
                <p className="text-lg font-bold text-white">{strategy.metrics.sharpeRatio}</p>
              </div>
            </div>

            {selectedStrategy === strategy.type && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="border-t border-gray-700 pt-4 mt-4"
              >
                <p className="text-xs text-gray-500 uppercase mb-2">Key Characteristics</p>
                <ul className="space-y-1">
                  {strategy.characteristics.map((char, i) => (
                    <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                      <span style={{ color: strategy.color }}>•</span>
                      {char}
                    </li>
                  ))}
                </ul>
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Comparison Views */}
      <div className="bg-gray-900 rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-white">Strategy Analysis</h3>
          <div className="flex gap-2">
            {(['overview', 'risk', 'returns'] as const).map((mode) => (
              <button
                key={mode}
                onClick={() => setComparisonMode(mode)}
                className={`px-4 py-2 rounded text-sm font-medium capitalize transition-all ${
                  comparisonMode === mode
                    ? 'bg-purple-500/20 text-purple-400 border border-purple-500/40'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {mode}
              </button>
            ))}
          </div>
        </div>

        {comparisonMode === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Radar Chart */}
            <div>
              <h4 className="text-sm text-gray-400 mb-4">Multi-dimensional Comparison</h4>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#374151" />
                  <PolarAngleAxis dataKey="metric" stroke="#9CA3AF" fontSize={12} />
                  <PolarRadiusAxis stroke="#9CA3AF" fontSize={10} />
                  <Radar
                    name="Conservative"
                    dataKey="Conservative"
                    stroke={COLORS.Conservative}
                    fill={COLORS.Conservative}
                    fillOpacity={0.3}
                  />
                  <Radar
                    name="Balanced"
                    dataKey="Balanced"
                    stroke={COLORS.Balanced}
                    fill={COLORS.Balanced}
                    fillOpacity={0.3}
                  />
                  <Radar
                    name="Degen"
                    dataKey="Degen"
                    stroke={COLORS.Degen}
                    fill={COLORS.Degen}
                    fillOpacity={0.3}
                  />
                  <Legend />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            {/* Bar Comparison */}
            <div>
              <h4 className="text-sm text-gray-400 mb-4">Key Metrics Comparison</h4>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={comparisonData} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis type="number" stroke="#9CA3AF" fontSize={12} />
                  <YAxis type="category" dataKey="metric" stroke="#9CA3AF" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1F2937',
                      border: '1px solid #374151',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Bar dataKey="Conservative" fill={COLORS.Conservative} />
                  <Bar dataKey="Balanced" fill={COLORS.Balanced} />
                  <Bar dataKey="Degen" fill={COLORS.Degen} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {comparisonMode === 'risk' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {Object.values(strategies).map((strategy) => (
                <div key={strategy.type} className="space-y-4">
                  <h4 className="font-semibold text-white flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: strategy.color }} />
                    {strategy.type} Risk Profile
                  </h4>
                  <div className="space-y-3">
                    <RiskMetric
                      label="Max Drawdown"
                      value={`${strategy.metrics.maxDrawdown}%`}
                      severity={strategy.metrics.maxDrawdown > 20 ? 'high' : strategy.metrics.maxDrawdown > 10 ? 'medium' : 'low'}
                    />
                    <RiskMetric
                      label="Volatility"
                      value={`${strategy.metrics.volatility}%`}
                      severity={strategy.metrics.volatility > 30 ? 'high' : strategy.metrics.volatility > 15 ? 'medium' : 'low'}
                    />
                    <RiskMetric
                      label="Leverage Used"
                      value={`${strategy.metrics.avgLeverage}x`}
                      severity={strategy.metrics.avgLeverage > 5 ? 'high' : strategy.metrics.avgLeverage > 2 ? 'medium' : 'low'}
                    />
                    <div className="pt-3 border-t border-gray-800">
                      <p className="text-xs text-gray-500 mb-2">Suitable For:</p>
                      <ul className="space-y-1">
                        {strategy.suitableFor.map((item, i) => (
                          <li key={i} className="text-xs text-gray-400">• {item}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {comparisonMode === 'returns' && (
          <div className="space-y-6">
            <div className="bg-gray-800 rounded-lg p-6">
              <h4 className="text-lg font-semibold text-white mb-4">Expected Returns Calculator</h4>
              <CapitalAllocationSimulator strategies={strategies} />
            </div>
          </div>
        )}
      </div>

      {/* Recommendation Section */}
      {selectedStrategy && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-6"
        >
          <h3 className="text-lg font-semibold text-white mb-4">
            Recommendation for {selectedStrategy} Strategy
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p className="text-sm text-gray-400 mb-2">Optimal Allocation</p>
              <p className="text-2xl font-bold text-purple-400">
                {selectedStrategy === 'Conservative' ? '40-60%' : 
                 selectedStrategy === 'Balanced' ? '30-40%' : '10-20%'}
              </p>
              <p className="text-xs text-gray-500 mt-1">of total portfolio</p>
            </div>
            <div>
              <p className="text-sm text-gray-400 mb-2">Risk Management</p>
              <ul className="space-y-1 text-sm text-gray-300">
                {selectedStrategy === 'Conservative' && (
                  <>
                    <li>• Monitor pool TVL changes</li>
                    <li>• Set 5% stop-loss limits</li>
                    <li>• Rebalance monthly</li>
                  </>
                )}
                {selectedStrategy === 'Balanced' && (
                  <>
                    <li>• Track correlation metrics</li>
                    <li>• Use 10% position limits</li>
                    <li>• Rebalance weekly</li>
                  </>
                )}
                {selectedStrategy === 'Degen' && (
                  <>
                    <li>• Set tight stop-losses</li>
                    <li>• Never exceed 20% allocation</li>
                    <li>• Take profits aggressively</li>
                  </>
                )}
              </ul>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}

// Risk Metric Component
function RiskMetric({ label, value, severity }: { 
  label: string
  value: string
  severity: 'low' | 'medium' | 'high' 
}) {
  const colors = {
    low: 'text-green-400 bg-green-500/10',
    medium: 'text-yellow-400 bg-yellow-500/10',
    high: 'text-red-400 bg-red-500/10'
  }

  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-gray-400">{label}</span>
      <span className={`text-sm font-medium px-2 py-1 rounded ${colors[severity]}`}>
        {value}
      </span>
    </div>
  )
}

// Capital Allocation Simulator
function CapitalAllocationSimulator({ strategies }: { strategies: Record<string, Strategy> }) {
  const [capital, setCapital] = useState(10000)
  const [allocations, setAllocations] = useState({
    Conservative: 40,
    Balanced: 35,
    Degen: 25
  })

  const calculateReturns = () => {
    let totalReturn = 0
    let weightedRisk = 0
    
    Object.entries(allocations).forEach(([strategy, allocation]) => {
      const strategyData = strategies[strategy as keyof typeof strategies]
      const strategyCapital = (capital * allocation) / 100
      const strategyReturn = (strategyCapital * strategyData.metrics.expectedReturn) / 100
      totalReturn += strategyReturn
      weightedRisk += (strategyData.metrics.riskLevel * allocation) / 100
    })

    return {
      totalReturn,
      finalValue: capital + totalReturn,
      weightedRisk: weightedRisk.toFixed(1),
      returnPercent: ((totalReturn / capital) * 100).toFixed(1)
    }
  }

  const results = calculateReturns()

  return (
    <div className="space-y-6">
      <div>
        <label className="text-sm text-gray-400">Initial Capital</label>
        <input
          type="number"
          value={capital}
          onChange={(e) => setCapital(Number(e.target.value))}
          className="w-full mt-1 px-4 py-2 bg-gray-700 rounded-lg text-white"
        />
      </div>

      <div className="space-y-4">
        {Object.entries(allocations).map(([strategy, value]) => (
          <div key={strategy}>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-gray-400">{strategy} Allocation</label>
              <span className="text-sm text-white">{value}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={value}
              onChange={(e) => setAllocations({ ...allocations, [strategy]: Number(e.target.value) })}
              className="w-full"
              style={{
                background: `linear-gradient(to right, ${strategies[strategy as keyof typeof strategies].color} 0%, ${strategies[strategy as keyof typeof strategies].color} ${value}%, #374151 ${value}%, #374151 100%)`
              }}
            />
          </div>
        ))}
      </div>

      <div className="border-t border-gray-700 pt-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-400">Expected Return</p>
            <p className="text-2xl font-bold text-green-400">+${results.totalReturn.toLocaleString()}</p>
            <p className="text-sm text-gray-500">+{results.returnPercent}%</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Final Portfolio Value</p>
            <p className="text-2xl font-bold text-white">${results.finalValue.toLocaleString()}</p>
            <p className="text-sm text-gray-500">Risk Score: {results.weightedRisk}/10</p>
          </div>
        </div>
      </div>

      <div className="text-xs text-gray-500">
        <p>* Based on historical average returns</p>
        <p>* Actual results may vary significantly</p>
      </div>
    </div>
  )
}