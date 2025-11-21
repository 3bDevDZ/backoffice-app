#!/usr/bin/env python
"""Clean duplicate msgstr entries in .po files."""
import re
from pathlib import Path

def clean_po_file(po_file_path):
    """Remove duplicate msgstr entries."""
    po_file = Path(po_file_path)
    if not po_file.exists():
        print(f"File not found: {po_file_path}")
        return
    
    content = po_file.read_text(encoding='utf-8')
    
    # Remove duplicate msgstr lines (keep the first non-empty one)
    # Pattern: msgstr "something"\nmsgstr ""
    content = re.sub(r'(msgstr "[^"]+")\nmsgstr ""', r'\1', content)
    
    # Also handle cases where there are multiple filled msgstr
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # If this is a filled msgstr, check if next line is also msgstr
        if line.startswith('msgstr "') and not line.startswith('msgstr ""'):
            # Check next line
            if i + 1 < len(lines) and lines[i + 1].startswith('msgstr'):
                # Skip the duplicate
                new_lines.append(line)
                i += 2  # Skip both lines
                continue
        new_lines.append(line)
        i += 1
    
    po_file.write_text('\n'.join(new_lines), encoding='utf-8')
    print(f"✓ Cleaned {po_file_path}")

if __name__ == '__main__':
    project_root = Path(__file__).parent.parent
    fr_po = project_root / "app" / "translations" / "fr" / "LC_MESSAGES" / "messages.po"
    clean_po_file(fr_po)

