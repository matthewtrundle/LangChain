'use client'

import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

interface WinRateMeterProps {
  winningPositions: number
  losingPositions: number
  className?: string
}

export default function WinRateMeter({ 
  winningPositions, 
  losingPositions,
  className = ''
}: WinRateMeterProps) {
  const [animatedWinRate, setAnimatedWinRate] = useState(0)
  const totalPositions = winningPositions + losingPositions
  const winRate = totalPositions > 0 ? (winningPositions / totalPositions) * 100 : 0
  
  useEffect(() => {
    // Animate the win rate counter
    const timer = setTimeout(() => {
      setAnimatedWinRate(winRate)
    }, 100)
    return () => clearTimeout(timer)
  }, [winRate])
  
  const getColorByWinRate = (rate: number) => {
    if (rate >= 70) return '#00ffaa' // Excellent
    if (rate >= 55) return '#10b981' // Good
    if (rate >= 45) return '#eab308' // Average
    if (rate >= 30) return '#f97316' // Poor
    return '#ef4444' // Bad
  }
  
  const getGradeByWinRate = (rate: number) => {
    if (rate >= 70) return 'S'
    if (rate >= 60) return 'A'
    if (rate >= 50) return 'B'
    if (rate >= 40) return 'C'
    if (rate >= 30) return 'D'
    return 'F'
  }
  
  const color = getColorByWinRate(winRate)
  const grade = getGradeByWinRate(winRate)
  const circumference = 2 * Math.PI * 80 // radius = 80
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className={`relative ${className}`}
    >
      <div className="relative w-48 h-48 mx-auto">
        {/* Background glow */}
        <motion.div
          animate={{
            opacity: [0.3, 0.6, 0.3],
            scale: [1, 1.1, 1]
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute inset-0 rounded-full blur-2xl"
          style={{ backgroundColor: color }}
        />
        
        {/* SVG Circle */}
        <svg className="w-full h-full transform -rotate-90 relative z-10">
          {/* Background circle */}
          <circle
            cx="96"
            cy="96"
            r="80"
            stroke="currentColor"
            strokeWidth="12"
            fill="none"
            className="text-terminal-surface"
          />
          
          {/* Animated progress circle */}
          <motion.circle
            cx="96"
            cy="96"
            r="80"
            stroke={color}
            strokeWidth="12"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ 
              strokeDashoffset: circumference - (animatedWinRate / 100) * circumference
            }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            style={{
              filter: `drop-shadow(0 0 8px ${color}80)`,
            }}
          />
          
          {/* Decorative dots */}
          {[...Array(12)].map((_, i) => {
            const angle = (i * 30 - 90) * (Math.PI / 180)
            const x = 96 + 80 * Math.cos(angle)
            const y = 96 + 80 * Math.sin(angle)
            const isActive = i <= Math.floor(winRate / 8.33)
            
            return (
              <motion.circle
                key={i}
                cx={x}
                cy={y}
                r="3"
                fill={isActive ? color : '#333'}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.5 + i * 0.05 }}
              />
            )
          })}
        </svg>
        
        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="text-center"
          >
            {/* Grade badge */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.7, type: "spring", stiffness: 200 }}
              className="text-lg font-bold mb-1"
              style={{ color }}
            >
              GRADE
            </motion.div>
            
            {/* Win rate percentage */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.8, type: "spring", stiffness: 150 }}
              className="relative"
            >
              <div className="text-5xl font-bold" style={{ color }}>
                {Math.round(animatedWinRate)}%
              </div>
              <motion.div
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 1 }}
                className="absolute -top-2 -right-6 text-2xl font-bold bg-terminal-card border-2 rounded-full w-10 h-10 flex items-center justify-center"
                style={{ borderColor: color, color }}
              >
                {grade}
              </motion.div>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.2 }}
              className="text-text-tertiary text-xs mt-1"
            >
              WIN RATE
            </motion.div>
          </motion.div>
        </div>
      </div>
      
      {/* Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1 }}
        className="flex justify-center gap-8 mt-6"
      >
        <div className="text-center">
          <div className="text-cyber-primary text-2xl font-bold">{winningPositions}</div>
          <div className="text-text-tertiary text-sm">Wins</div>
        </div>
        <div className="text-center">
          <div className="text-red-500 text-2xl font-bold">{losingPositions}</div>
          <div className="text-text-tertiary text-sm">Losses</div>
        </div>
        <div className="text-center">
          <div className="text-text-primary text-2xl font-bold">{totalPositions}</div>
          <div className="text-text-tertiary text-sm">Total</div>
        </div>
      </motion.div>
      
      {/* Performance message */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5 }}
        className="text-center mt-4"
      >
        <div className="text-sm text-text-secondary">
          {winRate >= 70 ? "🔥 Outstanding performance!" :
           winRate >= 55 ? "💪 Great job, keep it up!" :
           winRate >= 45 ? "📊 Room for improvement" :
           winRate >= 30 ? "⚠️ Consider adjusting strategy" :
           "🚨 Time to revisit your approach"}
        </div>
      </motion.div>
    </motion.div>
  )
}