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
    <div className="min-h-screen bg-terminal-bg relative overflow-hidden">
      {/* Animated background grid */}
      <div className="fixed inset-0 opacity-30">
        <div className="cyber-grid"></div>
      </div>
      
      {/* Main container */}
      <div className="relative z-10 container mx-auto px-6 py-12 max-w-8xl">
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
                  <div className="bg-terminal-surface/50 border border-terminal-border rounded-lg p-6 mb-6 backdrop-blur-sm">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-terminal text-xs uppercase tracking-widest">QUERY INPUT:</span>
                      <div className="flex-1 h-px bg-gradient-to-r from-cyber-primary/50 to-transparent"></div>
                    </div>
                    <p className="text-text-secondary font-mono text-sm leading-relaxed">
                      <span className="text-cyber-primary">$</span> {lastQuery}
                    </p>
                  </div>
                )}
                
                {agentResponse && (
                  <div className="bg-terminal-card/30 border border-terminal-border rounded-lg p-6 backdrop-blur-sm mb-6">
                    <div className="flex items-center gap-3 mb-4">
                      <span className="text-terminal text-xs uppercase tracking-widest">SYSTEM OUTPUT:</span>
                      <div className="flex-1 h-px bg-gradient-to-r from-cyber-tertiary/50 to-transparent"></div>
                    </div>
                    <pre className="text-sm text-text-secondary whitespace-pre-wrap font-mono leading-relaxed">
                      <span className="text-cyber-primary">></span> {agentResponse}
                    </pre>
                  </div>
                )}
                
                {scanStats && (
                  <div className="flex items-center gap-3 text-terminal text-xs">
                    <span className="uppercase tracking-widest">DATA SOURCES:</span>
                    <div className="flex items-center gap-2">
                      {scanStats.sources.map((source, i) => (
                        <span key={i} className="bg-terminal-surface px-2 py-1 rounded border border-cyber-primary/20">
                          {source}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Enhanced Opportunities Grid */}
            {pools.length > 0 && !isLoading && (
              <div className="space-y-8">
                <div className="flex items-center justify-between">
                  <h2 className="text-4xl font-bold text-text-primary flex items-center gap-4">
                    <span className="text-terminal text-lg">></span>
                    <span className="text-gradient">OPPORTUNITIES DISCOVERED</span>
                  </h2>
                  <div className="flex items-center gap-3">
                    <div className="status-dot status-online"></div>
                    <span className="text-terminal text-sm font-semibold">
                      {pools.length} POOLS FOUND
                    </span>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {pools.map((pool, index) => (
                    <div key={`${pool.pool_address}-${index}`} className="opportunity-card">
                      <OpportunityCard
                        pool={pool}
                        onAnalyze={handleAnalyze}
                      />
                    </div>
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