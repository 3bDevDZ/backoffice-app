# Spécification Fonctionnelle et Technique
## Système de Gestion Commerciale (MVP Phase 1)
### Version 0.1 — 15/11/2025 — Statut: Draft

---

## 1. Contexte & Objectifs

- Contexte: Besoin d’une solution intégrée couvrant produits, clients, stock et ventes, avec tableaux de bord de suivi et règles de gestion robustes.
- Objectifs fonctionnels (MVP):
  - Gestion Produits (catalogue, catégories, prix, variantes, import/export)
  - Gestion Clients (fiches B2B/B2C, adresses/contacts, conditions commerciales)
  - Gestion Stock (mouvements, inventaires, réapprovisionnement, valorisation)
  - Gestion Ventes (devis → commandes, workflow, réservation stock)
  - Dashboard (KPI essentiels)
- Objectifs techniques: performance <2s, 50+ utilisateurs simultanés, volumétrie élevée, sécurité (RBAC, chiffrement, audit), évolutivité modulaire.

---

## 2. Périmètre MVP (Phase 1 — Mois 1 à 4)

- Module Produits: CRUD complet, catégories hiérarchiques, images, prix multiples, variantes, recherche/filtres, import/export CSV/XLS.
- Module Clients: CRUD B2B/B2C, adresses multiples (facturation/livraison), contacts, conditions commerciales (délai, remise, liste de prix), historique.
- Module Stock: visualisation (physique, réservé, disponible, prévisionnel), mouvements (entrée/sortie/transfert/ajustement), inventaires, règles de réapprovisionnement, valorisation (Standard/AVCO/FIFO).
- Module Ventes: devis (numérotation, lignes, remises, PDF), workflow devis, commandes (vérifs stock/crédit, réservation, livraison), workflow commandes.
- Module Dashboard: KPI essentiels (CA, stock en alerte, commandes en cours).

Livrables clés:
- UI fonctionnelle selon écrans fournis (voir §7 Interfaces).
- API REST pour toutes opérations MVP.
- PDF pour devis/commandes (templates de base).
- Import/Export Produits & Clients.
- Journalisation des actions critiques.

Hors périmètre MVP:
- Facturation & Paiements (Phase 2)
- Achats, multi-emplacements avancés (Phase 2)
- POS, CRM, E-commerce, Mobile (Phase 3)

---

## 3. Rôles & Permissions (RBAC)

- Rôles initiaux:
  - Direction: lecture globale, dashboards, export.
  - Commercial: CRUD devis/commandes, lecture produits/clients.
  - Magasinier: mouvements stock, inventaires, lecture commandes.
  - Admin: gestion utilisateurs/permissions, paramètres.
- Principes: autorisations granulaires par module/fonction (ex: suppression produit), non-répudiation via logs horodatés.

---

## 4. Modèle de Données (Vue d’ensemble)

- Produit: `code` (unique), `nom`, `description`, `categories[]`, `images[]`, `prix`, `cout`, `uom`, `code_barres?`, `references`, `statut`, `variantes[]`.
- Variante: `code` (unique), `attributs{}`, `prix`, `stock`.
- Catégorie: hiérarchie parent/enfant.
- Listes de prix: `nom`, `règles`, `périodes`, `prix par produit`.
- Client: `code` auto, `type` (Entreprise/Particulier), infos légales (SIRET, TVA) si Entreprise, `email` (unique), `téléphones`, `categorie`, `notes`.
- Adresse: `type` (facturation/livraison), `ligne1..`, `ville`, `pays`, `par_defaut`.
- Contact: `nom`, `prénom`, `fonction`, `email`, `téléphone`, `droits`.
- Conditions commerciales: `delai_paiement`, `liste_prix`, `remise_defaut`, `limite_credit`.
- Stock: par `produit/variante` et `emplacement` (entrepôt → zone → allée → étagère → niveau). États: `physique`, `reservé`, `disponible`, `prévisionnel`.
- Mouvement stock: `type` (entrée/sortie/transfert/ajustement), `source`, `destination`, `quantite`, `lot/serie?`, `document_associe`, `auteur`, `horodatage`.
- Inventaire: `scope` (catégorie/emplacement/produits), `comptages[]`, `écarts`, `ajustements`.
- Devis: `numero DEV-YYYY-XXXXX`, `client`, `lignes[]` (produit, qté, prix, remise, TVA), `totaux`, `date_validite`, `etat`, `versions[]`, `pdf`.
- Commande: `numero CMD-YYYY-XXXXX`, `client`, `lignes[]`, `verification(stock, crédit)`, `reservation`, `dates_livraison`, `adresse_livraison`, `etat`, `documents`.

