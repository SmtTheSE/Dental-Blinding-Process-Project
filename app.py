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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_app(config_name='default'):
    # Determine config name from environment if not explicitly provided
    if config_name == 'default':
        config_name = os.environ.get('FLASK_ENV', 'production')  # Changed default to production
    
    app = Flask(__name__, static_folder='static')
    
    # Check if we're in Render environment
    is_render = bool(os.environ.get('RENDER'))
    
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
        app.logger.info(f'RENDER environment: {is_render}')
        app.logger.info(f'FLASK_ENV: {os.environ.get("FLASK_ENV", "not set")}')
        app.logger.info(f'SUPABASE_DB_URL: {"set" if os.environ.get("SUPABASE_DB_URL") else "not set"}')
        app.logger.info(f'Configured database URI: {app.config.get("SQLALCHEMY_DATABASE_URI", "not set")}'[:50] + "...")
        
        # Check Supabase Storage configuration
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_KEY')
        app.logger.info(f'SUPABASE_URL: {"set" if supabase_url else "NOT SET - OPG uploads will fail!"}')
        app.logger.info(f'SUPABASE_KEY: {"set" if supabase_key else "NOT SET - OPG uploads will fail!"}')
        if supabase_url:
            app.logger.info(f'Supabase URL domain: {supabase_url[:30]}...')
        
        # Check for missing database URL
        if not os.environ.get('SUPABASE_DB_URL') and not os.environ.get('DATABASE_URL'):
            app.logger.warning("CRITICAL WARNING: SUPABASE_DB_URL environment variable is not set!")
            app.logger.warning("Please ensure your Supabase database connection string is configured.")
    
    # Session configuration for security
    app.permanent_session_lifetime = datetime.timedelta(minutes=30)
    
    # Initialize extensions
    db.init_app(app)
    
    # Run database setup on Render deployments
    if is_render:
        with app.app_context():
            try:
                from setup_db import init_db
                init_db(app)
                app.logger.info("Database initialized successfully on Render")
            except Exception as e:
                app.logger.error(f"Failed to initialize database on Render: {str(e)}")
                app.logger.error(traceback.format_exc())
    
    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(main)
    
    # Initialize Flask-Talisman for security headers and HTTPS
    # Define Content Security Policy
    supabase_url = os.environ.get('SUPABASE_URL', '').replace('https://', '')
    supabase_domain = supabase_url.split('/')[0] if '/' in supabase_url else supabase_url
    
    # Talisman configuration for security headers
    # csp = { ... }
    # from flask_talisman import Talisman
    # Talisman disabled for debugging
    # Talisman(app, 
    #          content_security_policy=csp,
    #          force_https=not app.debug and not app.testing,
    #          session_cookie_secure=not app.debug and not app.testing,
    #          session_cookie_http_only=True)

    # Fix for Vercel/Proxy environments
    # This is CRITICAL for HTTPS and CSRF to work correctly behind a load balancer
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static', 'img'),
                                   'UDMM.jpeg', mimetype='image/jpeg')

    @app.context_processor
    def inject_global_csrf_token():
        """Inject CSRF token into all templates"""
        # Use the generate_csrf_token function from routes instead of auth
        from routes import generate_csrf_token
        return dict(csrf_token=generate_csrf_token())

    @app.context_processor
    def inject_user():
        """Inject current_user into all templates to mimic Flask-Login"""
        class UserWrapper:
            def __init__(self):
                self.id = session.get('user_id')
                self.username = session.get('username')
                self.role = session.get('role')
                self.is_authenticated = bool(self.id)
                self.is_anonymous = not bool(self.id)
        
        return dict(current_user=UserWrapper())
    
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
        
    @app.route('/debug/routes')
    def debug_routes():
        import urllib
        output = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            line = urllib.parse.unquote(f"{rule.endpoint}: {rule} ({methods})")
            output.append(line)
        return "<br>".join(sorted(output))

    @app.route('/view-users')
    def view_users():
        """Temporary route to view user information"""
        # Only allow this in development or with explicit environment variable
        if os.environ.get('FLASK_ENV') != 'development' and not os.environ.get('ALLOW_PASSWORD_RESET'):
            return redirect(url_for('auth.login'))
        
        from models import User
        users = User.query.all()
        users_info = []
        for user in users:
            users_info.append({
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'password_hash': user.password
            })
        
        return {'users': users_info}
    
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('main.dashboard'))
        # Show landing page for non-authenticated users
        return render_template('landing.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login_page():
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
    
    # Error handlers for debugging
    @app.errorhandler(400)
    def bad_request_error(e):
        app.logger.error(f"Bad Request (400): {e.description}")
        # Log headers to see what's wrong
        app.logger.info(f"Request Headers: {dict(request.headers)}")
        return f"Bad Request (400): {e.description}. <br><br>Endpoint: {request.endpoint}<br>Request Headers: {dict(request.headers)}", 400

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal Server Error (500): {e}")
        app.logger.error(traceback.format_exc())
        return f"Internal Server Error (500): {e}", 500

    # Log every request to see headers (Temporary for debugging)
    @app.before_request
    def log_request_info():
        # Skip logging for static files
        if request.path.startswith('/static'):
            return
        app.logger.info(f"Request: {request.method} {request.url}")
        app.logger.info(f"Scheme: {request.scheme}")
        app.logger.info(f"Remote Addr: {request.remote_addr}")
        app.logger.info(f"X-Forwarded-Proto: {request.headers.get('X-Forwarded-Proto')}")

    return app

# For gunicorn
if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5001))  # Changed default port to 5001 to avoid conflicts
    app.run(host='0.0.0.0', port=port)  # Removed debug=True for production

# Application factory for gunicorn
app = create_app()