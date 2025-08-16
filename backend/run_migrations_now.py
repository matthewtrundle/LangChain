#!/usr/bin/env python3
"""
Direct migration runner using provided credentials
"""

import asyncio
import asyncpg
from pathlib import Path

async def run_migrations_direct():
    # Using the public URL for external connection
    database_url = "postgresql://postgres:PTsgRXKJImryLugsgsXfeMoTpBdFaWhv@mainline.proxy.rlwy.net:54694/railway"
    
    print("🚀 Connecting to Railway PostgreSQL...")
    print("=" * 60)
    
    try:
        # Connect to database
        conn = await asyncpg.connect(database_url)
        print("✅ Connected successfully!")
        
        # Get PostgreSQL version
        version = await conn.fetchval('SELECT version()')
        print(f"📊 Database: {version.split(',')[0]}")
        
        # Read the enhanced schema
        schema_path = Path(__file__).parent / "database" / "enhanced_schema.sql"
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        print("\n🔧 Running migrations...")
        print("-" * 60)
        
        # Execute the schema
        await conn.execute(schema_sql)
        
        print("\n✅ All migrations completed successfully!")
        
        # List all tables
        tables = await conn.fetch("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename
        """)
        
        print(f"\n📊 Created/Updated {len(tables)} tables:")
        for table in tables:
            # Get row count for each table
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table['tablename']}")
            print(f"  ✅ {table['tablename']:<30} ({count} rows)")
        
        # Check specific important tables
        print("\n🔍 Verifying critical tables:")
        critical_tables = [
            ('pools_enhanced', 'Pool discovery and tracking'),
            ('pool_risk_analysis', 'Risk analysis results'),
            ('portfolio_positions', 'Active trading positions'),
            ('position_snapshots', 'P&L tracking over time'),
            ('alerts', 'Price and APY alerts'),
            ('trading_strategies', 'Bot trading configurations')
        ]
        
        for table_name, description in critical_tables:
            exists = await conn.fetchval(f"""
                SELECT EXISTS (
                    SELECT FROM pg_tables 
                    WHERE schemaname = 'public' 
                    AND tablename = '{table_name}'
                )
            """)
            status = "✅" if exists else "❌"
            print(f"  {status} {table_name:<25} - {description}")
        
        await conn.close()
        print("\n🎉 Database setup complete! Your backend can now connect.")
        print("\n📝 Next steps:")
        print("  1. Ensure your backend service has DATABASE_URL variable")
        print("  2. Redeploy your backend service")
        print("  3. Check logs to confirm connection")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔍 Troubleshooting:")
        print("  - Check if PostgreSQL service is running in Railway")
        print("  - Verify credentials haven't changed")
        print("  - Ensure your IP isn't blocked (unlikely)")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_migrations_direct())
    exit(0 if success else 1)