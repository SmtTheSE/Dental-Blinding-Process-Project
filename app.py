from flask import Flask, render_template, redirect, url_for, session, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from config import config
from models import db
from auth import auth
from routes import main
import os

def create_app(config_name='default'):
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(main)
    
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