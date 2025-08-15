#!/usr/bin/env python3
"""
Database setup script for Position Tracking system
Run this to initialize your PostgreSQL database with required tables
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from database.connection import db, test_connection

async def setup_database():
    """Initialize database with schema"""
    print("🚀 Setting up Position Tracking Database...")
    
    # Test connection
    print("\n1. Testing database connection...")
    connected = await test_connection()
    if not connected:
        print("❌ Failed to connect to database. Check your DATABASE_URL")
        return False
    
    print("✅ Database connection successful")
    
    # Read schema file
    print("\n2. Loading schema...")
    schema_path = Path(__file__).parent / "database" / "schema.sql"
    
    if not schema_path.exists():
        print(f"❌ Schema file not found at {schema_path}")
        return False
    
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # Execute schema
    print("\n3. Creating tables...")
    try:
        # Split by semicolons and execute each statement
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
        
        for i, statement in enumerate(statements):
            if statement:
                print(f"   Executing statement {i+1}/{len(statements)}...")
                await db.execute(statement)
        
        print("✅ All tables created successfully")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    # Verify tables exist
    print("\n4. Verifying tables...")
    tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """
    
    tables = await db.fetch(tables_query)
    print(f"\n📊 Created {len(tables)} tables:")
    for table in tables:
        print(f"   - {table['table_name']}")
    
    print("\n✅ Database setup complete!")
    return True

async def create_sample_data():
    """Create sample positions for testing"""
    print("\n📝 Creating sample data...")
    
    # Sample position
    query = """
        INSERT INTO positions (
            user_wallet, pool_address, protocol,
            entry_timestamp, entry_price_a, entry_price_b,
            entry_amount_a, entry_amount_b, entry_lp_tokens,
            entry_tx_hash, entry_value_usd,
            token_a_symbol, token_b_symbol,
            token_a_mint, token_b_mint,
            status, current_amount_a, current_amount_b
        ) VALUES (
            $1, $2, $3, NOW(), $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17
        ) RETURNING id;
    """
    
    try:
        position_id = await db.fetchval(
            query,
            'DemoWallet111111111111111111111111111111111',
            '7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU',
            'raydium',
            0.00001234,  # BONK price
            1.00,        # USDC price
            1000000,     # 1M BONK
            12.34,       # 12.34 USDC
            100.5,       # LP tokens
            'DemoTxHash111111111111111111111111111111111111111111111111111111111111111111',
            24.68,       # Total value
            'BONK', 'USDC',
            'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
            'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
            'ACTIVE',
            1000000,     # Current amounts
            12.34
        )
        
        print(f"✅ Created sample position: {position_id}")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")

async def main():
    """Main setup function"""
    load_dotenv()
    
    # Check if DATABASE_URL is set
    if not os.getenv('DATABASE_URL'):
        print("❌ DATABASE_URL not found in environment variables")
        print("   Please set it in your .env file or as an environment variable")
        return
    
    try:
        # Initialize connection pool
        await db.init_pool()
        
        # Setup database
        success = await setup_database()
        
        if success and '--create-samples' in sys.argv:
            await create_sample_data()
        
    finally:
        # Close connection pool
        await db.close_pool()

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════╗
    ║   Solana Degen Hunter - Database Setup    ║
    ╚═══════════════════════════════════════════╝
    """)
    
    asyncio.run(main())