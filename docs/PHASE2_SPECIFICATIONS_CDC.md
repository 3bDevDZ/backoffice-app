# Spécifications Phase 2 - Système de Gestion Commerciale
## Selon Cahier des Charges

**Source**: `cahier-des-charges-systeme-gestion-commerciale.md`  
**Périmètre**: Phase 2 - Complet (Mois 5-8)  
**Durée**: 16 semaines (4 mois)

---

## Vue d'Ensemble

La **Phase 2** étend le MVP (Phase 1) avec 5 modules supplémentaires essentiels pour une gestion commerciale complète :

1. **Module 6 : Facturation**
2. **Module 7 : Paiements**
3. **Module 8 : Achats**
4. **Module 9 : Multi-Emplacements**
5. **Module 10 : Reporting Avancé**

---

## Module 6 : Facturation

### Objectif
Générer des factures conformes à la législation française, avec numérotation légale, gestion des avoirs et envoi automatique.

### Fonctionnalités Principales

#### FP-FACT-001 : Génération Factures
- Création depuis commande livrée
- Numérotation légale séquentielle (FA-YYYY-XXXXX)
- Séquentielle **sans trou** (obligatoire légalement)
- Sélection lignes à facturer (facturation partielle)
- Calculs automatiques (HT, TVA, TTC)

#### FP-FACT-002 : Informations Obligatoires
- Numéro unique séquentiel
- Date facture et échéance
- Identité émetteur complète (raison sociale, SIRET, TVA, adresse)
- Identité client complète
- Détail lignes (quantité, prix unitaire, TVA)
- Total HT, TVA, TTC
- Conditions paiement
- Pénalités retard
- Indemnité forfaitaire (40€)
- Mentions légales complètes

#### FP-FACT-003 : Avoirs
- Création avoir (note de crédit)
- Lien facture d'origine obligatoire
- Raison avoir obligatoire
- Montant total ou partiel
- Numérotation séparée (AV-YYYY-XXXXX)

#### FP-FACT-004 : États Facture
- **Brouillon** : En cours de création
- **Validée** : Facture finalisée (non modifiable)
- **Envoyée** : Transmise au client
- **Partiellement payée** : Paiement partiel reçu
- **Payée** : Intégralement payée
- **Échue** : Date échéance dépassée, impayée
- **Annulée** : Via avoir uniquement

#### FP-FACT-005 : Envoi et Export
- Génération PDF conforme (format légal)
- Envoi email automatique au client
- Export comptable (FEC - Fichier des Écritures Comptables)
- Export CSV pour comptabilité
- Archivage légal (10 ans minimum)

### Règles de Gestion

**RG-FACT-001** : Numérotation strictement séquentielle (pas de saut)  
**RG-FACT-002** : Pas de trou dans numérotation (obligation légale)  
**RG-FACT-003** : Facture validée non modifiable (créer avoir si erreur)  
**RG-FACT-004** : Annulation uniquement par avoir  
**RG-FACT-005** : Conservation 10 ans minimum (archivage fiscal)  
**RG-FACT-006** : Date facture ≤ aujourd'hui  
**RG-FACT-007** : Échéance selon délai paiement client  
**RG-FACT-008** : Quantités facturées ≤ quantités livrées  

### Livrables Techniques

**Modèles de Domaine**:
- `Invoice` (Facture)
- `InvoiceLine` (Ligne facture)
- `CreditNote` (Avoir)

**Services**:
- `InvoiceService` : Génération, validation, numérotation
- `InvoicePDFService` : Génération PDF conforme
- `InvoiceEmailService` : Envoi automatique

**API Endpoints**:
- `POST /api/invoices` : Créer facture depuis commande
- `GET /api/invoices/{id}` : Détails facture
- `POST /api/invoices/{id}/validate` : Valider facture
- `POST /api/invoices/{id}/send` : Envoyer facture
- `POST /api/invoices/{id}/credit-note` : Créer avoir
- `GET /api/invoices/{id}/pdf` : Télécharger PDF
- `GET /api/invoices` : Liste factures (filtres, pagination)

**Frontend**:
- Page liste factures
- Page détail facture
- Formulaire création avoir
- Bouton "Facturer commande"

---

## Module 7 : Paiements

