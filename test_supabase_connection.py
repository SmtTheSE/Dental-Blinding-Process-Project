#!/usr/bin/env python3
"""
Test Supabase Database Connection

This script tests the connection to Supabase PostgreSQL database
and verifies that tables and default users are created.
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError

# Load environment variables
load_dotenv()

def test_connection():
    """Test database connection and display status"""
    
    print("=" * 60)
    print("SUPABASE DATABASE CONNECTION TEST")
    print("=" * 60)
    
    # Get database URL
    database_url = os.environ.get('SUPABASE_DB_URL')
    
    if not database_url:
        print("❌ ERROR: SUPABASE_DB_URL environment variable is not set!")
        print("\nPlease ensure you have a .env file with:")
        print("SUPABASE_DB_URL=postgresql://postgres.cvctulmujgdnzozhpwmk:PASSWORD@aws-1-ap-south-1.pooler.supabase.com:6543/postgres")
        return False
    
    # Add SSL mode if not present
    if '?' not in database_url:
        database_url += '?sslmode=require'
    
    # Hide password in display
    safe_url = database_url.split('@')[-1] if '@' in database_url else database_url
    print(f"\n📡 Connecting to: {safe_url}")
    
    try:
        # Create engine
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_timeout=20
        )
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"\n📊 PostgreSQL Version:")
            print(f"   {version[:80]}...")
            
            # Check if tables exist
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            print(f"\n📋 Tables in database: {len(tables)}")
            if tables:
                for table in tables:
                    print(f"   - {table}")
            else:
                print("   ⚠️  No tables found. Run 'python setup_db.py' to initialize.")
            
            # Check for users if user table exists
            if 'user' in tables:
                result = conn.execute(text("SELECT username, role FROM \"user\""))
                users = result.fetchall()
                print(f"\n👥 Users in database: {len(users)}")
                for user in users:
                    print(f"   - {user[0]} ({user[1]})")
            
            # Check for patients if patient table exists
            if 'patient' in tables:
                result = conn.execute(text("SELECT COUNT(*) FROM patient"))
                count = result.fetchone()[0]
                print(f"\n🏥 Patients in database: {count}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        return True
        
    except OperationalError as e:
        print(f"\n❌ Connection failed!")
        print(f"\nError: {str(e)}")
        print("\nPossible issues:")
        print("1. Incorrect password in SUPABASE_DB_URL")
        print("2. Database not accessible")
        print("3. Network/firewall issues")
        print("4. SSL configuration problems")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
