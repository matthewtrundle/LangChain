#!/usr/bin/env python3
"""
Test script for Position Tracking system
Tests all core functionality without needing the API
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from database.connection import db
from services.position_manager import position_manager
from services.price_oracle import price_oracle
from services.pnl_calculator import PnLCalculator

async def test_price_oracle():
    """Test price oracle functionality"""
    print("\n🔍 Testing Price Oracle...")
    
    # Test SOL price
    sol_price = await price_oracle.get_token_price(price_oracle.TOKENS["SOL"])
    print(f"   SOL Price: ${sol_price:.2f}")
    
    # Test multiple tokens
    tokens = ["SOL", "USDC", "BONK"]
    mints = [price_oracle.TOKENS[t] for t in tokens]
    prices = await price_oracle.get_token_prices(mints)
    
    print("   Token Prices:")
    for token, mint in zip(tokens, mints):
        price = prices.get(mint, 0)
        print(f"   - {token}: ${price:.6f}")
    
    return prices

async def test_pnl_calculator():
    """Test P&L calculations"""
    print("\n💰 Testing P&L Calculator...")
    
    calculator = PnLCalculator()
    
    # Example: SOL-USDC position
    # Entry: 10 SOL @ $100, 1000 USDC @ $1
    # Current: SOL @ $120, USDC @ $1
    
    pnl_result = calculator.calculate_net_pnl(
        entry_price_a=100,      # SOL was $100
        entry_price_b=1,        # USDC was $1
        current_price_a=120,    # SOL now $120
        current_price_b=1,      # USDC still $1
        entry_amount_a=10,      # 10 SOL
        entry_amount_b=1000,    # 1000 USDC
        fees_earned_a=0.1,      # Earned 0.1 SOL in fees
        fees_earned_b=10,       # Earned 10 USDC in fees
        current_apy=250         # Current APY 250%
    )
    
    print(f"   Initial Value: ${pnl_result.initial_value_usd:,.2f}")
    print(f"   Current Value: ${pnl_result.current_value_usd:,.2f}")
    print(f"   Impermanent Loss: {pnl_result.impermanent_loss_percent:.2f}% (${pnl_result.impermanent_loss_usd:,.2f})")
    print(f"   Fees Earned: ${pnl_result.fees_earned_usd:,.2f}")
    print(f"   Net P&L: {pnl_result.net_pnl_percent:.2f}% (${pnl_result.net_pnl_usd:,.2f})")

async def test_position_entry():
    """Test entering a new position"""
    print("\n📥 Testing Position Entry...")
    
    try:
        position = await position_manager.enter_position(
            wallet="TestWallet" + datetime.now().strftime("%Y%m%d%H%M%S"),
            pool_address="TestPool123",
            protocol="raydium",
            token_a_symbol="SOL",
            token_b_symbol="USDC",
            token_a_mint=price_oracle.TOKENS["SOL"],
            token_b_mint=price_oracle.TOKENS["USDC"],
            amount_a=1.5,
            amount_b=150,
            lp_tokens=15,
            tx_hash="TestTx" + datetime.now().strftime("%Y%m%d%H%M%S")
        )
        
        print(f"   ✅ Created position: {position.id}")
        print(f"   Pair: {position.pair_name}")
        print(f"   Entry Value: ${position.entry_value_usd}")
        
        return position
        
    except Exception as e:
        print(f"   ❌ Error creating position: {e}")
        return None

async def test_position_sync(position_id: str):
    """Test syncing a position"""
    print("\n🔄 Testing Position Sync...")
    
    try:
        # Wait a bit to simulate time passing
        await asyncio.sleep(2)
        
        synced = await position_manager.sync_position(position_id)
        if synced:
            print(f"   ✅ Synced position: {position_id}")
            print(f"   Fees earned: {synced.fees_earned_a} {synced.token_a_symbol}, {synced.fees_earned_b} {synced.token_b_symbol}")
        else:
            print(f"   ❌ Failed to sync position")
            
    except Exception as e:
        print(f"   ❌ Error syncing position: {e}")

async def test_portfolio_summary(wallet: str):
    """Test portfolio summary"""
    print("\n📊 Testing Portfolio Summary...")
    
    try:
        summary = await position_manager.calculate_portfolio_summary(wallet)
        
        print(f"   Total Positions: {summary['total_positions']}")
        print(f"   Total Value: ${summary['total_value_usd']:,.2f}")
        print(f"   Total P&L: ${summary['total_pnl_usd']:,.2f} ({summary['total_pnl_percent']:.2f}%)")
        print(f"   Total Fees: ${summary['total_fees_earned_usd']:,.2f}")
        
    except Exception as e:
        print(f"   ❌ Error getting portfolio summary: {e}")

async def test_position_exit(position_id: str):
    """Test exiting a position"""
    print("\n📤 Testing Position Exit...")
    
    try:
        exited = await position_manager.exit_position(
            position_id=position_id,
            tx_hash="ExitTx" + datetime.now().strftime("%Y%m%d%H%M%S")
        )
        
        if exited:
            print(f"   ✅ Exited position: {position_id}")
            print(f"   Exit Value: ${exited.exit_value_usd}")
            print(f"   Status: {exited.status.value}")
        else:
            print(f"   ❌ Failed to exit position")
            
    except Exception as e:
        print(f"   ❌ Error exiting position: {e}")

async def main():
    """Run all tests"""
    load_dotenv()
    
    # Check environment
    if not os.getenv('DATABASE_URL'):
        print("❌ DATABASE_URL not set. Please configure your .env file")
        return
    
    if not os.getenv('HELIUS_API_KEY'):
        print("⚠️  HELIUS_API_KEY not set. Price feeds may not work")
    
    try:
        # Initialize database connection
        await db.init_pool()
        
        # Run tests
        await test_price_oracle()
        await test_pnl_calculator()
        
        # Test with real position
        position = await test_position_entry()
        
        if position:
            await test_position_sync(position.id)
            await test_portfolio_summary(position.user_wallet)
            
            # Optionally test exit
            if input("\n❓ Test position exit? (y/n): ").lower() == 'y':
                await test_position_exit(position.id)
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        
    finally:
        # Close database connection
        await db.close_pool()

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════╗
    ║  Position Tracking System - Test Suite     ║
    ╚════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())