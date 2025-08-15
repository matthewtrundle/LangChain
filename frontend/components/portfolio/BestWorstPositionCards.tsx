'use client'

import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Trophy, AlertTriangle, Clock, Zap } from 'lucide-react'

interface PositionData {
  poolName: string
  pnl: number
  pnlPercent: number
  duration: string
  apy: number
  entryValue: number
  exitValue?: number
  date: string
}

interface BestWorstPositionCardsProps {
  bestPosition: PositionData | null
  worstPosition: PositionData | null
  className?: string
}

export default function BestWorstPositionCards({ 
  bestPosition, 
  worstPosition,
  className = ''
}: BestWorstPositionCardsProps) {
  
  const PositionCard = ({ 
    position, 
    type 
  }: { 
    position: PositionData | null
    type: 'best' | 'worst' 
  }) => {
    if (!position) return null
    
    const isBest = type === 'best'
    const Icon = isBest ? Trophy : AlertTriangle
    const TrendIcon = isBest ? TrendingUp : TrendingDown
    const borderColor = isBest ? 'border-cyber-primary' : 'border-red-500'
    const glowColor = isBest ? 'rgba(0, 255, 170, 0.3)' : 'rgba(239, 68, 68, 0.3)'
    const accentColor = isBest ? 'text-cyber-primary' : 'text-red-500'
    const bgGradient = isBest 
      ? 'from-cyber-primary/10 to-cyber-secondary/10' 
      : 'from-red-500/10 to-orange-500/10'
    
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        whileHover={{ scale: 1.02 }}
        className={`relative bg-terminal-surface/50 rounded-xl border ${borderColor} overflow-hidden`}
        style={{
          boxShadow: `0 0 30px ${glowColor}`,
        }}
      >
        {/* Background gradient */}
        <div className={`absolute inset-0 bg-gradient-to-br ${bgGradient} opacity-50`} />
        
        {/* Animated background particles */}
        <div className="absolute inset-0 overflow-hidden">
          {[...Array(5)].map((_, i) => (
            <motion.div
              key={i}
              className={`absolute w-1 h-1 ${isBest ? 'bg-cyber-primary' : 'bg-red-500'} rounded-full`}
              initial={{ 
                x: Math.random() * 100 + '%',
                y: 100 + '%'
              }}
              animate={{ 
                y: -10 + '%',
                opacity: [0, 1, 0]
              }}
              transition={{
                duration: 3 + Math.random() * 2,
                repeat: Infinity,
                delay: i * 0.5,
                ease: "linear"
              }}
            />
          ))}
        </div>
        
        <div className="relative z-10 p-6">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <motion.div
                animate={{ 
                  rotate: isBest ? [0, 360] : [0, -10, 10, -10, 0],
                  scale: isBest ? [1, 1.2, 1] : [1, 1.1, 1]
                }}
                transition={{ 
                  duration: isBest ? 2 : 0.5,
                  repeat: isBest ? Infinity : Infinity,
                  repeatDelay: isBest ? 3 : 2
                }}
                className={`p-3 rounded-lg bg-terminal-card border ${borderColor}`}
              >
                <Icon className={`w-6 h-6 ${accentColor}`} />
              </motion.div>
              <div>
                <div className="text-text-tertiary text-sm">
                  {isBest ? 'Best Performer' : 'Worst Performer'}
                </div>
                <div className="text-text-primary font-bold text-lg">
                  {position.poolName}
                </div>
              </div>
            </div>
            
            {/* P&L Badge */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.3, type: "spring", stiffness: 200 }}
              className={`px-3 py-1 rounded-full ${isBest ? 'bg-green-500/20' : 'bg-red-500/20'} border ${borderColor}`}
            >
              <div className="flex items-center gap-1">
                <TrendIcon className={`w-4 h-4 ${accentColor}`} />
                <span className={`font-bold ${accentColor}`}>
                  {position.pnlPercent >= 0 ? '+' : ''}{position.pnlPercent.toFixed(2)}%
                </span>
              </div>
            </motion.div>
          </div>
          
          {/* Main P&L Display */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-6"
          >
            <div className={`text-3xl font-bold ${accentColor}`}>
              {position.pnl >= 0 ? '+' : ''}${Math.abs(position.pnl).toLocaleString()}
            </div>
            <div className="text-text-tertiary text-sm">
              on ${position.entryValue.toLocaleString()} investment
            </div>
          </motion.div>
          
          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-terminal-card/50 rounded-lg p-3 border border-terminal-border"
            >
              <div className="flex items-center gap-2 text-text-tertiary text-sm mb-1">
                <Zap className="w-3 h-3" />
                APY
              </div>
              <div className="text-text-primary font-bold">
                {position.apy.toLocaleString()}%
              </div>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-terminal-card/50 rounded-lg p-3 border border-terminal-border"
            >
              <div className="flex items-center gap-2 text-text-tertiary text-sm mb-1">
                <Clock className="w-3 h-3" />
                Duration
              </div>
              <div className="text-text-primary font-bold">
                {position.duration}
              </div>
            </motion.div>
          </div>
          
          {/* Date */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-text-tertiary text-xs text-center"
          >
            {position.date}
          </motion.div>
          
          {/* Special effects for best position */}
          {isBest && (
            <motion.div
              className="absolute top-2 right-2"
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.6 }}
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                className="text-2xl"
              >
                ⭐
              </motion.div>
            </motion.div>
          )}
        </div>
      </motion.div>
    )
  }
  
  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 gap-6 ${className}`}>
      <PositionCard position={bestPosition} type="best" />
      <PositionCard position={worstPosition} type="worst" />
      
      {/* Empty state */}
      {!bestPosition && !worstPosition && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="col-span-2 bg-terminal-surface/30 rounded-xl border border-terminal-border p-8 text-center"
        >
          <div className="text-text-tertiary">
            No position history yet. Start trading to see your best and worst performers!
          </div>
        </motion.div>
      )}
    </div>
  )
}