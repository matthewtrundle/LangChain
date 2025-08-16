'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'
import { fetchWithConfig } from '@/lib/api'

interface PaperTradingContextType {
  isPaperMode: boolean
  setPaperMode: (mode: boolean) => void
  paperBalance: number
  paperPerformance: any
}

const PaperTradingContext = createContext<PaperTradingContextType>({
  isPaperMode: false,
  setPaperMode: () => {},
  paperBalance: 0,
  paperPerformance: null
})

export function PaperTradingProvider({ children }: { children: React.ReactNode }) {
  const [isPaperMode, setIsPaperMode] = useState(false)
  const [paperBalance, setPaperBalance] = useState(0)
  const [paperPerformance, setPaperPerformance] = useState(null)

  useEffect(() => {
    checkPaperTradingStatus()
  }, [])

  const checkPaperTradingStatus = async () => {
    try {
      const response = await fetchWithConfig('/paper-trading/status')
      const data = await response.json()
      setIsPaperMode(data.enabled || false)
      if (data.enabled && data.performance) {
        setPaperBalance(data.performance.current_balance || 0)
        setPaperPerformance(data.performance)
      }
    } catch (error) {
      console.error('Failed to check paper trading status:', error)
    }
  }

  const setPaperMode = (mode: boolean) => {
    setIsPaperMode(mode)
    if (mode) {
      checkPaperTradingStatus()
    }
  }

  return (
    <PaperTradingContext.Provider 
      value={{ 
        isPaperMode, 
        setPaperMode, 
        paperBalance, 
        paperPerformance 
      }}
    >
      {children}
    </PaperTradingContext.Provider>
  )
}

export const usePaperTrading = () => {
  const context = useContext(PaperTradingContext)
  if (!context) {
    throw new Error('usePaperTrading must be used within PaperTradingProvider')
  }
  return context
}