### Objectif
Gérer l'enregistrement des paiements, le rapprochement bancaire, les relances automatiques et le suivi des impayés.

### Fonctionnalités Principales

#### FP-PAY-001 : Enregistrement Paiements
- Saisie manuelle paiement
- Import relevé bancaire (CSV, OFX, QIF)
- Modes paiement :
  - Espèces
  - Chèque
  - Virement
  - Carte bancaire
  - Prélèvement
- Affectation sur facture(s)
- Paiement partiel possible
- Date valeur (différente date paiement)

#### FP-PAY-002 : Rapprochement Bancaire
- Import relevés bancaires
- Rapprochement automatique (par montant, référence)
- Rapprochement manuel
- Lettrage factures (lien paiement ↔ facture)
- Écarts de rapprochement

#### FP-PAY-003 : Relances
- Niveaux de relance (1, 2, 3)
- Automatisation :
  - **Relance 1** : J+7 après échéance
  - **Relance 2** : J+15 après échéance
  - **Relance 3** : J+30 après échéance
- Templates emails personnalisables
- Lettres de relance PDF
- Historique relances (qui, quand, type)

#### FP-PAY-004 : Suivi Impayés
- Liste factures échues
- Groupement par ancienneté :
  - 0-30 jours
  - 30-60 jours
  - 60-90 jours
  - >90 jours
- Montants par période
- Dashboard impayés (KPI)
- Alertes automatiques

### Règles de Gestion

**RG-PAY-001** : Montant paiement > 0  
**RG-PAY-002** : Montant paiement ≤ reste à payer  
**RG-PAY-003** : Date paiement ≥ date facture  
**RG-PAY-004** : Facture payée non modifiable  
**RG-PAY-005** : Relance si échéance dépassée  
**RG-PAY-006** : Libération crédit client après paiement  

### Livrables Techniques

**Modèles de Domaine**:
- `Payment` (Paiement)
- `PaymentAllocation` (Affectation paiement → facture)
- `PaymentReminder` (Relance)

**Services**:
- `PaymentService` : Enregistrement, affectation
- `BankReconciliationService` : Rapprochement
- `PaymentReminderService` : Relances automatiques (Celery)

**API Endpoints**:
- `POST /api/payments` : Enregistrer paiement
- `POST /api/payments/import` : Importer relevé bancaire
- `POST /api/payments/reconcile` : Rapprocher
- `GET /api/payments/overdue` : Liste impayés
- `POST /api/payments/{id}/remind` : Envoyer relance
- `GET /api/payments/aging` : Analyse par ancienneté

**Frontend**:
- Page enregistrement paiement
- Page rapprochement bancaire
- Dashboard impayés
- Liste relances

---

## Module 8 : Achats

### Objectif
Gérer le cycle complet des achats : demandes d'achat, commandes fournisseurs, réceptions et factures fournisseurs.

### Fonctionnalités Principales

#### FP-ACH-001 : Demandes d'Achat
- Création manuelle demande
- Génération automatique (si stock < minimum)
- Validation workflow (approuveur)
- Conversion en commande fournisseur
- Suivi statuts

#### FP-ACH-002 : Commandes Fournisseurs
- Création commande fournisseur
- Sélection fournisseur
- Ajout lignes produits
- Calculs automatiques (HT, TVA, TTC)
- Numérotation (BCA-YYYY-XXXXX)
- Envoi email fournisseur
- Suivi statuts (brouillon, envoyée, confirmée, reçue, facturée)

#### FP-ACH-003 : Réceptions
- Réception depuis commande fournisseur
- Vérification quantités reçues vs commandées
- Contrôle qualité (optionnel)
- Génération mouvement stock automatique
- Bon de réception PDF
- Gestion écarts quantités

#### FP-ACH-004 : Factures Fournisseurs
- Saisie facture fournisseur
- Rapprochement avec BC/réception
- Contrôle 3-way matching :
  - Commande (BC)
  - Réception (BR)
  - Facture (FA)
- Validation paiement
- Échéancier fournisseur

### Règles de Gestion

