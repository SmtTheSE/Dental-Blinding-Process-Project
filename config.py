import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database configuration with SSL settings for Supabase
    database_url = os.environ.get('SUPABASE_DB_URL') or os.environ.get('DATABASE_URL')
    if database_url:
        # Handle Supabase database URL with proper SSL configuration
        if 'postgresql://' in database_url and '?' not in database_url:
            database_url += '?sslmode=require'
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Default to localhost for development
        SQLALCHEMY_DATABASE_URI = 'postgresql://sittminthar@localhost:5432/dental_scheduler'

    # Configure SQLAlchemy engine options optimized for Supabase
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Validate connections before use
        'pool_recycle': 300,    # Recycle connections every 5 minutes
        'pool_timeout': 20,     # Timeout for getting a connection
        'max_overflow': 0,      # Don't allow overflow connections
        'pool_size': 5          # Number of connections to maintain
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SUPABASE_DB_URL') or os.environ.get('DEV_DATABASE_URL') or \
        'postgresql://sittminthar@localhost:5432/dental_scheduler'

class ProductionConfig(Config):
    DEBUG = False
    # Security Configuration - Only secure cookies if on HTTPS (usually Vercel/Render)
    # Browsers like Chrome usually allow Secure cookies on localhost even without HTTPS, 
    # but some environments are stricter.
    is_prod_env = os.environ.get('RENDER') or os.environ.get('VERCEL')
    SESSION_COOKIE_SECURE = True if is_prod_env else False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # PERMANENT_SESSION_LIFETIME is already set in app.py generally, but good to ensure security context

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}