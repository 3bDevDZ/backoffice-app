#!/usr/bin/env python3
"""
Script to modernize form templates with the new design system.
Replaces old Tailwind classes with modern design classes and CSS variables.
"""

import re
import os
from pathlib import Path

# Template files to modernize
FORM_TEMPLATES = [
    "app/templates/products/form.html",
    "app/templates/customers/form.html",
    "app/templates/purchases/suppliers/form.html",
    "app/templates/purchases/orders/form.html",
    "app/templates/sales/order_form.html",
    "app/templates/sales/quote_form.html",
]

# Replacement patterns
REPLACEMENTS = [
    # Card containers
    (r'class="bg-white rounded-xl shadow-sm border border-gray-100 p-6"', 
     'style="background: var(--color-bg-secondary); border: 1px solid var(--color-border-default); border-radius: var(--radius-xl); padding: var(--spacing-lg); box-shadow: var(--shadow-md);"'),
    
    # Headings
    (r'class="text-lg font-bold text-gray-900 mb-4"', 
     'class="text-lg font-bold mb-4" style="color: var(--color-text-primary);"'),
    
    # Labels
    (r'class="block text-sm font-medium text-gray-700 mb-2"', 
     'class="block text-sm font-medium mb-2" style="color: var(--color-text-secondary);"'),
    
    # Required asterisks
    (r'<span class="text-red-500">\*</span>', 
     '<span style="color: var(--color-error);">*</span>'),
    
    # Input fields
    (r'class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"', 
     'class="modern-input"'),
    (r'class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"', 
     'class="modern-input"'),
    
    # Select fields
    (r'class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"', 
     'class="modern-select"'),
    
    # Textareas
    (r'class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"', 
     'class="modern-input"'),
    
    # Buttons - Cancel/Secondary
    (r'class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"', 
     'class="btn-secondary"'),
    (r'class="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"', 
     'class="btn-secondary"'),
    
    # Buttons - Primary/Submit
    (r'class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"', 
     'class="btn-primary"'),
    (r'class="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"', 
     'class="btn-primary"'),
    
    # Small action buttons
    (r'class="px-3 py-1 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"', 
     'class="btn-primary" style="padding: var(--spacing-sm) var(--spacing-md); font-size: var(--font-size-sm);"'),
    
    # Radio button labels
    (r'<span class="{% if direction == \'rtl\' %}mr-2{% else %}ml-2{% endif %} text-sm text-gray-700">', 
     '<span class="{% if direction == \'rtl\' %}mr-2{% else %}ml-2{% endif %} text-sm" style="color: var(--color-text-secondary);">'),
    
    # Info boxes
    (r'class="bg-indigo-50 border border-indigo-200 rounded-lg p-4"', 
     'style="background: var(--color-info-light); border: 1px solid var(--color-info); border-radius: var(--radius-lg); padding: var(--spacing-md);"'),
    (r'class="bg-indigo-50 border border-indigo-200 rounded-xl p-6"', 
     'style="background: var(--color-info-light); border: 1px solid var(--color-info); border-radius: var(--radius-xl); padding: var(--spacing-lg);"'),
    
    # Text colors in info boxes
    (r'<span class="text-gray-700">', 
     '<span style="color: var(--color-text-secondary);">'),
    (r'<span class="font-bold text-gray-900"', 
     '<span class="font-bold" style="color: var(--color-text-primary);"'),
    
    # Quick actions section
    (r'class="text-sm font-bold text-indigo-900 mb-3"', 
     'class="text-sm font-bold mb-3" style="color: var(--color-primary-dark);"'),
    (r'class="block w-full text-{% if direction == \'rtl\' %}right{% else %}left{% endif %} px-3 py-2 text-sm text-indigo-700 hover:bg-indigo-100 rounded-lg transition"', 
     'class="block w-full text-{% if direction == \'rtl\' %}right{% else %}left{% endif %} px-3 py-2 text-sm rounded-lg transition" style="color: var(--color-primary);"'),
]

def modernize_template(file_path):
    """Modernize a single template file."""
    if not os.path.exists(file_path):
        print(f"  [WARN] File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all replacements
        for pattern, replacement in REPLACEMENTS:
            content = re.sub(pattern, replacement, content)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  [OK] Updated: {file_path}")
            return True
        else:
            print(f"  [SKIP] No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"  [ERROR] Error processing {file_path}: {e}")
        return False

def main():
    """Main function to modernize all form templates."""
    print("=" * 60)
    print("Modernizing Form Templates")
    print("=" * 60)
    print()
    
    updated_count = 0
    total_count = len(FORM_TEMPLATES)
    
    for template_path in FORM_TEMPLATES:
        print(f"Processing: {template_path}")
        if modernize_template(template_path):
            updated_count += 1
        print()
    
    print("=" * 60)
    print(f"Summary: {updated_count}/{total_count} templates updated")
    print("=" * 60)

if __name__ == "__main__":
    main()

