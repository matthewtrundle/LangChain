'use client';

import React, { useState, useEffect } from 'react';
import { X, DollarSign, Wallet, AlertCircle } from 'lucide-react';
import { Pool } from '../lib/types';
import { fetchWithConfig } from '../lib/api';

interface PositionEntryModalProps {
  isOpen: boolean;
  onClose: () => void;
  pool: Pool;
  onSuccess: () => void;
}

export default function PositionEntryModal({ isOpen, onClose, pool, onSuccess }: PositionEntryModalProps) {
  const [amount, setAmount] = useState('100');
  const [walletBalance, setWalletBalance] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      fetchWalletBalance();
    }
  }, [isOpen]);

  const fetchWalletBalance = async () => {
    try {
      const response = await fetchWithConfig('/wallet');
      const data = await response.json();
      setWalletBalance(data.available_balance);
    } catch (err) {
      console.error('Failed to fetch wallet balance:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const entryAmount = parseFloat(amount);
    if (isNaN(entryAmount) || entryAmount <= 0) {
      setError('Please enter a valid amount');
      setLoading(false);
      return;
    }

    if (entryAmount > walletBalance) {
      setError(`Insufficient balance. Available: $${walletBalance.toFixed(2)}`);
      setLoading(false);
      return;
    }

    try {
      const response = await fetchWithConfig('/position/enter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pool_address: pool.pool_address,
          pool_data: pool,
          amount: entryAmount
        })
      });

      if (response.ok) {
        onSuccess();
        onClose();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to enter position');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const quickAmounts = [100, 250, 500, 1000];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 rounded-xl p-6 max-w-md w-full border border-gray-800">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold">Enter Position</h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Pool Info */}
        <div className="bg-gray-800 rounded-lg p-4 mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-400">Pool</span>
            <span className="font-semibold">{pool.token_symbols}</span>
          </div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-400">APY</span>
            <span className="text-green-400 font-bold">{pool.apy.toFixed(1)}%</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-400">Protocol</span>
            <span className="capitalize">{pool.protocol}</span>
          </div>
        </div>

        {/* Wallet Balance */}
        <div className="bg-blue-900/20 border border-blue-600/30 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Wallet className="w-5 h-5 text-blue-400" />
              <span className="text-sm text-gray-400">Available Balance</span>
            </div>
            <span className="text-lg font-bold text-blue-400">
              ${walletBalance.toFixed(2)}
            </span>
          </div>
        </div>

        {/* Amount Form */}
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Position Amount</label>
            <div className="relative">
              <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg py-3 pl-10 pr-4 focus:outline-none focus:border-blue-500"
                placeholder="0.00"
                step="0.01"
                min="0"
                max={walletBalance}
              />
            </div>
          </div>

          {/* Quick Amount Buttons */}
          <div className="grid grid-cols-4 gap-2 mb-6">
            {quickAmounts.map((quickAmount) => (
              <button
                key={quickAmount}
                type="button"
                onClick={() => setAmount(quickAmount.toString())}
                disabled={quickAmount > walletBalance}
                className={`py-2 rounded-lg font-medium transition-colors ${
                  quickAmount > walletBalance
                    ? 'bg-gray-800 text-gray-600 cursor-not-allowed'
                    : 'bg-gray-800 hover:bg-gray-700 text-white'
                }`}
              >
                ${quickAmount}
              </button>
            ))}
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-900/20 border border-red-600/30 rounded-lg flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-400" />
              <span className="text-sm text-red-400">{error}</span>
            </div>
          )}

          {/* Estimated Returns */}
          {amount && parseFloat(amount) > 0 && (
            <div className="bg-gray-800 rounded-lg p-4 mb-6">
              <h4 className="text-sm font-medium text-gray-400 mb-2">Estimated Daily Returns</h4>
              <div className="text-2xl font-bold text-green-400">
                ${((parseFloat(amount) * pool.apy / 100) / 365).toFixed(2)}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Based on current {pool.apy.toFixed(1)}% APY
              </div>
            </div>
          )}

          {/* Submit Buttons */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-3 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || parseFloat(amount) <= 0 || parseFloat(amount) > walletBalance}
              className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Entering...' : 'Enter Position'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}