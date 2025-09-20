class Config:
    PASSWORD_MIN_LENGTH = 12  # Minimum password length
import logging
import re
from datetime import datetime, timedelta
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, current_app
from models import db, User
from werkzeug.security import check_password_hash, generate_password_hash
from config import Config

auth = Blueprint('auth', __name__)

# Configure logging
# Use app logger if available, otherwise create a basic logger
try:
    from flask import current_app
    logger = current_app.logger
except:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300  # 5 minutes in seconds

def validate_password(password):
    """Validate password strength"""
    if len(password) < Config.PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {Config.PASSWORD_MIN_LENGTH} characters long"
    
    # Check for at least one uppercase letter, one lowercase letter, and one digit
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    
    return True, "Password is valid"

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Sanitize inputs
        if not username or not password:
            flash('Username and password are required')
            return render_template('login.html')
        
        # Limit username length to prevent DoS
        if len(username) > 50:
            flash('Invalid username or password')
            return render_template('login.html')
            
        user = User.query.filter_by(username=username).first()
        
        if user:
            # Check if account is locked
            if user.locked_until and user.locked_until > datetime.utcnow():
                flash('Account is temporarily locked. Please try again later.')
                # Log lockout event
                logging.warning(f"Login attempt on locked account: {username}")
                return render_template('login.html')
                
            if check_password_hash(user.password, password):
                # Reset failed attempts and clear lockout on successful login
                user.failed_attempts = 0
                user.locked_until = None
                user.last_login = datetime.utcnow()  # Track last login time
                db.session.commit()
                
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                session.permanent = True  # Use permanent session
                
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                
                # Log successful login
                logging.info(f"Successful login for user: {username}")
                
                return redirect(url_for('main.dashboard'))
            else:
                # Increment failed attempts
                user.failed_attempts += 1
                
                # Lock account if too many failed attempts
                if user.failed_attempts >= MAX_LOGIN_ATTEMPTS:
                    user.locked_until = datetime.utcnow() + timedelta(seconds=LOCKOUT_TIME)
                    logging.warning(f"Account locked due to failed attempts: {username}")
                
                db.session.commit()
                
                flash('Invalid username or password')
                # Log failed login attempt
                logging.warning(f"Failed login attempt for user: {username}")
        else:
            # Handle non-existent users securely - same response as wrong password
            flash('Invalid username or password')
            # Log failed login attempt
            logging.warning(f"Failed login attempt for non-existent user: {username}")
    
    # For GET requests or after POST processing
    return render_template('login.html', is_post=request.method == 'POST')

@auth.route('/logout')
def logout():
    # Log logout
    username = session.get('username', 'unknown')
    logging.info(f"User logged out: {username}")
    
    session.clear()
    return redirect(url_for('auth.login'))

@auth.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        user = User.query.get(session['user_id'])
        
        if not user:
            flash('User not found')
            return redirect(url_for('auth.change_password'))
            
        # Check current password
        if not check_password_hash(user.password, current_password):
            flash('Current password is incorrect')
            return redirect(url_for('auth.change_password'))
            
        # Validate new password
        is_valid, message = validate_password(new_password)
        if not is_valid:
            flash(message)
            return redirect(url_for('auth.change_password'))
            
        # Check if new password matches confirmation
        if new_password != confirm_password:
            flash('New passwords do not match')
            return redirect(url_for('auth.change_password'))
            
        # Check if new password is different from current
        if check_password_hash(user.password, new_password):
            flash('New password must be different from current password')
            return redirect(url_for('auth.change_password'))
            
        # Update password with stronger hashing parameters
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=16)
        db.session.commit()
        
        flash('Password changed successfully')
        logging.info(f"Password changed for user: {user.username}")
        return redirect(url_for('main.dashboard'))
        
    return render_template('change_password.html')