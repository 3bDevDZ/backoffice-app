"""Frontend-friendly authentication decorators that redirect to login."""
from functools import wraps
from flask import redirect, url_for, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def require_auth_or_redirect(f):
    """Decorator that redirects to login if not authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            # If we get here, user is authenticated
            return f(*args, **kwargs)
        except Exception as e:
            # Not authenticated, redirect to login
            # Save the original URL to redirect back after login
            # Debug: log the exception (remove in production)
            import logging
            logging.debug(f"Auth failed: {type(e).__name__}: {str(e)}")
            return redirect(url_for('auth_frontend.login', next=request.url))
    return decorated_function


def require_roles_or_redirect(*required_roles):
    """Decorator that redirects to login if not authenticated, or checks roles."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                # If we get here, user is authenticated
                claims = get_jwt()
                roles = set(claims.get("roles", []))
                if not roles.intersection(set(required_roles)):
                    # User doesn't have required role, redirect to login
                    return redirect(url_for('auth_frontend.login', next=request.url))
                return fn(*args, **kwargs)
            except Exception as e:
                # Not authenticated, redirect to login
                # Debug: log the exception (remove in production)
                import logging
                logging.debug(f"Auth failed: {type(e).__name__}: {str(e)}")
                return redirect(url_for('auth_frontend.login', next=request.url))
        return wrapper
    return decorator

