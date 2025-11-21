# Interface de Configuration - Documentation

## Vue d'ensemble

L'interface de configuration permet de gérer les paramètres de l'entreprise et de l'application directement depuis l'interface web, sans modifier les fichiers de configuration ou les variables d'environnement.

## Accès

- **URL** : `/settings`
- **Permissions** : Admin et Direction uniquement
- **Menu** : Lien "Settings" dans la sidebar (visible uniquement pour admin/direction)

## Fonctionnalités

### 1. Informations de l'Entreprise (`/settings/company`)

Permet de configurer les informations de l'entreprise qui apparaissent sur les documents (factures, commandes, devis, etc.).

#### Champs disponibles :
- **Informations de base** :
  - Nom de l'entreprise (requis)
  - Raison sociale
  - SIRET (14 chiffres)
  - Numéro de TVA
  - RCS
  - Forme juridique

- **Adresse** :
  - Adresse complète
  - Code postal
  - Ville
  - Pays (par défaut: France)

- **Contact** :
  - Téléphone
  - Email
  - Site web

#### Utilisation :
1. Accéder à `/settings/company`
2. Remplir les champs souhaités
3. Cliquer sur "Save Settings"
4. Les informations sont immédiatement disponibles pour les PDFs et autres documents

### 2. Paramètres de l'Application (`/settings/app`)

Permet de configurer le comportement de l'application.

#### Sections disponibles :

**Gestion du Stock** :
- Mode Simple : Interface simplifiée, un seul entrepôt
- Mode Avancé : Multi-sites, transfers inter-sites, vue consolidée

**Valeurs par défaut** :
- Devise (EUR, USD, GBP, MAD)
- Taux de TVA par défaut (%)
- Langue par défaut (Français, Arabe)

**Préfixes de documents** :
- Factures (INV par défaut)
- Commandes d'achat (PO par défaut)
- Réceptions (REC par défaut)
- Devis (QUO par défaut)
- Validité des devis (jours)

**Paramètres de facturation** :
- Pied de page des factures (texte libre)

**Notifications email** :
- Activer/désactiver les notifications
- Confirmation de commande
- Envoi de factures

#### Utilisation :
1. Accéder à `/settings/app`
2. Modifier les paramètres souhaités
3. Cliquer sur "Save Settings"
4. Les changements sont immédiatement effectifs

## Intégration Technique

### Accès aux Settings dans le Code

```python
from app.utils.settings_helper import (
    get_company_settings,
    get_app_settings,
    get_stock_management_mode,
    get_default_currency,
    get_default_tax_rate,
    get_default_language
)

# Exemple d'utilisation
company = get_company_settings()
print(f"Company: {company.name}")

stock_mode = get_stock_management_mode()  # 'simple' ou 'advanced'
currency = get_default_currency()  # 'EUR'
tax_rate = get_default_tax_rate()  # 20.0
```

### Helper PDF

Le helper PDF (`app/services/pdf_service_helper.py`) utilise automatiquement les settings de la base de données :

```python
from app.services.pdf_service_helper import get_company_info

company_info = get_company_info()
# Retourne un dict avec name, address, postal_code, city, country, phone, email, website
```

### Pattern Singleton

Les settings utilisent un pattern singleton :
- Une seule entrée `CompanySettings` dans la base
- Une seule entrée `AppSettings` dans la base
- Les handlers créent automatiquement les settings par défaut s'ils n'existent pas

## Migration

La migration `0013_add_settings_tables` crée les tables nécessaires :

```bash
python -m alembic upgrade head
```

## Valeurs par Défaut

### CompanySettings
- `name`: "CommerceFlow"
- `country`: "France"
- Autres champs: `None`

### AppSettings
- `stock_management_mode`: "simple"
- `default_currency`: "EUR"
- `default_tax_rate`: 20.00
- `default_language`: "fr"
- `invoice_prefix`: "INV"
- `purchase_order_prefix`: "PO"
- `receipt_prefix`: "REC"
- `quote_prefix`: "QUO"
- `quote_validity_days`: 30
- `email_notifications_enabled`: `True`
- `email_order_confirmation`: `True`
- `email_invoice_sent`: `True`

## Impact sur les Fonctionnalités

### Mode Stock Simple vs Avancé

Le mode stock affecte :
- **Interface de réception** : Mode simple masque la sélection de site/location
- **Dashboard stock** : Mode avancé permet la vue multi-sites
- **Transfers** : Disponibles uniquement en mode avancé

### Informations Entreprise

Les informations de l'entreprise sont utilisées dans :
- En-têtes des PDFs (factures, commandes, devis, réceptions)
- Emails envoyés
- Documents exportés

## Sécurité

- Accès restreint aux rôles `admin` et `direction`
- Validation des données côté serveur
- Protection contre les injections SQL (SQLAlchemy ORM)

## Dépannage

### Les settings ne se sauvegardent pas
- Vérifier les permissions (admin/direction)
- Vérifier les logs d'erreur
- Vérifier que la migration a été exécutée

### Le mode stock ne change pas
- Vérifier que les settings ont été sauvegardés
- Vider le cache du navigateur
- Redémarrer l'application si nécessaire

### Les PDFs n'utilisent pas les nouvelles informations
- Vérifier que `get_company_info()` utilise bien les settings de la base
- Vérifier que les settings ont été sauvegardés correctement

