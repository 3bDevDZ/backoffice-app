# Template Conversion Guide: Design HTML to Jinja2 Templates

**Date**: 2025-01-27  
**Feature**: Commercial Management MVP System

## Overview

This guide explains how to convert the static HTML design files from `/design` folder into Jinja2 templates for Flask server-side rendering.

## Conversion Strategy

### 1. Create Base Template

Extract common layout from all design files into `templates/base.html`:

**Common Elements**:
- HTML structure (`<html>`, `<head>`, `<body>`)
- Sidebar navigation (64px width, indigo-900 background)
- Top bar with user info and notifications
- Footer (if present)
- Tailwind CSS and Font Awesome includes
- Language switcher component
- RTL/LTR direction handling

**Base Template Structure**:
```jinja2
<!DOCTYPE html>
<html lang="{{ locale }}" dir="{{ direction }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}CommerceFlow{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    {% if direction == 'rtl' %}
    <link rel="stylesheet" href="{{ url_for('static', filename='css/rtl.css') }}">
    {% endif %}
</head>
<body class="bg-gray-50">
    {% if current_user.is_authenticated %}
    <!-- Sidebar -->
    <div class="fixed inset-y-0 left-0 w-64 bg-indigo-900 text-white z-50">
        {% include 'partials/sidebar.html' %}
    </div>
    {% endif %}

    <!-- Main Content -->
    <div class="{% if current_user.is_authenticated %}ml-64{% endif %}">
        {% if current_user.is_authenticated %}
        <!-- Top Bar -->
        {% include 'partials/topbar.html' %}
        {% endif %}

        <!-- Page Content -->
        {% block content %}{% endblock %}
    </div>

    <!-- JavaScript -->
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

### 2. Create Partial Templates

**Sidebar** (`templates/partials/sidebar.html`):
```jinja2
<div class="flex flex-col h-full">
    <!-- Logo -->
    <div class="flex items-center justify-center h-16 bg-indigo-950 border-b border-indigo-800">
        <i class="fas fa-chart-line text-2xl mr-2"></i>
        <span class="text-xl font-bold">CommerceFlow</span>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 overflow-y-auto py-4">
        <a href="{{ url_for('dashboard.index') }}" 
           class="flex items-center px-6 py-3 {% if request.endpoint == 'dashboard.index' %}bg-indigo-800 border-r-4 border-indigo-400{% else %}hover:bg-indigo-800{% endif %}">
            <i class="fas fa-home w-5"></i>
            <span class="ml-3">{{ _('Dashboard') }}</span>
        </a>
        <a href="{{ url_for('products.list') }}" 
           class="flex items-center px-6 py-3 {% if request.endpoint.startswith('products') %}bg-indigo-800 border-r-4 border-indigo-400{% else %}hover:bg-indigo-800{% endif %}">
            <i class="fas fa-box w-5"></i>
            <span class="ml-3">{{ _('Products') }}</span>
        </a>
        <!-- ... other navigation items ... -->
    </nav>

    <!-- User Profile -->
    {% include 'partials/user_profile.html' %}
</div>
```

**Top Bar** (`templates/partials/topbar.html`):
```jinja2
<div class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
    <div class="px-6 py-4 flex items-center justify-between">
        <div>
            {% block page_title %}{% endblock %}
        </div>
        <div class="flex items-center space-x-4">
            <!-- Language Switcher -->
            <div class="flex items-center space-x-2">
                <a href="{{ url_for(request.endpoint, **request.view_args, locale='fr') }}" 
                   class="px-2 py-1 {% if locale == 'fr' %}bg-indigo-600 text-white{% else %}text-gray-600{% endif %} rounded">
                    FR
                </a>
                <a href="{{ url_for(request.endpoint, **request.view_args, locale='ar') }}" 
                   class="px-2 py-1 {% if locale == 'ar' %}bg-indigo-600 text-white{% else %}text-gray-600{% endif %} rounded">
                    AR
                </a>
            </div>
            <!-- Notifications, Date, etc. -->
        </div>
    </div>
</div>
```

### 3. Convert Design Files to Page Templates

**Example: Products List** (`templates/products/list.html`):

**Original** (`design/03-products-list.html`):
```html
<h1 class="text-2xl font-bold text-gray-900">Gestion des Produits</h1>
<p class="text-sm text-gray-600">Catalogue complet de vos produits</p>
```

**Converted** (`templates/products/list.html`):
```jinja2
{% extends "base.html" %}

