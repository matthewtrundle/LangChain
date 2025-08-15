'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'

interface PnLBreakdownProps {
  feesEarned: number
  impermanentLoss: number
  gasCosts: number
  totalValue: number
}

export default function PnLBreakdown({
  feesEarned,
  impermanentLoss,
  gasCosts,
  totalValue
}: PnLBreakdownProps) {
  const [hoveredItem, setHoveredItem] = useState<string | null>(null)
  
  const items = [
    {
      label: 'Fees Earned',
      value: feesEarned,
      percentage: (feesEarned / totalValue) * 100,
      color: '#00ffaa',
      gradient: 'from-green-500 to-emerald-400',
      icon: '💰',
      description: 'Total trading fees collected from LPs'
    },
    {
      label: 'Impermanent Loss',
      value: -Math.abs(impermanentLoss),
      percentage: (Math.abs(impermanentLoss) / totalValue) * 100,
      color: '#ff6b6b',
      gradient: 'from-red-500 to-orange-400',
      icon: '📉',
      description: 'Value lost due to price divergence'
    },
    {
      label: 'Gas Costs',
      value: -Math.abs(gasCosts),
      percentage: (Math.abs(gasCosts) / totalValue) * 100,
      color: '#a855f7',
      gradient: 'from-purple-500 to-pink-400',
      icon: '⛽',
      description: 'Total transaction fees paid'
    }
  ]
  
  const netPnL = feesEarned - impermanentLoss - gasCosts
  const netPnLPercentage = (netPnL / totalValue) * 100
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Net P&L Summary */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-terminal-surface/50 rounded-xl p-6 border border-terminal-border relative overflow-hidden"
      >
        {/* Background glow */}
        <div 
          className={`absolute inset-0 bg-gradient-to-r ${
            netPnL >= 0 ? 'from-green-500/20 to-emerald-500/20' : 'from-red-500/20 to-orange-500/20'
          } blur-3xl`}
        />
        
        <div className="relative z-10">
          <div className="text-text-tertiary text-sm mb-2">Net P&L</div>
          <div className="flex items-baseline gap-4">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.4, type: "spring", stiffness: 200 }}
              className={`text-4xl font-bold ${netPnL >= 0 ? 'text-cyber-primary' : 'text-red-500'}`}
            >
              {netPnL >= 0 ? '+' : ''}{netPnL.toLocaleString('en-US', { style: 'currency', currency: 'USD' })}
            </motion.div>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
              className={`text-lg ${netPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}
            >
              ({netPnLPercentage >= 0 ? '+' : ''}{netPnLPercentage.toFixed(2)}%)
            </motion.div>
          </div>
        </div>
      </motion.div>
      
      {/* Breakdown Items */}
      <div className="space-y-4">
        {items.map((item, index) => (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 + index * 0.1 }}
            onMouseEnter={() => setHoveredItem(item.label)}
            onMouseLeave={() => setHoveredItem(null)}
            className="relative"
          >
            <div className="bg-terminal-surface/30 rounded-lg p-4 border border-terminal-border transition-all duration-300 hover:border-cyber-primary/50">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <motion.div
                    animate={{ rotate: hoveredItem === item.label ? 360 : 0 }}
                    transition={{ duration: 0.5 }}
                    className="text-2xl"
                  >
                    {item.icon}
                  </motion.div>
                  <div>
                    <div className="text-text-primary font-semibold">{item.label}</div>
                    {hoveredItem === item.label && (
                      <motion.div
                        initial={{ opacity: 0, y: -5 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-text-tertiary text-xs mt-1"
                      >
                        {item.description}
                      </motion.div>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <div className={`font-bold ${item.value >= 0 ? 'text-cyber-primary' : 'text-red-500'}`}>
                    {item.value >= 0 ? '+' : ''}{item.value.toLocaleString('en-US', { style: 'currency', currency: 'USD' })}
                  </div>
                  <div className="text-text-tertiary text-sm">
                    {item.percentage.toFixed(2)}% of portfolio
                  </div>
                </div>
              </div>
              
              {/* Progress bar */}
              <div className="relative h-2 bg-terminal-surface rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(item.percentage, 100)}%` }}
                  transition={{ duration: 1, delay: 0.5 + index * 0.1, ease: "easeOut" }}
                  className={`absolute h-full bg-gradient-to-r ${item.gradient} rounded-full`}
                  style={{
                    boxShadow: `0 0 10px ${item.color}50`,
                  }}
                />
                {/* Glow effect on hover */}
                {hoveredItem === item.label && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent"
                  />
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
      
      {/* Tips */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="bg-gradient-to-r from-cyber-primary/10 to-cyber-secondary/10 rounded-lg p-4 border border-cyber-primary/30"
      >
        <div className="flex items-start gap-3">
          <div className="text-2xl">💡</div>
          <div className="text-sm text-text-secondary">
            <div className="font-semibold text-text-primary mb-1">Optimization Tip</div>
            {impermanentLoss > feesEarned * 0.5 ? (
              <div>Your IL is significantly impacting returns. Consider more stable pairs or tighter ranges.</div>
            ) : gasCosts > feesEarned * 0.2 ? (
              <div>Gas costs are eating into profits. Try larger positions or batch transactions.</div>
            ) : (
              <div>Good balance! Keep monitoring for opportunities to compound your yields.</div>
            )}
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}