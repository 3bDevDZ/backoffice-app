# CommerceFlow - Design Specification 2024/2025
## Modern Enterprise SaaS Design System

**Version:** 1.0  
**Date:** January 2025  
**Target:** Premium ERP/SaaS Application Aesthetic

---

## 1. Color Palette & Theme

### Primary Color Scheme

#### Main Brand Colors
- **Primary Blue:** `#4F46E5` (Indigo-600) - Main actions, links, active states
- **Primary Dark:** `#312E81` (Indigo-800) - Sidebar background, headers
- **Primary Light:** `#6366F1` (Indigo-500) - Hover states, accents
- **Primary Lighter:** `#818CF8` (Indigo-400) - Subtle accents, borders

#### Secondary Colors
- **Success Green:** `#10B981` (Emerald-500) - Success states, positive metrics
- **Success Light:** `#D1FAE5` (Emerald-100) - Success backgrounds
- **Warning Amber:** `#F59E0B` (Amber-500) - Warnings, draft states
- **Warning Light:** `#FEF3C7` (Amber-100) - Warning backgrounds
- **Error Red:** `#EF4444` (Red-500) - Errors, cancelled states
- **Error Light:** `#FEE2E2` (Red-100) - Error backgrounds
- **Info Blue:** `#3B82F6` (Blue-500) - Information, confirmed states
- **Info Light:** `#DBEAFE` (Blue-100) - Info backgrounds

#### Neutral Palette
- **Background Primary:** `#F8FAFC` (Slate-50) - Main content background
- **Background Secondary:** `#FFFFFF` - Cards, panels
- **Background Tertiary:** `#F1F5F9` (Slate-100) - Subtle sections
- **Text Primary:** `#0F172A` (Slate-900) - Headings, important text
- **Text Secondary:** `#475569` (Slate-600) - Body text, descriptions
- **Text Tertiary:** `#94A3B8` (Slate-400) - Placeholders, disabled text
- **Border Default:** `#E2E8F0` (Slate-200) - Standard borders
- **Border Light:** `#F1F5F9` (Slate-100) - Subtle dividers

#### Sidebar Colors
- **Sidebar Background:** `#1E293B` (Slate-800) - Modern dark slate instead of indigo
- **Sidebar Hover:** `#334155` (Slate-700) - Hover states
- **Sidebar Active:** `#475569` (Slate-600) - Active menu item
- **Sidebar Text:** `#F1F5F9` (Slate-100) - Primary text
- **Sidebar Text Muted:** `#94A3B8` (Slate-400) - Section headers
- **Sidebar Accent:** `#6366F1` (Indigo-500) - Active indicator bar

### Gradient Overlays
- **Primary Gradient:** `linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)` - Premium feel
- **Card Gradient:** `linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)` - Subtle depth
- **Sidebar Gradient:** `linear-gradient(180deg, #1E293B 0%, #0F172A 100%)` - Depth

### Color Usage Guidelines
- Use primary colors for interactive elements (buttons, links, active states)
- Use semantic colors (green/red/amber) sparingly and only for status
- Maintain 4.5:1 contrast ratio minimum for accessibility
- Use neutral grays for text hierarchy

---

## 2. Typography

### Font Family Stack
```css
Primary Font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
Monospace: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace
```

**Recommendation:** Use Google Fonts Inter (weights: 400, 500, 600, 700)

### Type Scale

#### Headings
- **H1 (Page Title):**
  - Font-size: `2.25rem` (36px)
  - Font-weight: `700` (Bold)
  - Line-height: `1.2`
  - Letter-spacing: `-0.02em`
  - Color: `#0F172A` (Slate-900)

- **H2 (Section Title):**
  - Font-size: `1.875rem` (30px)
  - Font-weight: `600` (Semi-bold)
  - Line-height: `1.3`
  - Letter-spacing: `-0.01em`
  - Color: `#0F172A` (Slate-900)

