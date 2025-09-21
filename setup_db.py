import os
import logging
import time
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash
import secrets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_secure_password(length=12):
    """Generate a secure random password"""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def update_user_table():
    """Add new columns to existing user table if they don't exist"""
    start_time = time.time()
    logger.info("Starting user table update")
    
    try:
        # This function should be called within an app context
        # Check if the columns exist, if not add them
        from sqlalchemy import text
        
        # Check if failed_attempts column exists
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user' AND column_name = 'failed_attempts'
        """))
        
        if not result.fetchone():
            # Add failed_attempts column
            alter_table_sql = text("ALTER TABLE \"user\" ADD COLUMN failed_attempts INTEGER DEFAULT 0")
            db.session.execute(alter_table_sql)
            logger.info("Added failed_attempts column to user table")
        
        # Check if last_login column exists
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user' AND column_name = 'last_login'
        """))
        
        if not result.fetchone():
            # Add last_login column
            alter_table_sql = text("ALTER TABLE \"user\" ADD COLUMN last_login TIMESTAMP")
            db.session.execute(alter_table_sql)
            logger.info("Added last_login column to user table")
            
        db.session.commit()
        logger.info(f"Successfully completed user table update in {time.time() - start_time:.2f} seconds")
    except Exception as e:
        logger.error(f"Error updating user table: {str(e)}", exc_info=True)
        db.session.rollback()
        raise type(e)(f"Database operation failed during user table update: {str(e)}") from e

def create_indexes():
    """Create database indexes for better performance"""
    start_time = time.time()
    logger.info("Starting index creation")
    
    try:
        # This function should be called within an app context
        # Create indexes on frequently queried columns
        from sqlalchemy import text
        
        # Index on patient_id for faster lookups
        index_sql = text("CREATE INDEX IF NOT EXISTS idx_patient_patient_id ON patient (patient_id)")
        db.session.execute(index_sql)
        logger.info("Created index on patient.patient_id")
        
        # Index on code_a and code_b for faster blinded data queries
        index_sql = text("CREATE INDEX IF NOT EXISTS idx_patient_code_a ON patient (code_a)")
        db.session.execute(index_sql)
        logger.info("Created index on patient.code_a")
        
        index_sql = text("CREATE INDEX IF NOT EXISTS idx_patient_code_b ON patient (code_b)")
        db.session.execute(index_sql)
        logger.info("Created index on patient.code_b")
        
        # Index on estimation entry codes
        index_sql = text("CREATE INDEX IF NOT EXISTS idx_estimation_entry_code ON estimation_entry (code)")
        db.session.execute(index_sql)
        logger.info("Created index on estimation_entry.code")
        
        db.session.commit()
        logger.info(f"Successfully completed index creation in {time.time() - start_time:.2f} seconds")
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}", exc_info=True)
        db.session.rollback()
        raise type(e)(f"Database operation failed during index creation: {str(e)}") from e

def init_db(app=None):
    """Initialize the database with all required tables, indexes, and default users"""
    start_time = time.time()
    logger.info("Starting database initialization")
    
    # Use the passed app or create a new one
    app_to_use = app or create_app('production')
    
    with app_to_use.app_context():
        try:
            app_to_use.logger.info(f"Database URI being used: {app_to_use.config.get('SQLALCHEMY_DATABASE_URI')}")
            
            # Create all tables
            db.create_all()
            creation_time = time.time()
            logger.info(f"Database tables created in {creation_time - start_time:.2f} seconds")
            
            # Update user table structure
            update_user_table()
            update_time = time.time()
            logger.info(f"User table structure updated in {update_time - creation_time:.2f} seconds")
            
            # Create indexes for better performance
            create_indexes()
            indexes_time = time.time()
            logger.info(f"Database indexes created in {indexes_time - update_time:.2f} seconds")
            
            # Create default users if they don't exist
            users_start = time.time()
            supervisor = User.query.filter_by(username='supervisor').first()
            if not supervisor:
                supervisor_password = os.environ.get('SUPERVISOR_PASSWORD') or generate_secure_password()
                supervisor = User(
                    username='supervisor',
                    password=generate_password_hash(supervisor_password),
                    role='supervisor'
                )
                db.session.add(supervisor)
                logger.info(f"Created supervisor user with password: {supervisor_password}")
            
            pi = User.query.filter_by(username='pi').first()
            if not pi:
                pi_password = os.environ.get('PI_PASSWORD') or generate_secure_password()
                pi = User(
                    username='pi',
                    password=generate_password_hash(pi_password),
                    role='pi'
                )
                db.session.add(pi)
                logger.info(f"Created PI user with password: {pi_password}")
            
            db.session.commit()
            users_time = time.time()
            logger.info(f"Default users created successfully in {users_time - users_start:.2f} seconds")
            
            total_time = time.time() - start_time
            logger.info(f"Database initialization completed successfully in {total_time:.2f} seconds")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error initializing database: {str(e)}", exc_info=True)
            logger.error(f"Database initialization failed after {time.time() - start_time:.2f} seconds")
            raise type(e)(f"Database initialization failed: {str(e)}") from e
if __name__ == '__main__':
    app = create_app('production')
    init_db(app)
    print("Database initialized successfully!")