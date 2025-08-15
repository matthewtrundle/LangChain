'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useWallet, useConnection } from '@solana/wallet-adapter-react'
import { Pool } from '@/lib/types'
import { JupiterSwapService, TOKEN_MINTS } from '@/lib/jupiter-swap'
import { LAMPORTS_PER_SOL } from '@solana/web3.js'

interface SwapModalProps {
  isOpen: boolean
  onClose: () => void
  pool: Pool | null
}

export default function SwapModal({ isOpen, onClose, pool }: SwapModalProps) {
  const { connection } = useConnection()
  const wallet = useWallet()
  const [jupiterService] = useState(() => new JupiterSwapService(connection))
  
  const [inputAmount, setInputAmount] = useState<string>('100')
  const [outputAmount, setOutputAmount] = useState<string>('0')
  const [isLoading, setIsLoading] = useState(false)
  const [isQuoting, setIsQuoting] = useState(false)
  const [error, setError] = useState<string>('')
  const [slippage, setSlippage] = useState<number>(0.5)
  const [solBalance, setSolBalance] = useState<number>(0)
  
  // Get SOL balance
  useEffect(() => {
    if (wallet.publicKey) {
      jupiterService.getTokenBalance(wallet.publicKey, TOKEN_MINTS.SOL)
        .then(setSolBalance)
        .catch(console.error)
    }
  }, [wallet.publicKey, jupiterService])
  
  // Get quote when input changes
  useEffect(() => {
    if (!pool || !inputAmount || parseFloat(inputAmount) <= 0) {
      setOutputAmount('0')
      return
    }
    
    const getQuote = async () => {
      setIsQuoting(true)
      setError('')
      
      try {
        // For demo, assume we're swapping SOL to USDC
        // In production, you'd extract the actual token mints from the pool
        const inputMint = TOKEN_MINTS.SOL
        const outputMint = TOKEN_MINTS.USDC
        const amountInLamports = parseFloat(inputAmount) * LAMPORTS_PER_SOL
        
        const quote = await jupiterService.getQuote(
          inputMint,
          outputMint,
          amountInLamports,
          slippage * 100 // Convert percentage to basis points
        )
        
        if ('error' in quote) {
          setError(quote.message)
          setOutputAmount('0')
        } else {
          // Convert output amount from smallest unit
          const output = parseInt(quote.outAmount) / 1e6 // USDC has 6 decimals
          setOutputAmount(output.toFixed(2))
        }
      } catch (err) {
        setError('Failed to get quote')
        setOutputAmount('0')
      } finally {
        setIsQuoting(false)
      }
    }
    
    const debounceTimer = setTimeout(getQuote, 500)
    return () => clearTimeout(debounceTimer)
  }, [inputAmount, slippage, pool, jupiterService])
  
  const handleSwap = async () => {
    if (!wallet.publicKey || !pool) return
    
    setIsLoading(true)
    setError('')
    
    try {
      const inputMint = TOKEN_MINTS.SOL
      const outputMint = TOKEN_MINTS.USDC
      const amountInLamports = parseFloat(inputAmount) * LAMPORTS_PER_SOL
      
      const result = await jupiterService.executeSwap(
        wallet,
        inputMint,
        outputMint,
        amountInLamports,
        slippage * 100
      )
      
      if ('error' in result) {
        setError(result.message)
      } else {
        // Success! Close modal and show success message
        alert(`Swap successful! Transaction: ${result.signature}`)
        onClose()
        
        // In production, you'd also:
        // 1. Track the position in your backend
        // 2. Show a success notification
        // 3. Update the positions dashboard
      }
    } catch (err: any) {
      setError(err.message || 'Swap failed')
    } finally {
      setIsLoading(false)
    }
  }
  
  if (!pool) return null
  
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            transition={{ type: "spring", damping: 25 }}
            className="bg-terminal-card border border-terminal-border rounded-xl p-6 max-w-md w-full"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-text-primary">Enter Position</h2>
              <button
                onClick={onClose}
                className="text-text-tertiary hover:text-text-primary transition-colors"
              >
                ✕
              </button>
            </div>
            
            {/* Pool Info */}
            <div className="bg-terminal-surface/50 rounded-lg p-4 mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-text-tertiary text-sm">Pool</span>
                <span className="text-text-primary font-semibold">
                  {pool.token_symbols || 'Unknown Pool'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-text-tertiary text-sm">Current APY</span>
                <span className="text-cyber-primary font-bold">
                  {pool.apy || pool.estimated_apy || 0}%
                </span>
              </div>
            </div>
            
            {/* Swap Interface */}
            <div className="space-y-4">
              {/* Input */}
              <div>
                <label className="text-text-secondary text-sm mb-2 block">
                  You Pay
                </label>
                <div className="bg-terminal-surface/50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <input
                      type="number"
                      value={inputAmount}
                      onChange={(e) => setInputAmount(e.target.value)}
                      className="bg-transparent text-2xl text-text-primary outline-none w-full"
                      placeholder="0.0"
                      disabled={isLoading}
                    />
                    <span className="text-text-primary font-semibold">SOL</span>
                  </div>
                  <div className="text-text-tertiary text-sm">
                    Balance: {solBalance.toFixed(4)} SOL
                  </div>
                </div>
              </div>
              
              {/* Arrow */}
              <div className="flex justify-center">
                <div className="text-text-tertiary">↓</div>
              </div>
              
              {/* Output */}
              <div>
                <label className="text-text-secondary text-sm mb-2 block">
                  You Receive (estimated)
                </label>
                <div className="bg-terminal-surface/50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <input
                      type="text"
                      value={isQuoting ? 'Loading...' : outputAmount}
                      readOnly
                      className="bg-transparent text-2xl text-text-primary outline-none w-full"
                      placeholder="0.0"
                    />
                    <span className="text-text-primary font-semibold">USDC</span>
                  </div>
                </div>
              </div>
              
              {/* Slippage Settings */}
              <div className="flex items-center justify-between">
                <span className="text-text-secondary text-sm">Slippage Tolerance</span>
                <div className="flex items-center gap-2">
                  {[0.1, 0.5, 1.0].map((value) => (
                    <button
                      key={value}
                      onClick={() => setSlippage(value)}
                      className={`px-3 py-1 rounded text-sm transition-colors ${
                        slippage === value
                          ? 'bg-cyber-primary text-black font-semibold'
                          : 'bg-terminal-surface text-text-tertiary hover:text-text-primary'
                      }`}
                    >
                      {value}%
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Error Message */}
              {error && (
                <div className="text-red-500 text-sm text-center">
                  {error}
                </div>
              )}
              
              {/* Action Buttons */}
              <div className="flex gap-4">
                <button
                  onClick={onClose}
                  className="flex-1 btn btn-secondary"
                  disabled={isLoading}
                >
                  Cancel
                </button>
                <button
                  onClick={handleSwap}
                  className="flex-1 btn btn-primary"
                  disabled={
                    isLoading || 
                    !wallet.publicKey || 
                    parseFloat(inputAmount) <= 0 ||
                    parseFloat(inputAmount) > solBalance
                  }
                >
                  {isLoading ? 'Swapping...' : 'Swap'}
                </button>
              </div>
            </div>
            
            {/* Warning */}
            <div className="mt-4 text-text-tertiary text-xs text-center">
              This will execute a real transaction on Solana mainnet.
              Please review carefully before confirming.
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}