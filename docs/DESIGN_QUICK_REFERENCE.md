# CommerceFlow - Design Quick Reference
## CSS Values & Design Tokens

Quick reference for implementing the modern design system.

---

## 🎨 Color Palette

### Primary Colors
```css
--primary: #4F46E5;        /* Indigo-600 - Main actions */
--primary-dark: #312E81;   /* Indigo-800 - Sidebar */
--primary-light: #6366F1;  /* Indigo-500 - Hover */
```

### Semantic Colors
```css
--success: #10B981;        /* Emerald-500 */
--warning: #F59E0B;        /* Amber-500 */
--error: #EF4444;          /* Red-500 */
--info: #3B82F6;           /* Blue-500 */
```

### Neutrals
```css
--bg-primary: #F8FAFC;      /* Slate-50 */
--bg-secondary: #FFFFFF;   /* White */
--text-primary: #0F172A;   /* Slate-900 */
--text-secondary: #475569; /* Slate-600 */
--border: #E2E8F0;        /* Slate-200 */
```

### Sidebar
```css
--sidebar-bg: #1E293B;    /* Slate-800 */
--sidebar-hover: #334155; /* Slate-700 */
--sidebar-active: #475569; /* Slate-600 */
```

---

## 📐 Spacing Scale (8px base)

```css
--spacing-xs: 0.25rem;  /* 4px */
--spacing-sm: 0.5rem;  /* 8px */
--spacing-md: 1rem;    /* 16px */
--spacing-lg: 1.5rem;  /* 24px */
--spacing-xl: 2rem;    /* 32px */
--spacing-2xl: 3rem;   /* 48px */
--spacing-3xl: 4rem;   /* 64px */
```

---

## 🔲 Border Radius

```css
--radius-xs: 4px;   /* Small elements */
--radius-sm: 6px;   /* Badges */
--radius-md: 10px;  /* Buttons, inputs */
--radius-lg: 12px;  /* Cards, containers */
--radius-xl: 16px;  /* Statistics cards */
--radius-2xl: 24px; /* Special containers */
```

---

## 🌑 Shadows (Elevation Levels)

```css
/* Level 1 - Subtle */
box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);

/* Level 2 - Card */
box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);

/* Level 3 - Raised */
box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);

/* Level 4 - Floating */
box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);

/* Level 5 - Modal */
box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
```

---

## 📝 Typography

### Font Family
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

### Font Sizes
```css
--text-xs: 0.75rem;    /* 12px - Captions */
--text-sm: 0.875rem;  /* 14px - Small text */
--text-base: 1rem;    /* 16px - Body */
--text-lg: 1.125rem;  /* 18px - Large body */
--text-xl: 1.25rem;   /* 20px - H4 */
--text-2xl: 1.5rem;   /* 24px - H3 */
--text-3xl: 1.875rem; /* 30px - H2 */
--text-4xl: 2.25rem;  /* 36px - H1 */
```

### Font Weights
```css
--weight-normal: 400;
--weight-medium: 500;
--weight-semibold: 600;
--weight-bold: 700;
```

---

## 🎴 Statistics Cards

```css
/* Base Card */
background: #FFFFFF;
border: 1px solid #E2E8F0;
border-radius: 16px;
padding: 1.5rem;
box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
transition: all 0.2s ease-in-out;

/* With Left Border Accent */
border-left: 4px solid; /* Color varies by status */

/* Hover State */
transform: translateY(-2px);
box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
```

### Metric Value
```css
font-size: 2rem;      /* 32px */
font-weight: 700;
line-height: 1.2;
```

### Label
```css
font-size: 0.875rem;  /* 14px */
font-weight: 500;
color: #64748B;
text-transform: uppercase;
letter-spacing: 0.05em;
```

---

## 📊 Data Tables

```css
/* Table Container */
background: #FFFFFF;
border-radius: 12px;
border: 1px solid #E2E8F0;
overflow: hidden;
box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);

/* Table Header */
background: #F8FAFC;
border-bottom: 2px solid #E2E8F0;
padding: 1rem 1.25rem;
font-weight: 600;
font-size: 0.875rem;
text-transform: uppercase;
letter-spacing: 0.05em;
color: #475569;

/* Table Row */
padding: 1rem 1.25rem;
border-bottom: 1px solid #F1F5F9;
transition: background-color 0.15s ease-in-out;

/* Table Row Hover */
background: #F8FAFC;
transform: scale(1.001);
```

