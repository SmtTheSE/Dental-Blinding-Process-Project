#!/usr/bin/env python3
"""
Test Supabase CRUD Operations

This script tests Create, Read, Update, and Delete operations
on the Supabase PostgreSQL database.
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Load environment variables
load_dotenv()

def test_crud_operations():
    """Test CRUD operations on the database"""
    
    print("=" * 60)
    print("SUPABASE CRUD OPERATIONS TEST")
    print("=" * 60)
    
    # Get database URL
    database_url = os.environ.get('SUPABASE_DB_URL')
    
    if not database_url:
        print("❌ ERROR: SUPABASE_DB_URL environment variable is not set!")
        return False
    
    # Add SSL mode if not present
    if '?' not in database_url:
        database_url += '?sslmode=require'
    
    try:
        # Create engine and session
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_timeout=20
        )
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Test patient ID for CRUD operations
        test_patient_id = f"TEST_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        print("\n1️⃣  CREATE TEST")
        print("-" * 60)
        
        # Create a test patient
        create_query = text("""
            INSERT INTO patient (patient_id, name, actual_age, sex, created_at)
            VALUES (:patient_id, :name, :age, :sex, :created_at)
            RETURNING id, patient_id, name
        """)
        
        result = session.execute(create_query, {
            'patient_id': test_patient_id,
            'name': 'Test Patient',
            'age': 25.5,
            'sex': 'male',
            'created_at': datetime.utcnow()
        })
        
        created = result.fetchone()
        session.commit()
        
        print(f"✅ Created patient:")
        print(f"   ID: {created[0]}")
        print(f"   Patient ID: {created[1]}")
        print(f"   Name: {created[2]}")
        
        # Store the database ID for later operations
        db_id = created[0]
        
        print("\n2️⃣  READ TEST")
        print("-" * 60)
        
        # Read the patient
        read_query = text("""
            SELECT id, patient_id, name, actual_age, sex
            FROM patient
            WHERE patient_id = :patient_id
        """)
        
        result = session.execute(read_query, {'patient_id': test_patient_id})
        patient = result.fetchone()
        
        print(f"✅ Read patient:")
        print(f"   ID: {patient[0]}")
        print(f"   Patient ID: {patient[1]}")
        print(f"   Name: {patient[2]}")
        print(f"   Age: {patient[3]}")
        print(f"   Sex: {patient[4]}")
        
        print("\n3️⃣  UPDATE TEST")
        print("-" * 60)
        
        # Update the patient
        update_query = text("""
            UPDATE patient
            SET name = :name, actual_age = :age
            WHERE patient_id = :patient_id
            RETURNING id, name, actual_age
        """)
        
        result = session.execute(update_query, {
            'patient_id': test_patient_id,
            'name': 'Updated Test Patient',
            'age': 26.0
        })
        
        updated = result.fetchone()
        session.commit()
        
        print(f"✅ Updated patient:")
        print(f"   ID: {updated[0]}")
        print(f"   Name: {updated[1]}")
        print(f"   Age: {updated[2]}")
        
        print("\n4️⃣  DELETE TEST")
        print("-" * 60)
        
        # Delete the patient
        delete_query = text("""
            DELETE FROM patient
            WHERE patient_id = :patient_id
            RETURNING patient_id
        """)
        
        result = session.execute(delete_query, {'patient_id': test_patient_id})
        deleted = result.fetchone()
        session.commit()
        
        print(f"✅ Deleted patient: {deleted[0]}")
        
        # Verify deletion
        verify_query = text("""
            SELECT COUNT(*) FROM patient WHERE patient_id = :patient_id
        """)
        
        result = session.execute(verify_query, {'patient_id': test_patient_id})
        count = result.fetchone()[0]
        
        if count == 0:
            print(f"✅ Verified: Patient no longer exists in database")
        else:
            print(f"❌ ERROR: Patient still exists after deletion!")
            return False
        
        session.close()
        
        print("\n" + "=" * 60)
        print("✅ ALL CRUD TESTS PASSED!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ CRUD test failed!")
        print(f"\nError: {str(e)}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return False

if __name__ == '__main__':
    success = test_crud_operations()
    sys.exit(0 if success else 1)
