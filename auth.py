import logging
from datetime import datetime, timedelta  # Add missing timedelta import
from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from models import db, User
from werkzeug.security import check_password_hash

auth = Blueprint('auth', __name__)

# Configure logging
logging.basicConfig(filename='auth.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300  # 5 minutes in seconds

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            # Check if account is locked
            # Check if account is locked
            if user.locked_until and user.locked_until > datetime.utcnow():
                flash('Account is temporarily locked. Please try again later.')
                return render_template('login.html')
                
            if check_password_hash(user.password, password):
                # Reset failed attempts and clear lockout on successful login
                user.failed_attempts = 0
                user.locked_until = None
                db.session.commit()
                
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                
                # Log successful login
                logging.info(f"Successful login for user: {username}")
                
                return redirect(url_for('main.dashboard'))
            else:
                # Increment failed attempts
                user.failed_attempts += 1
                
                # Handle failed login attempts and lockout
                user.failed_attempts += 1
                
                # Lock account if too many failed attempts
                if user.failed_attempts >= MAX_LOGIN_ATTEMPTS:
                    user.locked_until = datetime.utcnow() + timedelta(seconds=LOCKOUT_TIME)
                
                db.session.commit()
                
                flash('Invalid username or password')
                
                flash('Invalid username or password')
                # Log failed login attempt
                logging.warning(f"Failed login attempt for user: {username}")
        else:
            # Handle non-existent users securely
            flash('Invalid username or password')
    
    # For GET requests or after POST processing
    return render_template('login.html', is_post=request.method == 'POST')

@auth.route('/logout')
def logout():
    # Log logout
    username = session.get('username', 'unknown')
    logging.info(f"User logged out: {username}")
    
    session.clear()
    return redirect(url_for('auth.login'))