'use client'

import { useWallet, useConnection } from '@solana/wallet-adapter-react'
import { useWalletModal } from '@solana/wallet-adapter-react-ui'
import { useEffect, useState } from 'react'
import { LAMPORTS_PER_SOL, PublicKey } from '@solana/web3.js'
import { motion } from 'framer-motion'

interface TokenBalance {
  mint: string
  symbol: string
  balance: number
  decimals: number
  usdValue?: number
}

export default function WalletDashboardEnhanced() {
  const { connection } = useConnection()
  const { publicKey, disconnect, wallet } = useWallet()
  const { setVisible } = useWalletModal()
  const [solBalance, setSolBalance] = useState<number>(0)
  const [tokenBalances, setTokenBalances] = useState<TokenBalance[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [usdPrice, setUsdPrice] = useState<number>(0)

  // Fetch SOL balance
  useEffect(() => {
    if (!publicKey || !connection) return

    const fetchBalance = async () => {
      try {
        const balance = await connection.getBalance(publicKey)
        setSolBalance(balance / LAMPORTS_PER_SOL)
      } catch (error) {
        console.error('Error fetching balance:', error)
      }
    }

    fetchBalance()
    
    // Subscribe to balance changes
    const subscriptionId = connection.onAccountChange(
      publicKey,
      (accountInfo) => {
        setSolBalance(accountInfo.lamports / LAMPORTS_PER_SOL)
      }
    )

    return () => {
      connection.removeAccountChangeListener(subscriptionId)
    }
  }, [publicKey, connection])

  // Fetch SOL price
  useEffect(() => {
    const fetchPrice = async () => {
      try {
        const response = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd')
        const data = await response.json()
        setUsdPrice(data.solana.usd)
      } catch (error) {
        console.error('Error fetching SOL price:', error)
      }
    }

    fetchPrice()
    const interval = setInterval(fetchPrice, 60000) // Update every minute
    
    return () => clearInterval(interval)
  }, [])

  // Fetch token balances (simplified - in production, use proper token list)
  useEffect(() => {
    if (!publicKey || !connection) return

    const fetchTokenBalances = async () => {
      setIsLoading(true)
      try {
        // This is simplified - in production, you'd use getParsedTokenAccountsByOwner
        // For demo, we'll just show SOL and mock some common tokens
        const mockTokens: TokenBalance[] = [
          {
            mint: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
            symbol: 'USDC',
            balance: Math.random() * 1000,
            decimals: 6,
            usdValue: Math.random() * 1000
          },
          {
            mint: 'So11111111111111111111111111111111111111112',
            symbol: 'SOL',
            balance: solBalance,
            decimals: 9,
            usdValue: solBalance * usdPrice
          }
        ]
        
        setTokenBalances(mockTokens)
      } catch (error) {
        console.error('Error fetching token balances:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchTokenBalances()
  }, [publicKey, connection, solBalance, usdPrice])

  const handleConnect = () => {
    setVisible(true)
  }

  const handleDisconnect = async () => {
    await disconnect()
  }

  if (!publicKey) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-gradient p-6"
      >
        <h3 className="text-lg font-semibold text-text-primary mb-4">Wallet Connection</h3>
        <p className="text-text-secondary mb-4">Connect your wallet to start trading</p>
        <button
          onClick={handleConnect}
          className="w-full btn btn-primary"
        >
          Connect Wallet
        </button>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-gradient p-6 space-y-6"
    >
      {/* Wallet Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-text-primary">Wallet Connected</h3>
          <p className="text-text-tertiary text-sm">
            {publicKey.toBase58().slice(0, 6)}...{publicKey.toBase58().slice(-4)}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {wallet && (
            <img 
              src={wallet.adapter.icon} 
              alt={wallet.adapter.name} 
              className="w-6 h-6"
            />
          )}
          <button
            onClick={handleDisconnect}
            className="text-sm text-text-tertiary hover:text-red-500 transition-colors"
          >
            Disconnect
          </button>
        </div>
      </div>

      {/* SOL Balance */}
      <div className="bg-terminal-surface/50 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-text-secondary">SOL Balance</span>
          <span className="text-xl font-bold text-text-primary">
            {solBalance.toFixed(4)} SOL
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-text-tertiary text-sm">USD Value</span>
          <span className="text-text-secondary">
            ${(solBalance * usdPrice).toFixed(2)}
          </span>
        </div>
      </div>

      {/* Token Balances */}
      <div>
        <h4 className="text-sm font-semibold text-text-secondary mb-3">Token Balances</h4>
        {isLoading ? (
          <div className="text-text-tertiary text-center py-4">Loading tokens...</div>
        ) : (
          <div className="space-y-2">
            {tokenBalances.map((token) => (
              <div
                key={token.mint}
                className="flex items-center justify-between py-2 border-b border-terminal-border last:border-0"
              >
                <span className="text-text-secondary">{token.symbol}</span>
                <div className="text-right">
                  <div className="text-text-primary">{token.balance.toFixed(4)}</div>
                  {token.usdValue && (
                    <div className="text-text-tertiary text-sm">
                      ${token.usdValue.toFixed(2)}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Trading Readiness */}
      <div className="bg-cyber-primary/10 border border-cyber-primary/30 rounded-lg p-4">
        <div className="flex items-center gap-2 text-cyber-primary">
          <div className="w-2 h-2 bg-cyber-primary rounded-full animate-pulse" />
          <span className="text-sm font-semibold">Ready to Trade</span>
        </div>
        <p className="text-text-tertiary text-sm mt-1">
          Your wallet is connected and ready for swaps
        </p>
      </div>
    </motion.div>
  )
}