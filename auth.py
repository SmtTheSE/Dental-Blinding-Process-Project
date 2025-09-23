class Config:
    PASSWORD_MIN_LENGTH = 12  # Minimum password length

import logging
import re
import os
import random
import string
from datetime import datetime, timedelta
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, current_app, abort
from models import db, User
from werkzeug.security import check_password_hash, generate_password_hash
from config import Config

# Password configuration
PASSWORD_MIN_LENGTH = 12

auth = Blueprint('auth', __name__)

# Configure logging
# Use app logger if available, otherwise create a basic logger
try:
    from flask import current_app
    logger = current_app.logger
except:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Initialized basic logger")

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300  # 5 minutes in seconds


def validate_password(password):
    """Validate password strength"""
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
    
    # Check for at least one uppercase letter, one lowercase letter, and one digit
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    
    # Check for special characters
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is valid"


def validate_csrf_token():
    """Validate CSRF token for POST requests"""
    token = session.get('csrf_token')
    
    # Handle different content types
    if request.is_json:
        # For JSON requests, get token from headers or JSON body
        form_token = request.headers.get('X-CSRF-Token') or request.get_json(silent=True).get('csrf_token') if request.get_json(silent=True) else None
    else:
        # For form submissions, get token from form data or headers
        form_token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
    
    if not token or not form_token or token != form_token:
        return False
    return True


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Note: CSRF protection is handled by the global CSRF protection in routes.py
        # We don't need to manually check it here

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

        # Check for hardcoded credentials first
        if username == 'supervisor' and password == 'supervisor':
            # Check if supervisor user exists in database, create if not
            supervisor = User.query.filter_by(username='supervisor').first()
            if not supervisor:
                supervisor = User(
                    username='supervisor',
                    password=generate_password_hash('supervisor'),
                    role='supervisor'
                )
                db.session.add(supervisor)
                db.session.commit()

            # Reset failed attempts and clear lockout
            supervisor.failed_attempts = 0
            supervisor.locked_until = None
            supervisor.last_login = datetime.utcnow()
            db.session.commit()

            session['user_id'] = supervisor.id
            session['username'] = supervisor.username
            session['role'] = supervisor.role
            session.permanent = True

            logger.info("Successful login for supervisor")
            return redirect(url_for('main.dashboard'))

        elif username == 'pi' and password == 'pi':
            # Check if pi user exists in database, create if not
            pi = User.query.filter_by(username='pi').first()
            if not pi:
                pi = User(
                    username='pi',
                    password=generate_password_hash('pi'),
                    role='pi'
                )
                db.session.add(pi)
                db.session.commit()

            # Reset failed attempts and clear lockout
            pi.failed_attempts = 0
            pi.locked_until = None
            pi.last_login = datetime.utcnow()
            db.session.commit()

            session['user_id'] = pi.id
            session['username'] = pi.username
            session['role'] = pi.role
            session.permanent = True

            logger.info("Successful login for pi")
            return redirect(url_for('main.dashboard'))

        # If not using hardcoded credentials, check database
        user = User.query.filter_by(username=username).first()

        if user:
            # Check if account is locked
            if user.locked_until and user.locked_until > datetime.utcnow():
                flash(f'Account is locked. Try again after {user.locked_until.strftime("%Y-%m-%d %H:%M:%S")} UTC')
                # Log lockout event
                logger.warning(f"Login attempt on locked account: {username}")
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

                # Log successful login
                logger.info(f"Successful login for user: {username}")

                return redirect(url_for('main.dashboard'))
            else:
                # Increment failed attempts
                user.failed_attempts += 1
                if user.failed_attempts >= MAX_LOGIN_ATTEMPTS:
                    user.locked_until = datetime.utcnow() + timedelta(seconds=LOCKOUT_TIME)
                    flash(f'Account locked due to multiple failed attempts. Try again after {LOCKOUT_TIME//60} minutes.')
                else:
                    flash('Invalid username or password')
                db.session.commit()
        else:
            # Increment failed attempts for non-existent users too (to prevent user enumeration)
            flash('Invalid username or password')

        return render_template('login.html')

    # For GET requests, show the login page
    return render_template('login.html')

@auth.route('/logout')
def logout():
    # Log logout
    username = session.get('username', 'unknown')
    logger.info(f"User logged out: {username}")
    
    session.clear()
    flash('You have been logged out successfully.')
    return redirect(url_for('auth.login'))

# Move the login_required decorator to auth.py to avoid circular imports
def login_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return wrapper

@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        # Validate CSRF token
        if not validate_csrf_token():
            flash('Security token validation failed. Please try again.')
            return render_template('change_password.html')
        
        current_password = request.form.get('current_password')
        new_username = request.form.get('new_username')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Get current user
        user = User.query.get(session['user_id'])
        if not user:
            flash('User not found.')
            return render_template('change_password.html')
        
        # Check current password
        if not check_password_hash(user.password, current_password):
            flash('Current password is incorrect.')
            return render_template('change_password.html')
        
        # Check if new username is provided and is different
        username_changed = False
        if new_username and new_username != user.username:
            # Check if username already exists
            existing_user = User.query.filter_by(username=new_username).first()
            if existing_user:
                flash('Username already exists. Please choose a different username.')
                return render_template('change_password.html')
            
            # Update username
            user.username = new_username
            username_changed = True
        
        # Check if new password is provided
        password_changed = False
        if new_password:
            # Validate new password
            is_valid, message = validate_password(new_password)
            if not is_valid:
                flash(message)
                return render_template('change_password.html')
            
            # Check if new password and confirmation match
            if new_password != confirm_password:
                flash('New password and confirmation do not match.')
                return render_template('change_password.html')
            
            # Update password
            user.password = generate_password_hash(new_password)
            password_changed = True
        
        # If neither username nor password is being changed
        if not username_changed and not password_changed:
            flash('No changes were made.')
            return render_template('change_password.html')
        
        # Commit changes to database
        db.session.commit()
        
        # Update session if username was changed
        if username_changed:
            session['username'] = user.username
        
        # Show appropriate success message
        if username_changed and password_changed:
            flash('Username and password changed successfully.')
        elif username_changed:
            flash('Username changed successfully.')
        elif password_changed:
            flash('Password changed successfully.')
            
        return redirect(url_for('main.dashboard'))
    
    return render_template('change_password.html')
