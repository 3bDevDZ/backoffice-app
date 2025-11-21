#!/usr/bin/env python
"""
Comprehensive translation script for ALL views in CommerceFlow.
This script extracts all strings from messages.pot and fills missing translations
for French and Arabic using a comprehensive dictionary.
"""
import re
from pathlib import Path

# Comprehensive translation dictionary - covering ALL common strings
ALL_TRANSLATIONS = {
    'fr': {
        # ========== COMMON ACTIONS ==========
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
        
        # ========== TABLE HEADERS ==========
        'NAME': 'NOM',
        'DESCRIPTION': 'DESCRIPTION',
        'PRICE': 'PRIX',
        'QUANTITY': 'QUANTITÉ',
        'TOTAL': 'TOTAL',
        'AMOUNT': 'MONTANT',
        'DATE': 'DATE',
        'REFERENCE': 'RÉFÉRENCE',
        'NUMBER': 'NUMÉRO',
        'SUPPLIER': 'FOURNISSEUR',
        'CUSTOMER': 'CLIENT',
        'PRODUCT': 'PRODUIT',
        'LOCATION': 'EMPLACEMENT',
        'SITE': 'SITE',
        'SOURCE': 'SOURCE',
        'DESTINATION': 'DESTINATION',
        'REQUESTED': 'DEMANDÉ',
        'SHIPPED': 'EXPÉDIÉ',
        'RECEIVED': 'REÇU',
        'CREATED': 'CRÉÉ',
        'UPDATED': 'MIS À JOUR',
        'CREATED BY': 'CRÉÉ PAR',
        'UPDATED BY': 'MIS À JOUR PAR',
        'ACTIONS': 'ACTIONS',
        'STATUS': 'STATUT',
        'CODE': 'CODE',
        'TYPE': 'TYPE',
        'EMAIL': 'EMAIL',
        'PHONE': 'TÉLÉPHONE',
        'PRODUITS': 'PRODUITS',
        
        # ========== COMMON FIELDS ==========
        'Name': 'Nom',
        'Description': 'Description',
        'Status': 'Statut',
        'Created': 'Créé',
        'Products': 'Produits',
        'All Types': 'Tous les types',
        'All Statuses': 'Tous les statuts',
        'All Status': 'Tous les statuts',
        'B2B': 'B2B',
        'B2C': 'B2C',
        
        # ========== SEARCH PLACEHOLDERS ==========
        'Search by name, code, email...': 'Rechercher par nom, code, email...',
        'Search by name, code, reference...': 'Rechercher par nom, code, référence...',
        'Search by name or description...': 'Rechercher par nom ou description...',
        'Search by name, email, code...': 'Rechercher par nom, email, code...',
        'Search by name or description': 'Rechercher par nom ou description',
        
        # ========== PRICE LISTS ==========
        'Price Lists': 'Listes de prix',
        'New Price List': 'Nouvelle liste de prix',
        'Back to Products': 'Retour aux produits',
        'Manage multiple pricing tiers for different customers': 'Gérez plusieurs niveaux de prix pour différents clients',
        'Total Price Lists': 'Total des listes de prix',
        'Active Price Lists': 'Listes de prix actives',
        'Inactive Price Lists': 'Listes de prix inactives',
        'No price lists found.': 'Aucune liste de prix trouvée.',
        'Create First Price List': 'Créer la première liste de prix',
        'Are you sure you want to delete this price list?': 'Êtes-vous sûr de vouloir supprimer cette liste de prix ?',
        'View Products': 'Voir les produits',
        
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
    },
    
    'ar': {
        # ========== COMMON ACTIONS ==========
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
        
        # ========== TABLE HEADERS ==========
        'NAME': 'الاسم',
        'DESCRIPTION': 'الوصف',
        'PRICE': 'السعر',
        'QUANTITY': 'الكمية',
        'TOTAL': 'الإجمالي',
        'AMOUNT': 'المبلغ',
        'DATE': 'التاريخ',
        'REFERENCE': 'المرجع',
        'NUMBER': 'الرقم',
        'SUPPLIER': 'المورد',
        'CUSTOMER': 'العميل',
        'PRODUCT': 'المنتج',
        'LOCATION': 'الموقع',
        'SITE': 'الموقع',
        'SOURCE': 'المصدر',
        'DESTINATION': 'الوجهة',
        'REQUESTED': 'مطلوب',
        'SHIPPED': 'مشحون',
        'RECEIVED': 'مستلم',
        'CREATED': 'تم الإنشاء',
        'UPDATED': 'تم التحديث',
        'CREATED BY': 'تم الإنشاء بواسطة',
        'UPDATED BY': 'تم التحديث بواسطة',
        'ACTIONS': 'الإجراءات',
        'STATUS': 'الحالة',
        'CODE': 'الرمز',
        'TYPE': 'النوع',
        'EMAIL': 'البريد الإلكتروني',
        'PHONE': 'الهاتف',
        'PRODUITS': 'المنتجات',
        
        # ========== COMMON FIELDS ==========
        'Name': 'الاسم',
        'Description': 'الوصف',
        'Status': 'الحالة',
        'Created': 'تم الإنشاء',
        'Products': 'المنتجات',
        'All Types': 'جميع الأنواع',
        'All Statuses': 'جميع الحالات',
        'All Status': 'جميع الحالات',
        'B2B': 'B2B',
        'B2C': 'B2C',
        
        # ========== SEARCH PLACEHOLDERS ==========
        'Search by name, code, email...': 'البحث بالاسم، الرمز، البريد الإلكتروني...',
        'Search by name, code, reference...': 'البحث بالاسم، الرمز، المرجع...',
        'Search by name or description...': 'البحث بالاسم أو الوصف...',
        'Search by name, email, code...': 'البحث بالاسم، البريد الإلكتروني، الرمز...',
        'Search by name or description': 'البحث بالاسم أو الوصف',
        
        # ========== PRICE LISTS ==========
        'Price Lists': 'قوائم الأسعار',
        'New Price List': 'قائمة أسعار جديدة',
        'Back to Products': 'العودة إلى المنتجات',
        'Manage multiple pricing tiers for different customers': 'إدارة مستويات أسعار متعددة لعملاء مختلفين',
        'Total Price Lists': 'إجمالي قوائم الأسعار',
        'Active Price Lists': 'قوائم الأسعار النشطة',
        'Inactive Price Lists': 'قوائم الأسعار غير النشطة',
        'No price lists found.': 'لم يتم العثور على قوائم أسعار.',
        'Create First Price List': 'إنشاء أول قائمة أسعار',
        'Are you sure you want to delete this price list?': 'هل أنت متأكد من أنك تريد حذف قائمة الأسعار هذه؟',
        'View Products': 'عرض المنتجات',
        
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
    print("CommerceFlow - Comprehensive Translation for ALL Views")
    print("============================================================")
    
    translations_dir = Path('app/translations')
    
    # Fill French and Arabic translations
    for lang in ['fr', 'ar']:
        po_file = translations_dir / lang / 'LC_MESSAGES' / 'messages.po'
        if po_file.exists():
            print(f"\n[{lang.upper()}] Filling comprehensive translations...")
            count = fill_po_file(po_file, ALL_TRANSLATIONS[lang], lang)
            print(f"  ✓ Filled {count} translations")
        else:
            print(f"\n[{lang.upper()}] ✗ File not found: {po_file}")
    
    print("\n============================================================")
    print("✓ Comprehensive translation filling completed!")
    print("\nNext step: Run 'pybabel compile -d app/translations' to compile")
    print("============================================================")

if __name__ == '__main__':
    main()