- **H3 (Subsection):**
  - Font-size: `1.5rem` (24px)
  - Font-weight: `600` (Semi-bold)
  - Line-height: `1.4`
  - Color: `#1E293B` (Slate-800)

- **H4 (Card Title):**
  - Font-size: `1.25rem` (20px)
  - Font-weight: `600` (Semi-bold)
  - Line-height: `1.4`
  - Color: `#1E293B` (Slate-800)

#### Body Text
- **Body Large:**
  - Font-size: `1.125rem` (18px)
  - Font-weight: `400` (Regular)
  - Line-height: `1.6`
  - Color: `#475569` (Slate-600)

- **Body Regular:**
  - Font-size: `1rem` (16px)
  - Font-weight: `400` (Regular)
  - Line-height: `1.6`
  - Color: `#475569` (Slate-600)

- **Body Small:**
  - Font-size: `0.875rem` (14px)
  - Font-weight: `400` (Regular)
  - Line-height: `1.5`
  - Color: `#64748B` (Slate-500)

#### UI Elements
- **Button Text:**
  - Font-size: `0.9375rem` (15px)
  - Font-weight: `500` (Medium)
  - Letter-spacing: `0.01em`

- **Label Text:**
  - Font-size: `0.875rem` (14px)
  - Font-weight: `500` (Medium)
  - Color: `#475569` (Slate-600)

- **Caption/Helper:**
  - Font-size: `0.75rem` (12px)
  - Font-weight: `400` (Regular)
  - Color: `#94A3B8` (Slate-400)

---

## 3. Layout & Spacing

### Grid System
- **Container Max Width:** `1280px` (xl breakpoint)
- **Container Padding:** `1.5rem` (24px) on mobile, `2rem` (32px) on desktop
- **Grid Gutter:** `1.5rem` (24px) standard, `2rem` (32px) for large sections

### Spacing Scale (8px base unit)
- **xs:** `0.25rem` (4px) - Tight spacing
- **sm:** `0.5rem` (8px) - Small spacing
- **md:** `1rem` (16px) - Medium spacing
- **lg:** `1.5rem` (24px) - Large spacing
- **xl:** `2rem` (32px) - Extra large spacing
- **2xl:** `3rem` (48px) - Section spacing
- **3xl:** `4rem` (64px) - Major section spacing

### Component Spacing
- **Card Padding:** `1.5rem` (24px) standard, `2rem` (32px) for important cards
- **Card Gap:** `1.5rem` (24px) between cards
- **Form Field Spacing:** `1.25rem` (20px) vertical between fields
- **Button Padding:** `0.75rem 1.5rem` (12px 24px) standard buttons
- **Table Cell Padding:** `1rem 1.25rem` (16px 20px)
- **Sidebar Item Padding:** `0.75rem 1.5rem` (12px 24px)

### Layout Structure
- **Sidebar Width:** `280px` (expanded), `80px` (collapsed)
- **Top Bar Height:** `72px` (4.5rem)
- **Content Padding:** `2rem` (32px) top/bottom, `2.5rem` (40px) left/right
- **Section Margin:** `2rem` (32px) between major sections

---

## 4. Component Styling

### Statistics Cards

#### Base Card Style
- **Background:** `#FFFFFF` (white)
- **Border:** `1px solid #E2E8F0` (Slate-200)
- **Border Radius:** `16px` (rounded-2xl)
- **Padding:** `1.5rem` (24px)
- **Box Shadow:** `0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)`
- **Transition:** `all 0.2s ease-in-out`

#### Enhanced Card with Gradient Accent
- **Border Left:** `4px solid` (color varies by metric type)
- **Gradient Overlay:** Subtle gradient from top-left corner
- **Hover Effect:** 
  - Shadow: `0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)`
  - Transform: `translateY(-2px)`
  - Border color intensifies

#### Metric Value Styling
- **Font Size:** `2rem` (32px) for main number
- **Font Weight:** `700` (Bold)
- **Color:** Varies by status (use semantic colors)
- **Line Height:** `1.2`
- **Icon:** `1.5rem` (24px) size, positioned top-right with opacity `0.1`

