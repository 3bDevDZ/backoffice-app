"""
Script to replace hardcoded Euro symbols (€) with currency filter in templates.
This ensures all currency displays use the configured currency.
"""
import os
import re
from pathlib import Path

# Patterns to replace
PATTERNS = [
    # Template patterns: {{ "%.2f"|format(value) }} €
    (r'\{\{\s*"%.2f"\s*\|\s*format\(([^)]+)\)\s*\}\}\s*€', r'{{ \1|currency }}'),
    (r'\{\{\s*"%.3f"\s*\|\s*format\(([^)]+)\)\s*\}\}\s*€', r'{{ \1|currency }}'),
    (r'\{\{\s*"%.1f"\s*\|\s*format\(([^)]+)\)\s*\}\}\s*€', r'{{ \1|currency }}'),
    # JavaScript patterns: value.toFixed(2) + ' €'
    (r"(\w+)\.toFixed\((\d+)\)\s*\+\s*['\"]\s*€\s*['\"]", r'formatCurrencyValue(\1)'),
    # JavaScript patterns: `${value.toFixed(2)} €`
    (r'\$\{(\w+)\.toFixed\((\d+)\)\}\s*€', r'formatCurrencyValue(\1)'),
    # JavaScript patterns: value + ' €'
    (r"(\w+)\s*\+\s*['\"]\s*€\s*['\"]", r'formatCurrencyValue(\1)'),
]

def replace_in_file(file_path):
    """Replace currency symbols in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = False
        
        # Apply all patterns
        for pattern, replacement in PATTERNS:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                changes_made = True
                content = new_content
        
        # Write back if changes were made
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Updated: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"[ERROR] Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all template files."""
    templates_dir = Path('app/templates')
    
    if not templates_dir.exists():
        print(f"Templates directory not found: {templates_dir}")
        return
    
    html_files = list(templates_dir.rglob('*.html'))
    print(f"Found {len(html_files)} template files")
    
    updated_count = 0
    for html_file in html_files:
        if replace_in_file(html_file):
            updated_count += 1
    
    print(f"\n[OK] Updated {updated_count} files")
    print("⚠ Note: Please review the changes manually, especially JavaScript code")

if __name__ == '__main__':
    main()

