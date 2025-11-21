#!/usr/bin/env python
"""
Copy msgid to msgstr for all empty translations.
This allows compilation while we work on proper translations.
"""
from pathlib import Path
from babel.messages.pofile import read_po, write_po

def copy_msgid_to_msgstr(po_file_path, lang_code):
    """Copy msgid to msgstr for all empty translations."""
    po_file = Path(po_file_path)
    if not po_file.exists():
        print(f"[ERROR] File not found: {po_file_path}")
        return 0
    
    # Read the .po file
    with open(po_file, 'rb') as f:
        catalog = read_po(f)
    
    filled_count = 0
    for message in catalog:
        # Check if this message has an empty translation
        if message.string == '' and message.id:
            # Copy msgid to msgstr
            message.string = message.id
            filled_count += 1
    
    # Write the updated catalog back to the file
    with open(po_file, 'wb') as f:
        write_po(f, catalog)
    
    return filled_count

def main():
    print("============================================================")
    print("CommerceFlow - Copy msgid to msgstr for empty translations")
    print("============================================================")
    
    project_root = Path(__file__).parent.parent
    translations_dir = project_root / 'app' / 'translations'
    
    # Process French and Arabic translations
    for lang in ['fr', 'ar']:
        po_file = translations_dir / lang / 'LC_MESSAGES' / 'messages.po'
        if po_file.exists():
            print(f"\n[{lang.upper()}] Copying msgid to msgstr for empty translations...")
            count = copy_msgid_to_msgstr(po_file, lang)
            print(f"  [OK] Copied {count} translations")
        else:
            print(f"\n[{lang.upper()}] [ERROR] File not found: {po_file}")
    
    print("\n============================================================")
    print("[OK] Copy operation finished!")
    print("\nNext step: Run 'pybabel compile -d app/translations' to compile")
    print("============================================================")

if __name__ == '__main__':
    main()

