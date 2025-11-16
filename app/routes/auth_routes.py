"""Frontend route handlers for authentication pages."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_babel import get_locale, gettext as _
from app.security.session_auth import login_user, logout_user, get_current_user
from app.application.common.mediator import mediator
from app.application.users.commands.commands import LoginCommand
from app.api.schemas.auth_schema import LoginSchema

auth_routes = Blueprint('auth_frontend', __name__)


def _get_safe_next_url():
    """Get and validate next URL to prevent open redirects."""
    next_url = request.args.get('next') or request.form.get('next')
    if not next_url:
        return url_for('dashboard.index')
    
    # If it's a full URL, extract just the path
    from urllib.parse import urlparse
    parsed = urlparse(next_url)
    if parsed.netloc:  # It's a full URL
        # Only allow same host
        if parsed.netloc != request.host:
            return url_for('dashboard.index')
        next_url = parsed.path or '/'
    
    # Ensure it's a local path (starts with /)
    if not next_url.startswith('/'):
        return url_for('dashboard.index')
    
    # Default to dashboard if root
    if next_url == '/':
        return url_for('dashboard.index')
    
    return next_url


@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    """Render login page and handle login form submission."""
    # If already logged in, redirect
    if 'user_id' in session:
        next_url = _get_safe_next_url()
        return redirect(next_url)
    
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get next URL to redirect after login
    next_url = _get_safe_next_url()
    
    # Handle POST (form submission)
    if request.method == 'POST':
        try:
            # Get form data
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if not username or not password:
                flash(_('Username and password are required'), 'error')
                return render_template(
                    'auth/login.html',
                    locale=locale,
                    direction=direction,
                    next_url=next_url
                )
            
            # Authenticate using LoginCommand (reuses existing logic)
            command = LoginCommand(username=username, password=password)
            user_dto = mediator.dispatch(command)
            
            if user_dto is None:
                flash(_('Invalid username or password'), 'error')
                return render_template(
                    'auth/login.html',
                    locale=locale,
                    direction=direction,
                    next_url=next_url
                )
            
            # Get user object for session
            from app.infrastructure.db import get_session
            from app.domain.models.user import User
            with get_session() as db:
                user = db.query(User).filter_by(id=user_dto.id).first()
                if user:
                    # Store user info in session (this copies the values, not the object)
                    login_user(user)
                    # Session is already set to permanent in login_user()
                    # Flask will save it automatically
                    
                    flash(_('Login successful'), 'success')
                    # Get safe next URL
                    redirect_url = _get_safe_next_url()
                    # Ensure we redirect to a valid URL
                    if not redirect_url or redirect_url == '/':
                        redirect_url = url_for('dashboard.index')
                    return redirect(redirect_url)
                else:
                    flash(_('User not found'), 'error')
        except Exception as e:
            flash(_('Login failed. Please try again.'), 'error')
            import logging
            import traceback
            logging.error(f"Login error: {e}")
            logging.error(traceback.format_exc())
            # Return to login page with error
            return render_template(
                'auth/login.html',
                locale=locale,
                direction=direction,
                next_url=next_url
            )
    
    # GET request - render login form
    return render_template(
        'auth/login.html',
        locale=locale,
        direction=direction,
        next_url=next_url
    )


@auth_routes.route('/logout')
def logout():
    """Handle logout."""
    logout_user()
    flash(_('You have been logged out successfully'), 'info')
    return redirect(url_for('auth_frontend.login'))