Notes:
- Traçabilité lot/série activable par produit.
- Réservation stock: au changement d’état commande → Confirmée.

---

## 5. Règles de Gestion (Synthèse MVP)

- Produits:
  - Code produit unique obligatoire (≤50 car.).
  - Prix de vente ≥ 0, coût ≥ 0; ≥ une catégorie.
  - Code-barres unique si présent; suppression impossible si utilisé.
- Clients:
  - Email unique et valide; code auto.
  - Entreprise: raison sociale obligatoire; Adresse de facturation requise.
  - Limite crédit ≥ 0; remise défaut 0–100%.
- Stock:
  - Stock physique ≥ 0 (sauf autorisation); réservé ≤ physique.
  - Mouvement avec source et/ou destination valides.
  - Inventaire bloque mouvements sur produits en cours.
  - Transfert: source ≥ quantité.
- Ventes:
  - Devis/commande: ≥1 ligne; qté > 0; prix ≥ 0; remise ≤ 100%.
  - Date expiration > date devis; conversion commande si devis accepté.
  - Blocage si crédit insuffisant; alerte si stock insuffisant.
  - Annulation commande libère stock réservé; remise >15% nécessite validation.

---

## 6. API REST (Surface MVP)

- Auth: `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`.
- Produits: `GET/POST/PUT/DELETE /products`, `GET /products/{id}`, `POST /products/import`, `GET /products/export`.
- Catégories: `GET/POST/PUT/DELETE /categories`.
- Listes de prix: `GET/POST/PUT/DELETE /price-lists`.
- Clients: `GET/POST/PUT/DELETE /clients`, `GET /clients/{id}`, `POST /clients/import`, `GET /clients/export`.
- Adresses/Contacts: `GET/POST/PUT/DELETE /clients/{id}/addresses`, `/clients/{id}/contacts`.
- Stock: `GET /stock`, `GET /stock/alerts`, `POST /stock/movements`, `GET /stock/movements`.
- Inventaires: `POST /inventories`, `POST /inventories/{id}/counts`, `POST /inventories/{id}/close`.
- Devis: `GET/POST/PUT /quotes`, `POST /quotes/{id}/send`, `POST /quotes/{id}/version`, `GET /quotes/{id}/pdf`.
- Commandes: `GET/POST/PUT /orders`, `POST /orders/{id}/reserve`, `POST /orders/{id}/cancel`, `GET /orders/{id}/pdf`.
- Dashboard: `GET /dashboard/kpi` (CA, stock alertes, commandes en cours).

Notes:
- Filtrage, pagination, tri standard (query params).
- Statuts exposés via champs `status` et endpoints d’action (workflows).

---

## 7. Interfaces (mapping écrans)

