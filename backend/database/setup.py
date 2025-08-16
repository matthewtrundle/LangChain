"""
Database Setup and Migration Script
Runs the full enhanced schema for production use
"""

import asyncio
import asyncpg
import os
from pathlib import Path

async def run_migrations():
    """Run all database migrations"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        database_url = "postgresql://postgres:password@localhost:5432/soldegen"
        print("[DB Setup] Warning: Using local database URL")
    
    print(f"[DB Setup] Connecting to database...")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(database_url)
        
        # Read the enhanced schema
        schema_path = Path(__file__).parent / "enhanced_schema.sql"
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        print("[DB Setup] Running migrations...")
        
        # Execute the schema
        await conn.execute(schema_sql)
        
        print("✅ Database tables created successfully!")
        
        # Verify tables were created
        tables = await conn.fetch("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename
        """)
        
        print(f"\n📊 Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table['tablename']}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

async def verify_connection():
    """Verify database connection and tables"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        database_url = "postgresql://postgres:password@localhost:5432/soldegen"
    
    try:
        conn = await asyncpg.connect(database_url)
        
        # Check PostgreSQL version
        version = await conn.fetchval('SELECT version()')
        print(f"✅ Connected to: {version.split(',')[0]}")
        
        # Count tables
        table_count = await conn.fetchval("""
            SELECT COUNT(*) FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        print(f"📊 Found {table_count} tables in database")
        
        # Check specific important tables
        important_tables = [
            'pools_enhanced',
            'pool_risk_analysis', 
            'portfolio_positions',
            'position_snapshots'
        ]
        
        for table in important_tables:
            exists = await conn.fetchval(f"""
                SELECT EXISTS (
                    SELECT FROM pg_tables 
                    WHERE schemaname = 'public' 
                    AND tablename = '{table}'
                )
            """)
            status = "✅" if exists else "❌"
            print(f"{status} Table '{table}': {'exists' if exists else 'missing'}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection verification failed: {e}")
        return False

if __name__ == "__main__":
    # Run migrations when executed directly
    asyncio.run(run_migrations())
    print("\nVerifying setup...")
    asyncio.run(verify_connection())