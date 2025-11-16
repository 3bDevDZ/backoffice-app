# Service PDF avec ReportLab

## Vue d'ensemble

Le service PDF utilise **ReportLab** pour générer des PDFs professionnels à partir de données structurées. ReportLab est une bibliothèque Python pure qui ne nécessite **aucune dépendance système externe**, ce qui le rend parfaitement compatible avec Windows, Linux et macOS.

## Avantages de ReportLab

✅ **Aucune dépendance système** - Fonctionne immédiatement après `pip install reportlab`  
✅ **Cross-platform** - Windows, Linux, macOS  
✅ **Contrôle total** - Génération programmatique avec contrôle précis du layout  
✅ **Performant** - Rapide et efficace  
✅ **Gratuit et open-source** - Licence BSD  

## Installation

ReportLab est déjà inclus dans `requirements.txt` :

```bash
pip install reportlab xhtml2pdf
```

## Utilisation

### Génération de PDF de devis

```python
from app.services.pdf_service import pdf_service

quote_data = {
    'number': 'DEV-2025-00001',
    'version': 1,
    'status': 'draft',
    'customer': {
        'name': 'Client ABC',
        'code': 'CUST-001'
    },
    'created_at': '2025-01-27',
    'valid_until': '2025-02-27',
    'lines': [
        {
            'product_name': 'Produit 1',
            'product_code': 'PROD-001',
            'quantity': 10,
            'unit_price': 100.00,
            'discount_percent': 5.0,
            'line_total_ht': 950.00,
            'tax_rate': 20.0,
            'line_total_ttc': 1140.00
        }
    ],
    'subtotal': 950.00,
    'discount_amount': 47.50,
    'discount_percent': 5.0,
    'tax_amount': 180.25,
    'total': 1082.75,
    'notes': 'Notes du devis'
}

pdf_buffer = pdf_service.generate_quote_pdf(quote_data)
```

### Structure du PDF généré

Le PDF de devis contient :

1. **En-tête** : Titre "DEVIS" avec numéro
2. **Informations du devis** : Numéro, version, date, statut
3. **Informations client** : Nom et code client
4. **Tableau des lignes** : Produits avec quantités, prix, remises, totaux
5. **Section totaux** : Sous-total HT, remise, TVA, Total TTC
6. **Validité** : Date d'expiration du devis
7. **Notes** : Notes client si présentes
8. **Pied de page** : Mention automatique

## Formatage

- **Couleurs** : Vert (#4CAF50) pour les en-têtes et accents
- **Tableaux** : Alternance de couleurs pour les lignes
- **Typographie** : Helvetica pour le texte, styles personnalisés
- **Mise en page** : Marges de 20mm, format A4

## Personnalisation

Pour modifier le style du PDF, éditer `app/services/pdf_service.py` :

- **Couleurs** : Modifier les valeurs `colors.HexColor('#4CAF50')`
- **Tailles de police** : Ajuster `fontSize` dans les styles
- **Marges** : Modifier `rightMargin`, `leftMargin`, etc. dans `SimpleDocTemplate`
- **Layout** : Modifier les `colWidths` des tableaux

## Alternative : xhtml2pdf

Le service inclut également une méthode `generate_pdf_from_html()` qui utilise `xhtml2pdf` pour convertir du HTML en PDF. Cette méthode est utile si vous préférez utiliser des templates HTML/CSS.

```python
html_content = "<html><body><h1>Mon PDF</h1></body></html>"
pdf_buffer = pdf_service.generate_pdf_from_html(html_content)
```

**Note** : xhtml2pdf a un support CSS limité comparé à WeasyPrint, mais fonctionne sans dépendances système.

## Intégration avec les emails

Le service PDF est automatiquement utilisé lors de l'envoi de devis par email :

```python
# Dans app/tasks/email_tasks.py
quote_pdf = pdf_service.generate_quote_pdf(quote_data)
email_service.send_quote_email(
    to=recipient_email,
    quote_number=quote_dto.number,
    quote_pdf=quote_pdf,
    customer_name=quote_dto.customer_name
)
```

## Tests

Pour tester la génération de PDF :

```python
from app.services.pdf_service import pdf_service

# Données de test
test_data = {
    'number': 'TEST-001',
    'version': 1,
    'status': 'draft',
    'customer': {'name': 'Test', 'code': 'TEST'},
    'created_at': '2025-01-27',
    'lines': [],
    'subtotal': 0,
    'tax_amount': 0,
    'total': 0
}

pdf = pdf_service.generate_quote_pdf(test_data)
print(f"PDF généré: {len(pdf.getvalue())} bytes")
```

## Support RTL (Right-To-Left)

ReportLab supporte le texte RTL pour l'arabe. Pour activer le support RTL dans les PDFs, il faudrait utiliser `python-bidi` et `arabic-reshaper` (déjà installés via xhtml2pdf).

## Performance

- **Génération** : ~50-200ms pour un devis standard
- **Taille** : ~3-10 KB pour un devis avec quelques lignes
- **Mémoire** : Faible empreinte mémoire

## Limitations

- ReportLab génère des PDFs programmatiquement (pas de templates HTML/CSS complets)
- Le support CSS est limité comparé à WeasyPrint
- Pour des layouts très complexes, considérer xhtml2pdf ou des templates HTML

## Migration depuis WeasyPrint

Si vous aviez des templates HTML pour WeasyPrint, vous pouvez :
1. Les convertir en structure de données pour ReportLab
2. Utiliser `generate_pdf_from_html()` avec xhtml2pdf (support CSS limité)
3. Créer des templates ReportLab personnalisés

