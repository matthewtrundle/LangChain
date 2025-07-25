'use client'

import { useState, useEffect } from 'react'
import { XIcon, AlertTriangleIcon, TrendingUpIcon, ShieldIcon } from './icons/Icons'

interface AnalysisModalProps {
  isOpen: boolean
  onClose: () => void
  poolAddress: string
  analysisResult: string
  scoreData?: any
}

export default function AnalysisModal({ 
  isOpen, 
  onClose, 
  poolAddress, 
  analysisResult,
  scoreData 
}: AnalysisModalProps) {
  const [isClosing, setIsClosing] = useState(false)

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }

    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  const handleClose = () => {
    setIsClosing(true)
    setTimeout(() => {
      onClose()
      setIsClosing(false)
    }, 300)
  }

  if (!isOpen) return null

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'EXTREME': return 'text-red-500'
      case 'HIGH': return 'text-orange-500'
      case 'MEDIUM': return 'text-yellow-500'
      case 'LOW': return 'text-green-500'
      default: return 'text-text-secondary'
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-red-500'
    if (score >= 6) return 'text-orange-500'
    if (score >= 4) return 'text-yellow-500'
    return 'text-green-500'
  }

  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center p-4 ${isClosing ? 'animate-fade-out' : 'animate-fade-in'}`}>
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className={`relative bg-terminal-card border border-terminal-border rounded-xl max-w-2xl w-full max-h-[90vh] overflow-hidden ${isClosing ? 'animate-slide-down' : 'animate-slide-up'}`}>
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-terminal-border">
          <h2 className="text-2xl font-bold text-text-primary flex items-center gap-3">
            <TrendingUpIcon className="text-cyber-primary" />
            Pool Analysis
          </h2>
          <button
            onClick={handleClose}
            className="text-text-tertiary hover:text-text-primary transition-colors"
          >
            <XIcon />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {/* Pool Address */}
          <div className="mb-4">
            <p className="text-sm text-text-tertiary mb-1">Pool Address</p>
            <p className="font-mono text-sm text-text-primary">
              {poolAddress.slice(0, 20)}...{poolAddress.slice(-20)}
            </p>
          </div>

          {/* Score Data if available */}
          {scoreData && (
            <div className="mb-6 space-y-4">
              {/* Degen Score */}
              <div className="bg-terminal-surface/50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-text-tertiary">DEGEN SCORE</span>
                  <span className={`text-3xl font-bold ${getScoreColor(scoreData.degen_score || 0)}`}>
                    {scoreData.degen_score || 'N/A'}/10
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-tertiary">RISK LEVEL</span>
                  <span className={`text-lg font-bold ${getRiskColor(scoreData.risk_level || 'UNKNOWN')}`}>
                    {scoreData.risk_level || 'UNKNOWN'}
                  </span>
                </div>
              </div>

              {/* Score Breakdown */}
              {scoreData.score_breakdown && (
                <div className="space-y-2">
                  <h3 className="text-sm font-semibold text-text-primary mb-2">Score Breakdown</h3>
                  {Object.entries(scoreData.score_breakdown).map(([key, value]: [string, any]) => (
                    <div key={key} className="flex items-center justify-between">
                      <span className="text-xs text-text-tertiary capitalize">
                        {key.replace(/_/g, ' ')}
                      </span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-terminal-surface rounded-full h-2">
                          <div 
                            className="h-full bg-cyber-primary rounded-full transition-all"
                            style={{ width: `${(value / 10) * 100}%` }}
                          />
                        </div>
                        <span className="text-xs text-text-secondary w-8 text-right">
                          {typeof value === 'number' ? value.toFixed(1) : value}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Red Flags */}
              {scoreData.red_flags && scoreData.red_flags.length > 0 && (
                <div className="bg-red-900/20 border border-red-500/50 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-red-500 mb-2 flex items-center gap-2">
                    <AlertTriangleIcon className="w-4 h-4" />
                    Red Flags
                  </h3>
                  <ul className="space-y-1">
                    {scoreData.red_flags.map((flag: string, i: number) => (
                      <li key={i} className="text-xs text-red-400">
                        {flag}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Analysis Result */}
          <div className="bg-terminal-surface/30 rounded-lg p-4">
            <pre className="whitespace-pre-wrap text-sm text-text-secondary font-mono leading-relaxed">
              {analysisResult}
            </pre>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-terminal-border">
          <button
            onClick={handleClose}
            className="btn-primary w-full"
          >
            Close Analysis
          </button>
        </div>
      </div>
    </div>
  )
}