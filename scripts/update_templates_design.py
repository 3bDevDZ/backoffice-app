#!/usr/bin/env python3
"""
Update all list templates with modern design classes
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "app" / "templates"

def update_template(file_path):
    """Update a template file with modern design"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Update stats cards gap
        content = re.sub(r'gap-4 mb-6">', 'gap-6 mb-8">', content)
        
        # Update old card classes to stat-card
        content = re.sub(
            r'class="bg-white rounded-lg shadow-sm p-4 border border-gray-100"',
            'class="stat-card"',
            content
        )
        
        # Update metric classes
        content = re.sub(
            r'class="text-2xl font-bold text-gray-900"',
            'class="stat-card-metric" style="color: var(--color-text-primary);"',
            content
        )
        content = re.sub(
            r'class="text-2xl font-bold text-green-600"',
            'class="stat-card-metric" style="color: var(--color-success);"',
            content
        )
        content = re.sub(
            r'class="text-2xl font-bold text-blue-600"',
            'class="stat-card-metric" style="color: var(--color-info);"',
            content
        )
        content = re.sub(
            r'class="text-2xl font-bold text-yellow-600"',
            'class="stat-card-metric" style="color: var(--color-warning);"',
            content
        )
        content = re.sub(
            r'class="text-2xl font-bold text-red-600"',
            'class="stat-card-metric" style="color: var(--color-error);"',
            content
        )
        content = re.sub(
            r'class="text-2xl font-bold text-purple-600"',
            'class="stat-card-metric" style="color: #7C3AED;"',
            content
        )
        
        # Update label classes
        content = re.sub(
            r'class="text-sm text-gray-600 mb-1"',
            'class="stat-card-label"',
            content
        )
        
        # Update buttons
        content = re.sub(
            r'class="px-4 py-2 bg-indigo-600 text-white rounded-lg shadow-sm hover:bg-indigo-700 transition flex items-center',
            'class="btn-primary',
            content
        )
        content = re.sub(
            r'class="px-4 py-2 bg-white text-gray-700 rounded-lg shadow-sm border border-gray-200 hover:bg-gray-50 transition flex items-center',
            'class="btn-secondary',
            content
        )
        
        # Update inputs
        content = re.sub(
            r'class="block w-full.*?border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"',
            'class="modern-input',
            content,
            flags=re.DOTALL
        )
        
        # Update selects
        content = re.sub(
            r'class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"',
            'class="modern-select',
            content
        )
        
        # Update filter containers
        content = re.sub(
            r'class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6"',
            'class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6" style="border-radius: var(--radius-lg); box-shadow: var(--shadow-md);"',
            content
        )
        
        # Update tables
        content = re.sub(
            r'<div class="bg-white rounded-xl shadow-sm border border-gray-100.*?overflow-hidden">',
            '<div class="modern-table-container">',
            content,
            flags=re.DOTALL
        )
        content = re.sub(
            r'<table class="min-w-full divide-y divide-gray-200">',
            '<table class="modern-table">',
            content
        )
        content = re.sub(
            r'<table class="w-full">',
            '<table class="modern-table">',
            content
        )
        content = re.sub(
            r'<thead class="bg-gray-50">',
            '<thead>',
            content
        )
        content = re.sub(
            r'<tbody class="bg-white divide-y divide-gray-100">',
            '<tbody>',
            content
        )
        content = re.sub(
            r'<tr class="hover:bg-gray-50">',
            '<tr>',
            content
        )
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Templates to update
templates = [
    "sales/orders_list.html",
    "sales/quotes_list.html",
    "purchases/suppliers/list.html",
    "stock/index.html",
    "stock/locations.html",
    "stock/movements.html",
    "stock/alerts.html",
]

updated = []
for template in templates:
    path = TEMPLATES_DIR / template
    if path.exists():
        if update_template(path):
            updated.append(template)
            print(f"[OK] {template}")
        else:
            print(f"[SKIP] {template}")
    else:
        print(f"[NOT FOUND] {template}")

print(f"\nUpdated {len(updated)} templates")