#### Label Styling
- **Font Size:** `0.875rem` (14px)
- **Font Weight:** `500` (Medium)
- **Color:** `#64748B` (Slate-500)
- **Text Transform:** `uppercase`
- **Letter Spacing:** `0.05em`

#### Card Variants by Status
- **Total/Draft:** Left border `#F59E0B` (Amber-500), subtle amber gradient
- **Confirmed:** Left border `#3B82F6` (Blue-500), subtle blue gradient
- **Received:** Left border `#10B981` (Emerald-500), subtle green gradient
- **Cancelled:** Left border `#EF4444` (Red-500), subtle red gradient

### Data Tables

#### Table Container
- **Background:** `#FFFFFF` (white)
- **Border Radius:** `12px` (rounded-xl)
- **Border:** `1px solid #E2E8F0` (Slate-200)
- **Overflow:** `hidden` (for rounded corners)
- **Box Shadow:** `0 1px 3px 0 rgba(0, 0, 0, 0.1)`

#### Table Header
- **Background:** `#F8FAFC` (Slate-50)
- **Border Bottom:** `2px solid #E2E8F0` (Slate-200)
- **Padding:** `1rem 1.25rem` (16px 20px)
- **Font Weight:** `600` (Semi-bold)
- **Font Size:** `0.875rem` (14px)
- **Text Transform:** `uppercase`
- **Letter Spacing:** `0.05em`
- **Color:** `#475569` (Slate-600)

#### Table Rows
- **Padding:** `1rem 1.25rem` (16px 20px)
- **Border Bottom:** `1px solid #F1F5F9` (Slate-100)
- **Transition:** `background-color 0.15s ease-in-out`
- **Hover State:**
  - Background: `#F8FAFC` (Slate-50)
  - Cursor: `pointer`
  - Transform: `scale(1.001)` (subtle)

#### Table Cells
- **Vertical Alignment:** `middle`
- **Font Size:** `0.9375rem` (15px)
- **Color:** `#1E293B` (Slate-800)

#### Alternating Rows (Optional)
- **Even Rows:** Background `#FAFBFC` (very subtle)
- **Odd Rows:** Background `#FFFFFF` (white)

#### Table Actions Column
- **Width:** `120px`
- **Text Align:** `right`
- **Button Spacing:** `0.5rem` (8px) between action buttons

### Sidebar Navigation

#### Sidebar Container
- **Background:** `#1E293B` (Slate-800) with subtle gradient
- **Width:** `280px` (expanded), `80px` (collapsed)
- **Box Shadow:** `4px 0 6px -1px rgba(0, 0, 0, 0.1)`
- **Border Right:** `1px solid #334155` (Slate-700)

#### Logo Section
- **Height:** `72px` (4.5rem)
- **Padding:** `1rem 1.5rem` (16px 24px)
- **Border Bottom:** `1px solid #334155` (Slate-700)
- **Background:** `#0F172A` (Slate-900)

#### Navigation Items
- **Padding:** `0.75rem 1.5rem` (12px 24px)
- **Margin:** `0.25rem 0.5rem` (4px 8px) vertical
- **Border Radius:** `8px` (rounded-lg)
- **Transition:** `all 0.2s ease-in-out`

#### Active State
- **Background:** `#334155` (Slate-700)
- **Border Left:** `3px solid #6366F1` (Indigo-500)
- **Color:** `#FFFFFF` (white)
- **Font Weight:** `600` (Semi-bold)

#### Hover State
- **Background:** `#334155` (Slate-700)
- **Transform:** `translateX(2px)` (subtle slide)
- **Opacity:** `0.9`

#### Icon Styling
- **Width:** `1.25rem` (20px)
- **Height:** `1.25rem` (20px)
- **Margin Right:** `0.75rem` (12px)
- **Color:** `#CBD5E1` (Slate-300)
- **Active Icon Color:** `#6366F1` (Indigo-500)

