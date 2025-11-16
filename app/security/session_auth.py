"""Session-based authentication for frontend routes."""
from functools import wraps
from flask import session, redirect, url_for, request, g
from app.infrastructure.db import get_session
from app.domain.models.user import User


def login_user(user: User) -> None:
    """Store user information in session."""
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role
    session['locale'] = user.locale if hasattr(user, 'locale') else 'fr'
    session.permanent = True  # Make session persistent


def logout_user() -> None:
    """Clear user session."""
    session.clear()


def get_current_user() -> User | None:
    """Get current user from session. Returns expunged object that can be used after session closes."""
    if 'user_id' not in session:
        return None
    
    with get_session() as db:
        user = db.query(User).filter_by(id=session['user_id']).first()
        if user:
            # Expunge the object so it can be used after session closes
            # Access all needed attributes first to ensure they're loaded
            _ = user.id, user.username, user.role, getattr(user, 'locale', 'fr')
            db.expunge(user)
        return user


def require_auth_or_redirect(f):
    """Decorator that redirects to login if not authenticated (session-based)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Use path only, not full URL
            next_path = request.path
            if request.query_string:
                next_path += '?' + request.query_string.decode('utf-8')
            return redirect(url_for('auth_frontend.login', next=next_path))
        
        # Load user into g for template access
        g.user = get_current_user()
        if g.user is None:
            # Session has invalid user_id, clear it
            logout_user()
            next_path = request.path
            if request.query_string:
                next_path += '?' + request.query_string.decode('utf-8')
            return redirect(url_for('auth_frontend.login', next=next_path))
        
        return f(*args, **kwargs)
    return decorated_function


def require_roles_or_redirect(*required_roles):
    """Decorator that redirects to login if not authenticated or lacks required roles."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                # Use path only, not full URL
                next_path = request.path
                if request.query_string:
                    next_path += '?' + request.query_string.decode('utf-8')
                return redirect(url_for('auth_frontend.login', next=next_path))
            
            # Load user into g for template access
            g.user = get_current_user()
            if g.user is None:
                logout_user()
                next_path = request.path
                if request.query_string:
                    next_path += '?' + request.query_string.decode('utf-8')
                return redirect(url_for('auth_frontend.login', next=next_path))
            
            # Check roles
            user_role = session.get('role')
            if user_role not in required_roles:
                next_path = request.path
                if request.query_string:
                    next_path += '?' + request.query_string.decode('utf-8')
                return redirect(url_for('auth_frontend.login', next=next_path))
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

