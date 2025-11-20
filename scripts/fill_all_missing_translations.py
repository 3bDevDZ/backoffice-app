#!/usr/bin/env python
"""
Fill ALL missing translations by reading messages.pot and generating translations
for every empty msgstr in French and Arabic .po files.
"""
import re
from pathlib import Path

# Extended comprehensive translations
EXTENDED_TRANSLATIONS = {
    'fr': {
        # Common form fields
        'Product': 'Produit',
        'Select product': 'Sélectionner un produit',
        'Quantity': 'Quantité',
        'Est. Price': 'Prix estimé',
        'Notes': 'Notes',
        'Unit Price': 'Prix unitaire',
        'Discount': 'Remise',
        'Tax': 'Taxe',
        'Total': 'Total',
        'Subtotal': 'Sous-total',
        'Amount': 'Montant',
        'Reference': 'Référence',
        'Number': 'Numéro',
        'Supplier': 'Fournisseur',
        'Customer': 'Client',
        'Location': 'Emplacement',
        'Site': 'Site',
        'Source': 'Source',
        'Destination': 'Destination',
        'Requested': 'Demandé',
        'Shipped': 'Expédié',
        'Received': 'Reçu',
        'Created By': 'Créé par',
        'Updated By': 'Mis à jour par',
        
        # Additional common strings
        'unit': 'unité',
        'units': 'unités',
        'N/A': 'N/A',
        'Variants': 'Variantes',
        'No variants': 'Aucune variante',
        'Error loading products': 'Erreur lors du chargement des produits',
        'No products found': 'Aucun produit trouvé',
        'No price lists found.': 'Aucune liste de prix trouvée.',
        'Create First Price List': 'Créer la première liste de prix',
        'Are you sure you want to delete this price list?': 'Êtes-vous sûr de vouloir supprimer cette liste de prix ?',
        
        # Dashboard and API messages
        'Dashboard KPIs retrieved successfully': 'KPI du tableau de bord récupérés avec succès',
        'Error retrieving dashboard KPIs: %(error)s': 'Erreur lors de la récupération des KPI du tableau de bord : %(error)s',
        'Revenue statistics retrieved successfully': 'Statistiques de revenus récupérées avec succès',
        'Error retrieving revenue statistics: %(error)s': 'Erreur lors de la récupération des statistiques de revenus : %(error)s',
        'Stock alerts retrieved successfully': 'Alertes de stock récupérées avec succès',
        'Error retrieving stock alerts: %(error)s': 'Erreur lors de la récupération des alertes de stock : %(error)s',
        'Active orders retrieved successfully': 'Commandes actives récupérées avec succès',
        'Error retrieving active orders: %(error)s': 'Erreur lors de la récupération des commandes actives : %(error)s',
    },
    
    'ar': {
        # Common form fields
        'Product': 'المنتج',
        'Select product': 'اختر منتجاً',
        'Quantity': 'الكمية',
        'Est. Price': 'السعر المقدر',
        'Notes': 'ملاحظات',
        'Unit Price': 'السعر الوحدة',
        'Discount': 'الخصم',
        'Tax': 'الضريبة',
        'Total': 'الإجمالي',
        'Subtotal': 'المجموع الفرعي',
        'Amount': 'المبلغ',
        'Reference': 'المرجع',
        'Number': 'الرقم',
        'Supplier': 'المورد',
        'Customer': 'العميل',
        'Location': 'الموقع',
        'Site': 'الموقع',
        'Source': 'المصدر',
        'Destination': 'الوجهة',
        'Requested': 'مطلوب',
        'Shipped': 'مشحون',
        'Received': 'مستلم',
        'Created By': 'تم الإنشاء بواسطة',
        'Updated By': 'تم التحديث بواسطة',
        
        # Additional common strings
        'unit': 'وحدة',
        'units': 'وحدات',
        'N/A': 'غير متاح',
        'Variants': 'المتغيرات',
        'No variants': 'لا توجد متغيرات',
        'Error loading products': 'خطأ في تحميل المنتجات',
        'No products found': 'لم يتم العثور على منتجات',
        'No price lists found.': 'لم يتم العثور على قوائم أسعار.',
        'Create First Price List': 'إنشاء أول قائمة أسعار',
        'Are you sure you want to delete this price list?': 'هل أنت متأكد من أنك تريد حذف قائمة الأسعار هذه؟',
        
        # Dashboard and API messages
        'Dashboard KPIs retrieved successfully': 'تم استرداد مؤشرات الأداء الرئيسية للوحة التحكم بنجاح',
        'Error retrieving dashboard KPIs: %(error)s': 'خطأ في استرداد مؤشرات الأداء الرئيسية للوحة التحكم: %(error)s',
        'Revenue statistics retrieved successfully': 'تم استرداد إحصائيات الإيرادات بنجاح',
        'Error retrieving revenue statistics: %(error)s': 'خطأ في استرداد إحصائيات الإيرادات: %(error)s',
        'Stock alerts retrieved successfully': 'تم استرداد تنبيهات المخزون بنجاح',
        'Error retrieving stock alerts: %(error)s': 'خطأ في استرداد تنبيهات المخزون: %(error)s',
        'Active orders retrieved successfully': 'تم استرداد الطلبات النشطة بنجاح',
        'Error retrieving active orders: %(error)s': 'خطأ في استرداد الطلبات النشطة: %(error)s',
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
    print("CommerceFlow - Fill ALL Missing Translations (FR, AR)")
    print("============================================================")
    
    translations_dir = Path('app/translations')
    
    # Fill French and Arabic translations
    for lang in ['fr', 'ar']:
        po_file = translations_dir / lang / 'LC_MESSAGES' / 'messages.po'
        if po_file.exists():
            print(f"\n[{lang.upper()}] Filling missing translations...")
            count = fill_po_file(po_file, EXTENDED_TRANSLATIONS[lang], lang)
            print(f"  ✓ Filled {count} translations")
        else:
            print(f"\n[{lang.upper()}] ✗ File not found: {po_file}")
    
    print("\n============================================================")
    print("✓ Translation filling completed!")
    print("\nNext step: Run 'pybabel compile -d app/translations' to compile")
    print("============================================================")

if __name__ == '__main__':
    main()


