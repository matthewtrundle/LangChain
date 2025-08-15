'use client'

// Enhanced version with all visual components
import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { debugInfo } from '@/lib/debug'
import { Pool, ScanResult, CoordinatorResponse } from '@/lib/types'
import { apiClient } from '@/lib/api'
import { useWebSocket, usePoolDiscovery, usePositionUpdates } from '@/lib/websocket'

// Import all our new components
import AnimatedHero from '@/components/AnimatedHero'
import PoolDiscoveryNotification from '@/components/PoolDiscoveryNotification'
import RiskVisualization from '@/components/RiskVisualization'
import PnLChart from '@/components/PnLChart'
import SuccessCelebration, { triggerSuccessCelebration } from '@/components/SuccessCelebration'
import OpportunityCard from '@/components/OpportunityCard'
import SearchBar from '@/components/SearchBar'
import SystemStatus from '@/components/SystemStatus'
import AgentFlowVisualizer from '@/components/AgentFlowVisualizer'
import AnalysisModal from '@/components/AnalysisModal'
import PositionDashboard from '@/components/PositionDashboard'
import WalletDashboard from '@/components/WalletDashboard'
import FilterBar, { FilterOptions } from '@/components/FilterBar'
import { TrendingUpIcon, ActivityIcon, DatabaseIcon, BriefcaseIcon } from '@/components/icons/Icons'

// Mock P&L data for demo
const mockPnLData = [
  { timestamp: new Date(Date.now() - 7200000).toISOString(), value: 1000, pnl: 0, fees: 0, il: 0 },
  { timestamp: new Date(Date.now() - 6300000).toISOString(), value: 1050, pnl: 5, fees: 10, il: 5 },
  { timestamp: new Date(Date.now() - 5400000).toISOString(), value: 1080, pnl: 8, fees: 20, il: 10 },
  { timestamp: new Date(Date.now() - 4500000).toISOString(), value: 1120, pnl: 12, fees: 35, il: 15 },
  { timestamp: new Date(Date.now() - 3600000).toISOString(), value: 1100, pnl: 10, fees: 50, il: 25 },
  { timestamp: new Date(Date.now() - 2700000).toISOString(), value: 1150, pnl: 15, fees: 70, il: 30 },
  { timestamp: new Date(Date.now() - 1800000).toISOString(), value: 1180, pnl: 18, fees: 90, il: 35 },
  { timestamp: new Date(Date.now() - 900000).toISOString(), value: 1220, pnl: 22, fees: 110, il: 40 },
  { timestamp: new Date(Date.now()).toISOString(), value: 1250, pnl: 25, fees: 130, il: 45 }
]

