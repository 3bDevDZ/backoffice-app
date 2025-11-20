#!/usr/bin/env python
"""
Fill missing translations for Price Lists page in French and Arabic.
"""
import re
from pathlib import Path

# Price Lists specific translations
PRICE_LISTS_TRANSLATIONS = {
    'fr': {
        'New Price List': 'Nouvelle liste de prix',
        'Back to Products': 'Retour aux produits',
        'Manage multiple pricing tiers for different customers': 'Gérez plusieurs niveaux de prix pour différents clients',
        'Total Price Lists': 'Total des listes de prix',
        'Active Price Lists': 'Listes de prix actives',
        'Inactive Price Lists': 'Listes de prix inactives',
        'All Status': 'Tous les statuts',
        'Search by name or description...': 'Rechercher par nom ou description...',
        'No price lists found.': 'Aucune liste de prix trouvée.',
        'Create First Price List': 'Créer la première liste de prix',
        'price lists': 'listes de prix',
        'Are you sure you want to delete this price list?': 'Êtes-vous sûr de vouloir supprimer cette liste de prix ?',
        'View Products': 'Voir les produits',
        'Products': 'Produits',
        'Name': 'Nom',
        'Description': 'Description',
        'Status': 'Statut',
        'Created': 'Créé',
        'Actions': 'Actions',
    },
    'ar': {
        'New Price List': 'قائمة أسعار جديدة',
        'Back to Products': 'العودة إلى المنتجات',
        'Manage multiple pricing tiers for different customers': 'إدارة مستويات أسعار متعددة لعملاء مختلفين',
        'Total Price Lists': 'إجمالي قوائم الأسعار',
        'Active Price Lists': 'قوائم الأسعار النشطة',
        'Inactive Price Lists': 'قوائم الأسعار غير النشطة',
        'All Status': 'جميع الحالات',
        'Search by name or description...': 'البحث بالاسم أو الوصف...',
        'No price lists found.': 'لم يتم العثور على قوائم أسعار.',
        'Create First Price List': 'إنشاء أول قائمة أسعار',
        'price lists': 'قوائم الأسعار',
        'Are you sure you want to delete this price list?': 'هل أنت متأكد من أنك تريد حذف قائمة الأسعار هذه؟',
        'View Products': 'عرض المنتجات',
        'Products': 'المنتجات',
        'Name': 'الاسم',
        'Description': 'الوصف',
        'Status': 'الحالة',
        'Created': 'تم الإنشاء',
        'Actions': 'الإجراءات',
    }
}

def fill_po_file(po_file_path, translations_dict, lang_code):
    """Fill a .po file with translations."""
    po_file = Path(po_file_path)
    if not po_file.exists():
        print(f"✗ File not found: {po_file_path}")
        return 0
    
    content = po_file.read_text(encoding='utf-8')
    lines = content.split('\n')
    new_lines = []
    i = 0
    filled_count = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a msgid line
        if line.startswith('msgid '):
            # Extract the msgid value (handle multi-line msgid)
            msgid_lines = [line]
            j = i + 1
            while j < len(lines) and (lines[j].startswith('"') or lines[j].strip() == ''):
                if lines[j].startswith('"'):
                    msgid_lines.append(lines[j])
                j += 1
            
            # Find the corresponding msgstr
            msgstr_index = j
            if msgstr_index < len(lines) and lines[msgstr_index].startswith('msgstr '):
                # Extract full msgid
                msgid_full = '\n'.join(msgid_lines)
                msgid_match = re.search(r'msgid\s+"(.+?)"', msgid_full, re.DOTALL)
                if msgid_match:
                    msgid = msgid_match.group(1).replace('\\n', '\n').replace('\\"', '"')
                    
                    # Check if we have a translation
                    if msgid in translations_dict:
                        translation = translations_dict[msgid]
                        # Check if msgstr is empty
                        msgstr_line = lines[msgstr_index]
                        if msgstr_line == 'msgstr ""' or msgstr_line.startswith('msgstr ""'):
                            # Replace the msgstr line
                            new_lines.extend(msgid_lines)
                            # Escape quotes in translation
                            translation_escaped = translation.replace('"', '\\"').replace('\n', '\\n')
                            new_lines.append(f'msgstr "{translation_escaped}"')
                            i = msgstr_index + 1
                            filled_count += 1
                            continue
        
        new_lines.append(line)
        i += 1
    
    po_file.write_text('\n'.join(new_lines), encoding='utf-8')
    return filled_count

def main():
    print("============================================================")
    print("CommerceFlow - Fill Price Lists Translations (FR, AR)")
    print("============================================================")
    
    translations_dir = Path('app/translations')
    
    # Fill French and Arabic translations
    for lang in ['fr', 'ar']:
        po_file = translations_dir / lang / 'LC_MESSAGES' / 'messages.po'
        if po_file.exists():
            print(f"\n[{lang.upper()}] Filling Price Lists translations...")
            count = fill_po_file(po_file, PRICE_LISTS_TRANSLATIONS[lang], lang)
            print(f"  ✓ Filled {count} translations")
        else:
            print(f"\n[{lang.upper()}] ✗ File not found: {po_file}")
    
    print("\n============================================================")
    print("✓ Translation filling completed!")
    print("\nNext step: Run 'pybabel compile -d app/translations' to compile")
    print("============================================================")

if __name__ == '__main__':
    main()


