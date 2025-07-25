#!/usr/bin/env python3
"""
Test script to demonstrate the mock wallet functionality
"""

import asyncio
import random
from services.wallet_service import wallet_service
from services.position_manager import position_manager
from models.position import ExitReason

async def run_wallet_demo():
    print("🏦 SOLANA DEGEN HUNTER - WALLET DEMO")
    print("=" * 50)
    
    # Show initial wallet state
    balance = wallet_service.get_balance()
    print(f"\n💰 Starting Balance: ${balance:,.2f}")
    
    # Simulate some trading activity
    test_pools = [
        {
            "pool_address": "11111111111111111111111111111111",
            "token_symbols": "BONK/SOL",
            "apy": 850.5,
            "tvl": 125000,
            "volume_24h": 45000
        },
        {
            "pool_address": "22222222222222222222222222222222",
            "token_symbols": "WIF/USDC",
            "apy": 1250.0,
            "tvl": 85000,
            "volume_24h": 32000
        },
        {
            "pool_address": "33333333333333333333333333333333",
            "token_symbols": "PEPE/SOL",
            "apy": 420.69,
            "tvl": 250000,
            "volume_24h": 125000
        }
    ]
    
    print("\n📊 Entering Positions:")
    print("-" * 50)
    
    positions = []
    for i, pool in enumerate(test_pools):
        amount = random.choice([100, 250, 500])
        
        # Check if we can afford it
        if wallet_service.can_afford(amount):
            position = position_manager.enter_position(pool, amount)
            positions.append(position)
            print(f"✅ Entered ${amount} in {pool['token_symbols']} at {pool['apy']}% APY")
            await asyncio.sleep(0.5)  # Small delay for effect
        else:
            print(f"❌ Insufficient funds for ${amount} position")
    
    # Show wallet after entries
    balance = wallet_service.get_balance()
    print(f"\n💰 Balance after entries: ${balance:,.2f}")
    
    # Simulate some time passing and P&L
    print("\n⏰ Simulating 24 hours of trading...")
    await asyncio.sleep(1)
    
    # Update positions with random P&L
    for _ in range(3):
        position_manager.simulate_position_updates()
        await asyncio.sleep(0.5)
    
    # Exit some positions
    print("\n📤 Exiting Positions:")
    print("-" * 50)
    
    # Exit first position with profit
    if positions:
        pos = positions[0]
        pos.current_value = pos.entry_amount * 1.25  # 25% profit
        pos.pnl_amount = pos.current_value - pos.entry_amount
        pos.pnl_percent = 25.0
        exited = position_manager.exit_position(pos.id, ExitReason.TAKE_PROFIT)
        print(f"✅ Exited {pos.pool_data['token_symbols']} with +{exited.pnl_percent:.1f}% profit")
    
    # Exit second position with loss
    if len(positions) > 1:
        pos = positions[1]
        pos.current_value = pos.entry_amount * 0.85  # 15% loss
        pos.pnl_amount = pos.current_value - pos.entry_amount
        pos.pnl_percent = -15.0
        exited = position_manager.exit_position(pos.id, ExitReason.STOP_LOSS)
        print(f"❌ Exited {pos.pool_data['token_symbols']} with {exited.pnl_percent:.1f}% loss")
    
    # Show final wallet state
    print("\n📊 FINAL WALLET SUMMARY")
    print("=" * 50)
    
    balance = wallet_service.get_balance()
    metrics = wallet_service.get_performance_metrics()
    
    print(f"💰 Final Balance: ${balance:,.2f}")
    print(f"📈 Total P&L: ${metrics['total_pnl']:,.2f} ({metrics['total_pnl_percent']:.1f}%)")
    print(f"🎯 Win Rate: {metrics['win_rate']:.1f}%")
    print(f"📊 Positions: {metrics['total_positions']} total, {metrics['winning_positions']} wins")
    print(f"💸 Total Fees: ${metrics['total_fees']:,.2f}")
    
    # Show recent transactions
    print("\n📜 Recent Transactions:")
    print("-" * 50)
    transactions = wallet_service.get_transactions(limit=5)
    for tx in transactions:
        emoji = "🟢" if tx['amount'] > 0 else "🔴"
        print(f"{emoji} {tx['type']}: ${abs(tx['amount']):,.2f} - {tx['description']}")
    
    print("\n✨ Demo Complete!")

if __name__ == "__main__":
    asyncio.run(run_wallet_demo())