#!/usr/bin/env python
"""
Script to compile Flask-Babel translations for CommerceFlow.
This script extracts translatable strings, initializes translation files,
and compiles them for all supported languages (en, fr, ar).
"""
import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Step: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"Error: Command not found. Make sure Babel is installed:")
        print("  pip install Babel")
        return False

def check_babel_installed():
    """Check if Babel is installed."""
    try:
        import babel
        print(f"✓ Babel is installed (version: {babel.__version__})")
        return True
    except ImportError:
        print("✗ Babel is not installed")
        print("  Install it with: pip install Babel")
        return False

def main():
    """Main function to compile translations."""
    print("\n" + "="*60)
    print("CommerceFlow - Translation Compilation Script")
    print("="*60)
    
    # Check if Babel is installed
    if not check_babel_installed():
        sys.exit(1)
    
    # Define paths
    babel_cfg = project_root / "babel.cfg"
    translations_dir = project_root / "app" / "translations"
    messages_pot = project_root / "messages.pot"
    
    # Supported languages
    languages = ['en', 'fr', 'ar']
    
    # Step 1: Extract translatable strings
    print("\n[1/4] Extracting translatable strings...")
    if not run_command(
        ['pybabel', 'extract', '-F', str(babel_cfg), '-k', '_l', '-o', str(messages_pot), '.'],
        "Extract translatable strings"
    ):
        print("Failed to extract strings. Continuing anyway...")
    
    # Step 2: Initialize translation files for each language
    print("\n[2/4] Initializing translation files...")
    for lang in languages:
        lang_dir = translations_dir / lang / "LC_MESSAGES"
        messages_po = lang_dir / "messages.po"
        
        if messages_po.exists():
            print(f"  ✓ Translation file for '{lang}' already exists")
            # Update existing translations
            print(f"  → Updating translations for '{lang}'...")
            run_command(
                ['pybabel', 'update', '-i', str(messages_pot), '-d', str(translations_dir), '-l', lang],
                f"Update translations for {lang}"
            )
        else:
            print(f"  → Initializing translations for '{lang}'...")
            if not run_command(
                ['pybabel', 'init', '-i', str(messages_pot), '-d', str(translations_dir), '-l', lang],
                f"Initialize translations for {lang}"
            ):
                print(f"  ⚠ Warning: Failed to initialize {lang}. Creating directory structure...")
                lang_dir.mkdir(parents=True, exist_ok=True)
                # Create a minimal messages.po file
                minimal_po = f'''# {lang.upper()} translations for CommerceFlow
# Copyright (C) 2025
msgid ""
msgstr ""
"Language: {lang}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

'''
                messages_po.write_text(minimal_po, encoding='utf-8')
                print(f"  ✓ Created minimal translation file for '{lang}'")
    
    # Step 3: Compile translations
    print("\n[3/4] Compiling translations...")
    if not run_command(
        ['pybabel', 'compile', '-d', str(translations_dir)],
        "Compile translations"
    ):
        print("⚠ Warning: Some translations may not have compiled correctly")
    
    # Step 4: Verify compiled files
    print("\n[4/4] Verifying compiled translations...")
    all_ok = True
    for lang in languages:
        messages_mo = translations_dir / lang / "LC_MESSAGES" / "messages.mo"
        if messages_mo.exists():
            size = messages_mo.stat().st_size
            print(f"  ✓ {lang}: messages.mo exists ({size} bytes)")
        else:
            print(f"  ✗ {lang}: messages.mo NOT FOUND")
            all_ok = False
    
    # Summary
    print("\n" + "="*60)
    if all_ok:
        print("✓ Translation compilation completed successfully!")
        print("\nNext steps:")
        print("  1. Restart your Flask development server")
        print("  2. Test language switching in the UI")
        print("  3. Edit translation files in app/translations/<lang>/LC_MESSAGES/messages.po")
        print("  4. Re-run this script after editing translations")
    else:
        print("⚠ Translation compilation completed with warnings")
        print("  Some translation files may be missing or incomplete")
    print("="*60 + "\n")
    
    return 0 if all_ok else 1

if __name__ == '__main__':
    sys.exit(main())

