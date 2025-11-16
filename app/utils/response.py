"""API response utilities for consistent JSON responses with locale metadata."""
from flask import jsonify, request
from flask_babel import get_locale


def success_response(data=None, message=None, status_code=200):
    """
    Create a successful API response with locale metadata.
    
    Args:
        data: Response data (dict, list, or None)
        message: Success message (optional)
        status_code: HTTP status code (default: 200)
    
    Returns:
        Flask Response with JSON data
    """
    locale_obj = get_locale()
    locale = str(locale_obj) if locale_obj else 'fr'
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    response = {
        'success': True,
        'data': data,
        'meta': {
            'locale': locale,
            'direction': direction
        }
    }
    
    if message:
        response['message'] = message
    
    return jsonify(response), status_code


def error_response(message, errors=None, status_code=400):
    """
    Create an error API response with locale metadata.
    
    Args:
        message: Error message
        errors: Additional error details (optional)
        status_code: HTTP status code (default: 400)
    
    Returns:
        Flask Response with JSON error data
    """
    locale_obj = get_locale()
    locale = str(locale_obj) if locale_obj else 'fr'
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    response = {
        'success': False,
        'error': {
            'message': message,
            'meta': {
                'locale': locale,
                'direction': direction
            }
        }
    }
    
    if errors:
        response['error']['details'] = errors
    
    return jsonify(response), status_code


def paginated_response(items, total, page, page_size, status_code=200):
    """
    Create a paginated API response with locale metadata.
    
    Args:
        items: List of items for current page
        total: Total number of items
        page: Current page number
        page_size: Items per page
        status_code: HTTP status code (default: 200)
    
    Returns:
        Flask Response with JSON paginated data
    """
    locale_obj = get_locale()
    locale = str(locale_obj) if locale_obj else 'fr'
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    response = {
        'success': True,
        'data': {
            'items': items,
            'pagination': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size if page_size > 0 else 0
            }
        },
        'meta': {
            'locale': locale,
            'direction': direction
        }
    }
    
    return jsonify(response), status_code

