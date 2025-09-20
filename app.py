from flask import Flask, render_template, redirect, url_for, session, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from config import config
from models import db
from auth import auth
from routes import main
import os
from datetime import timedelta

def create_app(config_name='default'):
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config[config_name])
    
    # Session configuration for security
    app.permanent_session_lifetime = timedelta(minutes=30)
    
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
        if not app.config['DEBUG']:
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

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)