'use client'

import { useState } from 'react'
import { SearchIcon, ZapIcon, TrendingUpIcon, AlertTriangleIcon } from './icons/Icons'

interface SearchBarProps {
  onSearch: (query: string) => void
  onQuickScan: (minApy: number) => void
  isLoading?: boolean
}

export default function SearchBar({ onSearch, onQuickScan, isLoading }: SearchBarProps) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query.trim())
    }
  }

  const quickActions = [
    { label: 'Extreme', sublabel: '2000%+', apy: 2000, icon: AlertTriangleIcon, color: 'text-degen-primary' },
    { label: 'High', sublabel: '1000%+', apy: 1000, icon: ZapIcon, color: 'text-accent-orange' },
    { label: 'Medium', sublabel: '500%+', apy: 500, icon: TrendingUpIcon, color: 'text-degen-warning' },
    { label: 'Safe', sublabel: '100%+', apy: 100, icon: TrendingUpIcon, color: 'text-degen-success' },
  ]

  return (
    <div className="space-y-6">
      {/* Main Search */}
      <div className="card-gradient">
        <form onSubmit={handleSubmit}>
          <div className="flex gap-3">
            <div className="relative flex-1">
              <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-tertiary" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask the AI agents: 'Find me degen yields over 1000% APY with locked liquidity'"
                className="input w-full pl-10 pr-4 py-3 text-base"
                disabled={isLoading}
              />
            </div>
            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="btn-primary btn-lg px-8"
            >
              {isLoading ? (
                <>
                  <div className="loading-spinner w-5 h-5 mr-2" />
                  Hunting...
                </>
              ) : (
                <>
                  <SearchIcon className="w-5 h-5 mr-2" />
                  Hunt
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Quick Actions */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-text-tertiary">Quick Scan:</span>
          <div className="h-px bg-degen-border flex-1"></div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {quickActions.map((action) => {
            const IconComponent = action.icon
            return (
              <button
                key={action.apy}
                onClick={() => onQuickScan(action.apy)}
                disabled={isLoading}
                className="btn-secondary group hover:border-degen-primary/50 p-4 h-auto flex-col items-center gap-2 disabled:opacity-50"
              >
                <IconComponent className={`w-5 h-5 ${action.color} group-hover:scale-110 transition-transform`} />
                <div className="text-center">
                  <div className="font-medium text-text-primary">{action.label}</div>
                  <div className="text-xs text-text-tertiary">{action.sublabel}</div>
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* Example Queries */}
      <div className="bg-terminal-surface/30 rounded-lg p-4">
        <h4 className="text-sm font-medium text-text-tertiary mb-3">Example Queries:</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
          <button
            onClick={() => setQuery("Find me new Raydium pools with over 1000% APY and locked liquidity")}
            className="text-left text-text-tertiary hover:text-degen-primary transition-colors"
          >
            "Find me new Raydium pools with over 1000% APY and locked liquidity"
          </button>
          <button
            onClick={() => setQuery("Show me the riskiest degen plays on Solana right now")}
            className="text-left text-text-tertiary hover:text-degen-primary transition-colors"
          >
            "Show me the riskiest degen plays on Solana right now"
          </button>
          <button
            onClick={() => setQuery("What are the best BONK farming opportunities?")}
            className="text-left text-text-tertiary hover:text-degen-primary transition-colors"
          >
            "What are the best BONK farming opportunities?"
          </button>
          <button
            onClick={() => setQuery("Find pools less than 24 hours old with high sustainability")}
            className="text-left text-text-tertiary hover:text-degen-primary transition-colors"
          >
            "Find pools less than 24 hours old with high sustainability"
          </button>
        </div>
      </div>
    </div>
  )
}