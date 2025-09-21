import logging
import os
import datetime
import traceback
from flask import Flask, render_template, redirect, url_for, session, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from config import config
from models import db
from auth import auth
from routes import main

def create_app(config_name='default'):
    # Determine config name from environment if not explicitly provided
    if config_name == 'default':
        config_name = os.environ.get('FLASK_ENV', 'production')  # Changed default to production
    
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config[config_name])
    
    # Set up logging
    if not app.debug and not app.testing:
        # In production, log to stderr
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        stream_handler.setFormatter(formatter)
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Dental Age Estimation System startup')
        app.logger.info(f'FLASK_ENV: {os.environ.get("FLASK_ENV", "not set")}')
        app.logger.info(f'DATABASE_URL: {os.environ.get("DATABASE_URL", "not set")}')
        app.logger.info(f'Configured database URI: {app.config.get("SQLALCHEMY_DATABASE_URI", "not set")}')
    
    # Session configuration for security
    app.permanent_session_lifetime = datetime.timedelta(minutes=30)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(main)
    
    # Security headers
    @app.after_request
    def after_request(response):
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        
        # XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Content type sniffing protection
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Strict transport security (only in production)
        if not app.config['DEBUG'] and app.config.get('SESSION_COOKIE_SECURE', False):
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
        # Content security policy - allow inline images for charts
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:"
        
        return response
    
    @app.context_processor
    def inject_global_csrf_token():
        """Inject CSRF token into all templates"""
        # Use the generate_csrf_token function from routes instead of auth
        from routes import generate_csrf_token
        return dict(csrf_token=generate_csrf_token())
    
    @app.before_request
    def before_request():
        # Force HTTPS in production
        if not app.config['DEBUG'] and not request.is_secure and request.url.startswith('http://'):
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
    
    # Health check endpoint for Render
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'timestamp': str(datetime.datetime.utcnow())}
    
    @app.route('/debug/csrf')
    def debug_csrf():
        from routes import generate_csrf_token
        token = generate_csrf_token()
        return {
            'session_token': session.get('csrf_token'),
            'generated_token': token,
            'tokens_match': session.get('csrf_token') == token
        }
    
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            # Handle login
            from auth import login
            app.logger.info("Processing POST request to login")
            result = login()
            app.logger.info("Login function returned")
            return result
        
        if 'user_id' in session:
            return redirect(url_for('main.dashboard'))
        app.logger.info("Showing login page")
        # Make sure CSRF token is generated for the login page
        from routes import generate_csrf_token
        generate_csrf_token()
        return render_template('login.html')
    
    @app.route('/setup')
    def setup():
        try:
            app.logger.info(f'FLASK_ENV: {os.environ.get("FLASK_ENV", "not set")}')
            app.logger.info(f'DATABASE_URL: {os.environ.get("DATABASE_URL", "not set")}')
            app.logger.info(f'Configured database URI: {app.config.get("SQLALCHEMY_DATABASE_URI", "not set")}')
            
            from setup_db import init_db
            success = init_db(app)
            if success:
                app.logger.info("Database initialized successfully")
                return "Database initialized successfully!"
            else:
                return "Database initialization failed", 500
        except Exception as e:
            error_msg = str(e)
            app.logger.error(f"Error initializing database: {error_msg}")
            app.logger.error(traceback.format_exc())
            
            # Provide specific guidance for common issues
            if "localhost" in error_msg or "127.0.0.1" in error_msg:
                return ("Database connection failed. The application is trying to connect to a local database "
                        "which doesn't exist in the Render environment. Please ensure that:\n"
                        "1. You have a PostgreSQL database service in Render\n"
                        "2. The DATABASE_URL environment variable is properly set\n"
                        "3. Your web service is linked to the database service\n\n"
                        f"Error details: {error_msg}"), 500
            else:
                return f"Error initializing database: {error_msg}", 500
    
    return app

# For gunicorn
if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5001))  # Changed default port to 5001 to avoid conflicts
    app.run(host='0.0.0.0', port=port)  # Removed debug=True for production

# Application factory for gunicorn
app = create_app()