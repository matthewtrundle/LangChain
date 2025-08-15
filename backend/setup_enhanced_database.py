"""
Setup Enhanced Database Tables
Run this to add the new tables for risk analysis and portfolio tracking
"""

import asyncio
import os
from database.connection import get_db_connection

async def setup_enhanced_tables():
    """Create new tables for enhanced features"""
    conn = await get_db_connection()
    
    try:
        # Read the enhanced schema
        with open('database/enhanced_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        print("Creating enhanced tables...")
        
        # Execute the schema
        await conn.execute(schema_sql)
        
        print("✅ Successfully created:")
        print("  - pools_enhanced (enhanced pool data)")
        print("  - pool_risk_analysis (auto risk scoring)")
        print("  - positions_enhanced (detailed position tracking)")
        print("  - position_snapshots_hf (P&L history)")
        print("  - portfolio_history (portfolio performance)")
        print("  - Materialized views for analytics")
        
        # Check what tables exist
        tables = await conn.fetch("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename;
        """)
        
        print("\n📊 All tables in database:")
        for table in tables:
            print(f"  - {table['tablename']}")
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("\nIf tables already exist, that's OK!")
    finally:
        await conn.close()

if __name__ == "__main__":
    print("🚀 Setting up enhanced database tables...")
    print(f"📍 Using database: {os.getenv('DATABASE_URL', 'Not set!')}")
    asyncio.run(setup_enhanced_tables())