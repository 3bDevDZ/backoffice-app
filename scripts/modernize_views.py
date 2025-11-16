#!/usr/bin/env python3
"""
Script to modernize view templates (order_view.html, quote_view.html) with the new design system.
"""

import re
import os
from pathlib import Path

# Template files to modernize
VIEW_TEMPLATES = [
    "app/templates/sales/order_view.html",
    "app/templates/sales/quote_view.html",
]

# Replacement patterns
REPLACEMENTS = [
    # Main container card
    (r'class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6"', 
     'style="background: var(--color-bg-secondary); border: 1px solid var(--color-border-default); border-radius: var(--radius-xl); padding: var(--spacing-lg); margin-bottom: var(--spacing-lg); box-shadow: var(--shadow-md);"'),
    
    # Headings
    (r'class="text-2xl font-bold text-gray-900"', 
     'class="text-2xl font-bold" style="color: var(--color-text-primary);"'),
    (r'class="text-sm font-medium text-gray-500 mb-2"', 
     'class="text-sm font-medium mb-2" style="color: var(--color-text-tertiary);"'),
    
    # Text colors
    (r'class="text-sm text-gray-500 mt-1"', 
     'class="text-sm mt-1" style="color: var(--color-text-tertiary);"'),
    (r'class="text-sm text-gray-600"', 
     'class="text-sm" style="color: var(--color-text-secondary);"'),
    (r'class="text-sm font-medium text-gray-900"', 
     'class="text-sm font-medium" style="color: var(--color-text-primary);"'),
    
    # Links
    (r'class="text-indigo-600 hover:text-indigo-800"', 
     'style="color: var(--color-primary);"'),
    
    # Status badges - Draft
    (r'class="px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full bg-blue-100 text-blue-800"', 
     'class="badge badge-draft"'),
    
    # Status badges - Confirmed/Sent
    (r'class="px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800"', 
     'class="badge badge-confirmed"'),
    
    # Status badges - Ready/Accepted
    (r'class="px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full bg-green-100 text-green-800"', 
     'class="badge badge-received"'),
    
    # Status badges - Shipped/Delivered
    (r'class="px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full bg-purple-100 text-purple-800"', 
     'class="badge badge-sent"'),
    (r'class="px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full bg-indigo-100 text-indigo-800"', 
     'class="badge badge-sent"'),
    
    # Status badges - Canceled/Rejected
    (r'class="px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full bg-red-100 text-red-800"', 
     'class="badge badge-cancelled"'),
    
    # Status badges - Expired/Gray
    (r'class="px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full bg-gray-100 text-gray-800"', 
     'class="badge" style="background: var(--color-bg-tertiary); color: var(--color-text-secondary);"'),
    
    # Discount text
    (r'class="text-sm font-medium text-red-600"', 
     'class="text-sm font-medium" style="color: var(--color-error);"'),
    
    # Total text
    (r'class="text-lg font-bold text-gray-900"', 
     'class="text-lg font-bold" style="color: var(--color-text-primary);"'),
    
    # Buttons - Primary
    (r'class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"', 
     'class="btn-primary"'),
    (r'class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"', 
     'class="btn-primary" style="background: var(--color-success);"'),
    (r'class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"', 
     'class="btn-primary" style="background: var(--color-error);"'),
    
    # Buttons - Secondary
    (r'class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"', 
     'class="btn-secondary"'),
    
    # Table containers
    (r'class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"', 
     'class="modern-table-container"'),
    (r'class="min-w-full divide-y divide-gray-200"', 
     'class="modern-table"'),
    
    # Table headers
    (r'class="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"', 
     'class="modern-table-header"'),
    
    # Table cells
    (r'class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"', 
     'class="px-6 py-4 whitespace-nowrap text-sm" style="color: var(--color-text-primary);"'),
    (r'class="px-6 py-4 whitespace-nowrap text-sm text-gray-500"', 
     'class="px-6 py-4 whitespace-nowrap text-sm" style="color: var(--color-text-secondary);"'),
    
    # Info boxes
    (r'class="bg-blue-50 border border-blue-200 rounded-lg p-4"', 
     'style="background: var(--color-info-light); border: 1px solid var(--color-info); border-radius: var(--radius-lg); padding: var(--spacing-md);"'),
    (r'class="bg-yellow-50 border border-yellow-200 rounded-lg p-4"', 
     'style="background: var(--color-warning-light); border: 1px solid var(--color-warning); border-radius: var(--radius-lg); padding: var(--spacing-md);"'),
    (r'class="bg-green-50 border border-green-200 rounded-lg p-4"', 
     'style="background: var(--color-success-light); border: 1px solid var(--color-success); border-radius: var(--radius-lg); padding: var(--spacing-md);"'),
    (r'class="bg-red-50 border border-red-200 rounded-lg p-4"', 
     'style="background: var(--color-error-light); border: 1px solid var(--color-error); border-radius: var(--radius-lg); padding: var(--spacing-md);"'),
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
    """Main function to modernize all view templates."""
    print("=" * 60)
    print("Modernizing View Templates")
    print("=" * 60)
    print()
    
    updated_count = 0
    total_count = len(VIEW_TEMPLATES)
    
    for template_path in VIEW_TEMPLATES:
        print(f"Processing: {template_path}")
        if modernize_template(template_path):
            updated_count += 1
        print()
    
    print("=" * 60)
    print(f"Summary: {updated_count}/{total_count} templates updated")
    print("=" * 60)

if __name__ == "__main__":
    main()

