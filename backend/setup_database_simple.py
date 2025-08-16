#!/usr/bin/env python3
"""
Simple database setup using subprocess to run psql
"""

import subprocess
import os
from pathlib import Path

def run_migrations():
    # Connection details
    db_url = "postgresql://postgres:PTsgRXKJImryLugsgsXfeMoTpBdFaWhv@mainline.proxy.rlwy.net:54694/railway"
    
    print("🚀 Setting up Solana Degen Hunter Database...")
    print("=" * 60)
    
    # Path to schema file
    schema_path = Path(__file__).parent / "database" / "enhanced_schema.sql"
    
    if not schema_path.exists():
        print(f"❌ Schema file not found at {schema_path}")
        return False
    
    print(f"📄 Using schema file: {schema_path}")
    
    # Create a temporary file with commands
    temp_sql = f"""
-- Connect and run schema
\\echo '🔧 Running database migrations...'
\\i {schema_path}
\\echo '✅ Migrations complete!'

-- List tables
\\echo ''
\\echo '📊 Database tables:'
\\dt

-- Count rows in important tables
\\echo ''
\\echo '🔍 Table status:'
SELECT 'pools_enhanced' as table_name, COUNT(*) as row_count FROM pools_enhanced
UNION ALL
SELECT 'pool_risk_analysis', COUNT(*) FROM pool_risk_analysis
UNION ALL
SELECT 'portfolio_positions', COUNT(*) FROM portfolio_positions
UNION ALL
SELECT 'position_snapshots', COUNT(*) FROM position_snapshots;
"""
    
    # Write temp SQL file
    temp_file = Path(__file__).parent / "temp_setup.sql"
    with open(temp_file, 'w') as f:
        f.write(temp_sql)
    
    try:
        # Run psql command
        print("\n🔄 Connecting to PostgreSQL...")
        result = subprocess.run([
            'psql',
            db_url,
            '-f', str(temp_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("\n✅ Success! Database setup complete.")
            print("\nOutput:")
            print(result.stdout)
            return True
        else:
            print("\n❌ Error running migrations:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("\n❌ psql command not found. Trying alternative method...")
        
        # Alternative: Output SQL commands for manual execution
        print("\n📋 Copy and run these commands in your PostgreSQL client:")
        print("-" * 60)
        print(f"-- 1. Connect to: {db_url}")
        print(f"-- 2. Run the schema file: {schema_path}")
        print("-- 3. Or copy the contents below:")
        print()
        
        with open(schema_path, 'r') as f:
            print(f.read())
            
        return False
        
    finally:
        # Clean up temp file
        if temp_file.exists():
            os.remove(temp_file)

if __name__ == "__main__":
    success = run_migrations()
    
    if success:
        print("\n📝 Next steps:")
        print("  1. Make sure your backend has DATABASE_URL set in Railway")
        print("  2. Redeploy your backend service")
        print("  3. Your database is now ready!")
    else:
        print("\n💡 Alternative setup methods:")
        print("  1. Use TablePlus or another PostgreSQL client")
        print("  2. Update your Railway start command to:")
        print("     cd backend && python run_migrations.py && python main.py")
        print("  3. Use Railway CLI: railway run python run_migrations.py")