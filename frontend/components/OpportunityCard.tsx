'use client'

import { Pool } from '@/lib/types'
import { useState } from 'react'
import { 
  TrendingUpIcon, 
  AlertTriangleIcon, 
  DollarSignIcon, 
  ActivityIcon, 
  LockIcon, 
  DatabaseIcon, 
  ExternalLinkIcon,
  ZapIcon,
  BarChartIcon
} from './icons/Icons'

interface OpportunityCardProps {
  pool: Pool
  onAnalyze?: (poolAddress: string) => void
}

export default function OpportunityCard({ pool, onAnalyze }: OpportunityCardProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleAnalyze = async () => {
    if (onAnalyze) {
      setIsAnalyzing(true)
      await onAnalyze(pool.pool_address)
      setIsAnalyzing(false)
    }
  }

  const getRiskBadgeClass = (risk: string) => {
    switch (risk) {
      case 'LOW': return 'badge-success'
      case 'MEDIUM': return 'badge-warning'
      case 'HIGH': return 'badge-danger'
      case 'EXTREME': return 'badge-primary'
      default: return 'badge-secondary'
    }
  }

  const getApyTextClass = (apy: number) => {
    if (apy > 2000) return 'text-apy-extreme'
    if (apy > 1000) return 'text-apy-high'
    if (apy > 500) return 'text-apy-medium'
    return 'text-apy'
  }

  const formatValue = (value: number) => {
    if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`
    if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`
    return `$${value.toFixed(0)}`
  }

  const formatAge = () => {
    const hours = pool.age_hours || (pool.age_days ? pool.age_days * 24 : 0)
    if (hours < 1) return '< 1h'
    if (hours < 24) return `${hours.toFixed(0)}h`
    return `${(hours / 24).toFixed(1)}d`
  }

  const apy = pool.apy || pool.estimated_apy || 0
  const isHighRisk = pool.risk_level === 'HIGH' || pool.risk_level === 'EXTREME'

  return (
    <div className="card hover-lift group">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-lg font-semibold text-white group-hover:text-gradient transition-colors">
              {pool.token_symbols || `${pool.token_a}/${pool.token_b}`}
            </h3>
            {isHighRisk && (
              <AlertTriangleIcon className="text-degen-warning" />
            )}
          </div>
          <div className="flex items-center gap-2 text-sm text-surface-400">
            <span className="capitalize">{pool.protocol}</span>
            <span>•</span>
            <span>{formatAge()}</span>
            {pool.real_data && (
              <>
                <span>•</span>
                <DatabaseIcon className="w-4 h-4 text-degen-secondary" />
                <span className="text-degen-secondary">Live</span>
              </>
            )}
          </div>
        </div>
        <div className="text-right">
          <div className={`text-3xl font-bold ${getApyTextClass(apy)} group-hover:scale-110 transition-transform`}>
            {apy.toFixed(1)}%
          </div>
          <div className="text-xs text-surface-400 uppercase tracking-wide">APY</div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-surface-800/50 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <DollarSignIcon className="w-4 h-4 text-surface-400" />
            <span className="text-xs text-surface-400 uppercase tracking-wide">TVL</span>
          </div>
          <div className="text-lg font-semibold text-white">{formatValue(pool.tvl)}</div>
        </div>
        <div className="bg-surface-800/50 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <ActivityIcon className="w-4 h-4 text-surface-400" />
            <span className="text-xs text-surface-400 uppercase tracking-wide">24h Volume</span>
          </div>
          <div className="text-lg font-semibold text-white">{formatValue(pool.volume_24h)}</div>
        </div>
      </div>

      {/* Status Badges */}
      <div className="flex flex-wrap gap-2 mb-4">
        {pool.risk_level && (
          <span className={getRiskBadgeClass(pool.risk_level)}>
            {pool.risk_level}
          </span>
        )}
        {pool.liquidity_locked && (
          <span className="badge-success">
            <LockIcon className="w-3 h-3 mr-1" />
            Locked
          </span>
        )}
        {pool.degen_score && (
          <span className="badge-secondary">
            <BarChartIcon className="w-3 h-3 mr-1" />
            {pool.degen_score.toFixed(1)}/10
          </span>
        )}
        <span className="badge-secondary">
          {pool.source}
        </span>
      </div>

      {/* Recommendation */}
      {pool.recommendation && (
        <div className="bg-surface-800/30 border border-degen-border rounded-lg p-3 mb-4">
          <p className="text-sm text-surface-300 leading-relaxed">
            {pool.recommendation}
          </p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-2">
        <button
          onClick={handleAnalyze}
          disabled={isAnalyzing}
          className="btn-primary flex-1 disabled:opacity-50"
        >
          {isAnalyzing ? (
            <>
              <div className="loading-spinner w-4 h-4 mr-2" />
              Analyzing...
            </>
          ) : (
            <>
              <TrendingUpIcon className="w-4 h-4 mr-2" />
              Analyze
            </>
          )}
        </button>
        <button className="btn-secondary">
          <ExternalLinkIcon className="w-4 h-4 mr-2" />
          View
        </button>
      </div>

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-degen-border">
        <div className="flex items-center justify-between text-xs text-surface-500">
          <span>Pool: {pool.pool_address.slice(0, 8)}...{pool.pool_address.slice(-6)}</span>
          {pool.sustainability_score && (
            <span>Sustainability: {pool.sustainability_score.toFixed(1)}/10</span>
          )}
        </div>
      </div>
    </div>
  )
}