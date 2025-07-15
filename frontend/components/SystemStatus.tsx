'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'
import { CheckCircleIcon, XCircleIcon, ActivityIcon, AlertTriangleIcon } from './icons/Icons'

interface SystemStatusProps {
  className?: string
}

export default function SystemStatus({ className }: SystemStatusProps) {
  const [status, setStatus] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        setError(null)
        const [healthStatus, systemStatus] = await Promise.all([
          apiClient.checkHealth(),
          apiClient.getSystemStatus()
        ])
        setStatus({ health: healthStatus, system: systemStatus })
      } catch (error) {
        console.error('Failed to fetch system status:', error)
        setError('Unable to connect to backend')
      } finally {
        setIsLoading(false)
      }
    }

    fetchStatus()
    const interval = setInterval(fetchStatus, 30000) // Update every 30 seconds
    return () => clearInterval(interval)
  }, [])

  if (isLoading) {
    return (
      <div className={`card ${className}`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">System Status</h3>
          <div className="loading-spinner w-5 h-5" />
        </div>
        <div className="space-y-3">
          <div className="loading-skeleton h-4 w-full" />
          <div className="loading-skeleton h-4 w-3/4" />
          <div className="loading-skeleton h-4 w-1/2" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`card border-degen-danger/50 ${className}`}>
        <div className="flex items-center gap-3 mb-4">
          <XCircleIcon className="text-degen-danger" />
          <h3 className="text-lg font-semibold text-white">System Status</h3>
        </div>
        <div className="flex items-center gap-2 text-degen-danger">
          <AlertTriangleIcon className="w-4 h-4" />
          <span className="text-sm">{error}</span>
        </div>
      </div>
    )
  }

  const { health, system } = status
  const isSystemHealthy = health?.status === 'healthy'

  return (
    <div className={`card ${isSystemHealthy ? 'border-degen-success/50' : 'border-degen-danger/50'} ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Multi-Agent System</h3>
        <div className="flex items-center gap-2">
          <div className={`status-dot ${isSystemHealthy ? 'status-online' : 'status-offline'}`} />
          <span className={`text-sm font-medium ${isSystemHealthy ? 'text-degen-success' : 'text-degen-danger'}`}>
            {isSystemHealthy ? 'Online' : 'Offline'}
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {/* Agent Status */}
        {health?.agents && (
          <div className="bg-surface-800/30 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <ActivityIcon className="w-4 h-4 text-surface-400" />
              <span className="text-sm font-medium text-surface-300">Agent Status</span>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(health.agents).map(([agent, status]) => (
                <div key={agent} className="flex items-center justify-between">
                  <span className="text-sm text-surface-400 capitalize">
                    {agent.replace('_', ' ')}
                  </span>
                  <CheckCircleIcon className="w-4 h-4 text-degen-success" />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* API Keys Status */}
        <div className="bg-surface-800/30 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircleIcon className="w-4 h-4 text-surface-400" />
            <span className="text-sm font-medium text-surface-300">API Configuration</span>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-surface-400">Helius</span>
              <div className="flex items-center gap-1">
                {health?.config?.has_helius_key ? (
                  <CheckCircleIcon className="w-4 h-4 text-degen-success" />
                ) : (
                  <XCircleIcon className="w-4 h-4 text-degen-danger" />
                )}
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-surface-400">OpenAI</span>
              <div className="flex items-center gap-1">
                {health?.config?.has_openai_key ? (
                  <CheckCircleIcon className="w-4 h-4 text-degen-success" />
                ) : (
                  <XCircleIcon className="w-4 h-4 text-degen-danger" />
                )}
              </div>
            </div>
          </div>
        </div>

        {/* System Info */}
        <div className="border-t border-degen-border pt-4">
          <div className="flex items-center justify-between text-xs text-surface-500">
            <span>Environment: {health?.config?.environment || 'Unknown'}</span>
            <span>Version: 2.0.0</span>
          </div>
        </div>
      </div>
    </div>
  )
}