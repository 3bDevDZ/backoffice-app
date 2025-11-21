"""i18n API endpoints for frontend translations."""
from flask import Blueprint, request, jsonify, session
from flask_babel import get_locale, gettext as _, force_locale

i18n_bp = Blueprint("i18n", __name__)


@i18n_bp.get("/translations")
def get_translations():
    """
    Get translations for the current locale.
    Returns a JSON object with all translated strings for frontend use.
    """
    try:
        locale_obj = get_locale()
        # Convert Locale object to string if needed
        locale = str(locale_obj) if locale_obj else 'fr'
        
        # Common translations that are frequently used in JavaScript
        # These are the most common strings used in frontend
        # Using gettext to get translations for current locale
        common_translations = {
            # General
            'Loading...': _('Loading...'),
            'Error': _('Error'),
            'Success': _('Success'),
            'Warning': _('Warning'),
            'Info': _('Info'),
            'Cancel': _('Cancel'),
            'Save': _('Save'),
            'Delete': _('Delete'),
            'Edit': _('Edit'),
            'View': _('View'),
            'Create': _('Create'),
            'Update': _('Update'),
            'Submit': _('Submit'),
            'Back': _('Back'),
            'Next': _('Next'),
            'Previous': _('Previous'),
            'Search': _('Search'),
            'Filter': _('Filter'),
            'Reset': _('Reset'),
            'Close': _('Close'),
            'Confirm': _('Confirm'),
            'Yes': _('Yes'),
            'No': _('No'),
            'OK': _('OK'),
            
            # Messages
            'Are you sure?': _('Are you sure?'),
            'This action cannot be undone.': _('This action cannot be undone.'),
            'Please wait...': _('Please wait...'),
            'Operation successful': _('Operation successful'),
            'Operation failed': _('Operation failed'),
            'An error occurred': _('An error occurred'),
            'Invalid input': _('Invalid input'),
            'Required field': _('Required field'),
            
            # Status
            'Active': _('Active'),
            'Inactive': _('Inactive'),
            'Draft': _('Draft'),
            'Confirmed': _('Confirmed'),
            'Cancelled': _('Cancelled'),
            'Completed': _('Completed'),
            'Pending': _('Pending'),
            
            # Actions
            'Add': _('Add'),
            'Remove': _('Remove'),
            'Select': _('Select'),
            'Choose': _('Choose'),
            'Upload': _('Upload'),
            'Download': _('Download'),
            'Export': _('Export'),
            'Import': _('Import'),
            'Print': _('Print'),
            
            # Dates
            'Date': _('Date'),
            'From': _('From'),
            'To': _('To'),
            'Today': _('Today'),
            'Yesterday': _('Yesterday'),
            'This week': _('This week'),
            'This month': _('This month'),
            'This year': _('This year'),
            
            # Pagination
            'Page': _('Page'),
            'of': _('of'),
            'Showing': _('Showing'),
            'to': _('to'),
            'results': _('results'),
            'No results found': _('No results found'),
            
            # Validation
            'Please fill in all required fields': _('Please fill in all required fields'),
            'Invalid email address': _('Invalid email address'),
            'Invalid phone number': _('Invalid phone number'),
            'Value must be greater than 0': _('Value must be greater than 0'),
            'Value must be a number': _('Value must be a number'),
        }
        
        return jsonify({
            'success': True,
            'locale': locale,
            'direction': 'rtl' if locale == 'ar' else 'ltr',
            'translations': common_translations
        })
    except Exception as e:
        locale_obj = get_locale()
        locale_str = str(locale_obj) if locale_obj else 'fr'
        return jsonify({
            'success': False,
            'error': str(e),
            'locale': locale_str,
            'direction': 'rtl' if locale_str == 'ar' else 'ltr',
            'translations': {}
                }), 500