**RG-ACH-001** : Demande validée avant conversion commande  
**RG-ACH-002** : Réception partielle autorisée  
**RG-ACH-003** : Écart réception > 10% nécessite validation  
**RG-ACH-004** : Facture ≤ commande (montant)  
**RG-ACH-005** : Mise à jour coût produit après réception  

### Livrables Techniques

**Modèles de Domaine**:
- `PurchaseRequest` (Demande d'achat)
- `PurchaseOrder` (Déjà existant - à étendre)
- `PurchaseReceipt` (Réception)
- `SupplierInvoice` (Facture fournisseur)

**Services**:
- `PurchaseRequestService` : Génération auto, validation
- `PurchaseOrderService` : Création, envoi
- `PurchaseReceiptService` : Réception, contrôle
- `SupplierInvoiceService` : Saisie, rapprochement

**API Endpoints**:
- `POST /api/purchase-requests` : Créer demande
- `POST /api/purchase-requests/{id}/approve` : Approuver
- `POST /api/purchase-orders` : Créer commande
- `POST /api/purchase-orders/{id}/receive` : Réceptionner
- `POST /api/supplier-invoices` : Saisir facture
- `POST /api/supplier-invoices/{id}/match` : Rapprocher

**Frontend**:
- Page demandes d'achat
- Page commandes fournisseurs (déjà existante - à étendre)
- Page réceptions
- Page factures fournisseurs

---

## Module 9 : Multi-Emplacements

### Objectif
Gérer plusieurs entrepôts/magasins avec transferts inter-sites et visibilité globale du stock.

### Fonctionnalités Principales

#### FP-LOC-001 : Gestion Multi-Sites
- Plusieurs entrepôts/magasins
- Structure hiérarchique par site :
  - Site → Entrepôt → Zone → Allée → Étagère → Niveau
- Informations par site (adresse, responsable)
- Statut site (actif/inactif)

#### FP-LOC-002 : Transferts Inter-Sites
- Création transfert entre sites
- Sélection produits et quantités
- Génération ordre de transfert
- Suivi statut (créé, en transit, reçu)
- Génération mouvements stock automatiques :
  - Sortie site source
  - Entrée site destination

#### FP-LOC-003 : Visibilité Globale
- Vue consolidée stock tous sites
- Vue détaillée par site
- Recherche produit (tous sites ou site spécifique)
- Alertes stock par site
- Dashboard multi-sites

### Règles de Gestion

**RG-LOC-001** : Transfert nécessite site source ET destination différents  
**RG-LOC-002** : Stock source ≥ quantité transférée  
**RG-LOC-003** : Transfert en transit bloque stock source  
**RG-LOC-004** : Réception transfert crée stock destination  

### Livrables Techniques

**Modèles de Domaine**:
- `Site` (Site/Emplacement principal)
- `Location` (Déjà existant - à étendre avec `site_id`)
- `StockTransfer` (Transfert inter-sites)
- `StockTransferLine` (Ligne transfert)

**Services**:
- `SiteService` : Gestion sites
- `StockTransferService` : Création, suivi transferts

**API Endpoints**:
- `GET /api/sites` : Liste sites
- `POST /api/sites` : Créer site
- `POST /api/stock-transfers` : Créer transfert
- `POST /api/stock-transfers/{id}/receive` : Réceptionner
- `GET /api/stock/global` : Vue consolidée

**Frontend**:
- Page gestion sites
- Page transferts inter-sites
- Vue stock multi-sites
- Dashboard multi-sites

---

## Module 10 : Reporting Avancé

### Objectif
Fournir des rapports personnalisables, analyses ventes/marges et prévisions.

### Fonctionnalités Principales

#### FP-REP-001 : Rapports Personnalisables
- Création rapports personnalisés
- Sélection colonnes
- Filtres avancés (dates, produits, clients, etc.)
- Tri et groupement
- Formules calculées
- Sauvegarde templates

#### FP-REP-002 : Export Excel/PDF
- Export Excel (formats multiples)
- Export PDF
- Export CSV
- Mise en forme personnalisable
- Graphiques intégrés

#### FP-REP-003 : Analyses Ventes/Marges
- Analyse CA par période
- Analyse par produit
- Analyse par client
- Analyse par commercial
- Calcul marges (CA - Coût)
- Évolution temporelle
- Comparaisons périodes

#### FP-REP-004 : Prévisions
- Prévisions ventes (basées sur historique)
- Prévisions stock (besoins futurs)
- Tendances
- Alertes prévisionnelles

### Rapports Standard

1. **Rapport Ventes**:
   - CA par période
   - Top produits
   - Top clients
   - Évolution CA

2. **Rapport Marges**:
   - Marge par produit
   - Marge par client
   - Marge globale

3. **Rapport Stock**:
   - Valeur stock
   - Rotation stock
   - Produits lents
   - Produits rapides

4. **Rapport Clients**:
   - CA par client
   - Fréquence achat
   - Panier moyen
   - Délai paiement

5. **Rapport Achats**:
   - Achats par fournisseur
   - Évolution prix
   - Délais livraison

### Livrables Techniques

**Services**:
- `ReportService` : Génération rapports
- `AnalyticsService` : Calculs analytiques
- `ForecastService` : Prévisions

**API Endpoints**:
- `GET /api/reports/sales` : Rapport ventes
- `GET /api/reports/margins` : Rapport marges
- `GET /api/reports/stock` : Rapport stock
- `GET /api/reports/custom` : Rapport personnalisé
- `POST /api/reports/export` : Export rapport

**Frontend**:
- Page rapports
- Constructeur rapports personnalisés
- Visualisations graphiques (charts)
- Export rapports

---

## Planning Phase 2 (16 semaines)

### Sprint 9-10 (Semaines 17-20) : Facturation
- Module facturation
- Numérotation légale
- Génération PDF conforme
- Avoirs
- Envoi emails automatiques

### Sprint 11-12 (Semaines 21-24) : Paiements & Achats
- Gestion paiements
- Rapprochement bancaire
- Relances automatiques
- Module achats complet
- Commandes fournisseurs
- Réceptions
- Factures fournisseurs

### Sprint 13-14 (Semaines 25-28) : Multi-Emplacements & Reporting
- Gestion multi-sites
- Transferts inter-sites
- Reporting avancé
- Export Excel/PDF
- Analytics et prévisions

### Sprint 15-16 (Semaines 29-32) : Finalisation
- Tests complets
- Optimisations performance
- Corrections bugs
- Formation complète
- Migration données
- Déploiement production

---

## Livrables Phase 2

- ✅ Application complète (MVP + Phase 2)
- ✅ Migration données OK
- ✅ Formation effectuée
- ✅ Production lancée

---

## Critères de Sortie Phase 2

- ✅ 100% fonctionnalités Phase 2 développées
- ✅ Tests unitaires >80% couverture
- ✅ Tests d'intégration OK
- ✅ Tests utilisateurs OK
- ✅ Performance conforme (<2s)
- ✅ Sécurité validée
- ✅ Conformité légale (facturation)
- ✅ Documentation complète

---

## Dépendances Techniques

### Dépendances Phase 1 (MVP)
- Module Produits ✅
- Module Clients ✅
- Module Stock ✅
- Module Ventes (Devis/Commandes) ✅
- Dashboard basique ✅

### Nouvelles Dépendances Phase 2
- Module Facturation → Nécessite Commandes livrées
- Module Paiements → Nécessite Factures
- Module Achats → Nécessite Fournisseurs (déjà existant)
- Multi-Emplacements → Nécessite Stock
- Reporting → Nécessite toutes les données

---

## Estimation Effort

| Module | Complexité | Effort Estimé |
|--------|------------|---------------|
| Facturation | Haute | 4 semaines |
| Paiements | Moyenne | 3 semaines |
| Achats | Moyenne | 3 semaines |
| Multi-Emplacements | Moyenne | 2 semaines |
| Reporting Avancé | Haute | 3 semaines |
| Tests & Polish | - | 1 semaine |
| **TOTAL** | - | **16 semaines** |

---

## Notes Importantes

1. **Conformité Légale** : La facturation doit respecter strictement l'article 289 du CGI (Code Général des Impôts)
2. **Numérotation Factures** : Séquentielle sans trou (obligation légale)
3. **Archivage** : Conservation factures 10 ans minimum
4. **Performance** : Les rapports doivent rester <5s même avec volumes importants
5. **Sécurité** : Accès factures/paiements restreint (rôles comptables)