- `design/01-login.html`: Authentification (email/mot de passe), messages d’erreur, verrouillage après 5 tentatives.
- `design/02-dashboard.html`: KPI essentiels; CA jour/mois/année; stocks en alerte; commandes en cours.
- `design/03-products-list.html`: Liste, recherche full-text, filtres catégorie/prix/stock/statut; export.
- `design/04-product-form.html`: Fiche produit; variantes; images; prix; catégories; validation.
- `design/05-customers-list.html`: Liste clients; recherche; filtres; import/export.
- `design/06-customer-form.html`: Fiche B2B/B2C; adresses multiples; contacts; conditions commerciales.
- `design/07-stock.html`: Visualisation par produit/emplacement; mouvements; inventaires; réappro.
- `design/08-orders-list.html`: Liste commandes; états; filtres; actions (réserver, annuler).
- `design/09-order-form.html`: Création/édition; lignes produits; vérification stock/crédit; livraison.

Principes UX:
- Actions critiques avec confirmation (ex: annulation, ajustements inventaire).
- Codes couleur stock (vert/orange/rouge) selon seuils.

---

## 8. Exigences Non-Fonctionnelles

- Performance:
  - Pages < 2s (95% des cas)
  - Recherche < 1s pour 10k enregistrements
  - Rapports < 5s (12 mois)
- Charge:
  - 50 utilisateurs simultanés min (100 cible)
- Volumétrie:
  - 100k produits, 50k clients, 1M docs/an
- Disponibilité:
  - 99,5% annuel
- Compatibilité:
  - Navigateurs: Chrome/Firefox/Edge/Safari versions 100+/15+
  - OS: Windows/macOS/Linux; Mobile cible futur (Phase 3)
- Sécurité:
  - Auth forte, 2FA optionnelle; expiration session 30 min
  - RBAC; audit et logs 1 an; HTTPS (TLS 1.2+)
  - Protection RGPD (droit à l’oubli, portabilité, consentement)

---

## 9. Architecture & Tech (proposition)

- Frontend: SPA (TypeScript), UI responsive basée sur écrans `design/`.
- Backend: API REST modulaire, stateless, avec journaux d’audit.
- Base de données: PostgreSQL (recommandé), schémas par modules.
- Stock & Réservation: transactions et verrous pessimistes sur mouvements sensibles.
- Fichiers: stockage d’images produits; PDF génération server-side.
- Modules indépendants pour extensibilité (Phase 2/3).

---

## 10. Workflows Clés

- Devis:
  - Brouillon → Envoyé → Accepté/Refusé/Expiré/Annulé; versioning post-envoi.
  - Relances auto J+7/J+15 (notification).
- Commande:
  - Brouillon → Confirmée → En préparation → Prête → Expédiée → Livrée → Facturée → Annulée.
  - Réservation stock à la confirmation; annulation libère réservations.
- Inventaire:
  - Création scope → Comptages → Comparaison → Ajustements → Clôture; blocage mouvements sur scope.

---

## 11. Critères de Validation (MVP)

- Produits/Clients: CRUD complet avec validations et import/export.
- Stock: mouvements et visualisation cohérente; inventaire produit des ajustements corrects.
- Ventes: devis et commandes avec workflows; PDF générés.
- Dashboard: KPI affichés et actualisés.
- Sécurité: RBAC fonctionnel; sessions; logs d’audit.
- Performance: respect des SLA cibles en environnement de test.

---

## 12. Planning indicatif (Mois 1–4)

- Semaine 1–2: Modèles de données, fondations API, Auth & RBAC.
- Semaine 3–5: Produits (CRUD, prix, variantes, import/export) + UI.
- Semaine 6–7: Clients (CRUD, adresses/contacts, conditions) + UI.
- Semaine 8–9: Stock (mouvements, visualisation, inventaires) + UI.
- Semaine 10–11: Ventes (devis/commandes, workflows, PDF) + UI.
- Semaine 12–13: Dashboard + KPI + optimisations.
- Semaine 14–16: Tests, durcissement sécurité, perf, documentation.

---

## 13. Risques & Hypothèses

- Hypothèses: PostgreSQL dispo; authentification email/mot de passe; génération PDF acceptée côté serveur.
- Risques: performances des listes volumineuses; complexité variantes; cohérence réservations sous concurrence.