export default function EnhancedHome() {
  const [pools, setPools] = useState<Pool[]>([])
  const [filteredPools, setFilteredPools] = useState<Pool[]>([])
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
  const [showRiskViz, setShowRiskViz] = useState(false)
  const [selectedPool, setSelectedPool] = useState<Pool | null>(null)
  const [showPnLChart, setShowPnLChart] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
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

  // WebSocket hooks
  const { isConnected } = useWebSocket()
  
  // Handle real-time pool discoveries
  usePoolDiscovery(useCallback((pool: any) => {
    console.log('New pool discovered via WebSocket:', pool)
    // Add to pools list with animation
    setPools(prevPools => [pool, ...prevPools].slice(0, 50)) // Keep max 50 pools
  }, []))
  
  // Handle position updates
  usePositionUpdates(useCallback((position: any) => {
    console.log('Position update:', position)
    // Check if position is profitable
    if (position.pnl_percent > 20) {
      setShowSuccess(true)
      triggerSuccessCelebration(position.pnl_usd)
    }
  }, []))

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
        setFilteredPools(discoveredPools) // Reset filtered pools
        setAgentResponse(`✅ ${response.coordination_summary || 'Search completed'}${timeMsg}`)
        
        setScanStats({
          found: discoveredPools.length,
          sources: (response as any).agents_used || ['Multi-Agent System']
        })
      } else {
        console.error('Hunt failed - response not successful:', response)
        setAgentResponse(`❌ ${(response as any).error || 'Failed to process request'}`)
      }
    } catch (error: any) {
      console.error('Hunt failed:', error)
      setAgentResponse('❌ Search failed. Please try again.')
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
      setFilteredPools(pools) // Reset filtered pools
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
        
        // Show success celebration for demo
        setShowSuccess(true)
        setTimeout(() => setShowSuccess(false), 4000)
        
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
  
  // Apply filters to pools
  useEffect(() => {
    let filtered = [...pools]
    
    // Apply APY filter
    filtered = filtered.filter(pool => {
      const apy = pool.apy || pool.estimated_apy || 0
      if (filters.minApy && apy < filters.minApy) return false
      if (filters.maxApy && apy > filters.maxApy) return false
      return true
    })
    
    // Apply TVL filter
    filtered = filtered.filter(pool => {
      if (filters.minTvl && pool.tvl < filters.minTvl) return false
      if (filters.maxTvl && pool.tvl > filters.maxTvl) return false
      return true
    })
    
    // Apply sorting
    filtered.sort((a, b) => {
      let aVal: number = 0
      let bVal: number = 0
      
      switch (filters.sortBy) {
        case 'apy':
          aVal = a.apy || a.estimated_apy || 0
          bVal = b.apy || b.estimated_apy || 0
          break
        case 'tvl':
          aVal = a.tvl || 0
          bVal = b.tvl || 0
          break
      }
      
      return filters.sortOrder === 'desc' ? bVal - aVal : aVal - bVal
    })
    
    setFilteredPools(filtered)
  }, [pools, filters])

  return (
    <div className="min-h-screen bg-terminal-bg relative overflow-hidden">
      {/* Animated background grid */}
      <div className="fixed inset-0 opacity-30">
        <div className="cyber-grid"></div>
      </div>
      
      {/* Pool Discovery Notifications */}
      <PoolDiscoveryNotification />
      
      {/* Success Celebration */}
      <SuccessCelebration 
        show={showSuccess} 
        profit={250}
        onComplete={() => setShowSuccess(false)}
      />
      
      {/* Main container */}
      <div className="relative z-10 container mx-auto px-6 py-12 max-w-8xl">

        {/* Enhanced Animated Header */}
        <AnimatedHero />
        
        {/* WebSocket Connection Status */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2.5 }}
          className="flex justify-center mb-8"
        >
          <div className={`flex items-center gap-2 px-4 py-2 rounded-full bg-terminal-surface border ${
            isConnected ? 'border-green-500/50' : 'border-red-500/50'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            } animate-pulse`} />
            <span className="text-xs text-text-tertiary">
              {isConnected ? 'Real-time updates active' : 'Connecting to WebSocket...'}
            </span>
          </div>
        </motion.div>
        
        {/* Agent Flow Visualizer */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 2.8, duration: 0.5 }}
          className="mb-12"
        >
          <AgentFlowVisualizer isProcessing={isLoading} />
        </motion.div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-3 space-y-8">
            {/* Search Interface */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 3, duration: 0.5 }}
            >
              <SearchBar
                onSearch={handleSearch}
                onQuickScan={handleQuickScan}
                isLoading={isLoading}
              />
            </motion.div>
            
            {/* Filter Bar */}
            {pools.length > 0 && !isLoading && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <FilterBar
                  onFilterChange={setFilters}
                  isExpanded={false}
                />
              </motion.div>
            )}

            {/* Results Section with animations */}
            {(agentResponse || scanStats) && !isLoading && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                className="card-gradient"
              >
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-text-primary">Agent Response</h2>
                  {scanStats && (
                    <div className="flex items-center gap-2 text-sm text-text-tertiary">
                      <span>{scanStats.found} opportunities found</span>
                    </div>
                  )}
                </div>
                
                {agentResponse && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    className="bg-terminal-card/30 border border-terminal-border rounded-lg p-6 backdrop-blur-sm mb-6"
                  >
                    <pre className="text-sm text-text-secondary whitespace-pre-wrap font-mono leading-relaxed">
                      <span className="text-cyber-primary">&gt;</span> {agentResponse}
                    </pre>
                  </motion.div>
                )}
              </motion.div>
            )}

            {/* Opportunities Grid with staggered animations */}
            {pools && pools.length > 0 && !isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="space-y-8"
              >
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
                  {filteredPools.map((pool, index) => (
                    <motion.div
                      key={`${pool.pool_address}-${index}`}
                      initial={{ opacity: 0, y: 50 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ 
                        duration: 0.5,
                        delay: index * 0.1 // Staggered animation
                      }}
                      className="opportunity-card"
                    >
                      <OpportunityCard
                        pool={pool}
                        onAnalyze={(poolAddress) => {
                          handleAnalyze(poolAddress)
                          setSelectedPool(pool)
                          setShowRiskViz(true)
                        }}
                        onEnterPosition={handleEnterPosition}
                      />
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
          </div>

          {/* Enhanced Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 3.2, duration: 0.5 }}
            >
              <SystemStatus />
            </motion.div>
            
            {/* Risk Visualization Panel */}
            <AnimatePresence>
              {showRiskViz && selectedPool && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.9, y: 20 }}
                  transition={{ duration: 0.3 }}
                  className="card-gradient p-6"
                >
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-lg font-semibold text-text-primary">Risk Analysis</h3>
                    <button
                      onClick={() => setShowRiskViz(false)}
                      className="text-text-tertiary hover:text-text-primary"
                    >
                      ✕
                    </button>
                  </div>
                  <RiskVisualization
                    riskScore={selectedPool.degen_score || 75}
                    sustainabilityScore={selectedPool.sustainability_score || 3}
                    impermanentLossRisk={65}
                    volatility={80}
                  />
                </motion.div>
              )}
            </AnimatePresence>
            
            {/* P&L Chart Demo */}
            <AnimatePresence>
              {showPnLChart && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.9, y: 20 }}
                  transition={{ duration: 0.3 }}
                >
                  <PnLChart
                    data={mockPnLData}
                    initialValue={1000}
                    className="shadow-xl"
                  />
                </motion.div>
              )}
            </AnimatePresence>
            
            {/* Demo Controls */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 3.5 }}
              className="card p-4 space-y-2"
            >
              <h4 className="text-sm font-semibold text-text-tertiary mb-2">Demo Features</h4>
              <button
                onClick={() => setShowPnLChart(!showPnLChart)}
                className="w-full text-left text-sm text-cyber-primary hover:text-cyber-secondary transition-colors"
              >
                {showPnLChart ? '▼' : '▶'} P&L Chart
              </button>
              <button
                onClick={() => setShowSuccess(true)}
                className="w-full text-left text-sm text-cyber-primary hover:text-cyber-secondary transition-colors"
              >
                ▶ Success Animation
              </button>
              <button
                onClick={() => setShowPositions(true)}
                className="w-full text-left text-sm text-cyber-primary hover:text-cyber-secondary transition-colors"
              >
                ▶ Position Dashboard
              </button>
            </motion.div>
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
      <AnimatePresence>
        {showPositions && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 overflow-y-auto"
          >
            <motion.div 
              initial={{ y: 100, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 100, opacity: 0 }}
              transition={{ type: "spring" as const, damping: 25 }}
              className="min-h-screen px-4 py-8"
            >
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
                
                {/* Position Dashboard with P&L Charts */}
                <PositionDashboard key={positionRefreshKey} />
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}