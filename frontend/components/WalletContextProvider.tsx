'use client'

import { FC, ReactNode, useMemo } from 'react'
import { ConnectionProvider, WalletProvider } from '@solana/wallet-adapter-react'
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui'
import { 
  PhantomWalletAdapter,
  SolflareWalletAdapter,
  TorusWalletAdapter,
  LedgerWalletAdapter,
} from '@solana/wallet-adapter-wallets'
import { clusterApiUrl } from '@solana/web3.js'

// Import wallet adapter CSS
import '@solana/wallet-adapter-react-ui/styles.css'

interface WalletContextProviderProps {
  children: ReactNode
}

export const WalletContextProvider: FC<WalletContextProviderProps> = ({ children }) => {
  // You can also use custom RPC endpoint like Helius
  const endpoint = useMemo(() => {
    // Use Helius if available, otherwise fallback to public RPC
    return process.env.NEXT_PUBLIC_HELIUS_RPC_URL || clusterApiUrl('mainnet-beta')
  }, [])

  const wallets = useMemo(
    () => [
      new PhantomWalletAdapter(),
      new SolflareWalletAdapter(),
      new TorusWalletAdapter(),
      new LedgerWalletAdapter(),
    ],
    []
  )

  return (
    <ConnectionProvider endpoint={endpoint}>
      <WalletProvider wallets={wallets} autoConnect>
        <WalletModalProvider>
          {children}
        </WalletModalProvider>
      </WalletProvider>
    </ConnectionProvider>
  )
}