from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash
import secrets

app = create_app()

def generate_secure_password(length=12):
    """Generate a secure random password"""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def update_user_table():
    """Add new columns to existing user table"""
    with app.app_context():
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

with app.app_context():
    # Create all tables
    db.create_all()
    
    # Update user table with new columns
    update_user_table()
    
    # Check if default users exist, if not create them
    supervisor = User.query.filter_by(username='supervisor').first()
    pi = User.query.filter_by(username='pi').first()
    
    if not supervisor and not pi:
        # Create default users with securely hashed passwords
        supervisor = User(
            username='supervisor',
            password=generate_password_hash('supervisor', method='pbkdf2:sha256', salt_length=16),
            role='supervisor'
        )
        db.session.add(supervisor)
        
        pi = User(
            username='pi',
            password=generate_password_hash('pi', method='pbkdf2:sha256', salt_length=16),
            role='pi'
        )
        db.session.add(pi)
        
        db.session.commit()
        print('Database setup complete! Tables created and default users added.')
        print('SECURITY WARNING: Please change the default passwords immediately!')
        print('Default credentials:')
        print('  Supervisor: username=supervisor, password=supervisor')
        print('  PI: username=pi, password=pi')
    else:
        print('Default users already exist. No changes made.')