#### Section Headers
- **Padding:** `1rem 1.5rem 0.5rem` (16px 24px 8px)
- **Font Size:** `0.75rem` (12px)
- **Font Weight:** `600` (Semi-bold)
- **Text Transform:** `uppercase`
- **Letter Spacing:** `0.1em`
- **Color:** `#94A3B8` (Slate-400)

### Buttons

#### Primary Button
- **Background:** `#4F46E5` (Indigo-600)
- **Background Hover:** `#4338CA` (Indigo-700)
- **Color:** `#FFFFFF` (white)
- **Padding:** `0.75rem 1.5rem` (12px 24px)
- **Border Radius:** `10px` (rounded-lg)
- **Font Weight:** `500` (Medium)
- **Font Size:** `0.9375rem` (15px)
- **Box Shadow:** `0 4px 6px -1px rgba(79, 70, 229, 0.3), 0 2px 4px -2px rgba(79, 70, 229, 0.3)`
- **Hover Shadow:** `0 10px 15px -3px rgba(79, 70, 229, 0.4), 0 4px 6px -4px rgba(79, 70, 229, 0.4)`
- **Transform Hover:** `translateY(-1px)`
- **Transition:** `all 0.2s ease-in-out`
- **Cursor:** `pointer`

#### Secondary Button
- **Background:** `#FFFFFF` (white)
- **Background Hover:** `#F8FAFC` (Slate-50)
- **Color:** `#475569` (Slate-600)
- **Border:** `1px solid #E2E8F0` (Slate-200)
- **Border Hover:** `1px solid #CBD5E1` (Slate-300)
- **Padding:** `0.75rem 1.5rem` (12px 24px)
- **Border Radius:** `10px` (rounded-lg)
- **Box Shadow:** `0 1px 2px 0 rgba(0, 0, 0, 0.05)`
- **Hover Shadow:** `0 4px 6px -1px rgba(0, 0, 0, 0.1)`

#### Ghost Button
- **Background:** `transparent`
- **Background Hover:** `#F1F5F9` (Slate-100)
- **Color:** `#475569` (Slate-600)
- **Border:** `none`
- **Padding:** `0.5rem 1rem` (8px 16px)

#### Icon Button
- **Padding:** `0.5rem` (8px)
- **Border Radius:** `8px` (rounded-lg)
- **Width/Height:** `2.5rem` (40px)
- **Display:** `flex`, `align-items: center`, `justify-content: center`

### Form Elements

#### Input Fields
- **Background:** `#FFFFFF` (white)
- **Border:** `1px solid #E2E8F0` (Slate-200)
- **Border Radius:** `10px` (rounded-lg)
- **Padding:** `0.75rem 1rem` (12px 16px)
- **Font Size:** `0.9375rem` (15px)
- **Color:** `#1E293B` (Slate-800)
- **Transition:** `all 0.2s ease-in-out`

#### Input Focus State
- **Border:** `2px solid #4F46E5` (Indigo-600)
- **Box Shadow:** `0 0 0 3px rgba(79, 70, 229, 0.1)`
- **Outline:** `none`

#### Input Hover State
- **Border:** `1px solid #CBD5E1` (Slate-300)`

#### Select Dropdowns
- **Same as Input Fields**
- **Background Image:** Custom chevron icon
- **Padding Right:** `2.5rem` (40px) for icon space

#### Textarea
- **Min Height:** `120px`
- **Resize:** `vertical` only

#### Labels
- **Font Size:** `0.875rem` (14px)
- **Font Weight:** `500` (Medium)
- **Color:** `#475569` (Slate-600)
- **Margin Bottom:** `0.5rem` (8px)
- **Display:** `block`

#### Helper Text
- **Font Size:** `0.75rem` (12px)
- **Color:** `#94A3B8` (Slate-400)
- **Margin Top:** `0.25rem` (4px)

#### Error States
- **Border:** `2px solid #EF4444` (Red-500)
- **Background:** `#FEF2F2` (Red-50)
- **Error Text Color:** `#DC2626` (Red-600)