---

## 🎯 Sidebar Navigation

```css
/* Sidebar Container */
background: #1E293B;
width: 280px; /* expanded */
width: 80px;  /* collapsed */
box-shadow: 4px 0 6px -1px rgba(0, 0, 0, 0.1);
border-right: 1px solid #334155;

/* Navigation Item */
padding: 0.75rem 1.5rem;
border-radius: 8px;
margin: 0.25rem 0.5rem;
transition: all 0.2s ease-in-out;

/* Active State */
background: #334155;
border-left: 3px solid #6366F1;
color: #FFFFFF;
font-weight: 600;

/* Hover State */
background: #334155;
transform: translateX(2px);
```

---

## 🔘 Buttons

### Primary Button
```css
background: #4F46E5;
color: #FFFFFF;
padding: 0.75rem 1.5rem;
border-radius: 10px;
font-weight: 500;
font-size: 0.9375rem;
box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.3), 0 2px 4px -2px rgba(79, 70, 229, 0.3);
transition: all 0.2s ease-in-out;

/* Hover */
background: #4338CA;
transform: translateY(-1px);
box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.4), 0 4px 6px -4px rgba(79, 70, 229, 0.4);
```

### Secondary Button
```css
background: #FFFFFF;
color: #475569;
border: 1px solid #E2E8F0;
padding: 0.75rem 1.5rem;
border-radius: 10px;
box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);

/* Hover */
background: #F8FAFC;
border-color: #CBD5E1;
box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
```

---

## 📝 Form Elements

### Input Field
```css
background: #FFFFFF;
border: 1px solid #E2E8F0;
border-radius: 10px;
padding: 0.75rem 1rem;
font-size: 0.9375rem;
color: #1E293B;
transition: all 0.2s ease-in-out;

/* Focus */
border: 2px solid #4F46E5;
box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
outline: none;
transform: scale(1.01);
```

### Label
```css
font-size: 0.875rem;
font-weight: 500;
color: #475569;
margin-bottom: 0.5rem;
display: block;
```

---

## 🏷️ Status Badges

```css
/* Base Badge */
display: inline-flex;
align-items: center;
padding: 0.375rem 0.75rem;
border-radius: 6px;
font-size: 0.75rem;
font-weight: 600;
text-transform: uppercase;
letter-spacing: 0.05em;

/* Draft */
background: #FEF3C7;
color: #92400E;
border: 1px solid #FCD34D;

/* Confirmed */
background: #DBEAFE;
color: #1E40AF;
border: 1px solid #93C5FD;

/* Received */
background: #D1FAE5;
color: #065F46;
border: 1px solid #6EE7B7;

/* Cancelled */
background: #FEE2E2;
color: #991B1B;
border: 1px solid #FCA5A5;
```

---

## ✨ Micro-interactions

### Hover Transitions
```css
transition: all 0.2s ease-in-out;
```

### Button Hover
```css
transform: translateY(-1px);
```

### Card Hover
```css
transform: translateY(-2px);
```

### Sidebar Item Hover
```css
transform: translateX(2px);
```

---

## 🎨 Gradients

### Primary Gradient
```css
background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
```

### Card Gradient
```css
background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
```

### Sidebar Gradient
```css
background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
```

---

## 📱 Responsive Breakpoints

```css
/* Mobile */
@media (max-width: 640px) { }

/* Tablet */
@media (min-width: 641px) and (max-width: 1024px) { }

/* Desktop */
@media (min-width: 1025px) { }
```

---

## ♿ Accessibility

### Focus States
```css
outline: 2px solid #4F46E5;
outline-offset: 2px;
box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
```

### Minimum Touch Target
```css
min-width: 44px;
min-height: 44px;
```

---

**Quick Reference End**

For detailed explanations, see `DESIGN_SPECIFICATION_2025.md`

