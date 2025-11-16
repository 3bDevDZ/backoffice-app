"""Locale detection utilities for Flask-Babel integration."""
from flask import request, g
from flask_babel import get_locale


def get_user_locale():
    """
    Get locale from multiple sources in priority order:
    1. URL parameter (?locale=fr|ar)
    2. User preference (from database)
    3. Accept-Language header
    4. Default to 'fr'
    """
    # 1. Check URL parameter
    locale = request.args.get('locale')
    if locale in ['fr', 'ar']:
        return locale
    
    # 2. Check user preference (if logged in)
    if hasattr(g, 'user') and g.user and hasattr(g.user, 'locale'):
        user_locale = g.user.locale
        if user_locale in ['fr', 'ar']:
            return user_locale
    
    # 3. Check Accept-Language header
    if request.accept_languages:
        best_match = request.accept_languages.best_match(['fr', 'ar'])
        if best_match:
            return best_match
    
    # 4. Fallback to default
    return 'fr'


def get_text_direction(locale=None):
    """Get text direction (ltr/rtl) for a given locale."""
    if locale is None:
        locale = get_locale() or 'fr'
    return 'rtl' if locale == 'ar' else 'ltr'

