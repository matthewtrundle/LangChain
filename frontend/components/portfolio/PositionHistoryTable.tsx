'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'
import { ChevronDown, ChevronUp, TrendingUp, TrendingDown, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react'

interface Position {
  id: string
  poolName: string
  entryDate: string
  exitDate?: string
  duration: string
  entryValue: number
  exitValue?: number
  pnl: number
  pnlPercent: number
  fees: number
  apy: number
  status: 'active' | 'closed' | 'liquidated'
}

interface PositionHistoryTableProps {
  positions: Position[]
  className?: string
}

export default function PositionHistoryTable({ positions, className = '' }: PositionHistoryTableProps) {
  const [sortBy, setSortBy] = useState<keyof Position>('entryDate')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [expandedRow, setExpandedRow] = useState<string | null>(null)

  const sortedPositions = [...positions].sort((a, b) => {
    const aVal = a[sortBy]
    const bVal = b[sortBy]
    
    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return sortOrder === 'asc' ? aVal - bVal : bVal - aVal
    }
    
    const aStr = String(aVal)
    const bStr = String(bVal)
    return sortOrder === 'asc' ? aStr.localeCompare(bStr) : bStr.localeCompare(aStr)
  })

  const handleSort = (column: keyof Position) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(column)
      setSortOrder('desc')
    }
  }

  const getStatusIcon = (status: Position['status']) => {
    switch (status) {
      case 'active':
        return <Clock className="w-4 h-4 text-blue-500" />
      case 'closed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'liquidated':
        return <XCircle className="w-4 h-4 text-red-500" />
    }
  }

  const getStatusBadge = (status: Position['status']) => {
    const colors = {
      active: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      closed: 'bg-green-500/20 text-green-400 border-green-500/30',
      liquidated: 'bg-red-500/20 text-red-400 border-red-500/30'
    }
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${colors[status]} flex items-center gap-1`}>
        {getStatusIcon(status)}
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`bg-terminal-surface/50 rounded-xl border border-terminal-border overflow-hidden ${className}`}
    >
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-terminal-surface/80 border-b border-terminal-border">
              <th className="px-4 py-3 text-left">
                <button
                  onClick={() => handleSort('poolName')}
                  className="flex items-center gap-1 text-text-tertiary hover:text-text-primary transition-colors"
                >
                  Pool
                  {sortBy === 'poolName' && (
                    sortOrder === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />
                  )}
                </button>
              </th>
              <th className="px-4 py-3 text-left">
                <button
                  onClick={() => handleSort('status')}
                  className="flex items-center gap-1 text-text-tertiary hover:text-text-primary transition-colors"
                >
                  Status
                  {sortBy === 'status' && (
                    sortOrder === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />
                  )}
                </button>
              </th>
              <th className="px-4 py-3 text-right">
                <button
                  onClick={() => handleSort('entryValue')}
                  className="flex items-center gap-1 text-text-tertiary hover:text-text-primary transition-colors ml-auto"
                >
                  Entry
                  {sortBy === 'entryValue' && (
                    sortOrder === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />
                  )}
                </button>
              </th>
              <th className="px-4 py-3 text-right">
                <button
                  onClick={() => handleSort('pnl')}
                  className="flex items-center gap-1 text-text-tertiary hover:text-text-primary transition-colors ml-auto"
                >
                  P&L
                  {sortBy === 'pnl' && (
                    sortOrder === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />
                  )}
                </button>
              </th>
              <th className="px-4 py-3 text-right">
                <button
                  onClick={() => handleSort('apy')}
                  className="flex items-center gap-1 text-text-tertiary hover:text-text-primary transition-colors ml-auto"
                >
                  APY
                  {sortBy === 'apy' && (
                    sortOrder === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />
                  )}
                </button>
              </th>
              <th className="px-4 py-3 text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            {sortedPositions.map((position, index) => (
              <motion.tr
                key={position.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="border-b border-terminal-border hover:bg-terminal-surface/50 transition-colors group"
              >
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div>
                      <div className="text-text-primary font-medium">{position.poolName}</div>
                      <div className="text-text-tertiary text-xs">{position.duration}</div>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3">
                  {getStatusBadge(position.status)}
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="text-text-primary font-medium">
                    ${position.entryValue.toLocaleString()}
                  </div>
                  <div className="text-text-tertiary text-xs">
                    {position.entryDate}
                  </div>
                </td>
                <td className="px-4 py-3 text-right">
                  <div className={`font-medium ${position.pnl >= 0 ? 'text-cyber-primary' : 'text-red-500'}`}>
                    {position.pnl >= 0 ? '+' : ''}${position.pnl.toLocaleString()}
                  </div>
                  <div className={`text-xs flex items-center justify-end gap-1 ${position.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {position.pnl >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                    {position.pnlPercent >= 0 ? '+' : ''}{position.pnlPercent.toFixed(2)}%
                  </div>
                </td>
                <td className="px-4 py-3 text-right">
                  <motion.div
                    className="text-text-primary font-medium"
                    animate={{
                      color: position.apy > 1000 ? ['#fff', '#00ffaa', '#fff'] : '#fff'
                    }}
                    transition={{
                      duration: 2,
                      repeat: position.apy > 1000 ? Infinity : 0,
                      ease: "easeInOut"
                    }}
                  >
                    {position.apy.toLocaleString()}%
                  </motion.div>
                  {position.apy > 2000 && (
                    <div className="text-xs text-yellow-500 flex items-center justify-end gap-1">
                      <AlertCircle className="w-3 h-3" />
                      High Risk
                    </div>
                  )}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => setExpandedRow(expandedRow === position.id ? null : position.id)}
                      className="text-text-tertiary hover:text-cyber-primary transition-colors"
                    >
                      {expandedRow === position.id ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                  </div>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* Summary Footer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="px-4 py-3 bg-terminal-surface/80 border-t border-terminal-border flex items-center justify-between text-sm"
      >
        <div className="text-text-tertiary">
          Total Positions: <span className="text-text-primary font-medium">{positions.length}</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-text-tertiary">
            Total P&L: 
            <span className={`font-medium ml-1 ${
              positions.reduce((sum, p) => sum + p.pnl, 0) >= 0 ? 'text-cyber-primary' : 'text-red-500'
            }`}>
              ${positions.reduce((sum, p) => sum + p.pnl, 0).toLocaleString()}
            </span>
          </div>
          <div className="text-text-tertiary">
            Avg APY: 
            <span className="text-text-primary font-medium ml-1">
              {(positions.reduce((sum, p) => sum + p.apy, 0) / positions.length).toFixed(0)}%
            </span>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}