---

## 14. Annexes

- Références d’écrans dans `design/00-index.html` à `design/09-order-form.html`.
- Évolution Phase 2: Facturation, Paiements, Achats, Multi-emplacements.
- Évolution Phase 3: POS, CRM, E-commerce, Mobile.

---

## 15. Architecture DDD + CQRS + Domain Events + Outbox (Flask)

Objectif: reprendre les principes du guide d’architecture (DDD/CQRS/Events) et les adapter à une implémentation Python/Flask, en conservant les mêmes flux métier.

Layering (conceptuel):
- Présentation: UI web basée sur `design/*.html` (ou autre SPA futur)
- Web API: Flask (Blueprints par module)
- Application (CQRS): Commands (write) et Queries (read), orchestrées par des services applicatifs
- Domaine: Aggregates, invariants, Domain Events (internes)
- Infrastructure: SQLAlchemy (ORM), OutboxEvents (table), Background Worker (Celery), RabbitMQ pour Integration Events uniquement
- Data: PostgreSQL

Principes CQRS:
- Commands (write): modifient l’état, ne retournent que succès/échec; utilisent Aggregates; lèvent Domain Events.
- Queries (read): lecture seule; DTO optimisés; accès DB dédié (sans Aggregates).

Domain Events vs Integration Events:
- Domain Events (internes):
  - Traités synchronement dans la même transaction
  - Dispatch interne (service d’événements) vers des handlers de domaine
  - Ne sortent pas du bounded context
- Integration Events (externes):
  - Persistés dans `OutboxEvents`
  - Publiés de façon asynchrone par un worker (Celery) vers RabbitMQ
  - Consommés par systèmes externes (e-commerce, etc.)

Flux — Domain Events (interne, transactionnel):
1) Aggregate applique une commande (ex: `Order.confirm()`)
2) Lève un DomainEvent (ex: `OrderConfirmedDomainEvent`)
3) Le dispatcher interne invoque les DomainEventHandlers
4) Les handlers exécutent logique métier (ex: réserver stock)
5) Tout reste dans la même transaction DB

Flux — Integration Events (outbox → RabbitMQ):
1) Un DomainEvent est levé et traité
2) Le handler mappe DomainEvent → IntegrationEvent (si nécessaire)
3) L’IntegrationEvent est stocké en Outbox (même transaction)
4) Un background worker (Celery beat) lit les outbox non publiés
5) Publication vers RabbitMQ; systèmes externes consomment

Mapping technologique (Flask):
- `MediatR (.NET)` → Service d’événements Python (simple dispatcher + registres de handlers)
- `EF Core` → `SQLAlchemy`
- `Hangfire` → `Celery` (tasks + beat)
- `RabbitMQ` → `pika`/`kombu` pour publish

Structure projet (résumé):
- `app/blueprints/*`: endpoints REST par module
- `app/services/*`: logique applicative (commands/queries orchestrées)
- `app/models/*`: entités et aggregates SQLAlchemy
- `app/events/*`: domain events + handlers; integration events + outbox service
- `app/tasks/*`: workers Celery (publication RabbitMQ, relances devis)
- `app/pdf_templates/*`: Jinja templates pour PDF

Contraintes et concurrence:
- Mouvements stock et réservation: transactions + verrous (`SELECT ... FOR UPDATE` via SQLAlchemy) sur `StockItem`
- Inventaire: bloque les mouvements sur le scope concerné jusqu’à clôture
- Annulation commande: libère les réservations atomiquement

Exigences de sécurité et audit:
- RBAC par rôle (Admin, Direction, Commercial, Magasinier) et permission par action
- Journaux d’audit: `{user, action, ressource, avant/après, timestamp}`

Nota:
- Les diagrammes et exemples .NET du document d’architecture sont interprétés ici pour Flask; la sémantique (flux, patterns, responsabilités) reste inchangée.