'use client';

import React, { useEffect, useState } from 'react';
import { 
  Wallet, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Activity,
  RefreshCw,
  AlertTriangle
} from 'lucide-react';
import { fetchWithConfig } from '../lib/api';

interface WalletData {
  balance: number;
  initial_balance: number;
  available_balance: number;
  performance: {
    total_pnl: number;
    total_pnl_percentage: number;
    winning_positions: number;
    losing_positions: number;
    total_positions: number;
    win_rate: number;
    best_position_pnl: number;
    worst_position_pnl: number;
    avg_position_pnl: number;
    total_fees_paid: number;
  };
  transaction_count: number;
}

interface Transaction {
  id: string;
  timestamp: string;
  type: string;
  amount: number;
  balance_after: number;
  position_id?: string;
  description: string;
  metadata?: any;
}

export default function WalletDashboard() {
  const [walletData, setWalletData] = useState<WalletData | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [showTransactions, setShowTransactions] = useState(false);

  const fetchWalletData = async () => {
    try {
      const [walletResponse, transactionsResponse] = await Promise.all([
        fetchWithConfig('/wallet'),
        fetchWithConfig('/wallet/transactions?limit=10')
      ]);

      const walletJson = await walletResponse.json();
      const transactionsJson = await transactionsResponse.json();

      setWalletData(walletJson);
      setTransactions(transactionsJson.transactions);
    } catch (error) {
      console.error('Error fetching wallet data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWalletData();
    const interval = setInterval(fetchWalletData, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const resetWallet = async () => {
    if (!confirm('Are you sure you want to reset the wallet? This will clear all positions and transaction history.')) {
      return;
    }

    try {
      const response = await fetchWithConfig('/wallet/reset', { method: 'POST' });
      if (response.ok) {
        await fetchWalletData();
      }
    } catch (error) {
      console.error('Error resetting wallet:', error);
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 animate-pulse">
        <div className="h-8 bg-gray-800 rounded w-48 mb-4"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="h-24 bg-gray-800 rounded"></div>
          <div className="h-24 bg-gray-800 rounded"></div>
          <div className="h-24 bg-gray-800 rounded"></div>
        </div>
      </div>
    );
  }

  if (!walletData) {
    return (
      <div className="bg-gray-900 rounded-lg p-6">
        <div className="text-center text-gray-400">
          <AlertTriangle className="w-12 h-12 mx-auto mb-2" />
          <p>Failed to load wallet data</p>
        </div>
      </div>
    );
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case 'position_entry':
        return <TrendingDown className="w-4 h-4 text-red-400" />;
      case 'position_exit':
        return <TrendingUp className="w-4 h-4 text-green-400" />;
      case 'fee':
        return <DollarSign className="w-4 h-4 text-yellow-400" />;
      default:
        return <Activity className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <div className="bg-gray-900 rounded-lg p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <Wallet className="w-8 h-8 text-blue-400" />
          <h2 className="text-2xl font-bold">Mock Wallet</h2>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchWalletData}
            className="p-2 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
          <button
            onClick={resetWallet}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
          >
            Reset Wallet
          </button>
        </div>
      </div>

      {/* Balance Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* Current Balance */}
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex justify-between items-start mb-2">
            <span className="text-gray-400 text-sm">Current Balance</span>
            <Wallet className="w-5 h-5 text-gray-500" />
          </div>
          <div className="text-2xl font-bold">{formatCurrency(walletData.balance)}</div>
          <div className={`text-sm mt-1 ${walletData.performance.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {formatPercentage(walletData.performance.total_pnl_percentage)} from start
          </div>
        </div>

        {/* Total P&L */}
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex justify-between items-start mb-2">
            <span className="text-gray-400 text-sm">Total P&L</span>
            {walletData.performance.total_pnl >= 0 ? (
              <TrendingUp className="w-5 h-5 text-green-400" />
            ) : (
              <TrendingDown className="w-5 h-5 text-red-400" />
            )}
          </div>
          <div className={`text-2xl font-bold ${walletData.performance.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {formatCurrency(walletData.performance.total_pnl)}
          </div>
          <div className="text-sm text-gray-400 mt-1">
            Win Rate: {walletData.performance.win_rate.toFixed(1)}%
          </div>
        </div>

        {/* Positions Summary */}
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex justify-between items-start mb-2">
            <span className="text-gray-400 text-sm">Positions</span>
            <Activity className="w-5 h-5 text-gray-500" />
          </div>
          <div className="text-2xl font-bold">{walletData.performance.total_positions}</div>
          <div className="text-sm text-gray-400 mt-1">
            <span className="text-green-400">{walletData.performance.winning_positions}W</span>
            {' / '}
            <span className="text-red-400">{walletData.performance.losing_positions}L</span>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <div className="bg-gray-800 rounded-lg p-3">
          <div className="text-xs text-gray-400 mb-1">Best Position</div>
          <div className={`text-lg font-semibold ${walletData.performance.best_position_pnl > 0 ? 'text-green-400' : 'text-gray-300'}`}>
            {formatCurrency(walletData.performance.best_position_pnl)}
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-3">
          <div className="text-xs text-gray-400 mb-1">Worst Position</div>
          <div className={`text-lg font-semibold ${walletData.performance.worst_position_pnl < 0 ? 'text-red-400' : 'text-gray-300'}`}>
            {formatCurrency(walletData.performance.worst_position_pnl)}
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-3">
          <div className="text-xs text-gray-400 mb-1">Avg P&L</div>
          <div className={`text-lg font-semibold ${walletData.performance.avg_position_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {formatCurrency(walletData.performance.avg_position_pnl)}
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-3">
          <div className="text-xs text-gray-400 mb-1">Total Fees</div>
          <div className="text-lg font-semibold text-yellow-400">
            {formatCurrency(walletData.performance.total_fees_paid)}
          </div>
        </div>
      </div>

      {/* Recent Transactions */}
      <div>
        <button
          onClick={() => setShowTransactions(!showTransactions)}
          className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors mb-3"
        >
          <Activity className="w-4 h-4" />
          Recent Transactions ({walletData.transaction_count})
          <span className="text-xs">{showTransactions ? '▼' : '▶'}</span>
        </button>

        {showTransactions && (
          <div className="space-y-2">
            {transactions.map((tx) => (
              <div key={tx.id} className="bg-gray-800 rounded-lg p-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {getTransactionIcon(tx.type)}
                  <div>
                    <div className="text-sm font-medium">{tx.description}</div>
                    <div className="text-xs text-gray-400">
                      {new Date(tx.timestamp).toLocaleString()}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`font-semibold ${tx.amount >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {tx.amount >= 0 ? '+' : ''}{formatCurrency(Math.abs(tx.amount))}
                  </div>
                  <div className="text-xs text-gray-400">
                    Balance: {formatCurrency(tx.balance_after)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}