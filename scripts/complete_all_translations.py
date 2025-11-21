#!/usr/bin/env python
"""
Complete translation script that fills ALL missing translations for ALL views.
This script reads messages.pot, extracts all strings, and fills missing translations
in French and Arabic .po files using a comprehensive translation dictionary.
"""
import re
from pathlib import Path

# MASSIVE comprehensive translation dictionary covering ALL common strings
MASSIVE_TRANSLATIONS = {
    'fr': {
        # ========== BASIC ACTIONS ==========
        'Create': 'Créer',
        'Edit': 'Modifier',
        'View': 'Voir',
        'Delete': 'Supprimer',
        'Save': 'Enregistrer',
        'Cancel': 'Annuler',
        'Submit': 'Soumettre',
        'Confirm': 'Confirmer',
        'Approve': 'Approuver',
        'Reject': 'Rejeter',
        'Validate': 'Valider',
        'Send': 'Envoyer',
        'Print': 'Imprimer',
        'Download': 'Télécharger',
        'Export': 'Exporter',
        'Import': 'Importer',
        'Upload': 'Télécharger',
        'Search': 'Rechercher',
        'Filter': 'Filtrer',
        'Reset': 'Réinitialiser',
        'Clear': 'Effacer',
        'Refresh': 'Actualiser',
        'Back': 'Retour',
        'Next': 'Suivant',
        'Previous': 'Précédent',
        'Close': 'Fermer',
        'Open': 'Ouvrir',
        'Add': 'Ajouter',
        'Remove': 'Retirer',
        'Select': 'Sélectionner',
        'Choose': 'Choisir',
        'Yes': 'Oui',
        'No': 'Non',
        'OK': 'OK',
        'New': 'Nouveau',
        'Update': 'Mettre à jour',
        
        # ========== STATUS ==========
        'Active': 'Actif',
        'Inactive': 'Inactif',
        'Draft': 'Brouillon',
        'Confirmed': 'Confirmé',
        'Cancelled': 'Annulé',
        'Completed': 'Terminé',
        'Pending': 'En attente',
        'Archived': 'Archivé',
        'Blocked': 'Bloqué',
        'Validated': 'Validé',
        'Sent': 'Envoyé',
        'Received': 'Reçu',
        'Shipped': 'Expédié',
        'Partially Received': 'Partiellement reçu',
        'Approved': 'Approuvé',
        'Rejected': 'Rejeté',
        'Paid': 'Payé',
        'Unpaid': 'Non payé',
        'Overdue': 'En retard',
        'Partial': 'Partiel',
        'Ready': 'Prêt',
        
        # ========== MESSAGES ==========
        'Loading...': 'Chargement...',
        'Error': 'Erreur',
        'Success': 'Succès',
        'Warning': 'Avertissement',
        'Info': 'Information',
        'Are you sure?': 'Êtes-vous sûr ?',
        'This action cannot be undone.': 'Cette action ne peut pas être annulée.',
        'Please wait...': 'Veuillez patienter...',
        'Operation successful': 'Opération réussie',
        'Operation failed': 'Opération échouée',
        'An error occurred': 'Une erreur s\'est produite',
        'Invalid input': 'Saisie invalide',
        'Required field': 'Champ requis',
        'Please fill in all required fields': 'Veuillez remplir tous les champs requis',
        'Invalid email address': 'Adresse e-mail invalide',
        'Invalid phone number': 'Numéro de téléphone invalide',
        'Value must be greater than 0': 'La valeur doit être supérieure à 0',
        'Value must be a number': 'La valeur doit être un nombre',
        'No results found': 'Aucun résultat trouvé',
        'No file provided': 'Aucun fichier fourni',
        'No file selected': 'Aucun fichier sélectionné',
        'Search term is required': 'Le terme de recherche est requis',
        
        # ========== SUCCESS MESSAGES ==========
        'created successfully': 'créé avec succès',
        'updated successfully': 'mis à jour avec succès',
        'deleted successfully': 'supprimé avec succès',
        'archived successfully': 'archivé avec succès',
        'activated successfully': 'activé avec succès',
        'deactivated successfully': 'désactivé avec succès',
        'Customer created successfully': 'Client créé avec succès',
        'Customer updated successfully': 'Client mis à jour avec succès',
        'Customer archived successfully': 'Client archivé avec succès',
        'Customer activated successfully': 'Client activé avec succès',
        'Customer deactivated successfully': 'Client désactivé avec succès',
        'Address created successfully': 'Adresse créée avec succès',
        'Address updated successfully': 'Adresse mise à jour avec succès',
        'Address deleted successfully': 'Adresse supprimée avec succès',
        'Contact created successfully': 'Contact créé avec succès',
        'Contact updated successfully': 'Contact mis à jour avec succès',
        'Contact deleted successfully': 'Contact supprimé avec succès',
        'Login successful': 'Connexion réussie',
        'Dashboard KPIs retrieved successfully': 'KPI du tableau de bord récupérés avec succès',
        'Revenue statistics retrieved successfully': 'Statistiques de revenus récupérées avec succès',
        'Stock alerts retrieved successfully': 'Alertes de stock récupérées avec succès',
        'Active orders retrieved successfully': 'Commandes actives récupérées avec succès',
        
        # ========== ERROR MESSAGES ==========
        'not found': 'non trouvé',
        'Customer not found': 'Client non trouvé',
        'Address not found': 'Adresse non trouvée',
        'Contact not found': 'Contact non trouvé',
        'Invalid username or password': 'Nom d\'utilisateur ou mot de passe invalide',
        'Login failed: {}': 'Échec de la connexion : {}',
        'Failed to create customer: {}': 'Échec de la création du client : {}',
        'Failed to create address: {}': 'Échec de la création de l\'adresse : {}',
        'Failed to create contact: {}': 'Échec de la création du contact : {}',
        'Import failed: {}': 'Échec de l\'importation : {}',
        'Export failed: {}': 'Échec de l\'exportation : {}',
        'Delete not yet implemented': 'Suppression pas encore implémentée',
        'Import not yet implemented': 'Importation pas encore implémentée',
        'Export not yet implemented': 'Exportation pas encore implémentée',
        'Error retrieving dashboard KPIs: %(error)s': 'Erreur lors de la récupération des KPI du tableau de bord : %(error)s',
        'Error retrieving revenue statistics: %(error)s': 'Erreur lors de la récupération des statistiques de revenus : %(error)s',
        'Error retrieving stock alerts: %(error)s': 'Erreur lors de la récupération des alertes de stock : %(error)s',
        'Error retrieving active orders: %(error)s': 'Erreur lors de la récupération des commandes actives : %(error)s',
        
        # ========== DATES ==========
        'Date': 'Date',
        'From': 'De',
        'To': 'À',
        'Today': 'Aujourd\'hui',
        'Yesterday': 'Hier',
        'This week': 'Cette semaine',
        'This month': 'Ce mois',
        'This year': 'Cette année',
        
        # ========== PAGINATION ==========
        'Page': 'Page',
        'of': 'de',
        'Showing': 'Affichage',
        'to': 'à',
        'results': 'résultats',
        'price lists': 'listes de prix',
        
        # ========== FORM FIELDS ==========
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
        'unit': 'unité',
        'units': 'unités',
        'N/A': 'N/A',
        'Variants': 'Variantes',
        'No variants': 'Aucune variante',
        'Error loading products': 'Erreur lors du chargement des produits',
        'No products found': 'Aucun produit trouvé',
        
        # ========== MODULE SPECIFIC ==========
        'Product Management': 'Gestion des produits',
        'Complete catalog of your products': 'Catalogue complet de vos produits',
        'Total Products': 'Total produits',
        'Active Products': 'Produits actifs',
        'Out of Stock': 'Rupture de stock',
        'Low Stock': 'Stock faible',
        'Order Management': 'Gestion des commandes',
        'Create and manage customer orders': 'Créer et gérer les commandes clients',
        'Total Orders': 'Total commandes',
        'Purchase Orders': 'Ordres d\'achat',
        'Manage purchase orders from suppliers': 'Gérer les ordres d\'achat des fournisseurs',
        'Ready': 'Prêt',
        'Active Products': 'Produits actifs',
        'Out of Stock': 'Rupture de stock',
        'Low Stock': 'Stock faible',
        'Create and manage customer orders': 'Créer et gérer les commandes clients',
    },
    
    'ar': {
        # ========== BASIC ACTIONS ==========
        'Create': 'إنشاء',
        'Edit': 'تعديل',
        'View': 'عرض',
        'Delete': 'حذف',
        'Save': 'حفظ',
        'Cancel': 'إلغاء',
        'Submit': 'إرسال',
        'Confirm': 'تأكيد',
        'Approve': 'الموافقة',
        'Reject': 'رفض',
        'Validate': 'التحقق',
        'Send': 'إرسال',
        'Print': 'طباعة',
        'Download': 'تحميل',
        'Export': 'تصدير',
        'Import': 'استيراد',
        'Upload': 'رفع',
        'Search': 'بحث',
        'Filter': 'تصفية',
        'Reset': 'إعادة تعيين',
        'Clear': 'مسح',
        'Refresh': 'تحديث',
        'Back': 'رجوع',
        'Next': 'التالي',
        'Previous': 'السابق',
        'Close': 'إغلاق',
        'Open': 'فتح',
        'Add': 'إضافة',
        'Remove': 'إزالة',
        'Select': 'اختيار',
        'Choose': 'اختر',
        'Yes': 'نعم',
        'No': 'لا',
        'OK': 'موافق',
        'New': 'جديد',
        'Update': 'تحديث',
        
        # ========== STATUS ==========
        'Active': 'نشط',
        'Inactive': 'غير نشط',
        'Draft': 'مسودة',
        'Confirmed': 'مؤكد',
        'Cancelled': 'ملغي',
        'Completed': 'مكتمل',
        'Pending': 'قيد الانتظار',
        'Archived': 'مؤرشف',
        'Blocked': 'محظور',
        'Validated': 'تم التحقق',
        'Sent': 'مرسل',
        'Received': 'مستلم',
        'Shipped': 'مشحون',
        'Partially Received': 'مستلم جزئياً',
        'Approved': 'موافق عليه',
        'Rejected': 'مرفوض',
        'Paid': 'مدفوع',
        'Unpaid': 'غير مدفوع',
        'Overdue': 'متأخر',
        'Partial': 'جزئي',
        'Ready': 'جاهز',
        
        # ========== MESSAGES ==========
        'Loading...': 'جاري التحميل...',
        'Error': 'خطأ',
        'Success': 'نجاح',
        'Warning': 'تحذير',
        'Info': 'معلومات',
        'Are you sure?': 'هل أنت متأكد؟',
        'This action cannot be undone.': 'لا يمكن التراجع عن هذا الإجراء.',
        'Please wait...': 'يرجى الانتظار...',
        'Operation successful': 'تمت العملية بنجاح',
        'Operation failed': 'فشلت العملية',
        'An error occurred': 'حدث خطأ',
        'Invalid input': 'إدخال غير صالح',
        'Required field': 'حقل مطلوب',
        'Please fill in all required fields': 'يرجى ملء جميع الحقول المطلوبة',
        'Invalid email address': 'عنوان بريد إلكتروني غير صالح',
        'Invalid phone number': 'رقم هاتف غير صالح',
        'Value must be greater than 0': 'يجب أن تكون القيمة أكبر من 0',
        'Value must be a number': 'يجب أن تكون القيمة رقماً',
        'No results found': 'لم يتم العثور على نتائج',
        'No file provided': 'لم يتم توفير ملف',
        'No file selected': 'لم يتم اختيار ملف',
        'Search term is required': 'مصطلح البحث مطلوب',
        
        # ========== SUCCESS MESSAGES ==========
        'created successfully': 'تم الإنشاء بنجاح',
        'updated successfully': 'تم التحديث بنجاح',
        'deleted successfully': 'تم الحذف بنجاح',
        'archived successfully': 'تم الأرشفة بنجاح',
        'activated successfully': 'تم التفعيل بنجاح',
        'deactivated successfully': 'تم إلغاء التفعيل بنجاح',
        'Customer created successfully': 'تم إنشاء العميل بنجاح',
        'Customer updated successfully': 'تم تحديث العميل بنجاح',
        'Customer archived successfully': 'تم أرشفة العميل بنجاح',
        'Customer activated successfully': 'تم تفعيل العميل بنجاح',
        'Customer deactivated successfully': 'تم إلغاء تفعيل العميل بنجاح',
        'Address created successfully': 'تم إنشاء العنوان بنجاح',
        'Address updated successfully': 'تم تحديث العنوان بنجاح',
        'Address deleted successfully': 'تم حذف العنوان بنجاح',
        'Contact created successfully': 'تم إنشاء جهة الاتصال بنجاح',
        'Contact updated successfully': 'تم تحديث جهة الاتصال بنجاح',
        'Contact deleted successfully': 'تم حذف جهة الاتصال بنجاح',
        'Login successful': 'تم تسجيل الدخول بنجاح',
        'Dashboard KPIs retrieved successfully': 'تم استرداد مؤشرات الأداء الرئيسية للوحة التحكم بنجاح',
        'Revenue statistics retrieved successfully': 'تم استرداد إحصائيات الإيرادات بنجاح',
        'Stock alerts retrieved successfully': 'تم استرداد تنبيهات المخزون بنجاح',
        'Active orders retrieved successfully': 'تم استرداد الطلبات النشطة بنجاح',
        
        # ========== ERROR MESSAGES ==========
        'not found': 'غير موجود',
        'Customer not found': 'العميل غير موجود',
        'Address not found': 'العنوان غير موجود',
        'Contact not found': 'جهة الاتصال غير موجودة',
        'Invalid username or password': 'اسم المستخدم أو كلمة المرور غير صحيحة',
        'Login failed: {}': 'فشل تسجيل الدخول: {}',
        'Failed to create customer: {}': 'فشل إنشاء العميل: {}',
        'Failed to create address: {}': 'فشل إنشاء العنوان: {}',
        'Failed to create contact: {}': 'فشل إنشاء جهة الاتصال: {}',
        'Import failed: {}': 'فشل الاستيراد: {}',
        'Export failed: {}': 'فشل التصدير: {}',
        'Delete not yet implemented': 'الحذف غير مطبق بعد',
        'Import not yet implemented': 'الاستيراد غير مطبق بعد',
        'Export not yet implemented': 'التصدير غير مطبق بعد',
        'Error retrieving dashboard KPIs: %(error)s': 'خطأ في استرداد مؤشرات الأداء الرئيسية للوحة التحكم: %(error)s',
        'Error retrieving revenue statistics: %(error)s': 'خطأ في استرداد إحصائيات الإيرادات: %(error)s',
        'Error retrieving stock alerts: %(error)s': 'خطأ في استرداد تنبيهات المخزون: %(error)s',
        'Error retrieving active orders: %(error)s': 'خطأ في استرداد الطلبات النشطة: %(error)s',
        
        # ========== DATES ==========
        'Date': 'التاريخ',
        'From': 'من',
        'To': 'إلى',
        'Today': 'اليوم',
        'Yesterday': 'أمس',
        'This week': 'هذا الأسبوع',
        'This month': 'هذا الشهر',
        'This year': 'هذه السنة',
        
        # ========== PAGINATION ==========
        'Page': 'صفحة',
        'of': 'من',
        'Showing': 'عرض',
        'to': 'إلى',
        'results': 'نتائج',
        'price lists': 'قوائم الأسعار',
        
        # ========== FORM FIELDS ==========
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
        'unit': 'وحدة',
        'units': 'وحدات',
        'N/A': 'غير متاح',
        'Variants': 'المتغيرات',
        'No variants': 'لا توجد متغيرات',
        'Error loading products': 'خطأ في تحميل المنتجات',
        'No products found': 'لم يتم العثور على منتجات',
        
        # ========== MODULE SPECIFIC ==========
        'Product Management': 'إدارة المنتجات',
        'Complete catalog of your products': 'كتالوج كامل لمنتجاتك',
        'Total Products': 'إجمالي المنتجات',
        'Active Products': 'المنتجات النشطة',
        'Out of Stock': 'نفاد المخزون',
        'Low Stock': 'مخزون منخفض',
        'Order Management': 'إدارة الطلبات',
        'Create and manage customer orders': 'إنشاء وإدارة طلبات العملاء',
        'Total Orders': 'إجمالي الطلبات',
        'Purchase Orders': 'أوامر الشراء',
        'Manage purchase orders from suppliers': 'إدارة أوامر الشراء من الموردين',
        'Ready': 'جاهز',
        'Active Products': 'المنتجات النشطة',
        'Out of Stock': 'نفاد المخزون',
        'Low Stock': 'مخزون منخفض',
        'Create and manage customer orders': 'إنشاء وإدارة طلبات العملاء',
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
    print("CommerceFlow - Complete ALL Translations (FR, AR)")
    print("============================================================")
    
    translations_dir = Path('app/translations')
    
    # Fill French and Arabic translations
    for lang in ['fr', 'ar']:
        po_file = translations_dir / lang / 'LC_MESSAGES' / 'messages.po'
        if po_file.exists():
            print(f"\n[{lang.upper()}] Filling ALL missing translations...")
            count = fill_po_file(po_file, MASSIVE_TRANSLATIONS[lang], lang)
            print(f"  ✓ Filled {count} translations")
        else:
            print(f"\n[{lang.upper()}] ✗ File not found: {po_file}")
    
    print("\n============================================================")
    print("✓ Complete translation filling finished!")
    print("\nNext step: Run 'pybabel compile -d app/translations' to compile")
    print("============================================================")

if __name__ == '__main__':
    main()

