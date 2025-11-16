# Internationalization (i18n) Requirements

**Date**: 2025-01-27  
**Feature**: Commercial Management MVP System

## Overview

The system must support multi-language interface with Arabic (AR) and French (FR) languages. The backend API must provide translated content and support RTL (right-to-left) layout for Arabic.

## Supported Languages

- **French (fr)**: Default language, LTR (left-to-right)
- **Arabic (ar)**: RTL (right-to-left) support required

## Implementation Requirements

### 1. Locale Detection

The system must detect user's preferred language through:

1. **Query Parameter** (highest priority):
   - `?locale=fr` or `?locale=ar`
   - Example: `GET /api/products?locale=ar`

2. **Accept-Language Header**:
   - Standard HTTP header: `Accept-Language: ar,fr;q=0.9`
   - Parsed and used if no query parameter provided

3. **User Preference** (stored in database):
   - User model includes `locale` field (default: 'fr')
   - Used if neither query parameter nor header provided

4. **System Default**:
   - Fallback to French ('fr') if no preference detected

### 2. Translation Coverage

The following content must be translated:

#### API Responses

- **Error Messages**:
  - Validation errors (field required, invalid format, etc.)
  - Business rule violations (stock insufficient, credit limit exceeded, etc.)
  - System errors (not found, unauthorized, etc.)

- **Status Labels**:
  - Quote statuses: Draft, Sent, Accepted, Rejected, Expired, Canceled
  - Order statuses: Draft, Confirmed, In Preparation, Ready, Shipped, Delivered, Invoiced, Canceled
  - Product statuses: Active, Inactive, Archived
  - Customer statuses: Active, Inactive, Archived, Blocked
  - Stock movement types: Entry, Exit, Transfer, Adjustment

- **Field Labels**:
  - Product fields: Name, Description, Price, Cost, Category, etc.
  - Customer fields: Name, Email, Address, Phone, etc.
  - Order fields: Number, Date, Total, Status, etc.

- **Success Messages**:
  - "Product created successfully"
  - "Order confirmed"
  - "Stock movement recorded"
  - etc.

#### Documents

- **PDF Documents**:
  - Quote PDFs (titles, labels, terms)
  - Order PDFs (titles, labels, terms)
  - Delivery notes

- **Email Templates**:
  - Quote emails
  - Order confirmation emails
  - Stock alert emails
  - Password reset emails

### 3. RTL Support for Arabic

When locale is Arabic (`ar`), the API must:

1. **Include Direction Metadata**:
   ```json
   {
     "data": {...},
     "meta": {
       "locale": "ar",
       "direction": "rtl"
     }
   }
   ```

2. **Date Formatting**:
   - Use Arabic date format (optional: Arabic calendar)
   - Format: DD/MM/YYYY or Arabic-Indic numerals

3. **Number Formatting**:
   - Standard: Use Western numerals (0-9) - recommended for consistency
   - Optional: Arabic-Indic numerals (٠-٩) - can be configured

4. **Text Alignment**:
   - Frontend handles text alignment based on `direction` metadata
   - Backend provides direction, frontend applies CSS classes

### 4. Translation File Structure

```
app/
└── translations/
    ├── fr/
    │   └── LC_MESSAGES/
    │       ├── messages.po      # Source translations
    │       └── messages.mo      # Compiled translations
    └── ar/
        └── LC_MESSAGES/
            ├── messages.po
            └── messages.mo
```

### 5. Translation Keys Organization

Translation keys organized by domain:

```
# Errors
error.validation.required = "Field is required"
error.stock.insufficient = "Insufficient stock"
error.credit.exceeded = "Credit limit exceeded"

# Statuses
status.quote.draft = "Draft"
status.quote.sent = "Sent"
status.order.confirmed = "Confirmed"

# Labels
label.product.name = "Product Name"
label.customer.email = "Email"
label.order.total = "Total"

# Messages
message.product.created = "Product created successfully"
message.order.confirmed = "Order confirmed"
```

### 6. API Response Format

All API responses must include locale metadata:

**Success Response**:
```json
{
  "data": {
    "id": 1,
    "name": "Product Name",
    "status": "Active"
  },
  "meta": {
    "locale": "fr",
    "direction": "ltr"
  }
}
```

**Error Response**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Le champ est requis",  // Translated
    "details": {
      "field": "name"
    }
  },
  "meta": {
    "locale": "fr",
    "direction": "ltr"
  }
}
```

### 7. User Locale Preference

**User Model Extension**:
```python
class User(Base):
    # ... existing fields ...
    locale = Column(String(5), default='fr')  # 'fr' or 'ar'
```

**API Endpoints**:
- `GET /api/user/preferences` - Get user preferences including locale
- `PUT /api/user/preferences` - Update user preferences including locale

### 8. Translation Workflow

1. **Development**:
   - Developers use translation keys: `gettext('error.validation.required')`
   - Extract strings: `flask babel extract`
   - Translate: Edit `.po` files
   - Compile: `flask babel compile`

2. **Translation Process**:
   - French translations: Native French speaker reviews
   - Arabic translations: Native Arabic speaker reviews
   - RTL testing: Verify Arabic interface layout

3. **Testing**:
   - Test all endpoints with `?locale=fr`
   - Test all endpoints with `?locale=ar`
   - Verify RTL metadata in responses
   - Test error message translations

## Example Implementation

### Flask-Babel Setup

```python
from flask_babel import Babel, gettext, ngettext, format_date, format_number

babel = Babel(app)

@babel.localeselector
def get_locale():
    # 1. Check query parameter
    locale = request.args.get('locale')
    if locale in ['fr', 'ar']:
        return locale
    
    # 2. Check Accept-Language header
    return request.accept_languages.best_match(['fr', 'ar'], 'fr')
```

### Using Translations in Code

```python
from flask_babel import gettext as _

# Error message
raise ValueError(_('error.validation.required'))

# Status label
status_label = _('status.quote.draft')

# Success message
return {'message': _('message.product.created')}
```

### API Endpoint with Locale

```python
@products_bp.get("")
def list_products():
    locale = request.args.get('locale') or g.locale or 'fr'
    products = mediator.dispatch(ListProductsQuery())
    
    return jsonify({
        'data': [p.to_dict() for p in products],
        'meta': {
            'locale': locale,
            'direction': 'rtl' if locale == 'ar' else 'ltr'
        }
    })
```

## Testing Requirements

1. **Unit Tests**:
   - Test translation functions with different locales
   - Test locale detection logic
   - Test RTL direction assignment

2. **Integration Tests**:
   - Test API endpoints with `?locale=fr`
   - Test API endpoints with `?locale=ar`
   - Verify translated error messages
   - Verify RTL metadata in responses

3. **Manual Testing**:
   - Test all UI screens in French
   - Test all UI screens in Arabic
   - Verify RTL layout in Arabic
   - Test PDF generation in both languages
   - Test email templates in both languages

## Future Enhancements

- Add more languages (English, Spanish, etc.)
- User-specific date/number format preferences
- Arabic calendar support (Hijri calendar)
- Automatic translation via API (Google Translate, etc.) - optional