{% block title %}{{ _('Products') }} - CommerceFlow{% endblock %}

{% block page_title %}
    <h1 class="text-2xl font-bold text-gray-900">{{ _('Product Management') }}</h1>
    <p class="text-sm text-gray-600">{{ _('Complete catalog of your products') }}</p>
{% endblock %}

{% block content %}
<div class="p-6">
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <!-- Convert static numbers to template variables -->
        <div class="bg-white rounded-lg shadow-sm p-4">
            <div class="text-sm text-gray-600">{{ _('Total Products') }}</div>
            <div class="text-2xl font-bold text-gray-900">{{ products|length }}</div>
        </div>
    </div>

    <!-- Filters & Search -->
    <form method="GET" class="mb-6">
        <input type="text" name="search" value="{{ request.args.get('search', '') }}" 
               placeholder="{{ _('Search by name, code, description...') }}">
        <!-- ... filters ... -->
    </form>

    <!-- Products Table -->
    <div class="bg-white rounded-lg shadow-sm">
        <table class="min-w-full">
            <thead>
                <tr>
                    <th>{{ _('Code') }}</th>
                    <th>{{ _('Name') }}</th>
                    <th>{{ _('Price') }}</th>
                    <th>{{ _('Status') }}</th>
                    <th>{{ _('Actions') }}</th>
                </tr>
            </thead>
            <tbody>
                {% for product in products %}
                <tr>
                    <td>{{ product.code }}</td>
                    <td>{{ product.name }}</td>
                    <td>{{ format_number(product.price) }} €</td>
                    <td>
                        <span class="px-2 py-1 rounded text-xs 
                            {% if product.status == 'active' %}bg-green-100 text-green-800
                            {% elif product.status == 'inactive' %}bg-gray-100 text-gray-800
                            {% else %}bg-red-100 text-red-800{% endif %}">
                            {{ _(product.status|title) }}
                        </span>
                    </td>
                    <td>
                        <a href="{{ url_for('products.edit', id=product.id) }}" 
                           class="text-indigo-600 hover:text-indigo-700">
                            {{ _('Edit') }}
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
```

### 4. Template Variables and Data

**Route Handler** (`app/routes/products_routes.py`):
```python
from flask import Blueprint, render_template, request
from flask_babel import get_locale, format_number
from app.application.common.mediator import mediator
from app.application.products.queries.queries import ListProductsQuery
from app.security.rbac import require_roles

products_routes = Blueprint('products', __name__)

@products_routes.route('/products')
@require_roles('admin', 'commercial', 'direction')
def list_products():
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get data via CQRS
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    products = mediator.dispatch(ListProductsQuery(page=page, search=search))
    
    return render_template('products/list.html',
                         products=products,
                         locale=locale,
                         direction=direction,
                         format_number=format_number)
```

### 5. RTL Support in Templates

**RTL-Aware Classes**:
```jinja2
<div class="{% if direction == 'rtl' %}rtl text-right{% else %}ltr text-left{% endif %}">
    {{ _('Product Name') }}
</div>

<!-- Sidebar alignment -->
<div class="fixed inset-y-0 {% if direction == 'rtl' %}right-0{% else %}left-0{% endif %} w-64">
    <!-- Sidebar content -->
</div>

<!-- Main content margin -->
<div class="{% if direction == 'rtl' %}mr-64{% else %}ml-64{% endif %}">
    <!-- Main content -->
</div>
```

**RTL CSS** (`static/css/rtl.css`):
```css
.rtl {
    direction: rtl;
    text-align: right;
}

.rtl .ml-3 {
    margin-left: 0;
    margin-right: 0.75rem;
}

.rtl .mr-2 {
    margin-right: 0;
    margin-left: 0.5rem;
}

/* Tailwind RTL overrides */
.rtl .border-r-4 {
    border-right: 0;
    border-left: 4px solid;
}
```

### 6. Form Handling

**Template Form** (`templates/products/form.html`):
```jinja2
{% extends "base.html" %}

{% block content %}
<form method="POST" action="{{ url_for('products.create') }}" id="product-form">
    {{ csrf_token() }}
    
    <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">
            {{ _('Product Code') }}
        </label>
        <input type="text" name="code" value="{{ product.code if product else '' }}"
               class="w-full px-3 py-2 border rounded-lg"
               required>
        {% if errors and 'code' in errors %}
        <p class="text-red-600 text-sm mt-1">{{ errors['code'] }}</p>
        {% endif %}
    </div>
    
    <!-- ... other fields ... -->
    
    <button type="submit" class="px-4 py-2 bg-indigo-600 text-white rounded-lg">
        {{ _('Save') }}
    </button>
