# CommerceFlow Animations & Micro-interactions Guide

This document describes all available animations and micro-interactions in CommerceFlow.

## Table of Contents

1. [Button Interactions](#button-interactions)
2. [Form Interactions](#form-interactions)
3. [Page Transitions](#page-transitions)
4. [Loading States](#loading-states)
5. [Visual Feedback](#visual-feedback)
6. [Scroll Animations](#scroll-animations)
7. [Utility Animations](#utility-animations)

---

## Button Interactions

### Loading State

Add loading state to any button:

```javascript
// Set button to loading
setButtonLoading('#my-button', true);

// Remove loading state
setButtonLoading('#my-button', false);
```

Or use the class directly:

```html
<button class="btn-primary btn-loading">Loading...</button>
```

### Ripple Effect

All buttons automatically have ripple effect on click. No additional code needed.

### Hover Effects

Available classes:
- `hover-lift` - Lifts element on hover
- `hover-scale` - Scales element on hover
- `hover-glow` - Adds glow effect on hover

```html
<button class="btn-primary hover-lift">Hover me</button>
<div class="stat-card hover-scale">Card with scale</div>
```

---

## Form Interactions

### Enhanced Form Submission

```javascript
submitFormWithLoading(document.getElementById('my-form'), async function(e) {
  const formData = new FormData(this);
  const response = await fetch('/api/submit', {
    method: 'POST',
    body: formData
  });
  
  if (response.ok) {
    showSuccessToast('Form submitted successfully!');
  }
});
```

### Input Validation Feedback

```javascript
// Show validation feedback
showInputFeedback(inputElement, true, 'Valid email address');
showInputFeedback(inputElement, false, 'Invalid email address');
```

Inputs automatically get validation classes:
- `input-valid` - Green border and checkmark
- `input-invalid` - Red border with shake animation

### Focus Enhancement

All inputs automatically scale slightly on focus for better visual feedback.

---

## Page Transitions

### Automatic Page Enter

Pages automatically fade in on load. No code needed.

### Manual Transitions

```html
<div class="page-enter">Content fades in</div>
<div class="page-enter-right">Content slides from right</div>
<div class="page-enter-left">Content slides from left</div>
```

---

## Loading States

### Spinner

```html
<!-- Inline spinner -->
<div class="modern-spinner"></div>
<div class="modern-spinner modern-spinner-sm"></div>
<div class="modern-spinner modern-spinner-lg"></div>
```

### Skeleton Loading

```html
<!-- Text skeleton -->
<div class="skeleton skeleton-text"></div>
<div class="skeleton skeleton-title"></div>

<!-- Avatar skeleton -->
<div class="skeleton skeleton-avatar"></div>

<!-- Button skeleton -->
<div class="skeleton skeleton-button"></div>
```

### Progress Bar

```html
<div class="progress-bar">
  <div class="progress-fill" style="width: 60%;"></div>
</div>
```

---

## Visual Feedback

### Shake Animation

```html
<div class="shake">Shakes on error</div>
```

Or trigger programmatically:

```javascript
element.classList.add('shake');
setTimeout(() => element.classList.remove('shake'), 500);
```

### Pulse Animation

```html
<div class="pulse">Pulses continuously</div>
```

### Bounce Animation

```html
<div class="bounce">Bounces for attention</div>
```

---

## Scroll Animations

### Animate on Scroll

Add `data-animate-on-scroll` attribute:

```html
<div data-animate-on-scroll>Animates when scrolled into view</div>
```

Automatically initialized on page load.

### Staggered List Animations

```javascript
// Add staggered animation to list items
initStaggeredList('.my-list-item');
```

Or use the class directly:

```html
<ul>
  <li class="stagger-item">Item 1</li>
  <li class="stagger-item">Item 2</li>
  <li class="stagger-item">Item 3</li>
</ul>
```

---

## Utility Animations

### Card Entrance

```html
<div class="card-enter">Card with entrance animation</div>
<div class="card-enter-delay-1">Delayed by 0.1s</div>
<div class="card-enter-delay-2">Delayed by 0.2s</div>
<div class="card-enter-delay-3">Delayed by 0.3s</div>
```

### Smooth Scroll

```javascript
// Smooth scroll to element
smoothScrollTo('#target-element', {
  offset: 100,  // Offset from top
  behavior: 'smooth'
});
```

### Copy to Clipboard

```javascript
// Copy with visual feedback
copyToClipboard('Text to copy', buttonElement);

// Or show toast notification
copyToClipboard('Text to copy');
```

---

## Table Interactions

### Enhanced Row Hover

Table rows automatically have enhanced hover effects with slight translation and shadow.

### Row Click Handler

```javascript
initTableRowClick('.modern-table', function(e) {
  // Handle row click
  const rowId = this.dataset.id;
  window.location.href = `/details/${rowId}`;
});
```

---

## Stat Card Interactions

Stat cards automatically have:
- Hover lift effect
- Scale on hover
- Enhanced shadow

No additional code needed.

---

## Auto-dismiss Alerts

Flash messages automatically dismiss after 5 seconds:

```javascript
// Custom delay
initAutoDismissAlerts(3000); // 3 seconds
```

---

## Best Practices

1. **Performance**: Use `transform` and `opacity` for animations (GPU accelerated)
2. **Accessibility**: All animations respect `prefers-reduced-motion`
3. **Timing**: Keep animations under 300ms for micro-interactions
4. **Feedback**: Always provide visual feedback for user actions
5. **Loading**: Show loading states for operations longer than 300ms

---

## Reduced Motion

All animations automatically respect the user's `prefers-reduced-motion` preference. When enabled, animations are reduced to minimal or disabled entirely.

---

## Browser Support

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile: Full support with optimized performance

---

## Examples

### Complete Form with Loading

```html
<form id="product-form">
  <input type="text" class="modern-input" id="product-name" required>
  <button type="submit" class="btn-primary">Save Product</button>
</form>

<script>
submitFormWithLoading(document.getElementById('product-form'), async function(e) {
  const formData = new FormData(this);
  const response = await fetch('/api/products', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  
  if (result.success) {
    showSuccessToast('Product saved!');
    window.location.href = '/products';
  } else {
    showErrorToast(result.message);
  }
});
</script>
```

### Staggered Card List

```html
<div class="grid grid-cols-3 gap-4">
  <div class="stat-card stagger-item">Card 1</div>
  <div class="stat-card stagger-item">Card 2</div>
  <div class="stat-card stagger-item">Card 3</div>
</div>
```

---

## Performance Tips

1. Use `will-change` sparingly and only for elements that will animate
2. Prefer CSS animations over JavaScript when possible
3. Use `requestAnimationFrame` for JavaScript animations
4. Debounce scroll and resize handlers
5. Use Intersection Observer for scroll animations

