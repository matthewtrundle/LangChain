import { Connection, PublicKey, VersionedTransaction } from '@solana/web3.js'
import { WalletContextState } from '@solana/wallet-adapter-react'

const JUPITER_API_URL = 'https://quote-api.jup.ag/v6'

// Common token mints
export const TOKEN_MINTS = {
  SOL: 'So11111111111111111111111111111111111111112',
  USDC: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
  USDT: 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',
  BONK: 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
  WIF: 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm',
  JUP: 'JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN',
  PYTH: 'HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3',
  JTO: 'jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL',
}

export interface SwapQuote {
  inputMint: string
  outputMint: string
  inAmount: string
  outAmount: string
  otherAmountThreshold: string
  swapMode: string
  slippageBps: number
  platformFee: any
  priceImpactPct: string
  routePlan: any[]
  contextSlot?: number
  timeTaken?: number
}

export interface SwapError {
  error: string
  message: string
}

export class JupiterSwapService {
  private connection: Connection
  
  constructor(connection: Connection) {
    this.connection = connection
  }
  
  /**
   * Get a swap quote from Jupiter
   */
  async getQuote(
    inputMint: string,
    outputMint: string,
    amount: number,
    slippageBps: number = 50 // 0.5% default slippage
  ): Promise<SwapQuote | SwapError> {
    try {
      const params = new URLSearchParams({
        inputMint,
        outputMint,
        amount: amount.toString(),
        slippageBps: slippageBps.toString(),
        onlyDirectRoutes: 'false',
        asLegacyTransaction: 'false',
      })
      
      const response = await fetch(`${JUPITER_API_URL}/quote?${params}`)
      const data = await response.json()
      
      if (!response.ok) {
        return { error: 'QUOTE_ERROR', message: data.error || 'Failed to get quote' }
      }
      
      return data
    } catch (error) {
      console.error('Error getting quote:', error)
      return { error: 'NETWORK_ERROR', message: 'Failed to connect to Jupiter API' }
    }
  }
  
  /**
   * Get swap transaction from Jupiter
   */
  async getSwapTransaction(
    quote: SwapQuote,
    userPublicKey: string,
    wrapAndUnwrapSol: boolean = true,
    feeAccount?: string
  ): Promise<{ swapTransaction: string; lastValidBlockHeight: number } | SwapError> {
    try {
      const response = await fetch(`${JUPITER_API_URL}/swap`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          quoteResponse: quote,
          userPublicKey,
          wrapAndUnwrapSol,
          feeAccount,
          dynamicComputeUnitLimit: true,
          prioritizationFeeLamports: 'auto'
        })
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        return { error: 'SWAP_ERROR', message: data.error || 'Failed to create swap transaction' }
      }
      
      return data
    } catch (error) {
      console.error('Error getting swap transaction:', error)
      return { error: 'NETWORK_ERROR', message: 'Failed to create swap transaction' }
    }
  }
  
  /**
   * Execute a swap
   */
  async executeSwap(
    wallet: WalletContextState,
    inputMint: string,
    outputMint: string,
    amount: number,
    slippageBps: number = 50
  ): Promise<{ signature: string } | SwapError> {
    try {
      if (!wallet.publicKey || !wallet.signTransaction) {
        return { error: 'WALLET_ERROR', message: 'Wallet not connected' }
      }
      
      // Get quote
      const quote = await this.getQuote(inputMint, outputMint, amount, slippageBps)
      if ('error' in quote) {
        return quote
      }
      
      // Get swap transaction
      const swapResult = await this.getSwapTransaction(
        quote,
        wallet.publicKey.toString()
      )
      
      if ('error' in swapResult) {
        return swapResult
      }
      
      // Deserialize and sign transaction
      const swapTransactionBuf = Buffer.from(swapResult.swapTransaction, 'base64')
      const transaction = VersionedTransaction.deserialize(swapTransactionBuf)
      
      // Sign transaction
      const signedTransaction = await wallet.signTransaction(transaction)
      
      // Send transaction
      const rawTransaction = signedTransaction.serialize()
      const signature = await this.connection.sendRawTransaction(rawTransaction, {
        skipPreflight: false,
        maxRetries: 2
      })
      
      // Wait for confirmation
      const latestBlockhash = await this.connection.getLatestBlockhash()
      await this.connection.confirmTransaction({
        signature,
        blockhash: latestBlockhash.blockhash,
        lastValidBlockHeight: latestBlockhash.lastValidBlockHeight
      })
      
      return { signature }
    } catch (error: any) {
      console.error('Error executing swap:', error)
      return { 
        error: 'EXECUTION_ERROR', 
        message: error.message || 'Failed to execute swap' 
      }
    }
  }
  
  /**
   * Get token balance
   */
  async getTokenBalance(
    walletAddress: PublicKey,
    mintAddress: string
  ): Promise<number> {
    try {
      if (mintAddress === TOKEN_MINTS.SOL) {
        const balance = await this.connection.getBalance(walletAddress)
        return balance / 1e9 // Convert lamports to SOL
      }
      
      const mint = new PublicKey(mintAddress)
      const tokenAccounts = await this.connection.getParsedTokenAccountsByOwner(
        walletAddress,
        { mint }
      )
      
      if (tokenAccounts.value.length === 0) {
        return 0
      }
      
      const balance = tokenAccounts.value[0].account.data.parsed.info.tokenAmount.uiAmount
      return balance || 0
    } catch (error) {
      console.error('Error getting token balance:', error)
      return 0
    }
  }
}