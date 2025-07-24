'use client'

import { useState, useEffect } from 'react'
import { TrendingUpIcon, ActivityIcon, DatabaseIcon, BrainIcon } from './icons/Icons'

interface AgentState {
  scanner: 'idle' | 'active' | 'complete'
  analyzer: 'idle' | 'active' | 'complete'
  monitor: 'idle' | 'active' | 'complete'
  coordinator: 'idle' | 'active' | 'complete'
}

interface AgentFlowVisualizerProps {
  isProcessing: boolean
  currentPhase?: string
}

export default function AgentFlowVisualizer({ isProcessing, currentPhase }: AgentFlowVisualizerProps) {
  const [agentStates, setAgentStates] = useState<AgentState>({
    scanner: 'idle',
    analyzer: 'idle',
    monitor: 'idle',
    coordinator: 'idle'
  })

  const [dataFlow, setDataFlow] = useState({
    scannerToAnalyzer: false,
    analyzerToCoordinator: false,
    monitorToCoordinator: false
  })

  useEffect(() => {
    if (!isProcessing) {
      setAgentStates({
        scanner: 'idle',
        analyzer: 'idle',
        monitor: 'idle',
        coordinator: 'idle'
      })
      setDataFlow({
        scannerToAnalyzer: false,
        analyzerToCoordinator: false,
        monitorToCoordinator: false
      })
      return
    }

    // Simulate agent workflow
    const workflow = async () => {
      // Phase 1: Scanner starts
      setAgentStates(prev => ({ ...prev, scanner: 'active', coordinator: 'active' }))
      
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // Phase 2: Scanner sends data to Analyzer
      setAgentStates(prev => ({ ...prev, scanner: 'complete' }))
      setDataFlow(prev => ({ ...prev, scannerToAnalyzer: true }))
      
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Phase 3: Analyzer processes
      setAgentStates(prev => ({ ...prev, analyzer: 'active' }))
      setDataFlow(prev => ({ ...prev, scannerToAnalyzer: false }))
      
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Phase 4: Analyzer sends to Coordinator
      setAgentStates(prev => ({ ...prev, analyzer: 'complete' }))
      setDataFlow(prev => ({ ...prev, analyzerToCoordinator: true }))
      
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Phase 5: Monitor also sends data
      setAgentStates(prev => ({ ...prev, monitor: 'active' }))
      setDataFlow(prev => ({ ...prev, analyzerToCoordinator: false, monitorToCoordinator: true }))
      
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Phase 6: Complete
      setAgentStates(prev => ({ ...prev, monitor: 'complete', coordinator: 'complete' }))
      setDataFlow(prev => ({ ...prev, monitorToCoordinator: false }))
    }

    workflow()
  }, [isProcessing])

  const getAgentStyle = (state: 'idle' | 'active' | 'complete') => {
    switch (state) {
      case 'active':
        return 'ring-2 ring-cyber-primary shadow-cyber-glow animate-pulse-glow'
      case 'complete':
        return 'ring-2 ring-cyber-primary/50 bg-terminal-accent'
      default:
        return 'opacity-50'
    }
  }

  const getAgentColor = (state: 'idle' | 'active' | 'complete') => {
    switch (state) {
      case 'active':
        return 'text-cyber-primary'
      case 'complete':
        return 'text-cyber-primary/70'
      default:
        return 'text-text-tertiary'
    }
  }

  return (
    <div className="relative w-full">
      {/* Background grid effect */}
      <div className="absolute inset-0 opacity-10">
        <div className="cyber-grid"></div>
      </div>

      <div className="relative bg-terminal-card/50 border border-terminal-border rounded-xl p-8 backdrop-blur-sm">
        <h3 className="text-xl font-bold text-text-primary mb-6 flex items-center gap-3">
          <span className="text-terminal">&gt;</span>
          <span>MULTI-AGENT COORDINATION</span>
          {isProcessing && (
            <span className="text-xs text-cyber-primary bg-cyber-primary/20 px-2 py-1 rounded-full animate-pulse">
              PROCESSING
            </span>
          )}
        </h3>

        <div className="grid grid-cols-4 gap-8 relative">
          {/* Scanner Agent */}
          <div className="relative">
            <div className={`agent-node ${getAgentStyle(agentStates.scanner)}`}>
              <div className="bg-terminal-surface border border-terminal-border rounded-xl p-6 transition-all duration-300">
                <TrendingUpIcon className={`w-8 h-8 mb-3 ${getAgentColor(agentStates.scanner)}`} />
                <h4 className="text-sm font-bold text-text-primary mb-1">SCANNER</h4>
                <p className="text-xs text-text-tertiary">Pool Discovery</p>
                {agentStates.scanner === 'active' && (
                  <div className="mt-3">
                    <div className="text-xs text-terminal">Scanning protocols...</div>
                    <div className="w-full bg-terminal-bg rounded-full h-1 mt-2 overflow-hidden">
                      <div className="h-full bg-cyber-primary animate-pulse" style={{ width: '70%' }}></div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Analyzer Agent */}
          <div className="relative">
            <div className={`agent-node ${getAgentStyle(agentStates.analyzer)}`}>
              <div className="bg-terminal-surface border border-terminal-border rounded-xl p-6 transition-all duration-300">
                <ActivityIcon className={`w-8 h-8 mb-3 ${getAgentColor(agentStates.analyzer)}`} />
                <h4 className="text-sm font-bold text-text-primary mb-1">ANALYZER</h4>
                <p className="text-xs text-text-tertiary">Risk Assessment</p>
                {agentStates.analyzer === 'active' && (
                  <div className="mt-3">
                    <div className="text-xs text-terminal">Calculating scores...</div>
                    <div className="flex gap-1 mt-2">
                      {[1, 2, 3].map(i => (
                        <div key={i} className="w-2 h-2 bg-cyber-primary rounded-full animate-pulse" 
                             style={{ animationDelay: `${i * 0.2}s` }}></div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Monitor Agent */}
          <div className="relative">
            <div className={`agent-node ${getAgentStyle(agentStates.monitor)}`}>
              <div className="bg-terminal-surface border border-terminal-border rounded-xl p-6 transition-all duration-300">
                <DatabaseIcon className={`w-8 h-8 mb-3 ${getAgentColor(agentStates.monitor)}`} />
                <h4 className="text-sm font-bold text-text-primary mb-1">MONITOR</h4>
                <p className="text-xs text-text-tertiary">Track Positions</p>
                {agentStates.monitor === 'active' && (
                  <div className="mt-3">
                    <div className="text-xs text-terminal">Checking history...</div>
                    <div className="loader-grid mt-2">
                      {[...Array(4)].map((_, i) => (
                        <div key={i} className="w-2 h-2 bg-cyber-primary/30 rounded animate-pulse"
                             style={{ animationDelay: `${i * 0.1}s` }}></div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Coordinator Agent */}
          <div className="relative">
            <div className={`agent-node ${getAgentStyle(agentStates.coordinator)}`}>
              <div className="bg-terminal-surface border border-terminal-border rounded-xl p-6 transition-all duration-300">
                <BrainIcon className={`w-8 h-8 mb-3 ${getAgentColor(agentStates.coordinator)}`} />
                <h4 className="text-sm font-bold text-text-primary mb-1">COORDINATOR</h4>
                <p className="text-xs text-text-tertiary">Decision Engine</p>
                {agentStates.coordinator === 'active' && (
                  <div className="mt-3">
                    <div className="text-xs text-terminal">Orchestrating...</div>
                    <div className="mt-2 flex justify-center">
                      <div className="w-4 h-4 border-2 border-cyber-primary rounded-full animate-spin"></div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Data Flow Arrows */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 10 }}>
            {/* Scanner to Analyzer */}
            <defs>
              <marker id="arrowhead" markerWidth="10" markerHeight="7" 
                      refX="9" refY="3.5" orient="auto" fill="#00ff88">
                <polygon points="0 0, 10 3.5, 0 7" />
              </marker>
            </defs>
            
            {dataFlow.scannerToAnalyzer && (
              <g className="animate-pulse">
                <line
                  x1="200" y1="80" x2="350" y2="80"
                  stroke="#00ff88"
                  strokeWidth="2"
                  markerEnd="url(#arrowhead)"
                  className="animate-slide-right"
                />
                <circle r="4" fill="#00ff88">
                  <animateMotion dur="1s" repeatCount="indefinite" path="M 200 80 L 350 80" />
                </circle>
              </g>
            )}

            {/* Analyzer to Coordinator */}
            {dataFlow.analyzerToCoordinator && (
              <g className="animate-pulse">
                <line
                  x1="400" y1="80" x2="550" y2="80"
                  stroke="#00ff88"
                  strokeWidth="2"
                  markerEnd="url(#arrowhead)"
                />
                <circle r="4" fill="#00ff88">
                  <animateMotion dur="1s" repeatCount="indefinite" path="M 400 80 L 550 80" />
                </circle>
              </g>
            )}

            {/* Monitor to Coordinator */}
            {dataFlow.monitorToCoordinator && (
              <g className="animate-pulse">
                <line
                  x1="400" y1="130" x2="580" y2="100"
                  stroke="#00ff88"
                  strokeWidth="2"
                  markerEnd="url(#arrowhead)"
                />
                <circle r="4" fill="#00ff88">
                  <animateMotion dur="1s" repeatCount="indefinite" path="M 400 130 L 580 100" />
                </circle>
              </g>
            )}
          </svg>
        </div>

        {/* Status Messages */}
        <div className="mt-8 bg-terminal-bg/50 rounded-lg p-4 border border-terminal-border">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-terminal text-xs uppercase tracking-widest">SYSTEM LOG:</span>
            <div className="flex-1 h-px bg-gradient-to-r from-cyber-primary/50 to-transparent"></div>
          </div>
          <div className="space-y-1 text-xs font-mono text-text-tertiary">
            {agentStates.scanner === 'active' && (
              <div className="text-cyber-primary">&gt; Scanner Agent: Discovering new high-yield pools...</div>
            )}
            {agentStates.analyzer === 'active' && (
              <div className="text-cyber-tertiary">&gt; Analyzer Agent: Calculating degen scores and risk metrics...</div>
            )}
            {agentStates.monitor === 'active' && (
              <div className="text-performance-good">&gt; Monitor Agent: Checking historical performance data...</div>
            )}
            {agentStates.coordinator === 'complete' && (
              <div className="text-cyber-primary">&gt; Coordinator: Analysis complete. Results ready.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}