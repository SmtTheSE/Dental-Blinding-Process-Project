import os
import logging
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from models import db, User
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import secrets
import time

# Load environment variables from .env file
load_dotenv()

def get_database_uri():
    """Get database URI with proper SSL configuration for Supabase"""
    database_url = os.environ.get('SUPABASE_DB_URL') or os.environ.get('DATABASE_URL')
    if database_url:
        # Handle Supabase database URL with proper SSL configuration
        if 'postgresql://' in database_url and '?' not in database_url:
            database_url += '?sslmode=require'
        return database_url
    else:
        # Default to localhost for development
        return 'postgresql://sittminthar@localhost:5432/dental_scheduler'

def generate_secure_password(length=12):
    """Generate a secure random password"""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def update_user_table():
    """Add new columns to existing user table if they don't exist"""
    # This function should be called within an app context
    # Check if the columns exist, if not add them
    from sqlalchemy import text
    
    try:
        # Check if failed_attempts column exists
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user' AND column_name = 'failed_attempts'
        """))
        
        if not result.fetchone():
            # Add failed_attempts column
            db.session.execute(text("ALTER TABLE \"user\" ADD COLUMN failed_attempts INTEGER DEFAULT 0"))
        
        # Check if last_login column exists
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user' AND column_name = 'last_login'
        """))
        
        if not result.fetchone():
            # Add last_login column
            db.session.execute(text("ALTER TABLE \"user\" ADD COLUMN last_login TIMESTAMP"))
            
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

def update_patient_table():
    """Update patient table structure if needed"""
    # This function should be called within an app context
    from sqlalchemy import text
    
    try:
        # Check the current size of the opg_link column
        result = db.session.execute(text("""
            SELECT character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'patient' AND column_name = 'opg_link'
        """)).fetchone()
        
        if result and result[0] < 500:
            # Increase the size of opg_link column to accommodate Supabase signed URLs
            db.session.execute(text("ALTER TABLE patient ALTER COLUMN opg_link TYPE VARCHAR(500)"))
            
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

def create_indexes():
    """Create database indexes for better performance"""
    # This function should be called within an app context
    try:
        # Create indexes on frequently queried columns
        from sqlalchemy import text
        
        # Index on patient_id for faster lookups
        db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_patient_patient_id ON patient (patient_id)"))
        
        # Index on code_a and code_b for faster blinded data queries
        db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_patient_code_a ON patient (code_a)"))
        db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_patient_code_b ON patient (code_b)"))
        
        # Index on estimation entry codes
        db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_estimation_entry_code ON estimation_entry (code)"))
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

def init_db(app=None):
    """Initialize the database with proper connection handling"""
    start_time = time.time()
    
    try:
        if app:
            # Use the app's database configuration
            database_uri = app.config['SQLALCHEMY_DATABASE_URI']
            engine_options = app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {})
        else:
            # Use direct configuration
            database_uri = get_database_uri()
            engine_options = {
                'pool_pre_ping': True,
                'pool_recycle': 300,
                'pool_timeout': 20
            }
        
        # Log the database URI being used (without credentials)
        safe_uri = database_uri.split('@')[-1] if '@' in database_uri else database_uri
        logging.info(f"Database URI being used: {safe_uri}")
        
        if 'localhost' in database_uri or '127.0.0.1' in database_uri:
            logging.warning("WARNING: Using localhost database URI. This will not work in production!")
            logging.warning("Make sure SUPABASE_DB_URL environment variable is set.")
        
        # Create engine with connection options
        engine = create_engine(database_uri, **engine_options)
        
        # Test the connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        # Initialize tables
        if app:
            from app import create_app
            app_to_use = app or create_app('production')
            with app_to_use.app_context():
                db.create_all()
                logging.info("Database tables created")
                
                # Check and update user table structure
                update_user_table()
                logging.info("User table structure updated")
                
                # Check and update patient table structure
                update_patient_table()
                logging.info("Patient table structure updated")
                
                # Create indexes
                create_indexes()
                logging.info("Database indexes created")
        else:
            # For standalone usage
            db.create_all()
            logging.info("Database tables created")
            
            # Check and update user table structure
            update_user_table()
            logging.info("User table structure updated")
            
            # Check and update patient table structure
            update_patient_table()
            logging.info("Patient table structure updated")
            
            # Create indexes
            create_indexes()
            logging.info("Database indexes created")
            
        # Create default users if they don't exist
        supervisor = User.query.filter_by(username='supervisor').first()
        if not supervisor:
            supervisor_password = os.environ.get('SUPERVISOR_PASSWORD') or 'Dental@2026'
            supervisor = User(
                username='supervisor',
                password=generate_password_hash(supervisor_password),
                role='supervisor'
            )
            db.session.add(supervisor)
            logging.info(f"Created supervisor user with default password")
        
        pi = User.query.filter_by(username='pi').first()
        if not pi:
            pi_password = os.environ.get('PI_PASSWORD') or 'Dental@2026'
            pi = User(
                username='pi',
                password=generate_password_hash(pi_password),
                role='pi'
            )
            db.session.add(pi)
            logging.info(f"Created PI user with default password")
        
        db.session.commit()
        
        elapsed_time = time.time() - start_time
        logging.info(f"Database initialized successfully in {elapsed_time:.2f} seconds")
        return True
        
    except OperationalError as e:
        if "SSL error" in str(e):
            logging.error("SSL connection error. Trying to reconnect with different SSL settings...")
            # Try with different SSL mode
            if '?' in database_uri:
                alt_uri = database_uri.split('?')[0] + '?sslmode=prefer'
            else:
                alt_uri = database_uri + '?sslmode=prefer'
            
            try:
                engine = create_engine(alt_uri, **engine_options)
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    result.fetchone()
                logging.info("Successfully connected with alternative SSL settings")
                return True
            except Exception as alt_e:
                logging.error(f"Alternative connection also failed: {alt_e}")
                return False
        else:
            logging.error(f"Database connection failed: {e}")
            return False
    except Exception as e:
        logging.error(f"Unexpected error during database initialization: {e}")
        return False

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # Create Flask app for database initialization
    from app import create_app
    app = create_app('production')
    
    # Initialize database within app context
    with app.app_context():
        success = init_db(app)
        if success:
            print("\n" + "=" * 60)
            print("✅ DATABASE INITIALIZED SUCCESSFULLY!")
            print("=" * 60)
            print("\nDefault accounts created:")
            print("  - Username: supervisor | Password: Dental@2026")
            print("  - Username: pi         | Password: Dental@2026")
            print("\nYou can now run the application with: python run.py")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ DATABASE INITIALIZATION FAILED!")
            print("=" * 60)
            sys.exit(1)