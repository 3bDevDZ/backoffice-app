# GMFlow - Système de Gestion Commerciale

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**GMFlow** est un système de gestion commerciale complet développé avec une architecture moderne basée sur **DDD (Domain-Driven Design)**, **CQRS (Command Query Responsibility Segregation)** et **Domain Events**. Il permet de gérer l'ensemble du cycle commercial : produits, clients, stocks, ventes, achats et facturation.

## 📋 Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Stack Technique](#stack-technique)
- [Installation](#installation)
- [Structure du Projet](#structure-du-projet)
- [Tests](#tests)
- [Documentation](#documentation)
- [Contribuer](#contribuer)

## 🎯 Vue d'ensemble

GMFlow est une solution complète, moderne et évolutive pour la gestion commerciale, adaptée aux besoins spécifiques des entreprises B2B et B2C. Le système centralise toutes les données commerciales, automatise les tâches répétitives et offre une traçabilité complète avec un reporting en temps réel.

### Objectifs

- ✅ **Centralisation** : Toutes les données commerciales en un seul endroit
- ✅ **Automatisation** : Réduction de 40% du temps sur les tâches administratives
- ✅ **Traçabilité** : Suivi complet de tous les mouvements et transactions
- ✅ **Performance** : Temps de réponse < 2s, support de 50+ utilisateurs simultanés
- ✅ **Évolutivité** : Architecture modulaire supportant une croissance ×10

## 🚀 Fonctionnalités

### Phase 1 - MVP (Implémenté)

#### 📦 Gestion Produits
- Catalogue produits complet avec catégorisation hiérarchique
- Variantes produits (couleur, taille, etc.)
- Codes-barres et images multiples
- **Prix multiples** : Listes de prix, prix dégressifs (volume pricing), prix promotionnels
- Historique des prix et coûts
- Import/Export Excel/CSV

#### 👥 Gestion Clients
- Fiches clients complètes (B2B/B2C)
- Adresses et contacts multiples
- Conditions commerciales (délais paiement, remises, limites crédit)
- Historique complet des interactions
- Statistiques client (CA, panier moyen, fréquence)

#### 📊 Gestion Stock
- Suivi temps réel multi-emplacements
- Mouvements de stock (entrées/sorties/transferts/ajustements)
- Alertes rupture de stock
- Règles de réapprovisionnement automatiques
- Inventaires
- Valorisation AVCO (Average Cost Method)
- Traçabilité complète

#### 💼 Gestion Ventes
- **Devis** avec versioning et workflow complet
- Conversion devis → commande
- **Commandes** avec réservation automatique du stock
- Workflow de validation (brouillon → confirmée → en préparation → prête → expédiée → livrée)
- Génération PDF professionnel
- Envoi email automatique

#### 📈 Dashboard
- KPI essentiels en temps réel
- CA jour/mois/année
- Stock en alerte
- Commandes en cours

### Phase 2 - Complet (Implémenté)

#### 🧾 Facturation
- Génération de factures conformes (Article 289 CGI)
- Numérotation légale séquentielle sans trou (FA-YYYY-XXXXX)
- Facturation partielle depuis commandes livrées
- Avoirs (credit notes) avec numérotation séparée (AV-YYYY-XXXXX)
- Génération PDF légal avec mentions obligatoires
- Envoi automatique par email
- Export FEC (Fichier des Écritures Comptables)

#### 💰 Paiements
- Enregistrement des paiements
- Rapprochement bancaire
- Échéanciers
- Relances automatiques

#### 🛒 Achats
- Commandes fournisseurs
- Réceptions avec mise à jour automatique du stock
- Factures fournisseurs
- Mise à jour automatique des coûts produits (AVCO)

## 🏗️ Architecture

GMFlow suit une architecture **Clean Architecture** avec **DDD**, **CQRS** et **Domain Events**, adaptée au stack Python/Flask.

### Vue d'ensemble

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION                         │
│              (Templates Jinja2 + HTML/CSS/JS)           │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────┐
│                    WEB LAYER (Flask)                     │
│              (Blueprints + Routes)                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              APPLICATION LAYER (CQRS)                    │
│                                                          │
│  ┌──────────────┐              ┌──────────────┐        │
│  │  COMMANDS    │              │   QUERIES     │        │
│  │ (Write Side) │              │ (Read Side)   │        │
│  └──────┬───────┘              └──────┬────────┘        │
│         │                              │                 │
│         │ Mediator                     │ Mediator        │
│         ▼                              ▼                 │
│  ┌──────────────┐              ┌──────────────┐        │
│  │Command       │              │Query         │        │
│  │Handlers      │              │Handlers      │        │
│  └──────┬───────┘              └──────┬────────┘        │
└─────────┼──────────────────────────────┼─────────────────┘
          │                              │
          │                              │ Read-Only
┌─────────▼──────────────────────────────▼─────────────────┐
│                  DOMAIN LAYER                           │
│                                                          │
│  ┌────────────┐     ┌──────────────┐    ┌────────────┐ │
│  │ Aggregates │────►│Domain Events │───►│ Handlers   │ │
│  │            │     │              │    │            │ │
│  └────────────┘     └──────────────┘    └─────┬──────┘ │
│                                                 │        │
│                                                 ▼        │
│                                         ┌───────────────┐│
│                                         │ Business      ││
│                                         │ Logic         ││
│                                         └───────┬───────┘│
└─────────────────────────────────────────────────┼────────┘
                                                  │
┌─────────────────────────────────────────────────▼─────────┐
│              INFRASTRUCTURE LAYER                        │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ SQLAlchemy   │  │ OutboxEvents │  │ Celery Worker  │ │
│  │ ORM          │  │ Table        │  │ (Background)   │ │
│  └──────────────┘  └──────┬───────┘  └────────┬───────┘ │
│                            │                    │         │
│  ┌─────────────────────────▼────────────────────▼───────┐ │
│  │          PostgreSQL / SQLite Database               │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │   RabbitMQ (Integration Events uniquement)           │ │
│  │   (Communication vers systèmes externes)              │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

### Principes Architecturaux

#### 1. CQRS (Command Query Responsibility Segregation)

**Commands (Write Side) :**
- Modifient l'état du système
- Retournent succès/échec (pas de données)
- Utilisent les Aggregates
- Lèvent des Domain Events

**Queries (Read Side) :**
- Lecture seule
- Retournent des DTOs
- Optimisées pour la lecture
- Accès direct DB (pas d'Aggregates)

#### 2. Domain-Driven Design (DDD)

**Aggregates :**
- Cluster d'entités traitées comme une unité
- Aggregate Root = point d'entrée unique
- Validation des invariants métier
- Lèvent Domain Events lors des changements d'état

**Domain Events :**
- Événements métier levés par les Aggregates
- Communication INTERNE uniquement (même système)
- Traités de manière synchrone par des handlers

#### 3. Domain Events vs Integration Events

**Domain Events (Internes) :**
- Traités **SYNCHRONEMENT** dans la même transaction
- Handlers appelés via dispatcher Python
- Restent dans les limites du bounded context
- Exemples : `OrderPlacedDomainEvent`, `StockReservedDomainEvent`

**Integration Events (Externes) :**
- Sauvegardés dans table **OutboxEvents**
- Envoyés vers **RabbitMQ** par Background Worker (Celery)
- Traitement **ASYNCHRONE**
- Communication **INTER-BOUNDED CONTEXTS**
- Exemples : `InvoiceValidatedIntegrationEvent`, `OrderPlacedIntegrationEvent`

### Flow d'un Domain Event

```
1. UI Action (ex: Valider une commande)
   ↓
2. Route Flask → Command
   ↓
3. Command Handler → Aggregate
   ↓
4. Aggregate.Validate() → Raise DomainEvent
   ↓
5. SaveChanges → Dispatcher → DomainEventHandlers
   ↓
6. DomainEventHandler:
   ├─ MapToIntegrationEvent → Save to OutboxEvents
   └─ Handle() → Execute Business Logic (INTERNAL)
   ↓
7. Background Worker (Celery, every 30s)
   ├─ Get Unprocessed Outbox Events
   ├─ Publish to RabbitMQ
   └─ Mark as Processed
   ↓
8. External Systems Consume from RabbitMQ
```

## 🛠️ Stack Technique

### Backend

| Technologie | Version | Usage |
|------------|---------|-------|
| **Python** | 3.11+ | Langage principal |
| **Flask** | 3.0+ | Framework web |
| **SQLAlchemy** | 2.0+ | ORM |
| **Alembic** | 1.12+ | Migrations DB |
| **Celery** | 5.3+ | Tâches asynchrones |
| **RabbitMQ** | - | Message broker (Integration Events) |
| **PostgreSQL** | 14+ | Base de données (production) |
| **SQLite** | - | Base de données (développement) |
| **ReportLab** | 4.0+ | Génération PDF |
| **Flask-Babel** | 4.0+ | Internationalisation (FR/AR) |
| **JWT** | - | Authentification API |

### Frontend

| Technologie | Usage |
|------------|-------|
| **Jinja2** | Templates HTML |
| **Tailwind CSS** | Framework CSS |
| **JavaScript (Vanilla)** | Interactivité |
| **Select2** | Dropdowns enrichis |
| **Chart.js** | Graphiques (optionnel) |

### Testing

| Outil | Usage |
|-------|-------|
| **Pytest** | Tests unitaires et intégration |
| **Behave** | Tests BDD (Behavior-Driven Development) |
| **Playwright** | Tests E2E frontend |
| **Faker** | Génération de données de test |

### DevOps & Outils

| Outil | Usage |
|-------|-------|
| **Git** | Version control |
| **Black** | Formatage code Python |
| **Ruff** | Linting Python |
| **Alembic** | Migrations base de données |

## 📦 Installation

### Prérequis

- Python 3.11 ou supérieur
- PostgreSQL 14+ (optionnel, SQLite par défaut)
- RabbitMQ (optionnel, pour Integration Events)
- Node.js et npm (pour tests E2E)

### Installation

1. **Cloner le dépôt**
```bash
git clone https://github.com/3bDevDZ/backoffice-app.git
cd backoffice-app
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
# Créer un fichier .env
cp .env.example .env

# Éditer .env avec vos configurations
# DATABASE_URL=postgresql://user:password@localhost/gmflow
# SECRET_KEY=your-secret-key
# RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

5. **Initialiser la base de données**
```bash
# Créer les tables
python app/scripts/create_tables.py

# Créer l'utilisateur admin
python app/scripts/seed_admin.py

# (Optionnel) Ajouter des données de test
python app/scripts/seed_customers.py
python app/scripts/seed_products.py
```

6. **Lancer l'application**
```bash
python run.py
```

L'application sera accessible sur `http://localhost:5000`

**Identifiants par défaut :**
- Username: `admin`
- Password: `admin` (à changer en production !)

### Configuration Celery (Optionnel)

Pour les tâches asynchrones (expiration des prix promotionnels, envoi d'emails, etc.) :

```bash
# Terminal 1: Worker Celery
celery -A app.tasks.celery_config worker --loglevel=info

# Terminal 2: Beat (scheduler)
celery -A app.tasks.celery_config beat --loglevel=info
```

## 📁 Structure du Projet

```
gmflow/
├── app/
│   ├── __init__.py                 # Factory Flask app
│   ├── config.py                   # Configuration
│   │
│   ├── domain/                     # DOMAIN LAYER
│   │   ├── models/                 # Aggregates & Entities
│   │   │   ├── product.py         # Product Aggregate
│   │   │   ├── customer.py        # Customer Aggregate
│   │   │   ├── order.py            # Order Aggregate
│   │   │   ├── quote.py            # Quote Aggregate
│   │   │   ├── invoice.py         # Invoice Aggregate
│   │   │   ├── stock.py            # Stock Aggregate
│   │   │   └── ...
│   │   ├── events/                 # Domain Events
│   │   │   ├── domain_event.py
│   │   │   └── integration_event.py
│   │   └── primitives/             # Base classes
│   │       └── aggregate_root.py
│   │
│   ├── application/                # APPLICATION LAYER (CQRS)
│   │   ├── common/
│   │   │   ├── mediator.py        # Command/Query dispatcher
│   │   │   └── cqrs.py            # Base classes
│   │   │
│   │   ├── products/
│   │   │   ├── commands/          # Write operations
│   │   │   │   ├── commands.py
│   │   │   │   └── handlers.py
│   │   │   └── queries/           # Read operations
│   │   │       ├── queries.py
│   │   │       ├── handlers.py
│   │   │       └── product_dto.py
│   │   │
│   │   ├── sales/orders/          # Orders CQRS
│   │   ├── sales/quotes/          # Quotes CQRS
│   │   ├── billing/invoices/      # Invoices CQRS
│   │   ├── stock/                 # Stock CQRS
│   │   └── ...
│   │
│   ├── infrastructure/             # INFRASTRUCTURE LAYER
│   │   ├── db.py                  # Database session
│   │   ├── migrate.py             # Migration helpers
│   │   ├── messaging/             # RabbitMQ
│   │   │   └── rabbitmq_publisher.py
│   │   └── outbox/                # Outbox pattern
│   │       ├── outbox_event.py
│   │       └── outbox_service.py
│   │
│   ├── routes/                     # WEB LAYER (Flask Routes)
│   │   ├── auth_routes.py
│   │   ├── products_routes.py
│   │   ├── customers_routes.py
│   │   ├── sales_routes.py
│   │   ├── billing_routes.py
│   │   └── ...
│   │
│   ├── services/                   # Application Services
│   │   ├── pricing_service.py     # Calcul prix & remises
│   │   ├── stock_service.py       # Gestion stock AVCO
│   │   ├── invoice_pdf_service.py # Génération PDF factures
│   │   ├── invoice_numbering_service.py # Numérotation factures
│   │   └── ...
│   │
│   ├── security/                   # Sécurité
│   │   ├── auth.py                # JWT authentication
│   │   ├── session_auth.py        # Session authentication
│   │   └── rbac.py                # Role-Based Access Control
│   │
│   ├── tasks/                      # Celery tasks
│   │   ├── celery_config.py
│   │   ├── pricing_tasks.py       # Expiration prix promo
│   │   └── email_tasks.py         # Envoi emails
│   │
│   ├── templates/                  # Jinja2 templates
│   │   ├── base.html
│   │   ├── products/
│   │   ├── customers/
│   │   ├── sales/
│   │   ├── billing/
│   │   └── ...
│   │
│   └── static/                     # Assets statiques
│       ├── css/
│       ├── js/
│       └── images/
│
├── tests/
│   ├── unit/                       # Tests unitaires
│   ├── integration/                # Tests d'intégration
│   ├── bdd/                        # Tests BDD (Behave)
│   │   └── features/
│   └── e2e/                        # Tests E2E (Playwright)
│
├── migrations/                     # Alembic migrations
├── docs/                          # Documentation
├── specs/                         # Spécifications
│
├── requirements.txt                # Dépendances Python
├── pyproject.toml                  # Configuration projet
├── pytest.ini                      # Configuration Pytest
├── run.py                         # Point d'entrée
└── README.md                      # Ce fichier
```

## 🧪 Tests

### Tests Unitaires

```bash
# Lancer tous les tests unitaires
pytest tests/unit/

# Avec couverture
pytest tests/unit/ --cov=app --cov-report=html

# Un fichier spécifique
pytest tests/unit/test_product_handlers.py
```

### Tests BDD (Behave)

```bash
# Lancer tous les tests BDD
behave tests/bdd/features/

# Un scénario spécifique
behave tests/bdd/features/order_stock_reservation.feature
```

### Tests E2E (Playwright)

```bash
# Installer Playwright
npm install
npx playwright install

# Lancer les tests E2E
npm test

# Mode UI interactif
npm run test:ui
```

## 📚 Documentation

### Guides Utilisateur

- **[Guide Utilisateur Complet](docs/USER_GUIDE.md)** : Guide détaillé de toutes les fonctionnalités
- **[Guide de Démarrage Rapide](docs/QUICK_START.md)** : Installation et première utilisation en 15 minutes
- **[Guide d'Installation](docs/INSTALLATION_GUIDE.md)** : Installation locale et production
- **[Guide Administrateur](docs/ADMIN_GUIDE.md)** : Administration, maintenance et dépannage

### Documentation Technique

- **Architecture** : Voir `docs/ARCHITECTURE_REFERENCE.md`
- **Spécifications** : Voir `specs/` pour les spécifications détaillées par phase
- **Documentation Code** : Docstrings dans le code source

👉 **Voir [docs/README.md](docs/README.md) pour l'index complet de la documentation**

## 🔐 Sécurité

- **Authentification** : JWT pour API, Sessions pour frontend
- **Autorisation** : RBAC (Admin, Direction, Commercial, Magasinier)
- **Chiffrement** : HTTPS obligatoire en production
- **Validation** : Validation des entrées utilisateur
- **Audit** : Logs de toutes les actions importantes

## 🌍 Internationalisation

GMFlow supporte le français (FR) et l'arabe (AR) avec :
- Interface utilisateur traduite
- Support RTL pour l'arabe
- Formats de dates/nombres localisés
- Messages d'erreur traduits

## 🤝 Contribuer

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créer une branche pour votre feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Standards de Code

- Suivre PEP 8 pour Python
- Utiliser Black pour le formatage
- Ajouter des tests pour les nouvelles fonctionnalités
- Documenter le code avec des docstrings

## 📄 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Auteurs

- **3bDevDZ** - Développement initial

## 🙏 Remerciements

- Flask pour le framework web
- SQLAlchemy pour l'ORM
- Tous les contributeurs open-source qui ont rendu ce projet possible

---

**GMFlow** - Système de Gestion Commerciale Moderne et Évolutif

Pour toute question ou support, veuillez ouvrir une issue sur GitHub.
