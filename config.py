import os
import secrets

class Config:
    # Generate a secure secret key if not provided in environment
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Database configuration - support both local and Render PostgreSQL
    database_url = os.environ.get('DATABASE_URL')
    
    # Handle both postgres:// and postgresql:// prefixes
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    # Set database URL or provide a default with warning
    if database_url:
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Check if we're in Render environment
        if os.environ.get('RENDER'):
            # In Render but no DATABASE_URL - use a placeholder and warn
            SQLALCHEMY_DATABASE_URI = 'postgresql://missing-db-url/placeholder'
            print("WARNING: DATABASE_URL environment variable is not set!")
            print("Please ensure your PostgreSQL database is created and linked to your web service.")
        else:
            # Local development fallback
            SQLALCHEMY_DATABASE_URI = 'postgresql://sittminthar@localhost:5432/dental_scheduler'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security settings
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'  # Only send cookies over HTTPS in production
    SESSION_COOKIE_HTTPONLY = True  # Prevent XSS attacks
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    
    # Password policy
    PASSWORD_MIN_LENGTH = 8
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
class DevelopmentConfig(Config):
    DEBUG = True
    # In development, we might need to disable some security features
    SESSION_COOKIE_SECURE = False
    
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # Production-specific security settings
    SESSION_COOKIE_SECURE = True
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig  # Changed default to ProductionConfig
}