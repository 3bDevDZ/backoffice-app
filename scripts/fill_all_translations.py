#!/usr/bin/env python
"""
Script to fill translations for all languages (English, French, Arabic).
For English: copies msgid to msgstr (since keys are already in English)
For Arabic: adds Arabic translations
"""
import re
from pathlib import Path

# Arabic translations mapping
ARABIC_TRANSLATIONS = {
    "Dashboard": "لوحة التحكم",
    "Sales": "المبيعات",
    "Purchases": "المشتريات",
    "Inventory": "المخزون",
    "Catalog": "الكتالوج",
    "Settings": "الإعدادات",
    "Modules": "الوحدات",
    "Quick Actions": "إجراءات سريعة",
    "New Customer": "عميل جديد",
    "New Product": "منتج جديد",
    "New Order": "طلب جديد",
    "New Purchase Order": "أمر شراء جديد",
    "Stock Management": "إدارة المخزون",
    "Select a module to get started": "اختر وحدة للبدء",
    "Overview of your business KPIs, sales, and key metrics": "نظرة عامة على مؤشرات الأداء الرئيسية والمبيعات والمقاييس الرئيسية لعملك",
    "Manage customers, quotes, orders, invoices, and payments": "إدارة العملاء والعروض والطلبات والفواتير والمدفوعات",
    "Manage suppliers, purchase requests, orders, and receipts": "إدارة الموردين وطلبات الشراء والأوامر والإيصالات",
    "Track stock levels, locations, transfers, and movements": "تتبع مستويات المخزون والمواقع والتحويلات والحركات",
    "Manage products, categories, pricing, and variants": "إدارة المنتجات والفئات والأسعار والمتغيرات",
    "Configure company information and application settings": "تكوين معلومات الشركة وإعدادات التطبيق",
}

def fill_translations(po_file_path, translations_dict, is_english=False):
    """Fill translations in a .po file."""
    po_file = Path(po_file_path)
    if not po_file.exists():
        print(f"File not found: {po_file_path}")
        return
    
    content = po_file.read_text(encoding='utf-8')
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a msgid line
        if line.startswith('msgid '):
            # Extract the msgid value (handle multi-line msgid)
            msgid_lines = [line]
            j = i + 1
            while j < len(lines) and lines[j].startswith('"'):
                msgid_lines.append(lines[j])
                j += 1
            
            # Find the corresponding msgstr
            msgstr_index = j
            if msgstr_index < len(lines) and lines[msgstr_index].startswith('msgstr '):
                # Extract full msgid (handle multi-line)
                msgid_full = '\n'.join(msgid_lines)
                msgid_match = re.search(r'msgid\s+"(.+?)"', msgid_full, re.DOTALL)
                if msgid_match:
                    msgid = msgid_match.group(1).replace('\\n', '\n').replace('\\"', '"')
                    
                    # Check if we have a translation or if it's English (copy msgid)
                    if is_english:
                        # For English, copy msgid to msgstr
                        translation = msgid
                        # Replace the msgstr line
                        new_lines.extend(msgid_lines)
                        new_lines.append(f'msgstr "{translation}"')
                        i = msgstr_index + 1
                        continue
                    elif msgid in translations_dict:
                        translation = translations_dict[msgid]
                        # Replace the msgstr line
                        new_lines.extend(msgid_lines)
                        new_lines.append(f'msgstr "{translation}"')
                        i = msgstr_index + 1
                        continue
        
        new_lines.append(line)
        i += 1
    
    po_file.write_text('\n'.join(new_lines), encoding='utf-8')
    print(f"✓ Updated {po_file_path}")

def main():
    print("============================================================")
    print("CommerceFlow - Fill All Translations")
    print("============================================================")
    
    translations_dir = Path('app/translations')
    
    # English: copy msgid to msgstr
    en_po = translations_dir / 'en' / 'LC_MESSAGES' / 'messages.po'
    if en_po.exists():
        print("\n[1/2] Filling English translations (copying msgid to msgstr)...")
        fill_translations(en_po, {}, is_english=True)
    
    # Arabic: add Arabic translations
    ar_po = translations_dir / 'ar' / 'LC_MESSAGES' / 'messages.po'
    if ar_po.exists():
        print("\n[2/2] Filling Arabic translations...")
        fill_translations(ar_po, ARABIC_TRANSLATIONS, is_english=False)
    
    print("\n============================================================")
    print("✓ Translation filling completed!")
    print("\nNext step: Run 'pybabel compile -d app/translations' to compile")
    print("============================================================")

if __name__ == '__main__':
    main()