### Status Badges

#### Base Badge
- **Display:** `inline-flex`
- **Align Items:** `center`
- **Padding:** `0.375rem 0.75rem` (6px 12px)
- **Border Radius:** `6px` (rounded-md)
- **Font Size:** `0.75rem` (12px)
- **Font Weight:** `600` (Semi-bold)
- **Text Transform:** `uppercase`
- **Letter Spacing:** `0.05em`

#### Badge Variants
- **Draft:**
  - Background: `#FEF3C7` (Amber-100)
  - Color: `#92400E` (Amber-800)
  - Border: `1px solid #FCD34D` (Amber-300)

- **Confirmed:**
  - Background: `#DBEAFE` (Blue-100)
  - Color: `#1E40AF` (Blue-800)
  - Border: `1px solid #93C5FD` (Blue-300)

- **Received:**
  - Background: `#D1FAE5` (Emerald-100)
  - Color: `#065F46` (Emerald-800)
  - Border: `1px solid #6EE7B7` (Emerald-300)

- **Cancelled:**
  - Background: `#FEE2E2` (Red-100)
  - Color: `#991B1B` (Red-800)
  - Border: `1px solid #FCA5A5` (Red-300)

- **Partially Received:**
  - Background: `#F3E8FF` (Purple-100)
  - Color: `#6B21A8` (Purple-800)
  - Border: `1px solid #C4B5FD` (Purple-300)

---

## 5. Visual Enhancements

### Shadows & Depth

#### Elevation Levels
- **Level 0 (Flat):** No shadow
- **Level 1 (Subtle):** `0 1px 2px 0 rgba(0, 0, 0, 0.05)`
- **Level 2 (Card):** `0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)`
- **Level 3 (Raised):** `0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)`
- **Level 4 (Floating):** `0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)`
- **Level 5 (Modal):** `0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)`

#### Shadow Usage
- **Cards:** Level 2
- **Buttons:** Level 3 (hover: Level 4)
- **Dropdowns:** Level 4
- **Modals:** Level 5
- **Sidebar:** Level 2 (right side only)

### Border Radius

#### Radius Scale
- **xs:** `4px` (rounded) - Small elements, badges
- **sm:** `6px` (rounded-md) - Buttons, inputs
- **md:** `8px` (rounded-lg) - Cards, containers
- **lg:** `12px` (rounded-xl) - Large cards, modals
- **xl:** `16px` (rounded-2xl) - Statistics cards, hero sections
- **2xl:** `24px` (rounded-3xl) - Special containers

#### Usage Guidelines
- **Buttons:** `10px` (between sm and md)
- **Input Fields:** `10px`
- **Cards:** `16px` (xl)
- **Tables:** `12px` (lg) container, `0px` internal
- **Badges:** `6px` (sm)
- **Modals:** `16px` (xl)

### Icons

#### Icon Library Recommendation
**Primary:** Font Awesome 6.4.0 (already in use)  
**Alternative:** Heroicons (for more modern, minimal look)

#### Icon Sizing
- **xs:** `0.75rem` (12px) - Inline text
- **sm:** `1rem` (16px) - Small buttons
- **md:** `1.25rem` (20px) - Standard buttons, navigation
- **lg:** `1.5rem` (24px) - Large buttons, card icons
- **xl:** `2rem` (32px) - Hero sections, empty states

#### Icon Colors
- **Default:** `#64748B` (Slate-500)
- **Active:** `#6366F1` (Indigo-500)
- **Hover:** `#475569` (Slate-600)
- **Success:** `#10B981` (Emerald-500)
- **Warning:** `#F59E0B` (Amber-500)
- **Error:** `#EF4444` (Red-500)

#### Icon Spacing
- **With Text:** `0.5rem` (8px) margin
- **Button Icons:** `0.375rem` (6px) margin

### Micro-interactions & Hover States

#### Button Hover
- **Transform:** `translateY(-1px)`
- **Shadow Increase:** One level up
- **Transition:** `all 0.2s ease-in-out`

