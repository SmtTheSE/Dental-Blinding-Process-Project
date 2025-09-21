import os
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash
import secrets

# Use production config by default
app = create_app('production')

def generate_secure_password(length=12):
    """Generate a secure random password"""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def update_user_table():
    """Add new columns to existing user table if they don't exist"""
    with app.app_context():
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
                app.logger.info("Added failed_attempts column to user table")
            
            # Check if last_login column exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user' AND column_name = 'last_login'
            """))
            
            if not result.fetchone():
                # Add last_login column
                db.session.execute(text("ALTER TABLE \"user\" ADD COLUMN last_login TIMESTAMP"))
                app.logger.info("Added last_login column to user table")
                
            db.session.commit()
        except Exception as e:
            app.logger.error(f"Error updating user table: {str(e)}")
            db.session.rollback()

def create_indexes():
    """Create database indexes for better performance"""
    with app.app_context():
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
            app.logger.info("Database indexes created successfully")
        except Exception as e:
            app.logger.error(f"Error creating indexes: {str(e)}")
            db.session.rollback()

def init_db(app=None):
    """Initialize the database with all required tables, indexes, and default users"""
    # Use the passed app or the global one
    app_to_use = app or globals().get('app')
    
    with app_to_use.app_context():
        # Create all tables
        db.create_all()
        app_to_use.logger.info("Database tables created")
        
        # Update user table structure
        update_user_table()
        
        # Create indexes for better performance
        create_indexes()
        
        # Create default users if they don't exist
        supervisor = User.query.filter_by(username='supervisor').first()
        if not supervisor:
            supervisor_password = os.environ.get('SUPERVISOR_PASSWORD') or generate_secure_password()
            supervisor = User(
                username='supervisor',
                password=generate_password_hash(supervisor_password),
                role='supervisor'
            )
            db.session.add(supervisor)
            app_to_use.logger.info(f"Created supervisor user with password: {supervisor_password}")
        
        pi = User.query.filter_by(username='pi').first()
        if not pi:
            pi_password = os.environ.get('PI_PASSWORD') or generate_secure_password()
            pi = User(
                username='pi',
                password=generate_password_hash(pi_password),
                role='pi'
            )
            db.session.add(pi)
            app_to_use.logger.info(f"Created PI user with password: {pi_password}")
        
        try:
            db.session.commit()
            app_to_use.logger.info("Default users created successfully")
        except Exception as e:
            db.session.rollback()
            app_to_use.logger.error(f"Error creating default users: {str(e)}")

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")