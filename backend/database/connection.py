import os
from typing import Optional
import asyncpg
from asyncpg import Pool, Connection
import asyncio
from contextlib import asynccontextmanager

# Store DATABASE_URL immediately when module loads
_CACHED_DATABASE_URL = os.environ.get('DATABASE_URL')

class DatabaseConnection:
    """PostgreSQL connection manager for Railway"""
    
    def __init__(self):
        self.pool: Optional[Pool] = None
        # Debug: Print environment info
        print(f"[DB] RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT', 'not set')}")
        print(f"[DB] Environment keys count: {len(os.environ)}")
        
        # Try multiple sources for DATABASE_URL
        self._database_url = (
            os.environ.get('DATABASE_URL') or 
            _CACHED_DATABASE_URL or
            os.getenv('DATABASE_URL')
        )
        
        if self._database_url:
            print(f"[DB] Found DATABASE_URL: {self._database_url[:30]}...")
            # Handle Railway's internal vs public URL format if needed
            if "railway.internal" in self._database_url and os.environ.get('RAILWAY_ENVIRONMENT'):
                # Railway internal URLs don't work from local connections
                print(f"[DB] Detected Railway internal URL, keeping as-is for production")
        else:
            print(f"[DB] DATABASE_URL not found in environment")
            print(f"[DB] First 10 env keys: {list(os.environ.keys())[:10]}")
            print(f"[DB] Using fallback database URL")
            self._database_url = "postgresql://postgres:password@localhost:5432/soldegen"
    
    @property
    def database_url(self) -> str:
        """Get database URL"""
        return self._database_url
    
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