#### Card Hover
- **Transform:** `translateY(-2px)`
- **Shadow:** Level 3 to Level 4
- **Border Color:** Slight darkening
- **Transition:** `all 0.2s ease-in-out`

#### Link Hover
- **Color:** Darken by 10%
- **Underline:** Optional subtle underline
- **Transition:** `color 0.15s ease-in-out`

#### Input Focus
- **Scale:** `1.01` (very subtle)
- **Border:** 2px solid primary color
- **Shadow:** `0 0 0 3px rgba(79, 70, 229, 0.1)`
- **Transition:** `all 0.2s ease-in-out`

#### Table Row Hover
- **Background:** `#F8FAFC` (Slate-50)
- **Transform:** `scale(1.001)` (imperceptible but adds depth)
- **Transition:** `background-color 0.15s ease-in-out`

#### Sidebar Item Hover
- **Background:** `#334155` (Slate-700)
- **Transform:** `translateX(2px)` (slide right)
- **Transition:** `all 0.2s ease-in-out`

### Gradient Overlays

#### Card Gradients
- **Subtle:** `linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)`
- **Accent:** `linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)` (for premium cards)

#### Background Gradients
- **Page Background:** `linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 100%)`
- **Sidebar:** `linear-gradient(180deg, #1E293B 0%, #0F172A 100%)`

#### Gradient Usage
- Use gradients sparingly for premium feel
- Keep opacity low (10-20%) for overlays
- Apply to cards, buttons, or accent elements

---

## 6. Modern UI Patterns

### Glass Morphism (Optional - Use Sparingly)

#### Glass Card Style
- **Background:** `rgba(255, 255, 255, 0.7)`
- **Backdrop Filter:** `blur(10px)`
- **Border:** `1px solid rgba(255, 255, 255, 0.2)`
- **Box Shadow:** `0 8px 32px 0 rgba(31, 38, 135, 0.37)`
- **Use Case:** Modals, floating panels, notifications

### Neumorphism (Not Recommended)
- Too trendy, may date quickly
- Not accessible enough
- Skip for enterprise application

### Soft Shadows & Depth
- **Primary Pattern:** Use layered shadows for depth
- **Multiple Shadows:** Combine 2-3 shadow layers
- **Example:** `0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)`

### Rounded Corners (Modern Approach)
- **Consistent Radius:** Use 12-16px for most elements
- **Asymmetric:** Larger radius on top corners for cards
- **Avoid:** Over-rounding (keep it professional)

### Empty States
- **Icon Size:** `3rem` (48px)
- **Icon Color:** `#CBD5E1` (Slate-300)
- **Text Color:** `#64748B` (Slate-500)
- **Background:** Subtle pattern or gradient
- **Padding:** `3rem` (48px) vertical

### Loading States
- **Skeleton Loaders:** Use for content placeholders
- **Color:** `#F1F5F9` (Slate-100) background
- **Animation:** Subtle pulse or shimmer
- **Spinner:** Use primary color with 2s rotation

### Tooltips
- **Background:** `#1E293B` (Slate-800)
- **Color:** `#FFFFFF` (white)
- **Padding:** `0.5rem 0.75rem` (8px 12px)
- **Border Radius:** `6px` (rounded-md)
- **Font Size:** `0.75rem` (12px)
- **Arrow:** 4px triangle
- **Shadow:** Level 4

### Dropdowns & Menus
- **Background:** `#FFFFFF` (white)
- **Border:** `1px solid #E2E8F0` (Slate-200)
- **Border Radius:** `10px` (rounded-lg)
- **Padding:** `0.5rem` (8px)
- **Box Shadow:** Level 4
- **Min Width:** `200px`
- **Max Height:** `300px` with scroll

### Modals
- **Overlay:** `rgba(0, 0, 0, 0.5)` with backdrop blur
- **Background:** `#FFFFFF` (white)
- **Border Radius:** `16px` (rounded-2xl)
- **Padding:** `2rem` (32px)
- **Max Width:** `600px` (standard), `900px` (large)
- **Box Shadow:** Level 5
- **Animation:** Fade in + scale (0.95 to 1.0)

