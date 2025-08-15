'use client'

import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

interface RiskVisualizationProps {
  riskScore: number // 0-100
  sustainabilityScore: number // 0-10
  impermanentLossRisk: number // 0-100
  volatility: number // 0-100
  className?: string
}

export default function RiskVisualization({
  riskScore,
  sustainabilityScore,
  impermanentLossRisk,
  volatility,
  className = ''
}: RiskVisualizationProps) {
  const [isHovered, setIsHovered] = useState(false)
  
  const getRiskColor = (score: number) => {
    if (score >= 80) return '#ef4444' // red
    if (score >= 60) return '#f97316' // orange
    if (score >= 40) return '#eab308' // yellow
    if (score >= 20) return '#22c55e' // green
    return '#10b981' // emerald
  }
  
  const getRiskLabel = (score: number) => {
    if (score >= 80) return 'EXTREME'
    if (score >= 60) return 'HIGH'
    if (score >= 40) return 'MODERATE'
    if (score >= 20) return 'LOW'
    return 'MINIMAL'
  }
  
  // Calculate overall risk
  const overallRisk = Math.round(
    (riskScore * 0.4) + 
    ((10 - sustainabilityScore) * 10 * 0.3) + 
    (impermanentLossRisk * 0.2) + 
    (volatility * 0.1)
  )
  
  const riskColor = getRiskColor(overallRisk)
  const riskLabel = getRiskLabel(overallRisk)
  
  return (
    <div 
      className={`relative ${className}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Circular Risk Meter */}
      <div className="relative w-48 h-48 mx-auto">
        <svg className="w-full h-full transform -rotate-90">
          {/* Background circle */}
          <circle
            cx="96"
            cy="96"
            r="88"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            className="text-terminal-surface"
          />
          
          {/* Risk level arc */}
          <motion.circle
            cx="96"
            cy="96"
            r="88"
            stroke={riskColor}
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={`${2 * Math.PI * 88}`}
            initial={{ strokeDashoffset: 2 * Math.PI * 88 }}
            animate={{ 
              strokeDashoffset: 2 * Math.PI * 88 * (1 - overallRisk / 100)
            }}
            transition={{ duration: 1.5, ease: "easeOut" }}
          />
          
          {/* Animated glow effect */}
          {overallRisk > 60 && (
            <motion.circle
              cx="96"
              cy="96"
              r="88"
              stroke={riskColor}
              strokeWidth="16"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={`${2 * Math.PI * 88}`}
              strokeDashoffset={2 * Math.PI * 88 * (1 - overallRisk / 100)}
              animate={{ opacity: [0.3, 0.6, 0.3] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="blur-sm"
            />
          )}
        </svg>
        
        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.5, type: "spring", stiffness: 200 }}
          >
            <div className="text-4xl font-bold" style={{ color: riskColor }}>
              {overallRisk}%
            </div>
            <div className="text-sm text-text-tertiary uppercase tracking-wider">
              {riskLabel}
            </div>
          </motion.div>
        </div>
      </div>
      
      {/* Detailed metrics */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="mt-6 space-y-3"
      >
        {/* Risk Score */}
        <div className="space-y-1">
          <div className="flex justify-between text-sm">
            <span className="text-text-tertiary">Degen Score</span>
            <span className="text-text-primary font-semibold">{riskScore}%</span>
          </div>
          <div className="h-2 bg-terminal-surface rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{ backgroundColor: getRiskColor(riskScore) }}
              initial={{ width: 0 }}
              animate={{ width: `${riskScore}%` }}
              transition={{ duration: 1, delay: 1 }}
            />
          </div>
        </div>
        
        {/* Sustainability */}
        <div className="space-y-1">
          <div className="flex justify-between text-sm">
            <span className="text-text-tertiary">Sustainability</span>
            <span className="text-text-primary font-semibold">{sustainabilityScore}/10</span>
          </div>
          <div className="h-2 bg-terminal-surface rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full bg-cyber-primary"
              initial={{ width: 0 }}
              animate={{ width: `${sustainabilityScore * 10}%` }}
              transition={{ duration: 1, delay: 1.1 }}
            />
          </div>
        </div>
        
        {/* IL Risk */}
        <div className="space-y-1">
          <div className="flex justify-between text-sm">
            <span className="text-text-tertiary">IL Risk</span>
            <span className="text-text-primary font-semibold">{impermanentLossRisk}%</span>
          </div>
          <div className="h-2 bg-terminal-surface rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{ backgroundColor: getRiskColor(impermanentLossRisk) }}
              initial={{ width: 0 }}
              animate={{ width: `${impermanentLossRisk}%` }}
              transition={{ duration: 1, delay: 1.2 }}
            />
          </div>
        </div>
        
        {/* Volatility */}
        <div className="space-y-1">
          <div className="flex justify-between text-sm">
            <span className="text-text-tertiary">Volatility</span>
            <span className="text-text-primary font-semibold">{volatility}%</span>
          </div>
          <div className="h-2 bg-terminal-surface rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{ backgroundColor: getRiskColor(volatility) }}
              initial={{ width: 0 }}
              animate={{ width: `${volatility}%` }}
              transition={{ duration: 1, delay: 1.3 }}
            />
          </div>
        </div>
      </motion.div>
      
      {/* Hover tooltip */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: isHovered ? 1 : 0, scale: isHovered ? 1 : 0.9 }}
        transition={{ duration: 0.2 }}
        className="absolute -top-16 left-1/2 transform -translate-x-1/2 bg-terminal-card border border-terminal-border rounded-lg p-3 pointer-events-none z-10"
        style={{ minWidth: '200px' }}
      >
        <div className="text-xs text-text-tertiary space-y-1">
          <div>Overall risk calculated from:</div>
          <div>• Degen Score (40%)</div>
          <div>• Sustainability (30%)</div>
          <div>• IL Risk (20%)</div>
          <div>• Volatility (10%)</div>
        </div>
        <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full">
          <div className="border-t-8 border-t-terminal-card border-x-4 border-x-transparent"></div>
        </div>
      </motion.div>
    </div>
  )
}