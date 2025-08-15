'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useEffect, useState } from 'react'
import { Pool } from '@/lib/types'
import { TrendingUpIcon, AlertTriangleIcon } from './icons/Icons'

interface PoolNotification {
  pool: Pool
  id: string
  timestamp: Date
}

export default function PoolDiscoveryNotification() {
  const [notifications, setNotifications] = useState<PoolNotification[]>([])
  const [webSocket, setWebSocket] = useState<WebSocket | null>(null)
  
  useEffect(() => {
    // Connect to WebSocket for real-time updates
    const connectWebSocket = () => {
      const ws = new WebSocket(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws')
      
      ws.onopen = () => {
        console.log('WebSocket connected for pool notifications')
      }
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.type === 'pool_discovered' && data.pool) {
            const notification: PoolNotification = {
              pool: data.pool,
              id: `${data.pool.pool_address}-${Date.now()}`,
              timestamp: new Date()
            }
            
            // Add notification with auto-remove after 10 seconds
            setNotifications(prev => [...prev, notification].slice(-5)) // Keep max 5
            
            // Auto remove after 10 seconds
            setTimeout(() => {
              setNotifications(prev => prev.filter(n => n.id !== notification.id))
            }, 10000)
            
            // Play notification sound if high yield
            if (data.pool.apy > 1000) {
              playNotificationSound()
            }
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
      
      ws.onclose = () => {
        console.log('WebSocket disconnected, reconnecting...')
        setTimeout(connectWebSocket, 5000)
      }
      
      setWebSocket(ws)
      return ws
    }
    
    const ws = connectWebSocket()
    
    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [])
  
  const playNotificationSound = () => {
    // Create a simple notification sound using Web Audio API
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()
    
    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)
    
    oscillator.frequency.value = 800
    gainNode.gain.value = 0.1
    
    oscillator.start(audioContext.currentTime)
    oscillator.stop(audioContext.currentTime + 0.1)
  }
  
  const getRiskColor = (apy: number) => {
    if (apy > 5000) return 'text-red-500'
    if (apy > 2000) return 'text-orange-500'
    if (apy > 1000) return 'text-yellow-500'
    return 'text-cyber-primary'
  }
  
  const getRiskLabel = (apy: number) => {
    if (apy > 5000) return 'EXTREME RISK'
    if (apy > 2000) return 'VERY HIGH RISK'
    if (apy > 1000) return 'HIGH RISK'
    return 'MODERATE RISK'
  }
  
  return (
    <div className="fixed top-4 right-4 z-50 pointer-events-none">
      <AnimatePresence>
        {notifications.map((notification) => (
          <motion.div
            key={notification.id}
            initial={{ opacity: 0, x: 300, scale: 0.8 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 300, scale: 0.8 }}
            transition={{ 
              type: "spring",
              stiffness: 400,
              damping: 30
            }}
            className="mb-4 pointer-events-auto"
          >
            <div className="relative bg-terminal-card border border-cyber-primary/50 rounded-lg p-4 backdrop-blur-xl shadow-2xl overflow-hidden">
              {/* Animated border gradient */}
              <div className="absolute inset-0 rounded-lg">
                <div className="absolute inset-0 bg-gradient-to-r from-cyber-primary via-cyber-secondary to-cyber-primary animate-gradient-x opacity-20"></div>
              </div>
              
              {/* Content */}
              <div className="relative z-10">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                      className="text-cyber-primary"
                    >
                      <TrendingUpIcon className="w-5 h-5" />
                    </motion.div>
                    <span className="text-xs text-terminal font-mono uppercase tracking-wider">
                      New Pool Discovered
                    </span>
                  </div>
                  <span className="text-xs text-text-tertiary">
                    {new Date(notification.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-bold text-text-primary">
                      {notification.pool.token_symbols || 'Unknown Pool'}
                    </span>
                    <span className={`text-2xl font-bold ${getRiskColor(notification.pool.apy)}`}>
                      {notification.pool.apy.toLocaleString()}%
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-text-tertiary">
                      TVL: ${(notification.pool.tvl / 1000).toFixed(1)}K
                    </span>
                    <span className={`text-xs font-semibold ${getRiskColor(notification.pool.apy)}`}>
                      {getRiskLabel(notification.pool.apy)}
                    </span>
                  </div>
                  
                  <div className="text-xs text-text-tertiary">
                    {notification.pool.protocol} • {notification.pool.source}
                  </div>
                </div>
                
                {/* Risk indicator bar */}
                <motion.div 
                  className="mt-3 h-1 bg-terminal-surface rounded-full overflow-hidden"
                  initial={{ width: 0 }}
                  animate={{ width: "100%" }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                >
                  <motion.div
                    className={`h-full ${
                      notification.pool.apy > 5000 ? 'bg-red-500' :
                      notification.pool.apy > 2000 ? 'bg-orange-500' :
                      notification.pool.apy > 1000 ? 'bg-yellow-500' :
                      'bg-cyber-primary'
                    }`}
                    initial={{ x: "-100%" }}
                    animate={{ x: 0 }}
                    transition={{ duration: 0.8, delay: 0.3 }}
                  />
                </motion.div>
              </div>
              
              {/* Pulse effect for high yield */}
              {notification.pool.apy > 2000 && (
                <motion.div
                  className="absolute inset-0 rounded-lg border-2 border-red-500"
                  animate={{ opacity: [0.5, 0, 0.5] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                />
              )}
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}