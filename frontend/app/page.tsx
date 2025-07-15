'use client'

import { useState } from 'react'
import { Pool, ScanResult, CoordinatorResponse } from '@/lib/types'
import { apiClient } from '@/lib/api'
import OpportunityCard from '@/components/OpportunityCard'
import SearchBar from '@/components/SearchBar'
import SystemStatus from '@/components/SystemStatus'
import { TrendingUpIcon, ActivityIcon, DatabaseIcon } from '@/components/icons/Icons'

export default function Home() {
  const [pools, setPools] = useState<Pool[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [lastQuery, setLastQuery] = useState('')
  const [agentResponse, setAgentResponse] = useState('')
  const [scanStats, setScanStats] = useState<{ found: number; sources: string[] } | null>(null)

  const handleSearch = async (query: string) => {
    setIsLoading(true)
    setLastQuery(query)
    setAgentResponse('')
    
    try {
      const response: CoordinatorResponse = await apiClient.hunt(query)
      
      if (response.success) {
        // Extract pools from coordinator response
        const discoveredPools = response.results?.discovery?.top_opportunities || []
        setPools(discoveredPools)
        setAgentResponse(response.coordination_summary)
        
        setScanStats({
          found: discoveredPools.length,
          sources: ['Multi-Agent System']
        })
      } else {
        setAgentResponse('Failed to process request')
      }
    } catch (error) {
      console.error('Hunt failed:', error)
      setAgentResponse('Error: Unable to connect to agent system')
    } finally {
      setIsLoading(false)
    }
  }

  const handleQuickScan = async (minApy: number) => {
    setIsLoading(true)
    setLastQuery(`Quick scan for ${minApy}%+ APY`)
    setAgentResponse('')
    
    try {
      const response: ScanResult = await apiClient.scan(minApy)
      setPools(response.pools)
      setAgentResponse(`Scanner found ${response.found_pools} opportunities`)
      
      setScanStats({
        found: response.found_pools,
        sources: response.data_sources
      })
    } catch (error) {
      console.error('Scan failed:', error)
      setAgentResponse('Error: Unable to scan for opportunities')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAnalyze = async (poolAddress: string) => {
    try {
      const response = await apiClient.analyze(poolAddress)
      if (response.success) {
        console.log('Analysis complete:', response.result)
        // Update the specific pool with analysis results
        // For now, just log - in production would update pool data
      }
    } catch (error) {
      console.error('Analysis failed:', error)
    }
  }

  return (
    <div className="min-h-screen bg-degen-bg">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gradient mb-4">
            SolDegen
          </h1>
          <p className="text-xl text-surface-400 max-w-2xl mx-auto">
            Multi-agent AI system for discovering high-yield opportunities on Solana
          </p>
          <div className="flex items-center justify-center gap-6 mt-6 text-sm text-surface-500">
            <div className="flex items-center gap-2">
              <TrendingUpIcon className="w-4 h-4" />
              <span>Scanner Agent</span>
            </div>
            <div className="flex items-center gap-2">
              <ActivityIcon className="w-4 h-4" />
              <span>Analyzer Agent</span>
            </div>
            <div className="flex items-center gap-2">
              <DatabaseIcon className="w-4 h-4" />
              <span>Monitor Agent</span>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-3 space-y-8">
            {/* Search Interface */}
            <SearchBar
              onSearch={handleSearch}
              onQuickScan={handleQuickScan}
              isLoading={isLoading}
            />

            {/* Loading State */}
            {isLoading && (
              <div className="card text-center">
                <div className="flex flex-col items-center justify-center py-12">
                  <div className="loading-spinner w-12 h-12 mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">
                    Multi-Agent System Processing...
                  </h3>
                  <p className="text-surface-400 mb-4">
                    Agents are coordinating to find the best opportunities
                  </p>
                  <div className="flex items-center gap-4 text-sm text-surface-500">
                    <span>Scanner → Analyzer → Coordinator</span>
                  </div>
                </div>
              </div>
            )}

            {/* Results Section */}
            {(agentResponse || scanStats) && !isLoading && (
              <div className="card-gradient">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-white">Agent Response</h2>
                  {scanStats && (
                    <div className="flex items-center gap-2 text-sm text-surface-400">
                      <span>{scanStats.found} opportunities found</span>
                    </div>
                  )}
                </div>
                
                {lastQuery && (
                  <div className="bg-surface-800/50 border border-degen-border rounded-lg p-4 mb-4">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm font-medium text-surface-300">Query:</span>
                    </div>
                    <p className="text-white">{lastQuery}</p>
                  </div>
                )}
                
                {agentResponse && (
                  <div className="bg-degen-primary/10 border border-degen-primary/20 rounded-lg p-4 mb-4">
                    <p className="text-surface-200 leading-relaxed">{agentResponse}</p>
                  </div>
                )}
                
                {scanStats && (
                  <div className="flex items-center gap-2 text-xs text-surface-500">
                    <span>Data Sources:</span>
                    <span>{scanStats.sources.join(', ')}</span>
                  </div>
                )}
              </div>
            )}

            {/* Opportunities Grid */}
            {pools.length > 0 && !isLoading && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-3xl font-bold text-white">
                    Opportunities Discovered
                  </h2>
                  <div className="text-sm text-surface-400">
                    {pools.length} pools found
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {pools.map((pool, index) => (
                    <OpportunityCard
                      key={`${pool.pool_address}-${index}`}
                      pool={pool}
                      onAnalyze={handleAnalyze}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Empty State */}
            {pools.length === 0 && !isLoading && !agentResponse && (
              <div className="card text-center py-16">
                <div className="max-w-md mx-auto">
                  <div className="text-6xl mb-6 text-gradient">AI</div>
                  <h3 className="text-2xl font-bold text-white mb-4">
                    Ready to Hunt Yields
                  </h3>
                  <p className="text-surface-400 mb-6 leading-relaxed">
                    Our multi-agent system is standing by to discover the best DeFi opportunities on Solana.
                    Ask in natural language or use the quick scan buttons.
                  </p>
                  <div className="inline-flex items-center gap-2 text-sm text-surface-500 bg-surface-800/50 px-4 py-2 rounded-lg">
                    <span>Powered by LangChain & OpenAI</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <SystemStatus />
          </div>
        </div>
      </div>
    </div>
  )
}