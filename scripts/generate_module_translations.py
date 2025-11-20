#!/usr/bin/env python
"""
Generate comprehensive translations for all modules in three languages (EN, FR, AR).
This script extracts strings from templates and creates organized translations.
"""
import re
from pathlib import Path
from collections import defaultdict

# Comprehensive translations organized by module
MODULE_TRANSLATIONS = {
    # ========== COMMON / SHARED ==========
    'common': {
        'en': {
            'Loading...': 'Loading...',
            'Error': 'Error',
            'Success': 'Success',
            'Warning': 'Warning',
            'Info': 'Info',
            'Cancel': 'Cancel',
            'Save': 'Save',
            'Delete': 'Delete',
            'Edit': 'Edit',
            'View': 'View',
            'Create': 'Create',
            'Update': 'Update',
            'Submit': 'Submit',
            'Back': 'Back',
            'Next': 'Next',
            'Previous': 'Previous',
            'Search': 'Search',
            'Filter': 'Filter',
            'Reset': 'Reset',
            'Close': 'Close',
            'Confirm': 'Confirm',
            'Yes': 'Yes',
            'No': 'No',
            'OK': 'OK',
            'Add': 'Add',
            'Remove': 'Remove',
            'Select': 'Select',
            'Choose': 'Choose',
            'Upload': 'Upload',
            'Download': 'Download',
            'Export': 'Export',
            'Import': 'Import',
            'Print': 'Print',
            'Date': 'Date',
            'From': 'From',
            'To': 'To',
            'Today': 'Today',
            'Yesterday': 'Yesterday',
            'This week': 'This week',
            'This month': 'This month',
            'This year': 'This year',
            'Page': 'Page',
            'of': 'of',
            'Showing': 'Showing',
            'to': 'to',
            'results': 'results',
            'No results found': 'No results found',
            'Active': 'Active',
            'Inactive': 'Inactive',
            'Draft': 'Draft',
            'Confirmed': 'Confirmed',
            'Cancelled': 'Cancelled',
            'Completed': 'Completed',
            'Pending': 'Pending',
            'Archived': 'Archived',
            'Blocked': 'Blocked',
        },
        'fr': {
            'Loading...': 'Chargement...',
            'Error': 'Erreur',
            'Success': 'Succès',
            'Warning': 'Avertissement',
            'Info': 'Information',
            'Cancel': 'Annuler',
            'Save': 'Enregistrer',
            'Delete': 'Supprimer',
            'Edit': 'Modifier',
            'View': 'Voir',
            'Create': 'Créer',
            'Update': 'Mettre à jour',
            'Submit': 'Soumettre',
            'Back': 'Retour',
            'Next': 'Suivant',
            'Previous': 'Précédent',
            'Search': 'Rechercher',
            'Filter': 'Filtrer',
            'Reset': 'Réinitialiser',
            'Close': 'Fermer',
            'Confirm': 'Confirmer',
            'Yes': 'Oui',
            'No': 'Non',
            'OK': 'OK',
            'Add': 'Ajouter',
            'Remove': 'Retirer',
            'Select': 'Sélectionner',
            'Choose': 'Choisir',
            'Upload': 'Télécharger',
            'Download': 'Télécharger',
            'Export': 'Exporter',
            'Import': 'Importer',
            'Print': 'Imprimer',
            'Date': 'Date',
            'From': 'De',
            'To': 'À',
            'Today': "Aujourd'hui",
            'Yesterday': 'Hier',
            'This week': 'Cette semaine',
            'This month': 'Ce mois',
            'This year': 'Cette année',
            'Page': 'Page',
            'of': 'de',
            'Showing': 'Affichage',
            'to': 'à',
            'results': 'résultats',
            'No results found': 'Aucun résultat trouvé',
            'Active': 'Actif',
            'Inactive': 'Inactif',
            'Draft': 'Brouillon',
            'Confirmed': 'Confirmé',
            'Cancelled': 'Annulé',
            'Completed': 'Terminé',
            'Pending': 'En attente',
            'Archived': 'Archivé',
            'Blocked': 'Bloqué',
        },
        'ar': {
            'Loading...': 'جاري التحميل...',
            'Error': 'خطأ',
            'Success': 'نجاح',
            'Warning': 'تحذير',
            'Info': 'معلومات',
            'Cancel': 'إلغاء',
            'Save': 'حفظ',
            'Delete': 'حذف',
            'Edit': 'تعديل',
            'View': 'عرض',
            'Create': 'إنشاء',
            'Update': 'تحديث',
            'Submit': 'إرسال',
            'Back': 'رجوع',
            'Next': 'التالي',
            'Previous': 'السابق',
            'Search': 'بحث',
            'Filter': 'تصفية',
            'Reset': 'إعادة تعيين',
            'Close': 'إغلاق',
            'Confirm': 'تأكيد',
            'Yes': 'نعم',
            'No': 'لا',
            'OK': 'موافق',
            'Add': 'إضافة',
            'Remove': 'إزالة',
            'Select': 'اختيار',
            'Choose': 'اختر',
            'Upload': 'رفع',
            'Download': 'تحميل',
            'Export': 'تصدير',
            'Import': 'استيراد',
            'Print': 'طباعة',
            'Date': 'التاريخ',
            'From': 'من',
            'To': 'إلى',
            'Today': 'اليوم',
            'Yesterday': 'أمس',
            'This week': 'هذا الأسبوع',
            'This month': 'هذا الشهر',
            'This year': 'هذه السنة',
            'Page': 'صفحة',
            'of': 'من',
            'Showing': 'عرض',
            'to': 'إلى',
            'results': 'نتائج',
            'No results found': 'لم يتم العثور على نتائج',
            'Active': 'نشط',
            'Inactive': 'غير نشط',
            'Draft': 'مسودة',
            'Confirmed': 'مؤكد',
            'Cancelled': 'ملغي',
            'Completed': 'مكتمل',
            'Pending': 'قيد الانتظار',
            'Archived': 'مؤرشف',
            'Blocked': 'محظور',
        }
    },
    
    # ========== DASHBOARD ==========
    'dashboard': {
        'en': {
            'Dashboard': 'Dashboard',
            'Overview of your business KPIs, sales, and key metrics': 'Overview of your business KPIs, sales, and key metrics',
        },
        'fr': {
            'Dashboard': 'Tableau de bord',
            'Overview of your business KPIs, sales, and key metrics': "Aperçu des KPI, ventes et métriques clés de votre entreprise",
        },
        'ar': {
            'Dashboard': 'لوحة التحكم',
            'Overview of your business KPIs, sales, and key metrics': 'نظرة عامة على مؤشرات الأداء الرئيسية والمبيعات والمقاييس الرئيسية لعملك',
        }
    },
    
    # ========== SALES MODULE ==========
    'sales': {
        'en': {
            'Sales': 'Sales',
            'Manage your sales process from quotes to payments': 'Manage your sales process from quotes to payments',
            'Customers': 'Customers',
            'Manage customer database and information': 'Manage customer database and information',
            'Customer Management': 'Customer Management',
            'Manage your B2B and B2C customers': 'Manage your B2B and B2C customers',
            'Total Customers': 'Total Customers',
            'B2B Customers': 'B2B Customers',
            'B2C Customers': 'B2C Customers',
            'Active Customers': 'Active Customers',
            'New Customer': 'New Customer',
            'Search by name, code, email...': 'Search by name, code, email...',
            'All Types': 'All Types',
            'All Statuses': 'All Statuses',
            'CUSTOMER': 'CUSTOMER',
            'CODE': 'CODE',
            'TYPE': 'TYPE',
            'EMAIL': 'EMAIL',
            'PHONE': 'PHONE',
            'STATUS': 'STATUS',
            'ACTIONS': 'ACTIONS',
            'B2B': 'B2B',
            'B2C': 'B2C',
            'Quotes': 'Quotes',
            'Create and manage sales quotes': 'Create and manage sales quotes',
            'Orders': 'Orders',
            'Manage sales orders and fulfillment': 'Manage sales orders and fulfillment',
            'Promotions': 'Promotions',
            'Manage promotional campaigns and discounts': 'Manage promotional campaigns and discounts',
            'Invoices': 'Invoices',
            'Generate and manage customer invoices': 'Generate and manage customer invoices',
            'Payments': 'Payments',
            'Record payments and manage collections': 'Record payments and manage collections',
            'Payments Dashboard': 'Payments Dashboard',
            'View payment KPIs and aging reports': 'View payment KPIs and aging reports',
        },
        'fr': {
            'Sales': 'Ventes',
            'Manage your sales process from quotes to payments': 'Gérez votre processus de vente des devis aux paiements',
            'Customers': 'Clients',
            'Manage customer database and information': "Gérer la base de données et les informations clients",
            'Customer Management': 'Gestion des clients',
            'Manage your B2B and B2C customers': 'Gérez vos clients B2B et B2C',
            'Total Customers': 'Total clients',
            'B2B Customers': 'Clients B2B',
            'B2C Customers': 'Clients B2C',
            'Active Customers': 'Clients actifs',
            'New Customer': 'Nouveau client',
            'Search by name, code, email...': 'Rechercher par nom, code, email...',
            'All Types': 'Tous les types',
            'All Statuses': 'Tous les statuts',
            'CUSTOMER': 'CLIENT',
            'CODE': 'CODE',
            'TYPE': 'TYPE',
            'EMAIL': 'EMAIL',
            'PHONE': 'TÉLÉPHONE',
            'STATUS': 'STATUT',
            'ACTIONS': 'ACTIONS',
            'B2B': 'B2B',
            'B2C': 'B2C',
            'Quotes': 'Devis',
            'Create and manage sales quotes': 'Créer et gérer les devis de vente',
            'Orders': 'Commandes',
            'Manage sales orders and fulfillment': 'Gérer les commandes de vente et leur exécution',
            'Promotions': 'Promotions',
            'Manage promotional campaigns and discounts': 'Gérer les campagnes promotionnelles et les remises',
            'Invoices': 'Factures',
            'Generate and manage customer invoices': 'Générer et gérer les factures clients',
            'Payments': 'Paiements',
            'Record payments and manage collections': 'Enregistrer les paiements et gérer les recouvrements',
            'Payments Dashboard': 'Tableau de bord des paiements',
            'View payment KPIs and aging reports': 'Voir les KPI de paiement et les rapports de vieillissement',
        },
        'ar': {
            'Sales': 'المبيعات',
            'Manage your sales process from quotes to payments': 'إدارة عملية المبيعات من العروض إلى المدفوعات',
            'Customers': 'العملاء',
            'Manage customer database and information': 'إدارة قاعدة بيانات العملاء والمعلومات',
            'Customer Management': 'إدارة العملاء',
            'Manage your B2B and B2C customers': 'إدارة عملائك B2B و B2C',
            'Total Customers': 'إجمالي العملاء',
            'B2B Customers': 'عملاء B2B',
            'B2C Customers': 'عملاء B2C',
            'Active Customers': 'العملاء النشطون',
            'New Customer': 'عميل جديد',
            'Search by name, code, email...': 'البحث بالاسم، الرمز، البريد الإلكتروني...',
            'All Types': 'جميع الأنواع',
            'All Statuses': 'جميع الحالات',
            'CUSTOMER': 'العميل',
            'CODE': 'الرمز',
            'TYPE': 'النوع',
            'EMAIL': 'البريد الإلكتروني',
            'PHONE': 'الهاتف',
            'STATUS': 'الحالة',
            'ACTIONS': 'الإجراءات',
            'B2B': 'B2B',
            'B2C': 'B2C',
            'Quotes': 'العروض',
            'Create and manage sales quotes': 'إنشاء وإدارة عروض المبيعات',
            'Orders': 'الطلبات',
            'Manage sales orders and fulfillment': 'إدارة طلبات المبيعات والوفاء',
            'Promotions': 'الترقيات',
            'Manage promotional campaigns and discounts': 'إدارة الحملات الترويجية والخصومات',
            'Invoices': 'الفواتير',
            'Generate and manage customer invoices': 'إنشاء وإدارة فواتير العملاء',
            'Payments': 'المدفوعات',
            'Record payments and manage collections': 'تسجيل المدفوعات وإدارة التحصيل',
            'Payments Dashboard': 'لوحة تحكم المدفوعات',
            'View payment KPIs and aging reports': 'عرض مؤشرات الأداء الرئيسية للمدفوعات وتقارير التقادم',
        }
    },
    
    # ========== PURCHASES MODULE ==========
    'purchases': {
        'en': {
            'Purchases': 'Purchases',
            'Manage your complete purchase cycle from requests to invoices': 'Manage your complete purchase cycle from requests to invoices',
            'Suppliers': 'Suppliers',
            'Manage supplier database and information': 'Manage supplier database and information',
            'Purchase Requests': 'Purchase Requests',
            'Create and manage purchase requests': 'Create and manage purchase requests',
            'Purchase Orders': 'Purchase Orders',
            'Manage purchase orders from suppliers': 'Manage purchase orders from suppliers',
            'Purchase Receipts': 'Purchase Receipts',
            'Record goods received from suppliers': 'Record goods received from suppliers',
            'Supplier Invoices': 'Supplier Invoices',
            'Process and match supplier invoices': 'Process and match supplier invoices',
        },
        'fr': {
            'Purchases': 'Achats',
            'Manage your complete purchase cycle from requests to invoices': 'Gérez votre cycle d\'achat complet des demandes aux factures',
            'Suppliers': 'Fournisseurs',
            'Manage supplier database and information': 'Gérer la base de données et les informations fournisseurs',
            'Purchase Requests': 'Demandes d\'achat',
            'Create and manage purchase requests': 'Créer et gérer les demandes d\'achat',
            'Purchase Orders': 'Ordres d\'achat',
            'Manage purchase orders from suppliers': 'Gérer les ordres d\'achat des fournisseurs',
            'Purchase Receipts': 'Bons de réception',
            'Record goods received from suppliers': 'Enregistrer les marchandises reçues des fournisseurs',
            'Supplier Invoices': 'Factures fournisseurs',
            'Process and match supplier invoices': 'Traiter et faire correspondre les factures fournisseurs',
        },
        'ar': {
            'Purchases': 'المشتريات',
            'Manage your complete purchase cycle from requests to invoices': 'إدارة دورة الشراء الكاملة من الطلبات إلى الفواتير',
            'Suppliers': 'الموردون',
            'Manage supplier database and information': 'إدارة قاعدة بيانات الموردين والمعلومات',
            'Purchase Requests': 'طلبات الشراء',
            'Create and manage purchase requests': 'إنشاء وإدارة طلبات الشراء',
            'Purchase Orders': 'أوامر الشراء',
            'Manage purchase orders from suppliers': 'إدارة أوامر الشراء من الموردين',
            'Purchase Receipts': 'إيصالات الاستلام',
            'Record goods received from suppliers': 'تسجيل البضائع المستلمة من الموردين',
            'Supplier Invoices': 'فواتير الموردين',
            'Process and match supplier invoices': 'معالجة ومطابقة فواتير الموردين',
        }
    },
    
    # ========== INVENTORY MODULE ==========
    'inventory': {
        'en': {
            'Inventory': 'Inventory',
            'Manage stock levels, locations, and movements': 'Manage stock levels, locations, and movements',
            'Stock Overview': 'Stock Overview',
            'View current stock levels and availability': 'View current stock levels and availability',
            'Sites': 'Sites',
            'Manage warehouse sites and locations': 'Manage warehouse sites and locations',
            'Warehouses': 'Warehouses',
            'Manage warehouse locations structure': 'Manage warehouse locations structure',
            'Stock Transfers': 'Stock Transfers',
            'Transfer stock between sites': 'Transfer stock between sites',
            'Stock Movements': 'Stock Movements',
            'View and track stock movements history': 'View and track stock movements history',
            'Stock Alerts': 'Stock Alerts',
            'Monitor low stock and reorder alerts': 'Monitor low stock and reorder alerts',
        },
        'fr': {
            'Inventory': 'Inventaire',
            'Manage stock levels, locations, and movements': 'Gérer les niveaux de stock, emplacements et mouvements',
            'Stock Overview': 'Vue d\'ensemble du stock',
            'View current stock levels and availability': 'Voir les niveaux de stock actuels et la disponibilité',
            'Sites': 'Sites',
            'Manage warehouse sites and locations': 'Gérer les sites et emplacements d\'entrepôt',
            'Warehouses': 'Entrepôts',
            'Manage warehouse locations structure': 'Gérer la structure des emplacements d\'entrepôt',
            'Stock Transfers': 'Transferts de stock',
            'Transfer stock between sites': 'Transférer le stock entre les sites',
            'Stock Movements': 'Mouvements de stock',
            'View and track stock movements history': 'Voir et suivre l\'historique des mouvements de stock',
            'Stock Alerts': 'Alertes de stock',
            'Monitor low stock and reorder alerts': 'Surveiller les alertes de stock faible et de réapprovisionnement',
        },
        'ar': {
            'Inventory': 'المخزون',
            'Manage stock levels, locations, and movements': 'إدارة مستويات المخزون والمواقع والحركات',
            'Stock Overview': 'نظرة عامة على المخزون',
            'View current stock levels and availability': 'عرض مستويات المخزون الحالية والتوفر',
            'Sites': 'المواقع',
            'Manage warehouse sites and locations': 'إدارة مواقع المستودعات والمواقع',
            'Warehouses': 'المستودعات',
            'Manage warehouse locations structure': 'إدارة هيكل مواقع المستودعات',
            'Stock Transfers': 'تحويلات المخزون',
            'Transfer stock between sites': 'نقل المخزون بين المواقع',
            'Stock Movements': 'حركات المخزون',
            'View and track stock movements history': 'عرض وتتبع تاريخ حركات المخزون',
            'Stock Alerts': 'تنبيهات المخزون',
            'Monitor low stock and reorder alerts': 'مراقبة تنبيهات المخزون المنخفض وإعادة الطلب',
        }
    },
    
    # ========== CATALOG MODULE ==========
    'catalog': {
        'en': {
            'Catalog': 'Catalog',
            'Manage your product catalog and pricing': 'Manage your product catalog and pricing',
            'Products': 'Products',
            'Manage product catalog and variants': 'Manage product catalog and variants',
            'Price Lists': 'Price Lists',
            'Create and manage pricing lists': 'Create and manage pricing lists',
        },
        'fr': {
            'Catalog': 'Catalogue',
            'Manage your product catalog and pricing': 'Gérez votre catalogue de produits et vos tarifs',
            'Products': 'Produits',
            'Manage product catalog and variants': 'Gérer le catalogue de produits et les variantes',
            'Price Lists': 'Listes de prix',
            'Create and manage pricing lists': 'Créer et gérer les listes de prix',
        },
        'ar': {
            'Catalog': 'الكتالوج',
            'Manage your product catalog and pricing': 'إدارة كتالوج المنتجات والأسعار',
            'Products': 'المنتجات',
            'Manage product catalog and variants': 'إدارة كتالوج المنتجات والمتغيرات',
            'Price Lists': 'قوائم الأسعار',
            'Create and manage pricing lists': 'إنشاء وإدارة قوائم الأسعار',
        }
    },
    
    # ========== SETTINGS MODULE ==========
    'settings': {
        'en': {
            'Settings': 'Settings',
            'Configure company information and application settings': 'Configure company information and application settings',
            'Application Settings': 'Application Settings',
            'Company Information': 'Company Information',
            'Manage application and company settings': 'Manage application and company settings',
            'Default Language': 'Default Language',
            'Document Prefixes': 'Document Prefixes',
            'Stock Management': 'Stock Management',
        },
        'fr': {
            'Settings': 'Paramètres',
            'Configure company information and application settings': 'Configurer les informations de l\'entreprise et les paramètres de l\'application',
            'Application Settings': 'Paramètres de l\'application',
            'Company Information': 'Informations de l\'entreprise',
            'Manage application and company settings': 'Gérer les paramètres de l\'application et de l\'entreprise',
            'Default Language': 'Langue par défaut',
            'Document Prefixes': 'Préfixes de documents',
            'Stock Management': 'Gestion des stocks',
        },
        'ar': {
            'Settings': 'الإعدادات',
            'Configure company information and application settings': 'تكوين معلومات الشركة وإعدادات التطبيق',
            'Application Settings': 'إعدادات التطبيق',
            'Company Information': 'معلومات الشركة',
            'Manage application and company settings': 'إدارة إعدادات التطبيق والشركة',
            'Default Language': 'اللغة الافتراضية',
            'Document Prefixes': 'بادئات المستندات',
            'Stock Management': 'إدارة المخزون',
        }
    },
    
    # ========== MODULES ==========
    'modules': {
        'en': {
            'Modules': 'Modules',
            'Select a module to get started': 'Select a module to get started',
            'Back to Modules': 'Back to Modules',
            'Menu': 'Menu',
            'Module Menu': 'Module Menu',
            'Quick Actions': 'Quick Actions',
            'New Order': 'New Order',
            'New Purchase Order': 'New Purchase Order',
            'New Product': 'New Product',
            'New Customer': 'New Customer',
        },
        'fr': {
            'Modules': 'Modules',
            'Select a module to get started': 'Sélectionnez un module pour commencer',
            'Back to Modules': 'Retour aux modules',
            'Menu': 'Menu',
            'Module Menu': 'Menu du module',
            'Quick Actions': 'Actions rapides',
            'New Order': 'Nouvelle commande',
            'New Purchase Order': 'Nouvel ordre d\'achat',
            'New Product': 'Nouveau produit',
            'New Customer': 'Nouveau client',
        },
        'ar': {
            'Modules': 'الوحدات',
            'Select a module to get started': 'اختر وحدة للبدء',
            'Back to Modules': 'العودة إلى الوحدات',
            'Menu': 'القائمة',
            'Module Menu': 'قائمة الوحدة',
            'Quick Actions': 'إجراءات سريعة',
            'New Order': 'طلب جديد',
            'New Purchase Order': 'أمر شراء جديد',
            'New Product': 'منتج جديد',
            'New Customer': 'عميل جديد',
        }
    },
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
    print("CommerceFlow - Generate Module Translations (EN, FR, AR)")
    print("============================================================")
    
    translations_dir = Path('app/translations')
    
    # Combine all translations
    all_translations = {}
    for module_name, module_trans in MODULE_TRANSLATIONS.items():
        for lang in ['en', 'fr', 'ar']:
            if lang not in all_translations:
                all_translations[lang] = {}
            all_translations[lang].update(module_trans.get(lang, {}))
    
    # Fill each language file
    for lang in ['en', 'fr', 'ar']:
        po_file = translations_dir / lang / 'LC_MESSAGES' / 'messages.po'
        if po_file.exists():
            print(f"\n[{lang.upper()}] Filling translations...")
            count = fill_po_file(po_file, all_translations[lang], lang)
            print(f"  ✓ Filled {count} translations")
        else:
            print(f"\n[{lang.upper()}] ✗ File not found: {po_file}")
    
    print("\n============================================================")
    print("✓ Translation generation completed!")
    print("\nNext step: Run 'pybabel compile -d app/translations' to compile")
    print("============================================================")

if __name__ == '__main__':
    main()


