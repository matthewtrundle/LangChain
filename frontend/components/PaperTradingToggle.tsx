'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  TestTube, 
  Wallet, 
  AlertCircle, 
  Check,
  X
} from 'lucide-react'
import { fetchWithConfig } from '@/lib/api'

interface PaperTradingToggleProps {
  onModeChange?: (paperMode: boolean) => void
}

export default function PaperTradingToggle({ onModeChange }: PaperTradingToggleProps) {
  const [paperMode, setPaperMode] = useState(false)
  const [loading, setLoading] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [pendingMode, setPendingMode] = useState(false)

  useEffect(() => {
    checkPaperTradingStatus()
  }, [])

  const checkPaperTradingStatus = async () => {
    try {
      const response = await fetchWithConfig('/paper-trading/status')
      const data = await response.json()
      setPaperMode(data.enabled || false)
      onModeChange?.(data.enabled || false)
    } catch (error) {
      console.error('Failed to check paper trading status:', error)
    }
  }

  const handleToggle = () => {
    setPendingMode(!paperMode)
    setShowConfirm(true)
  }

  const confirmToggle = async () => {
    setLoading(true)
    setShowConfirm(false)
    
    try {
      const endpoint = pendingMode 
        ? '/strategies/paper-trading/enable' 
        : '/strategies/paper-trading/disable'
      
      const response = await fetchWithConfig(endpoint, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ total_capital: 10000 })
      })
      
      if (response.ok) {
        setPaperMode(pendingMode)
        onModeChange?.(pendingMode)
      }
    } catch (error) {
      console.error('Failed to toggle paper trading:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* Main Toggle */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`fixed top-4 right-4 z-40 transition-all ${
          paperMode ? 'animate-pulse-slow' : ''
        }`}
      >
        <div className={`rounded-lg p-4 backdrop-blur-md border ${
          paperMode 
            ? 'bg-yellow-500/10 border-yellow-500/50' 
            : 'bg-gray-900/80 border-gray-700'
        }`}>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              {paperMode ? (
                <TestTube className="w-5 h-5 text-yellow-500" />
              ) : (
                <Wallet className="w-5 h-5 text-green-500" />
              )}
              <div>
                <p className="text-sm font-medium text-white">
                  {paperMode ? 'Paper Trading' : 'Live Trading'}
                </p>
                <p className="text-xs text-gray-400">
                  {paperMode ? 'Testing mode active' : 'Real funds active'}
                </p>
              </div>
            </div>

            {/* Toggle Switch */}
            <button
              onClick={handleToggle}
              disabled={loading}
              className="relative w-14 h-7 rounded-full transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-purple-500"
              style={{
                backgroundColor: paperMode ? '#EAB308' : '#10B981'
              }}
            >
              <motion.div
                className="absolute top-0.5 left-0.5 w-6 h-6 bg-white rounded-full shadow-lg"
                animate={{
                  x: paperMode ? 28 : 0
                }}
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
              />
            </button>
          </div>

          {/* Warning/Info */}
          {paperMode && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-3 pt-3 border-t border-yellow-500/20"
            >
              <div className="flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-yellow-500 mt-0.5" />
                <div className="text-xs text-gray-400">
                  <p>No real funds at risk</p>
                  <p className="mt-1">Starting balance: $10,000</p>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </motion.div>

      {/* Confirmation Modal */}
      <AnimatePresence>
        {showConfirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowConfirm(false)}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              className="bg-gray-900 rounded-lg p-6 max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-bold text-white mb-4">
                {pendingMode ? 'Enable Paper Trading?' : 'Disable Paper Trading?'}
              </h3>
              
              <div className="space-y-4 mb-6">
                {pendingMode ? (
                  <>
                    <div className="flex items-start gap-3">
                      <TestTube className="w-5 h-5 text-yellow-500 mt-0.5" />
                      <div>
                        <p className="text-gray-300">Switch to testing mode</p>
                        <p className="text-sm text-gray-500 mt-1">
                          • No real funds will be used
                        </p>
                        <p className="text-sm text-gray-500">
                          • Start with $10,000 virtual balance
                        </p>
                        <p className="text-sm text-gray-500">
                          • Test strategies risk-free
                        </p>
                      </div>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="flex items-start gap-3">
                      <Wallet className="w-5 h-5 text-green-500 mt-0.5" />
                      <div>
                        <p className="text-gray-300">Switch to live trading</p>
                        <p className="text-sm text-gray-500 mt-1">
                          • Real funds will be at risk
                        </p>
                        <p className="text-sm text-gray-500">
                          • Requires wallet connection
                        </p>
                        <p className="text-sm text-gray-500">
                          • All trades will be executed
                        </p>
                      </div>
                    </div>
                    <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                      <p className="text-sm text-red-400 flex items-center gap-2">
                        <AlertCircle className="w-4 h-4" />
                        Ensure you understand the risks
                      </p>
                    </div>
                  </>
                )}
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowConfirm(false)}
                  className="flex-1 btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmToggle}
                  className={`flex-1 ${
                    pendingMode ? 'btn-warning' : 'btn-primary'
                  }`}
                >
                  {pendingMode ? 'Enable Paper Trading' : 'Switch to Live'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}