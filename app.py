import logging
import os
import datetime
from flask import Flask, render_template, redirect, url_for, session, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from config import config
from models import db
from auth import auth
from routes import main

def create_app(config_name='default'):
    # Determine config name from environment if not explicitly provided
    if config_name == 'default':
        config_name = os.environ.get('FLASK_ENV', 'development')
    
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
    
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            # Handle login
            from auth import login
            return login()
        
        if 'user_id' in session:
            return redirect(url_for('main.dashboard'))
        return render_template('login.html')

    @app.route('/setup')
    def setup():
        from setup_db import init_db
        init_db(app)
        return "Database initialized successfully!"
    
    return app

# For gunicorn
if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
