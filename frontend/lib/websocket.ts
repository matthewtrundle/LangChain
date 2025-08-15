/**
 * WebSocket Service for Real-time Updates
 * Handles pool discoveries, position updates, and system events
 */

export interface WebSocketMessage {
  type: 'pool_discovered' | 'position_update' | 'agent_status' | 'system_alert'
  data: any
  timestamp: string
  trace_id?: string
}

export interface PoolDiscoveryMessage {
  type: 'pool_discovered'
  pool: {
    pool_address: string
    protocol: string
    token_symbols: string
    apy: number
    tvl: number
    volume_24h: number
    age_hours: number
    source: string
    risk_score?: number
    sustainability_score?: number
  }
}

export interface PositionUpdateMessage {
  type: 'position_update'
  position: {
    id: string
    pool_address: string
    current_value: number
    pnl_usd: number
    pnl_percent: number
    il_percent: number
    fees_earned: number
  }
}

type MessageHandler = (message: WebSocketMessage) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectInterval: number = 5000
  private reconnectAttempts: number = 0
  private maxReconnectAttempts: number = 10
  private handlers: Map<string, Set<MessageHandler>> = new Map()
  private url: string
  private isConnecting: boolean = false
  
  constructor() {
    this.url = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'
  }
  
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve()
        return
      }
      
      if (this.isConnecting) {
        // Wait for existing connection attempt
        const checkConnection = setInterval(() => {
          if (this.ws?.readyState === WebSocket.OPEN) {
            clearInterval(checkConnection)
            resolve()
          } else if (!this.isConnecting) {
            clearInterval(checkConnection)
            reject(new Error('Connection failed'))
          }
        }, 100)
        return
      }
      
      this.isConnecting = true
      
      try {
        this.ws = new WebSocket(this.url)
        
        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.isConnecting = false
          this.reconnectAttempts = 0
          this.sendHeartbeat()
          resolve()
        }
        
        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }
        
        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          this.isConnecting = false
          reject(error)
        }
        
        this.ws.onclose = () => {
          console.log('WebSocket disconnected')
          this.isConnecting = false
          this.ws = null
          this.attemptReconnect()
        }
      } catch (error) {
        this.isConnecting = false
        reject(error)
      }
    })
  }
  
  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
  
  subscribe(eventType: string, handler: MessageHandler): () => void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set())
    }
    
    this.handlers.get(eventType)!.add(handler)
    
    // Return unsubscribe function
    return () => {
      const handlers = this.handlers.get(eventType)
      if (handlers) {
        handlers.delete(handler)
        if (handlers.size === 0) {
          this.handlers.delete(eventType)
        }
      }
    }
  }
  
  send(message: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket not connected. Message not sent:', message)
    }
  }
  
  private handleMessage(message: WebSocketMessage) {
    // Handle specific message types
    const handlers = this.handlers.get(message.type)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message)
        } catch (error) {
          console.error('Error in message handler:', error)
        }
      })
    }
    
    // Also check for wildcard handlers
    const wildcardHandlers = this.handlers.get('*')
    if (wildcardHandlers) {
      wildcardHandlers.forEach(handler => {
        try {
          handler(message)
        } catch (error) {
          console.error('Error in wildcard handler:', error)
        }
      })
    }
  }
  
  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      return
    }
    
    this.reconnectAttempts++
    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
    
    setTimeout(() => {
      this.connect().catch(error => {
        console.error('Reconnection failed:', error)
      })
    }, this.reconnectInterval)
  }
  
  private sendHeartbeat() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.send({ type: 'heartbeat', timestamp: new Date().toISOString() })
      
      // Send heartbeat every 30 seconds
      setTimeout(() => this.sendHeartbeat(), 30000)
    }
  }
  
  getConnectionState(): 'connecting' | 'connected' | 'disconnected' {
    if (this.isConnecting) return 'connecting'
    if (this.ws?.readyState === WebSocket.OPEN) return 'connected'
    return 'disconnected'
  }
}

// Singleton instance
const wsService = new WebSocketService()

// React hooks for WebSocket
import { useEffect, useState, useCallback } from 'react'

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false)
  
  useEffect(() => {
    wsService.connect()
      .then(() => setIsConnected(true))
      .catch(error => {
        console.error('Failed to connect WebSocket:', error)
        setIsConnected(false)
      })
    
    // Check connection status periodically
    const interval = setInterval(() => {
      setIsConnected(wsService.getConnectionState() === 'connected')
    }, 1000)
    
    return () => {
      clearInterval(interval)
    }
  }, [])
  
  const subscribe = useCallback((eventType: string, handler: MessageHandler) => {
    return wsService.subscribe(eventType, handler)
  }, [])
  
  const send = useCallback((message: any) => {
    wsService.send(message)
  }, [])
  
  return {
    isConnected,
    subscribe,
    send,
    connectionState: wsService.getConnectionState()
  }
}

export function usePoolDiscovery(onPoolDiscovered: (pool: any) => void) {
  const { subscribe, isConnected } = useWebSocket()
  
  useEffect(() => {
    const unsubscribe = subscribe('pool_discovered', (message) => {
      const poolMessage = message as PoolDiscoveryMessage
      onPoolDiscovered(poolMessage.pool)
    })
    
    return unsubscribe
  }, [subscribe, onPoolDiscovered])
  
  return { isConnected }
}

export function usePositionUpdates(onPositionUpdate: (position: any) => void) {
  const { subscribe, isConnected } = useWebSocket()
  
  useEffect(() => {
    const unsubscribe = subscribe('position_update', (message) => {
      const positionMessage = message as PositionUpdateMessage
      onPositionUpdate(positionMessage.position)
    })
    
    return unsubscribe
  }, [subscribe, onPositionUpdate])
  
  return { isConnected }
}

export default wsService