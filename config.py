import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database configuration with SSL settings
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Handle Render's database URL which might not have all SSL parameters
        if 'postgresql://' in database_url and '?' not in database_url:
            database_url += '?sslmode=require'
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Default to localhost for development
        SQLALCHEMY_DATABASE_URI = 'postgresql://sittminthar@localhost:5432/dental_scheduler'

    # Configure SQLAlchemy engine options for better connection handling
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
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'postgresql://sittminthar@localhost:5432/dental_scheduler'

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}