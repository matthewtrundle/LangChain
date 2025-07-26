'use client'

import { useState } from 'react'
import { SlidersIcon } from './icons/Icons'

export interface FilterOptions {
  minApy: number
  maxApy: number | null
  minTvl: number
  maxTvl: number | null
  protocols: string[]
  sortBy: 'apy' | 'tvl' | 'volume' | 'age'
  sortOrder: 'desc' | 'asc'
  showOnlyNew: boolean
  maxAge: number | null
}

interface FilterBarProps {
  onFilterChange: (filters: FilterOptions) => void
  isExpanded?: boolean
}

export default function FilterBar({ onFilterChange, isExpanded = false }: FilterBarProps) {
  const [showFilters, setShowFilters] = useState(isExpanded)
  const [filters, setFilters] = useState<FilterOptions>({
    minApy: 0,
    maxApy: null,
    minTvl: 0,
    maxTvl: null,
    protocols: [],
    sortBy: 'apy',
    sortOrder: 'desc',
    showOnlyNew: false,
    maxAge: null
  })

  const updateFilter = (key: keyof FilterOptions, value: any) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
    onFilterChange(newFilters)
  }

  const presetFilters = [
    { label: 'High APY + TVL', filters: { minApy: 1000, minTvl: 100000 } },
    { label: 'New Pools', filters: { showOnlyNew: true, maxAge: 24 } },
    { label: 'Safe Yields', filters: { minApy: 100, maxApy: 500, minTvl: 500000 } },
    { label: 'Degen Mode', filters: { minApy: 2000, sortBy: 'apy' as const } },
  ]

  return (
    <div className="card mb-6">
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center gap-2 text-text-primary hover:text-degen-primary transition-colors"
        >
          <SlidersIcon className="w-5 h-5" />
          <span className="font-medium">Filters & Sort</span>
        </button>
        
        {/* Preset Filters */}
        <div className="flex gap-2">
          {presetFilters.map((preset) => (
            <button
              key={preset.label}
              onClick={() => {
                const newFilters = { ...filters, ...preset.filters }
                setFilters(newFilters)
                onFilterChange(newFilters)
              }}
              className="btn-ghost text-xs"
            >
              {preset.label}
            </button>
          ))}
        </div>
      </div>

      {showFilters && (
        <div className="space-y-4">
          {/* APY Range */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-text-tertiary mb-1 block">Min APY %</label>
              <input
                type="number"
                value={filters.minApy}
                onChange={(e) => updateFilter('minApy', Number(e.target.value))}
                className="input text-sm"
                placeholder="0"
              />
            </div>
            <div>
              <label className="text-xs text-text-tertiary mb-1 block">Max APY %</label>
              <input
                type="number"
                value={filters.maxApy || ''}
                onChange={(e) => updateFilter('maxApy', e.target.value ? Number(e.target.value) : null)}
                className="input text-sm"
                placeholder="No limit"
              />
            </div>
          </div>

          {/* TVL Range */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-text-tertiary mb-1 block">Min TVL $</label>
              <input
                type="number"
                value={filters.minTvl}
                onChange={(e) => updateFilter('minTvl', Number(e.target.value))}
                className="input text-sm"
                placeholder="0"
              />
            </div>
            <div>
              <label className="text-xs text-text-tertiary mb-1 block">Max TVL $</label>
              <input
                type="number"
                value={filters.maxTvl || ''}
                onChange={(e) => updateFilter('maxTvl', e.target.value ? Number(e.target.value) : null)}
                className="input text-sm"
                placeholder="No limit"
              />
            </div>
          </div>

          {/* Sort Options */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-text-tertiary mb-1 block">Sort By</label>
              <select
                value={filters.sortBy}
                onChange={(e) => updateFilter('sortBy', e.target.value as any)}
                className="input text-sm"
              >
                <option value="apy">APY</option>
                <option value="tvl">TVL</option>
                <option value="volume">Volume</option>
                <option value="age">Age (Newest)</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-text-tertiary mb-1 block">Order</label>
              <select
                value={filters.sortOrder}
                onChange={(e) => updateFilter('sortOrder', e.target.value as any)}
                className="input text-sm"
              >
                <option value="desc">High to Low</option>
                <option value="asc">Low to High</option>
              </select>
            </div>
          </div>

          {/* Additional Filters */}
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.showOnlyNew}
                onChange={(e) => updateFilter('showOnlyNew', e.target.checked)}
                className="checkbox"
              />
              <span className="text-sm text-text-primary">New Pools Only</span>
            </label>
            
            {filters.showOnlyNew && (
              <div className="flex items-center gap-2">
                <label className="text-xs text-text-tertiary">Max Age (hours)</label>
                <input
                  type="number"
                  value={filters.maxAge || 24}
                  onChange={(e) => updateFilter('maxAge', Number(e.target.value))}
                  className="input text-sm w-20"
                  min="1"
                  max="168"
                />
              </div>
            )}
          </div>

          {/* Clear Filters */}
          <button
            onClick={() => {
              const defaultFilters: FilterOptions = {
                minApy: 0,
                maxApy: null,
                minTvl: 0,
                maxTvl: null,
                protocols: [],
                sortBy: 'apy',
                sortOrder: 'desc',
                showOnlyNew: false,
                maxAge: null
              }
              setFilters(defaultFilters)
              onFilterChange(defaultFilters)
            }}
            className="btn-ghost text-sm"
          >
            Clear All Filters
          </button>
        </div>
      )}
    </div>
  )
}