---

## 7. Responsive Design

### Breakpoints
- **Mobile:** `< 640px` (sm)
- **Tablet:** `640px - 1024px` (md-lg)
- **Desktop:** `> 1024px` (xl+)

### Mobile Adaptations
- **Sidebar:** Hidden by default, overlay on mobile
- **Cards:** Full width, stacked
- **Tables:** Horizontal scroll or card view
- **Padding:** Reduced to `1rem` (16px)
- **Font Sizes:** Slightly reduced (0.875rem base)

### Tablet Adaptations
- **Sidebar:** Collapsible, can be toggled
- **Grid:** 2 columns for cards
- **Tables:** Full width with scroll

---

## 8. Accessibility

### Color Contrast
- **Text on White:** Minimum 4.5:1 ratio
- **Text on Colored:** Minimum 4.5:1 ratio
- **Large Text:** Minimum 3:1 ratio

### Focus States
- **Visible Focus:** `2px solid #4F46E5` (Indigo-600)
- **Focus Ring:** `0 0 0 3px rgba(79, 70, 229, 0.2)`
- **Never Remove:** Focus outlines are essential

### Interactive Elements
- **Minimum Touch Target:** `44px × 44px`
- **Spacing Between:** `8px` minimum
- **Keyboard Navigation:** Full support required

---

## 9. Implementation Notes

### CSS Framework
- **Current:** Tailwind CSS (via CDN)
- **Recommendation:** Continue with Tailwind, but configure custom theme
- **Custom Config:** Extend Tailwind config with these color values

### Custom CSS File
Create `app/static/css/theme.css` with:
- Custom properties (CSS variables) for colors
- Utility classes for gradients
- Animation keyframes
- Component-specific overrides

### Icon Integration
- Keep Font Awesome 6.4.0
- Consider adding Heroicons for modern alternatives
- Use consistent sizing throughout

### Performance
- **Lazy Load:** Images and heavy components
- **Optimize Shadows:** Use transform instead of box-shadow where possible
- **Reduce Animations:** On low-end devices (prefers-reduced-motion)

---

## 10. Design Tokens Summary

### Quick Reference

```css
/* Colors */
--primary: #4F46E5;
--primary-dark: #312E81;
--success: #10B981;
--warning: #F59E0B;
--error: #EF4444;
--background: #F8FAFC;
--text-primary: #0F172A;
--text-secondary: #475569;
--border: #E2E8F0;

/* Spacing */
--spacing-xs: 0.25rem;  /* 4px */
--spacing-sm: 0.5rem;   /* 8px */
--spacing-md: 1rem;    /* 16px */
--spacing-lg: 1.5rem;  /* 24px */
--spacing-xl: 2rem;    /* 32px */

/* Border Radius */
--radius-sm: 6px;
--radius-md: 10px;
--radius-lg: 12px;
--radius-xl: 16px;

/* Shadows */
--shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
--shadow-md: 0 1px 3px rgba(0,0,0,0.1);
--shadow-lg: 0 4px 6px rgba(0,0,0,0.1);
--shadow-xl: 0 10px 15px rgba(0,0,0,0.1);
```

---

## 11. Migration Strategy

### Phase 1: Foundation
1. Update color palette in Tailwind config
2. Update typography (add Inter font)
3. Update spacing scale

### Phase 2: Components
1. Redesign statistics cards
2. Modernize tables
3. Update sidebar styling
4. Enhance buttons

### Phase 3: Polish
1. Add micro-interactions
2. Implement hover states
3. Add loading states
4. Enhance empty states

### Phase 4: Advanced
1. Add glass morphism (optional)
2. Implement animations
3. Add tooltips
4. Enhance modals

---

**End of Design Specification**

This document provides a comprehensive guide for modernizing CommerceFlow's UI. Implement changes incrementally, testing at each phase to ensure consistency and user experience.

