import os
import secrets

class Config:
    # Generate a secure secret key if not provided in environment
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://sittminthar@localhost:5432/dental_scheduler'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security settings
    SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent XSS attacks
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    
    # Password policy
    PASSWORD_MIN_LENGTH = 8
    
class DevelopmentConfig(Config):
    DEBUG = True
    # In development, we might need to disable some security features
    SESSION_COOKIE_SECURE = False
    
class ProductionConfig(Config):
    DEBUG = False
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}