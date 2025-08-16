#!/usr/bin/env python3
"""
Quick migration runner for Railway deployment
Run this to set up your database tables
"""

import asyncio
from database.setup import run_migrations, verify_connection

async def main():
    print("🚀 Starting PostgreSQL setup for Solana Degen Hunter...")
    print("=" * 50)
    
    # Run migrations
    success = await run_migrations()
    
    if success:
        print("\n✅ Success! Database is ready.")
        print("\n🔍 Verifying setup...")
        await verify_connection()
    else:
        print("\n❌ Migration failed. Check the error messages above.")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())