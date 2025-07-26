'use client'

// Force rebuild - v2
import { useState } from 'react'
import { debugInfo } from '@/lib/debug'
import { Pool, ScanResult, CoordinatorResponse } from '@/lib/types'
import { apiClient } from '@/lib/api'
import OpportunityCard from '@/components/OpportunityCard'
import SearchBar from '@/components/SearchBar'
import SystemStatus from '@/components/SystemStatus'
import AgentFlowVisualizer from '@/components/AgentFlowVisualizer'
import AnalysisModal from '@/components/AnalysisModal'
import PositionDashboard from '@/components/PositionDashboard'
import WalletDashboard from '@/components/WalletDashboard'
import { TrendingUpIcon, ActivityIcon, DatabaseIcon, BriefcaseIcon } from '@/components/icons/Icons'

export default function Home() {
  const [pools, setPools] = useState<Pool[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [lastQuery, setLastQuery] = useState('')
  const [agentResponse, setAgentResponse] = useState('')
  const [scanStats, setScanStats] = useState<{ found: number; sources: string[] } | null>(null)
  const [analysisModal, setAnalysisModal] = useState({
    isOpen: false,
    poolAddress: '',
    result: '',
    scoreData: null as any
  })
  const [showPositions, setShowPositions] = useState(false)
  const [positionRefreshKey, setPositionRefreshKey] = useState(0)

  const handleSearch = async (query: string) => {
    setIsLoading(true)
    setLastQuery(query)
    setAgentResponse('🔍 Initializing agent system...')
    
    try {
      console.log('Starting hunt with query:', query)
      
      // Show progress updates
      setAgentResponse('🤖 Scanner Agent: Discovering pools...')
      
      const response: CoordinatorResponse = await apiClient.hunt(query)
      console.log('Hunt response:', response)
      
      if (response.success) {
        // Extract pools from coordinator response
        const discoveredPools = response.results?.discovery?.top_opportunities || []
        console.log('Discovered pools:', discoveredPools)
        
        // Show execution time if available
        const execTime = (response as any).execution_time
        const timeMsg = execTime ? ` (${execTime.toFixed(1)}s)` : ''
        
        setPools(discoveredPools)
        setAgentResponse(`✅ ${response.coordination_summary || 'Search completed'}${timeMsg}`)
        
        setScanStats({
          found: discoveredPools.length,
          sources: (response as any).agents_used || ['Multi-Agent System']
        })
      } else {
        console.error('Hunt failed - response not successful:', response)
        setAgentResponse(`❌ ${(response as any).error || 'Failed to process request'}`)
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
      console.log('Starting quick scan with minApy:', minApy)
      const response: ScanResult = await apiClient.scan(minApy)
      console.log('Scan response:', response)
      
      // Handle the response data properly
      const pools = response.pools || []
      const foundCount = response.found_pools || pools.length || 0
      const sources = response.data_sources || ['Scanner Agent']
      
      setPools(pools)
      setAgentResponse(`Scanner found ${foundCount} opportunities`)
      
      setScanStats({
        found: foundCount,
        sources: sources
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
      console.log('Analyzing pool:', poolAddress)
      const response = await apiClient.analyze(poolAddress)
      console.log('Analysis response:', response)
      
      if (response.success) {
        // Extract key information from the analysis
        const analysisText = response.result || 'Analysis complete'
        
        // Show in modal
        setAnalysisModal({
          isOpen: true,
          poolAddress: poolAddress,
          result: analysisText,
          scoreData: (response as any).score_data || null
        })
        
        // You could also update the pool data with risk scores
        // setPools(pools.map(p => p.pool_address === poolAddress ? {...p, analyzed: true} : p))
      } else {
        setAnalysisModal({
          isOpen: true,
          poolAddress: poolAddress,
          result: 'Analysis failed: ' + (response.error || 'Unknown error'),
          scoreData: null
        })
      }
    } catch (error) {
      console.error('Analysis failed:', error)
      alert('Unable to analyze pool at this time')
    }
  }

  const handleEnterPosition = async (pool: Pool) => {
    try {
      console.log('Entering position for pool:', pool)
      const response = await fetch(`${apiClient.baseUrl}/position/enter`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pool_address: pool.pool_address,
          pool_data: pool,
          amount: 100 // Default $100
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        alert(`✅ Position entered successfully!\n\nPool: ${pool.token_symbols}\nAmount: $100\nAPY: ${pool.apy}%`)
        
        // Show positions dashboard
        setShowPositions(true)
        // Refresh position dashboard
        setPositionRefreshKey(prev => prev + 1)
      } else {
        const error = await response.json()
        alert(`Failed to enter position: ${error.detail || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Failed to enter position:', error)
      alert('Failed to enter position. Please try again.')
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

        {/* Enhanced Header */}
        <header className="mb-16">
          <div className="text-center space-y-6">
            <h1 className="text-cyber-title">
              SOL<span className="text-cyber-primary">DEGEN</span>
            </h1>
            <p className="text-xl text-text-secondary max-w-3xl mx-auto leading-relaxed">
              Multi-agent AI system hunting <span className="text-cyber-primary font-semibold">extreme yields</span> 
              across Solana DeFi protocols
            </p>
            
            {/* Live stats bar */}
            <div className="flex justify-center items-center gap-8 text-sm">
              <div className="flex items-center gap-2">
                <div className="status-dot status-online"></div>
                <span className="text-terminal">4 AGENTS ACTIVE</span>
              </div>
              <div className="text-text-tertiary">|</div>
              <div className="text-cyber-tertiary">SCANNING 47 PROTOCOLS</div>
              <div className="text-text-tertiary">|</div>
              <div className="text-performance-extreme font-bold">HIGHEST: 2,847% APY</div>
              <div className="text-text-tertiary">|</div>
              <button
                onClick={() => setShowPositions(!showPositions)}
                className="flex items-center gap-2 text-cyber-primary hover:text-cyber-secondary transition-colors"
              >
                <BriefcaseIcon className="w-4 h-4" />
                <span className="font-semibold">POSITIONS</span>
              </button>
            </div>
          </div>
        </header>
        
        {/* Agent Flow Visualizer */}
        <div className="mb-12">
          <AgentFlowVisualizer isProcessing={isLoading} />
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

            {/* Loading State - Now simplified since we have the visualizer */}
            {isLoading && (
              <div className="card text-center">
                <div className="flex flex-col items-center justify-center py-8">
                  <h3 className="text-xl font-bold text-cyber-primary mb-2">
                    PROCESSING YOUR REQUEST...
                  </h3>
                  <p className="text-text-tertiary">
                    Watch the agents coordinate above to find the best opportunities
                  </p>
                </div>
              </div>
            )}

            {/* Results Section */}
            {(agentResponse || scanStats) && !isLoading && (
              <div className="card-gradient">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-text-primary">Agent Response</h2>
                  {scanStats && (
                    <div className="flex items-center gap-2 text-sm text-text-tertiary">
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
                      <span className="text-cyber-primary">&gt;</span> {agentResponse}
                    </pre>
                  </div>
                )}
                
                {scanStats && scanStats.sources && (
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
            {pools && pools.length > 0 && !isLoading && (
              <div className="space-y-8">
                <div className="flex items-center justify-between">
                  <h2 className="text-4xl font-bold text-text-primary flex items-center gap-4">
                    <span className="text-terminal text-lg">&gt;</span>
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
                        onEnterPosition={handleEnterPosition}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Empty State */}
            {(!pools || pools.length === 0) && !isLoading && !agentResponse && (
              <div className="card text-center py-16">
                <div className="max-w-md mx-auto">
                  <div className="text-6xl mb-6 text-gradient">AI</div>
                  <h3 className="text-2xl font-bold text-text-primary mb-4">
                    Ready to Hunt Yields
                  </h3>
                  <p className="text-text-tertiary mb-6 leading-relaxed">
                    Our multi-agent system is standing by to discover the best DeFi opportunities on Solana.
                    Ask in natural language or use the quick scan buttons.
                  </p>
                  <div className="inline-flex items-center gap-2 text-sm text-text-tertiary bg-terminal-surface/50 px-4 py-2 rounded-lg">
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

      {/* Analysis Modal */}
      <AnalysisModal
        isOpen={analysisModal.isOpen}
        onClose={() => setAnalysisModal({ ...analysisModal, isOpen: false })}
        poolAddress={analysisModal.poolAddress}
        analysisResult={analysisModal.result}
        scoreData={analysisModal.scoreData}
      />

      {/* Positions Dashboard Modal */}
      {showPositions && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 overflow-y-auto">
          <div className="min-h-screen px-4 py-8">
            <div className="max-w-7xl mx-auto">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-3xl font-bold text-text-primary">Portfolio Management</h2>
                <button
                  onClick={() => setShowPositions(false)}
                  className="text-text-tertiary hover:text-text-primary transition-colors"
                >
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              {/* Wallet Dashboard */}
              <div className="mb-8">
                <WalletDashboard />
              </div>
              
              {/* Position Dashboard */}
              <PositionDashboard key={positionRefreshKey} />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}