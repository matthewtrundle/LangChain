import os
from typing import Optional
import asyncpg
from asyncpg import Pool, Connection
import asyncio
from contextlib import asynccontextmanager

class DatabaseConnection:
    """PostgreSQL connection manager for Railway"""
    
    def __init__(self):
        self.pool: Optional[Pool] = None
        self.database_url = os.getenv('DATABASE_URL')
        
        if not self.database_url:
            # Local development fallback
            self.database_url = "postgresql://postgres:password@localhost:5432/soldegen"
            print("[DB] Warning: Using local database URL")
    
    async def init_pool(self):
        """Initialize connection pool"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            print(f"[DB] Connection pool initialized")
    
    async def close_pool(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            print("[DB] Connection pool closed")
    
    @asynccontextmanager
    async def acquire(self):
        """Acquire a connection from the pool"""
        if not self.pool:
            await self.init_pool()
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def execute(self, query: str, *args):
        """Execute a query without returning results"""
        async with self.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        """Fetch multiple rows"""
        async with self.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """Fetch a single row"""
        async with self.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """Fetch a single value"""
        async with self.acquire() as conn:
            return await conn.fetchval(query, *args)

# Global database instance
db = DatabaseConnection()

# Function for direct connection (used by risk analysis service)
async def get_db_connection():
    """Get a direct database connection"""
    if not db.database_url:
        raise ValueError("DATABASE_URL not configured")
    
    conn = await asyncpg.connect(db.database_url)
    return conn

# Helper function to test connection
async def test_connection():
    """Test database connection"""
    try:
        version = await db.fetchval('SELECT version()')
        print(f"[DB] Connected to PostgreSQL: {version}")
        return True
    except Exception as e:
        print(f"[DB] Connection failed: {e}")
        return False