@i18n_bp.post("/set-locale")
def set_locale():
    """
    Set locale in session and return success response.
    This endpoint allows JavaScript to change the language without reloading the page.
    """
    try:
        data = request.get_json() or {}
        locale = data.get('locale', '').lower()
        
        if locale not in ['en', 'fr', 'ar']:
            return jsonify({
                'success': False,
                'error': 'Invalid locale. Supported: en, fr, ar'
            }), 400
        
        # Save to session
        session['locale'] = locale
        session.permanent = True
        session.modified = True
        
        # Get translations for the new locale
        with force_locale(locale):
            common_translations = {
                # General
                'Loading...': _('Loading...'),
                'Error': _('Error'),
                'Success': _('Success'),
                'Warning': _('Warning'),
                'Info': _('Info'),
                'Cancel': _('Cancel'),
                'Save': _('Save'),
                'Delete': _('Delete'),
                'Edit': _('Edit'),
                'View': _('View'),
                'Create': _('Create'),
                'Update': _('Update'),
                'Submit': _('Submit'),
                'Back': _('Back'),
                'Next': _('Next'),
                'Previous': _('Previous'),
                'Search': _('Search'),
                'Filter': _('Filter'),
                'Reset': _('Reset'),
                'Close': _('Close'),
                'Confirm': _('Confirm'),
                'Yes': _('Yes'),
                'No': _('No'),
                'OK': _('OK'),
            }
        
        return jsonify({
            'success': True,
            'locale': locale,
            'direction': 'rtl' if locale == 'ar' else 'ltr',
            'translations': common_translations,
            'message': _('Language changed successfully')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@i18n_bp.get("/translations/<locale>")
def get_translations_for_locale(locale):
    """
    Get translations for a specific locale.
    """
    if locale not in ['en', 'fr', 'ar']:
        return jsonify({
            'success': False,
            'error': 'Invalid locale. Supported: en, fr, ar'
        }), 400
    
    # Temporarily set locale to get translations
    with force_locale(locale):
        common_translations = {
            'Loading...': _('Loading...'),
            'Error': _('Error'),
            'Success': _('Success'),
            'Warning': _('Warning'),
            'Info': _('Info'),
            'Cancel': _('Cancel'),
            'Save': _('Save'),
            'Delete': _('Delete'),
            'Edit': _('Edit'),
            'View': _('View'),
            'Create': _('Create'),
            'Update': _('Update'),
            'Submit': _('Submit'),
            'Back': _('Back'),
            'Next': _('Next'),
            'Previous': _('Previous'),
            'Search': _('Search'),
            'Filter': _('Filter'),
            'Reset': _('Reset'),
            'Close': _('Close'),
            'Confirm': _('Confirm'),
            'Yes': _('Yes'),
            'No': _('No'),
            'OK': _('OK'),
            'Are you sure?': _('Are you sure?'),
            'This action cannot be undone.': _('This action cannot be undone.'),
            'Please wait...': _('Please wait...'),
            'Operation successful': _('Operation successful'),
            'Operation failed': _('Operation failed'),
            'An error occurred': _('An error occurred'),
            'Invalid input': _('Invalid input'),
            'Required field': _('Required field'),
            'Active': _('Active'),
            'Inactive': _('Inactive'),
            'Draft': _('Draft'),
            'Confirmed': _('Confirmed'),
            'Cancelled': _('Cancelled'),
            'Completed': _('Completed'),
            'Pending': _('Pending'),
            'Add': _('Add'),
            'Remove': _('Remove'),
            'Select': _('Select'),
            'Choose': _('Choose'),
            'Upload': _('Upload'),
            'Download': _('Download'),
            'Export': _('Export'),
            'Import': _('Import'),
            'Print': _('Print'),
            'Date': _('Date'),
            'From': _('From'),
            'To': _('To'),
            'Today': _('Today'),
            'Yesterday': _('Yesterday'),
            'This week': _('This week'),
            'This month': _('This month'),
            'This year': _('This year'),
            'Page': _('Page'),
            'of': _('of'),
            'Showing': _('Showing'),
            'to': _('to'),
            'results': _('results'),
            'No results found': _('No results found'),
            'Please fill in all required fields': _('Please fill in all required fields'),
            'Invalid email address': _('Invalid email address'),
            'Invalid phone number': _('Invalid phone number'),
            'Value must be greater than 0': _('Value must be greater than 0'),
            'Value must be a number': _('Value must be a number'),
        }
        
        return jsonify({
            'success': True,
            'locale': locale,
            'direction': 'rtl' if locale == 'ar' else 'ltr',
            'translations': common_translations
        })

