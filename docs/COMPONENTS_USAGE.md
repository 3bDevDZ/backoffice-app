# CommerceFlow Modern Components - Usage Guide

This document describes how to use the modern reusable components in CommerceFlow.

## Table of Contents

1. [Modal Component](#modal-component)
2. [Loading Spinner](#loading-spinner)
3. [Empty State](#empty-state)
4. [Tooltip](#tooltip)
5. [Toast Notifications](#toast-notifications)

---

## Modal Component

### Basic Usage

```html
<!-- Include the modal template -->
{% include 'components/modal.html' with {
  'id': 'my-modal',
  'title': 'Confirm Action',
  'body': '<p>Are you sure you want to proceed?</p>',
  'footer': '<button class="btn-secondary" onclick="closeModal(\'my-modal\')">Cancel</button><button class="btn-primary">Confirm</button>'
} %}

<!-- Trigger button -->
<button onclick="openModal('my-modal')" class="btn-primary">
  Open Modal
</button>
```

### Modal Sizes

- `sm` - Small (24rem / 384px)
- `md` - Medium (32rem / 512px) - Default
- `lg` - Large (48rem / 768px)
- `xl` - Extra Large (64rem / 1024px)

```html
{% include 'components/modal.html' with {
  'id': 'large-modal',
  'title': 'Large Modal',
  'size': 'lg',
  'body': '<p>Content here</p>'
} %}
```

### JavaScript API

```javascript
// Open modal
openModal('my-modal');

// Close modal
closeModal('my-modal');

// Close on Escape key (automatic)
// Close on outside click (automatic)
```

---

## Loading Spinner

### Inline Spinner

```html
<div class="modern-spinner"></div>
<div class="modern-spinner modern-spinner-sm"></div>
<div class="modern-spinner modern-spinner-lg"></div>
```

### Full Page Loading Overlay

```javascript
// Show loading
showLoading('Please wait...');

// Hide loading
hideLoading();
```

---

## Empty State

### Template Include

```html
{% include 'components/empty_state.html' with {
  'icon': 'fas fa-inbox',
  'title': 'No products found',
  'description': 'Start by adding your first product to the catalog.',
  'action': '<a href="{{ url_for(\'products_frontend.create\') }}" class="btn-primary">Add Product</a>'
} %}
```

### JavaScript API

```javascript
const emptyState = createEmptyState({
  icon: 'fas fa-inbox',
  title: 'No data available',
  description: 'There is no data to display.',
  action: '<button class="btn-primary">Add Item</button>'
});

document.getElementById('container').appendChild(emptyState);
```

---

## Tooltip

### HTML Attribute

```html
<button 
  data-tooltip="This is a tooltip"
  data-tooltip-position="top"
  class="btn-primary">
  Hover me
</button>
```

### Positions

- `top` - Default
- `bottom`
- `left`
- `right`

```html
<span data-tooltip="Tooltip text" data-tooltip-position="bottom">
  Hover for tooltip
</span>
```

### JavaScript API

```javascript
// Initialize all tooltips on page
initializeTooltips();
```

---

## Toast Notifications

### JavaScript API

```javascript
// Basic toast
showToast('Operation completed successfully', 'success');

// With title
showToast('Item saved', 'success', 'Success', 5000);

// Different types
showSuccessToast('Saved successfully!');
showErrorToast('An error occurred');
showWarningToast('Please check your input');
showInfoToast('New update available');

// Custom duration (0 = no auto-close)
showToast('Important message', 'warning', 'Warning', 0);
```

### Toast Types

- `success` - Green border, check icon
- `error` - Red border, exclamation icon
- `warning` - Yellow border, warning icon
- `info` - Blue border, info icon

### Auto-close Duration

- Default: 5000ms (5 seconds)
- Error: 7000ms (7 seconds)
- Warning: 6000ms (6 seconds)
- Info: 5000ms (5 seconds)
- Set to `0` to disable auto-close

### Example: Form Submission

```javascript
document.getElementById('my-form').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  showLoading('Saving...');
  
  try {
    const response = await fetch('/api/save', {
      method: 'POST',
      body: new FormData(this)
    });
    
    const result = await response.json();
    
    if (result.success) {
      showSuccessToast('Item saved successfully!');
      // Redirect or update UI
    } else {
      showErrorToast(result.message || 'An error occurred');
    }
  } catch (error) {
    showErrorToast('Network error. Please try again.');
  } finally {
    hideLoading();
  }
});
```

---

## Integration with Flask Flash Messages

You can automatically convert Flask flash messages to toast notifications:

```javascript
// In your template or main.js
{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    {% for category, message in messages %}
      <script>
        showToast('{{ message|tojson|safe }}', '{{ category|default("info") }}');
      </script>
    {% endfor %}
  {% endif %}
{% endwith %}
```

---

## Best Practices

1. **Modals**: Always provide a close button and ensure the modal can be closed via Escape key
2. **Loading**: Show loading state for async operations longer than 300ms
3. **Toasts**: Use appropriate types and durations. Errors should stay longer than success messages
4. **Empty States**: Provide actionable next steps when possible
5. **Tooltips**: Keep tooltip text concise (under 100 characters)

---

## Accessibility

- All components support keyboard navigation
- Focus states are clearly visible
- ARIA labels are included where appropriate
- Screen reader friendly
- Respects `prefers-reduced-motion` for animations

---

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari, Chrome Mobile

---

## Examples

See the following templates for real-world usage:
- `app/templates/stock/locations.html` - Modal usage
- `app/templates/purchases/orders/form.html` - Modal and loading states
- `app/templates/products/list.html` - Empty state (when no products)

