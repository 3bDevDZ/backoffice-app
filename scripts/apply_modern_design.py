#!/usr/bin/env python3
"""
Script to apply modern design classes to all templates
Replaces old Tailwind classes with modern design system classes
"""

import re
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "app" / "templates"

# Replacement patterns
REPLACEMENTS = [
    # Statistics Cards
    (r'class="bg-white rounded-lg shadow-sm p-4 border border-gray-100"', 
     'class="stat-card"'),
    (r'class="text-sm text-gray-600 mb-1"', 
     'class="stat-card-label"'),
    (r'class="text-2xl font-bold text-gray-900"', 
     'class="stat-card-metric" style="color: var(--color-text-primary);"'),
    (r'class="text-2xl font-bold text-green-600"', 
     'class="stat-card-metric" style="color: var(--color-success);"'),
    (r'class="text-2xl font-bold text-blue-600"', 
     'class="stat-card-metric" style="color: var(--color-info);"'),
    (r'class="text-2xl font-bold text-yellow-600"', 
     'class="stat-card-metric" style="color: var(--color-warning);"'),
    (r'class="text-2xl font-bold text-red-600"', 
     'class="stat-card-metric" style="color: var(--color-error);"'),
    
    # Buttons
    (r'class="px-4 py-2 bg-indigo-600 text-white rounded-lg shadow-sm hover:bg-indigo-700 transition flex items-center', 
     'class="btn-primary'),
    (r'class="px-4 py-2 bg-white text-gray-700 rounded-lg shadow-sm border border-gray-200 hover:bg-gray-50 transition flex items-center', 
     'class="btn-secondary'),
    
    # Inputs
    (r'class="block w-full.*?border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"', 
     'class="modern-input'),
    (r'class="block w-full.*?border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"', 
     'class="modern-input'),
    
    # Selects
    (r'class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"', 
     'class="modern-select'),
    
    # Tables
    (r'<div class="bg-white rounded-xl shadow-sm border border-gray-100.*?overflow-hidden">', 
     '<div class="modern-table-container">'),
    (r'<table class="min-w-full divide-y divide-gray-200">', 
     '<table class="modern-table">'),
    (r'<table class="w-full">', 
     '<table class="modern-table">'),
    (r'<thead class="bg-gray-50">', 
     '<thead>'),
    (r'<tbody class="bg-white divide-y divide-gray-100">', 
     '<tbody>'),
    (r'<tr class="hover:bg-gray-50">', 
     '<tr>'),
    
    # Filters container
    (r'class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6"', 
     'class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6" style="border-radius: var(--radius-lg); box-shadow: var(--shadow-md);"'),
]

def apply_replacements(content):
    """Apply all replacement patterns to content"""
    for pattern, replacement in REPLACEMENTS:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    return content

def process_template(file_path):
    """Process a single template file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        content = apply_replacements(content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all templates"""
    templates_to_process = [
        "customers/list.html",
        "purchases/suppliers/list.html",
        "sales/orders_list.html",
        "sales/quotes_list.html",
        "stock/index.html",
        "stock/locations.html",
        "stock/movements.html",
        "stock/alerts.html",
    ]
    
    updated = []
    for template_path in templates_to_process:
        full_path = TEMPLATES_DIR / template_path
        if full_path.exists():
            if process_template(full_path):
                updated.append(template_path)
                print(f"[OK] Updated: {template_path}")
            else:
                print(f"[SKIP] No changes: {template_path}")
        else:
            print(f"[ERROR] Not found: {template_path}")
    
    print(f"\n[SUMMARY] {len(updated)} templates updated")
    if updated:
        print("Updated templates:")
        for t in updated:
            print(f"  - {t}")

if __name__ == "__main__":
    main()

