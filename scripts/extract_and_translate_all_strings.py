#!/usr/bin/env python
"""
Extract all translatable strings from templates and generate comprehensive translations
for all modules in three languages (EN, FR, AR).
"""
import re
from pathlib import Path
from collections import defaultdict

# Extended translations for all modules
EXTENDED_TRANSLATIONS = {
    'fr': {
        # Common table headers
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
        
        # Common actions
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
        
        # Status
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
        
        # Messages
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
        
        # Dates
        'Date': 'Date',
        'From': 'De',
        'To': 'À',
        'Today': 'Aujourd\'hui',
        'Yesterday': 'Hier',
        'This week': 'Cette semaine',
        'This month': 'Ce mois',
        'This year': 'Cette année',
        
        # Pagination
        'Page': 'Page',
        'of': 'de',
        'Showing': 'Affichage',
        'to': 'à',
        'results': 'résultats',
        
        # Customer specific
        'Customer Management': 'Gestion des clients',
        'Manage your B2B and B2C customers': 'Gérez vos clients B2B et B2C',
        'Total Customers': 'Total clients',
        'B2B Customers': 'Clients B2B',
        'B2C Customers': 'Clients B2C',
        'Active Customers': 'Clients actifs',
        'New Customer': 'Nouveau client',
        'Edit Customer': 'Modifier le client',
        'View Customer': 'Voir le client',
        'Customer Details': 'Détails du client',
        'Customer Information': 'Informations client',
        'Contact Information': 'Informations de contact',
        'Billing Address': 'Adresse de facturation',
        'Shipping Address': 'Adresse de livraison',
        'Search by name, code, email...': 'Rechercher par nom, code, email...',
        'All Types': 'Tous les types',
        'All Statuses': 'Tous les statuts',
        'B2B': 'B2B',
        'B2C': 'B2C',
        
        # Product specific
        'Product Management': 'Gestion des produits',
        'Manage your product catalog': 'Gérez votre catalogue de produits',
        'New Product': 'Nouveau produit',
        'Edit Product': 'Modifier le produit',
        'View Product': 'Voir le produit',
        'Product Details': 'Détails du produit',
        'Product Information': 'Informations produit',
        'Product Variants': 'Variantes de produit',
        'Price Lists': 'Listes de prix',
        'Search by name, code, reference...': 'Rechercher par nom, code, référence...',
        
        # Order specific
        'Order Management': 'Gestion des commandes',
        'New Order': 'Nouvelle commande',
        'Edit Order': 'Modifier la commande',
        'View Order': 'Voir la commande',
        'Order Details': 'Détails de la commande',
        'Order Lines': 'Lignes de commande',
        'Order Summary': 'Résumé de la commande',
        'Confirm Order': 'Confirmer la commande',
        'Cancel Order': 'Annuler la commande',
        'Ship Order': 'Expédier la commande',
        
        # Purchase specific
        'Purchase Order Management': 'Gestion des ordres d\'achat',
        'New Purchase Order': 'Nouvel ordre d\'achat',
        'Edit Purchase Order': 'Modifier l\'ordre d\'achat',
        'View Purchase Order': 'Voir l\'ordre d\'achat',
        'Purchase Order Details': 'Détails de l\'ordre d\'achat',
        'Purchase Request': 'Demande d\'achat',
        'Purchase Requests': 'Demandes d\'achat',
        'New Purchase Request': 'Nouvelle demande d\'achat',
        'Purchase Receipt': 'Bon de réception',
        'Purchase Receipts': 'Bons de réception',
        'New Purchase Receipt': 'Nouveau bon de réception',
        'Supplier Invoice': 'Facture fournisseur',
        'Supplier Invoices': 'Factures fournisseurs',
        'New Supplier Invoice': 'Nouvelle facture fournisseur',
        'Create Receipt': 'Créer un bon de réception',
        'Create Invoice': 'Créer une facture',
        
        # Stock specific
        'Stock Management': 'Gestion des stocks',
        'Stock Overview': 'Vue d\'ensemble du stock',
        'Current Stock': 'Stock actuel',
        'Available Stock': 'Stock disponible',
        'Reserved Stock': 'Stock réservé',
        'Physical Stock': 'Stock physique',
        'Stock Movements': 'Mouvements de stock',
        'Stock Alerts': 'Alertes de stock',
        'Low Stock': 'Stock faible',
        'Out of Stock': 'Rupture de stock',
        'Stock Transfer': 'Transfert de stock',
        'Stock Transfers': 'Transferts de stock',
        'New Stock Transfer': 'Nouveau transfert de stock',
        'Ship Transfer': 'Expédier le transfert',
        'Receive Transfer': 'Réceptionner le transfert',
        'Cancel Transfer': 'Annuler le transfert',
        'Sites': 'Sites',
        'Warehouses': 'Entrepôts',
        'Locations': 'Emplacements',
        'New Site': 'Nouveau site',
        'New Warehouse': 'Nouvel entrepôt',
        'New Location': 'Nouvel emplacement',
        
        # Invoice specific
        'Invoice Management': 'Gestion des factures',
        'New Invoice': 'Nouvelle facture',
        'Edit Invoice': 'Modifier la facture',
        'View Invoice': 'Voir la facture',
        'Invoice Details': 'Détails de la facture',
        'Validate Invoice': 'Valider la facture',
        'Send Invoice': 'Envoyer la facture',
        'Download PDF': 'Télécharger le PDF',
        
        # Payment specific
        'Payment Management': 'Gestion des paiements',
        'New Payment': 'Nouveau paiement',
        'View Payment': 'Voir le paiement',
        'Payment Details': 'Détails du paiement',
        'Payment Allocation': 'Allocation de paiement',
        'Reconcile Payment': 'Rapprocher le paiement',
        'Payments Dashboard': 'Tableau de bord des paiements',
        'Overdue Invoices': 'Factures en retard',
        'Aging Report': 'Rapport de vieillissement',
        
        # Quote specific
        'Quote Management': 'Gestion des devis',
        'New Quote': 'Nouveau devis',
        'Edit Quote': 'Modifier le devis',
        'View Quote': 'Voir le devis',
        'Quote Details': 'Détails du devis',
        'Convert to Order': 'Convertir en commande',
        
        # Promotion specific
        'Promotion Management': 'Gestion des promotions',
        'New Promotion': 'Nouvelle promotion',
        'Edit Promotion': 'Modifier la promotion',
        'View Promotion': 'Voir la promotion',
        
        # Supplier specific
        'Supplier Management': 'Gestion des fournisseurs',
        'New Supplier': 'Nouveau fournisseur',
        'Edit Supplier': 'Modifier le fournisseur',
        'View Supplier': 'Voir le fournisseur',
        'Supplier Details': 'Détails du fournisseur',
        'Search by name, email, code...': 'Rechercher par nom, email, code...',
    },
    
    'ar': {
        # Common table headers
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
        
        # Common actions
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
        
        # Status
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
        
        # Messages
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
        
        # Dates
        'Date': 'التاريخ',
        'From': 'من',
        'To': 'إلى',
        'Today': 'اليوم',
        'Yesterday': 'أمس',
        'This week': 'هذا الأسبوع',
        'This month': 'هذا الشهر',
        'This year': 'هذه السنة',
        
        # Pagination
        'Page': 'صفحة',
        'of': 'من',
        'Showing': 'عرض',
        'to': 'إلى',
        'results': 'نتائج',
        
        # Customer specific
        'Customer Management': 'إدارة العملاء',
        'Manage your B2B and B2C customers': 'إدارة عملائك B2B و B2C',
        'Total Customers': 'إجمالي العملاء',
        'B2B Customers': 'عملاء B2B',
        'B2C Customers': 'عملاء B2C',
        'Active Customers': 'العملاء النشطون',
        'New Customer': 'عميل جديد',
        'Edit Customer': 'تعديل العميل',
        'View Customer': 'عرض العميل',
        'Customer Details': 'تفاصيل العميل',
        'Customer Information': 'معلومات العميل',
        'Contact Information': 'معلومات الاتصال',
        'Billing Address': 'عنوان الفوترة',
        'Shipping Address': 'عنوان الشحن',
        'Search by name, code, email...': 'البحث بالاسم، الرمز، البريد الإلكتروني...',
        'All Types': 'جميع الأنواع',
        'All Statuses': 'جميع الحالات',
        'B2B': 'B2B',
        'B2C': 'B2C',
        
        # Product specific
        'Product Management': 'إدارة المنتجات',
        'Manage your product catalog': 'إدارة كتالوج المنتجات',
        'New Product': 'منتج جديد',
        'Edit Product': 'تعديل المنتج',
        'View Product': 'عرض المنتج',
        'Product Details': 'تفاصيل المنتج',
        'Product Information': 'معلومات المنتج',
        'Product Variants': 'متغيرات المنتج',
        'Price Lists': 'قوائم الأسعار',
        'Search by name, code, reference...': 'البحث بالاسم، الرمز، المرجع...',
        
        # Order specific
        'Order Management': 'إدارة الطلبات',
        'New Order': 'طلب جديد',
        'Edit Order': 'تعديل الطلب',
        'View Order': 'عرض الطلب',
        'Order Details': 'تفاصيل الطلب',
        'Order Lines': 'بنود الطلب',
        'Order Summary': 'ملخص الطلب',
        'Confirm Order': 'تأكيد الطلب',
        'Cancel Order': 'إلغاء الطلب',
        'Ship Order': 'شحن الطلب',
        
        # Purchase specific
        'Purchase Order Management': 'إدارة أوامر الشراء',
        'New Purchase Order': 'أمر شراء جديد',
        'Edit Purchase Order': 'تعديل أمر الشراء',
        'View Purchase Order': 'عرض أمر الشراء',
        'Purchase Order Details': 'تفاصيل أمر الشراء',
        'Purchase Request': 'طلب شراء',
        'Purchase Requests': 'طلبات الشراء',
        'New Purchase Request': 'طلب شراء جديد',
        'Purchase Receipt': 'إيصال استلام',
        'Purchase Receipts': 'إيصالات الاستلام',
        'New Purchase Receipt': 'إيصال استلام جديد',
        'Supplier Invoice': 'فاتورة مورد',
        'Supplier Invoices': 'فواتير الموردين',
        'New Supplier Invoice': 'فاتورة مورد جديدة',
        'Create Receipt': 'إنشاء إيصال',
        'Create Invoice': 'إنشاء فاتورة',
        
        # Stock specific
        'Stock Management': 'إدارة المخزون',
        'Stock Overview': 'نظرة عامة على المخزون',
        'Current Stock': 'المخزون الحالي',
        'Available Stock': 'المخزون المتاح',
        'Reserved Stock': 'المخزون المحجوز',
        'Physical Stock': 'المخزون الفعلي',
        'Stock Movements': 'حركات المخزون',
        'Stock Alerts': 'تنبيهات المخزون',
        'Low Stock': 'مخزون منخفض',
        'Out of Stock': 'نفاد المخزون',
        'Stock Transfer': 'نقل المخزون',
        'Stock Transfers': 'تحويلات المخزون',
        'New Stock Transfer': 'نقل مخزون جديد',
        'Ship Transfer': 'شحن النقل',
        'Receive Transfer': 'استلام النقل',
        'Cancel Transfer': 'إلغاء النقل',
        'Sites': 'المواقع',
        'Warehouses': 'المستودعات',
        'Locations': 'المواقع',
        'New Site': 'موقع جديد',
        'New Warehouse': 'مستودع جديد',
        'New Location': 'موقع جديد',
        
        # Invoice specific
        'Invoice Management': 'إدارة الفواتير',
        'New Invoice': 'فاتورة جديدة',
        'Edit Invoice': 'تعديل الفاتورة',
        'View Invoice': 'عرض الفاتورة',
        'Invoice Details': 'تفاصيل الفاتورة',
        'Validate Invoice': 'التحقق من الفاتورة',
        'Send Invoice': 'إرسال الفاتورة',
        'Download PDF': 'تحميل PDF',
        
        # Payment specific
        'Payment Management': 'إدارة المدفوعات',
        'New Payment': 'دفعة جديدة',
        'View Payment': 'عرض الدفعة',
        'Payment Details': 'تفاصيل الدفعة',
        'Payment Allocation': 'تخصيص الدفعة',
        'Reconcile Payment': 'مطابقة الدفعة',
        'Payments Dashboard': 'لوحة تحكم المدفوعات',
        'Overdue Invoices': 'الفواتير المتأخرة',
        'Aging Report': 'تقرير التقادم',
        
        # Quote specific
        'Quote Management': 'إدارة العروض',
        'New Quote': 'عرض جديد',
        'Edit Quote': 'تعديل العرض',
        'View Quote': 'عرض العرض',
        'Quote Details': 'تفاصيل العرض',
        'Convert to Order': 'تحويل إلى طلب',
        
        # Promotion specific
        'Promotion Management': 'إدارة الترقيات',
        'New Promotion': 'ترقية جديدة',
        'Edit Promotion': 'تعديل الترقية',
        'View Promotion': 'عرض الترقية',
        
        # Supplier specific
        'Supplier Management': 'إدارة الموردين',
        'New Supplier': 'مورد جديد',
        'Edit Supplier': 'تعديل المورد',
        'View Supplier': 'عرض المورد',
        'Supplier Details': 'تفاصيل المورد',
        'Search by name, email, code...': 'البحث بالاسم، البريد الإلكتروني، الرمز...',
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
    print("CommerceFlow - Extract & Translate All Strings (FR, AR)")
    print("============================================================")
    
    translations_dir = Path('app/translations')
    
    # Fill French and Arabic translations
    for lang in ['fr', 'ar']:
        po_file = translations_dir / lang / 'LC_MESSAGES' / 'messages.po'
        if po_file.exists():
            print(f"\n[{lang.upper()}] Filling translations...")
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