</form>

{% block scripts %}
<script>
    // AJAX form submission (optional)
    document.getElementById('product-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const response = await fetch('{{ url_for("api.products.create") }}', {
            method: 'POST',
            body: formData
        });
        if (response.ok) {
            window.location.href = '{{ url_for("products.list") }}';
        }
    });
</script>
{% endblock %}
{% endblock %}
```

**Route Handler** (can handle both form POST and AJAX):
```python
@products_routes.route('/products', methods=['POST'])
@require_roles('admin', 'commercial')
def create_product():
    if request.is_json:
        # AJAX request - return JSON
        data = request.get_json()
        command = CreateProductCommand(**data)
        product = mediator.dispatch(command)
        return jsonify({'success': True, 'product': product.to_dict()}), 201
    else:
        # Form POST - redirect after creation
        data = request.form.to_dict()
        command = CreateProductCommand(**data)
        product = mediator.dispatch(command)
        flash(_('Product created successfully'), 'success')
        return redirect(url_for('products.list'))
```

### 7. Translation in Templates

**Using Flask-Babel in Templates**:
```jinja2
{# Simple translation #}
<h1>{{ _('Products') }}</h1>

{# Translation with variables #}
<p>{{ _('Showing %(count)d products', count=products|length) }}</p>

{# Pluralization #}
{{ ngettext('%(num)d product', '%(num)d products', products|length) }}

{# Date formatting #}
{{ format_date(product.created_at) }}

{# Number formatting #}
{{ format_number(product.price) }} €
```

### 8. JavaScript Integration

**API Client** (`static/js/api.js`):
```javascript
// API client with locale support
const API = {
    baseURL: '/api',
    locale: document.documentElement.lang || 'fr',
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}${endpoint.includes('?') ? '&' : '?'}locale=${this.locale}`;
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        return response.json();
    },
    
    async getProducts(filters = {}) {
        const params = new URLSearchParams({locale: this.locale, ...filters});
        return this.request(`/products?${params}`);
    }
};
```

**Language Switcher** (`static/js/i18n.js`):
```javascript
function switchLanguage(locale) {
    const currentUrl = new URL(window.location.href);
    currentUrl.searchParams.set('locale', locale);
    window.location.href = currentUrl.toString();
}
```

## Conversion Checklist

For each design file:

- [ ] Extract common layout to base template
- [ ] Create page template extending base.html
- [ ] Replace hardcoded text with `{{ _('...') }}` translations
- [ ] Replace static data with template variables
- [ ] Add form handling (POST or AJAX)
- [ ] Add RTL support classes
- [ ] Add pagination, filtering, sorting
- [ ] Add error message display
- [ ] Add success/error flash messages
- [ ] Test in both French and Arabic
- [ ] Verify RTL layout for Arabic

## File Mapping

| Design File | Template File | Route |
|------------|---------------|-------|
| `01-login.html` | `templates/auth/login.html` | `/login` |
| `02-dashboard.html` | `templates/dashboard/index.html` | `/dashboard` |
| `03-products-list.html` | `templates/products/list.html` | `/products` |
| `04-product-form.html` | `templates/products/form.html` | `/products/new`, `/products/<id>/edit` |
| `05-customers-list.html` | `templates/customers/list.html` | `/customers` |
| `06-customer-form.html` | `templates/customers/form.html` | `/customers/new`, `/customers/<id>/edit` |
| `07-stock.html` | `templates/stock/index.html` | `/stock` |
| `08-orders-list.html` | `templates/sales/orders_list.html` | `/orders` |
| `09-order-form.html` | `templates/sales/order_form.html` | `/orders/new`, `/orders/<id>/edit` |

## Best Practices

1. **Template Inheritance**: Always extend base.html
2. **Reusable Components**: Use includes for repeated components
3. **Translation Keys**: Use descriptive keys like `products.list.title`
4. **RTL Support**: Always check direction before applying margin/padding classes
5. **Form Validation**: Show validation errors in templates
6. **AJAX Enhancement**: Add JavaScript for dynamic updates without page reload
7. **SEO**: Use proper meta tags, semantic HTML
8. **Performance**: Lazy load images, minimize JavaScript

