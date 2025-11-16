# CAHIER DES CHARGES
## SYSTÈME DE GESTION COMMERCIALE
### Version 1.0 - Novembre 2025

---

## INFORMATIONS DU DOCUMENT

| Élément | Détail |
|---------|--------|
| **Projet** | Développement d'un système de gestion commerciale complet |
| **Client** | Usage interne / Commercial |
| **Date** | 15 Novembre 2025 |
| **Version** | 1.0 |
| **Statut** | Draft |

---

## TABLE DES MATIÈRES

1. [Présentation du Projet](#1-présentation-du-projet)
2. [Contexte et Objectifs](#2-contexte-et-objectifs)
3. [Périmètre Fonctionnel](#3-périmètre-fonctionnel)
4. [Spécifications Fonctionnelles](#4-spécifications-fonctionnelles)
5. [Exigences Techniques](#5-exigences-techniques)
6. [Architecture Système](#6-architecture-système)
7. [Interfaces et Intégrations](#7-interfaces-et-intégrations)
8. [Sécurité et Conformité](#8-sécurité-et-conformité)
9. [Organisation et Planning](#9-organisation-et-planning)
10. [Budget et Ressources](#10-budget-et-ressources)
11. [Critères de Validation](#11-critères-de-validation)

---

# 1. PRÉSENTATION DU PROJET

## 1.1 Résumé Exécutif

Développement d'un **système de gestion commerciale sur-mesure** permettant de gérer l'ensemble du cycle commercial : gestion produits, clients, stocks, ventes, achats et facturation.

**Objectif :** Solution complète, moderne et évolutive, adaptée aux besoins spécifiques, sans dépendance à des éditeurs tiers.

## 1.2 Problématique

### Constats actuels
- Outils multiples non connectés
- Ressaisies d'informations multiples  
- Manque de visibilité temps réel
- Erreurs de saisie fréquentes
- Processus manuels chronophages
- Difficulté à obtenir des statistiques

### Besoins identifiés
- Centralisation données commerciales
- Automatisation tâches répétitives
- Traçabilité complète
- Reporting temps réel
- Accessibilité multi-dispositifs
- Évolutivité

## 1.3 Bénéfices Attendus

### Gains opérationnels
- ⏱️ **Temps** : -40% sur tâches administratives
- 📉 **Erreurs** : -70%
- 📊 **Visibilité** : Temps réel
- 🚀 **Productivité** : +25%

### Gains financiers estimés
- Économie temps : 15-20K€/an
- Réduction licences : 5-10K€/an
- Optimisation stocks : 10-15K€/an
- Amélioration marges : 20-30K€/an

**ROI estimé : 12-18 mois**

---

# 2. CONTEXTE ET OBJECTIFS

## 2.1 Contexte Métier

**Activité** : Commerce B2B et/ou B2C  
**Volume** : 100 à 10 000 références produits  
**Clientèle** : 50 à 5 000 clients actifs  
**Effectif** : 5 à 50 personnes  
**Sites** : 1 à 5 emplacements

## 2.2 Objectifs du Projet

### Objectifs Fonctionnels

1. **Gestion Commerciale Complète**
   - Clients et prospects
   - Devis et commandes
   - Facturation conforme
   - Suivi paiements

2. **Gestion Stock Efficace**
   - Suivi temps réel
   - Multi-emplacements
   - Traçabilité
   - Optimisation réapprovisionnements

3. **Gestion Achats**
   - Commandes fournisseurs
   - Réceptions
   - Factures fournisseurs

4. **Reporting et Analyse**
   - Tableaux de bord
   - KPI temps réel
   - Rapports d'activité

### Objectifs Techniques

1. **Performance**
   - Temps réponse < 2s
   - Support 50+ utilisateurs simultanés
   - 100 000+ documents/an

2. **Fiabilité**
   - Disponibilité 99,5% minimum
   - Sauvegardes automatiques quotidiennes
   - Plan de reprise d'activité

3. **Évolutivité**
   - Architecture modulaire
   - Support croissance (×10 volume)

4. **Sécurité**
   - Données chiffrées
   - Authentification forte
   - Conformité RGPD

## 2.3 Utilisateurs Cibles

| Profil | Nombre | Besoins Principaux |
|--------|--------|-------------------|
| Direction | 1-3 | Tableaux de bord, KPI, reporting |
| Commerciaux | 5-20 | Clients, devis, commandes |
| Magasiniers | 2-10 | Stock, réceptions, préparations |
| Comptables | 1-3 | Facturation, paiements |
| Acheteurs | 1-5 | Commandes fournisseurs |

---

# 3. PÉRIMÈTRE FONCTIONNEL

## 3.1 Modules Inclus

### ✅ PHASE 1 - MVP (Mois 1-4)

**Module 1 : Gestion Produits**
- Catalogue produits complet
- Catégorisation hiérarchique
- Codes-barres et images
- Prix multiples (listes de prix)
- Variantes produits

**Module 2 : Gestion Clients**
- Fiche client complète (B2B/B2C)
- Adresses et contacts multiples
- Historique interactions
- Catégorisation
- Conditions commerciales
- Gestion crédit

**Module 3 : Gestion Stock**
- Suivi temps réel
- Mouvements (entrées/sorties/transferts)
- Emplacements
- Alertes rupture
- Règles réapprovisionnement
- Inventaires
- Valorisation (FIFO/AVCO/Standard)

**Module 4 : Gestion Ventes**
- Devis avec versioning
- Conversion devis → commande
- Gestion commandes
- Workflow validation
- Réservation stock

**Module 5 : Dashboard**
- KPI essentiels
- CA jour/mois/année
- Stock en alerte
- Commandes en cours

### ✅ PHASE 2 - Complet (Mois 5-8)

**Module 6 : Facturation**
- Factures conformes
- Numérotation légale
- Avoirs
- Factures partielles
- Export PDF
- Envoi automatique

**Module 7 : Paiements**
- Enregistrement paiements
- Rapprochement bancaire
- Échéanciers
- Relances automatiques

**Module 8 : Achats**
- Demandes d'achat
- Commandes fournisseurs
- Réceptions
- Factures fournisseurs

**Module 9 : Multi-Emplacements**
- Plusieurs entrepôts/magasins
- Transferts inter-sites
- Visibilité globale

**Module 10 : Reporting Avancé**
- Rapports personnalisables
- Export Excel/PDF
- Analyses ventes/marges
- Prévisions

### ✅ PHASE 3 - Avancé (Mois 9-12)

**Module 11 : Point de Vente (POS)**
- Interface tactile
- Vente rapide
- Paiements multiples
- Tickets de caisse

**Module 12 : CRM**
- Gestion prospects
- Pipeline commercial
- Opportunités
- Suivi commercial

**Module 13 : E-commerce** (Optionnel)
- Catalogue en ligne
- Panier et paiement
- Synchronisation stock

**Module 14 : Mobile**
- App iOS/Android
- Consultation stock
- Création commandes
- Scanner code-barres

## 3.2 Modules Exclus (Hors Périmètre)

❌ **Non inclus** :
- Production (Manufacturing/MRP)
- Ressources humaines (RH/Paie)
- Gestion de projets
- SAV avancé
- Comptabilité complète
- Gestion flotte véhicules
- Gestion qualité (ISO)
- GED avancée

## 3.3 Priorisation (MoSCoW)

**MUST HAVE (MVP)**
- Gestion produits, clients, stock
- Devis et commandes
- Dashboard basique

**SHOULD HAVE (Phase 2)**
- Facturation, paiements
- Achats, multi-emplacements
- Reporting avancé

**COULD HAVE (Phase 3)**
- POS, CRM
- E-commerce, Mobile

**WON'T HAVE (Exclu)**
- Production, RH, Projets

---

# 4. SPÉCIFICATIONS FONCTIONNELLES

## 4.1 Gestion Produits

### Fonctionnalités Principales

**FP-PROD-001 : CRUD Produits**
- Création fiche produit complète
- Modification (avec historique)
- Désactivation/Archivage
- Suppression (si non utilisé)

**FP-PROD-002 : Informations Produit**
- Code unique auto-généré
- Nom et description (court/long)
- Catégorie(s)
- Images multiples (max 10)
- Prix de vente et coût
- Unité de mesure
- Code-barres
- Références interne/fournisseur
- Poids, volume, dimensions
- Statut (actif/inactif)

**FP-PROD-003 : Gestion Prix**
- Prix de vente standard
- Listes de prix multiples
- Prix dégressifs par quantité
- Prix promotionnels (dates validité)
- Historique des prix

**FP-PROD-004 : Variantes**
- Produit parent
- Variantes multiples (couleur, taille, etc.)
- Code unique par variante
- Prix et stock par variante

**FP-PROD-005 : Recherche et Filtres**
- Recherche full-text
- Filtres : catégorie, prix, stock, statut
- Tri multi-critères
- Export résultats

**FP-PROD-006 : Import/Export**
- Import Excel/CSV (création/mise à jour)
- Template fourni
- Validation et rapport erreurs
- Export catalogue complet

### Règles de Gestion

**RG-PROD-001** : Code produit unique obligatoire (max 50 car.)  
**RG-PROD-002** : Prix vente ≥ 0, coût ≥ 0  
**RG-PROD-003** : Au moins une catégorie obligatoire  
**RG-PROD-004** : Si stock géré : stock initial obligatoire  
**RG-PROD-005** : Code-barres unique si renseigné  
**RG-PROD-006** : Suppression impossible si produit utilisé dans documents  

---

## 4.2 Gestion Clients

### Fonctionnalités Principales

**FP-CLI-001 : CRUD Clients**
- Création fiche client (B2B ou B2C)
- Modification
- Désactivation/Blocage
- Archivage

**FP-CLI-002 : Informations Client**
- Code client auto-généré (CLI-XXXXXX)
- Type : Entreprise ou Particulier
- Si Entreprise :
  - Raison sociale
  - SIRET, n° TVA, RCS
  - Forme juridique
- Si Particulier :
  - Nom, Prénom
  - Date naissance (optionnel)
- Email unique obligatoire
- Téléphones (fixe/mobile)
- Catégorisation (VIP, Standard, etc.)
- Notes internes

**FP-CLI-003 : Adresses**
- Adresse siège/domicile
- Adresses multiples :
  - Facturation
  - Livraison (plusieurs possibles)
- Par défaut configurables
- Géolocalisation (optionnel)

**FP-CLI-004 : Contacts**
- Contacts multiples par client
- Nom, prénom, fonction
- Email, téléphone
- Contact principal
- Droits (reçoit factures, devis, etc.)

**FP-CLI-005 : Conditions Commerciales**
- Délai paiement (30/60/90 jours)
- Liste de prix
- Remise par défaut (%)
- Limite de crédit
- Blocage automatique si dépassement

**FP-CLI-006 : Historique**
- Tous les devis
- Toutes les commandes
- Toutes les factures
- Tous les paiements
- Toutes les interactions
- Timeline chronologique

**FP-CLI-007 : Statistiques Client**
- CA total
- CA année en cours
- Panier moyen
- Fréquence d'achat
- Délai moyen paiement
- Top produits achetés

**FP-CLI-008 : Gestion Crédit**
- Limite de crédit définie
- Crédit utilisé (factures impayées)
- Crédit disponible
- Alertes (80%, 100%)
- Historique modifications limite

**FP-CLI-009 : Import/Export**
- Import clients Excel/CSV
- Export clients
- Export historique client

### Règles de Gestion

**RG-CLI-001** : Email unique et valide obligatoire  
**RG-CLI-002** : Code client unique auto-généré  
**RG-CLI-003** : Si entreprise : raison sociale obligatoire  
**RG-CLI-004** : Au moins une adresse de facturation  
**RG-CLI-005** : Limite crédit ≥ 0  
**RG-CLI-006** : Remise défaut 0-100%  
**RG-CLI-007** : Blocage commandes si limite crédit dépassée (paramétrable)  
**RG-CLI-008** : SIRET 14 chiffres (France)  

---

## 4.3 Gestion Stock

### Fonctionnalités Principales

**FP-STOCK-001 : Visualisation Stock**
- Stock par produit
- Stock par emplacement
- Stock physique, réservé, disponible
- Stock prévisionnel
- Code couleur (vert/orange/rouge)
- Actualisation temps réel

**FP-STOCK-002 : Mouvements de Stock**
- Types :
  - Entrée (réception, production, retour)
  - Sortie (vente, rebut, perte)
  - Transfert (entre emplacements)
  - Ajustement (inventaire)
- Saisie manuelle ou automatique
- Traçabilité complète (qui, quand, pourquoi)
- Documents associés (BC, BL)

**FP-STOCK-003 : Emplacements**
- Structure hiérarchique :
  - Entrepôt
  - Zone
  - Allée
  - Étagère
  - Niveau
- Emplacements virtuels (fournisseurs, clients)
- Capacité par emplacement (optionnel)

**FP-STOCK-004 : Inventaires**
- Inventaire complet ou partiel
- Sélection par :
  - Catégorie
  - Emplacement
  - Produits spécifiques
- Comptage :
  - Manuel
  - Scanner code-barres
  - Import fichier
- Comparaison stock/comptage
- Génération ajustements
- Rapport d'inventaire

**FP-STOCK-005 : Règles Réapprovisionnement**
- Configuration par produit :
  - Stock minimum
  - Stock maximum
  - Point de commande
  - Quantité à commander
- Alertes automatiques
- Génération demandes d'achat
- Dashboard "À réapprovisionner"

**FP-STOCK-006 : Valorisation**
- Méthodes :
  - Prix Standard (fixe)
  - AVCO (coût moyen pondéré)
  - FIFO (premier entré, premier sorti)
- Calcul valeur stock
- Rapport de valorisation
- Historique valorisation

**FP-STOCK-007 : Traçabilité**
- Par numéro de lot
- Par numéro de série
- Date péremption
- Date fabrication
- Suivi complet origine → destination

### Règles de Gestion

**RG-STOCK-001** : Stock physique ≥ 0 (sauf autorisation)  
**RG-STOCK-002** : Stock réservé ≤ stock physique  
**RG-STOCK-003** : Mouvement nécessite emplacement source ET/OU destination  
**RG-STOCK-004** : Lot/Série obligatoire si produit tracé  
**RG-STOCK-005** : Inventaire bloque mouvements sur produits concernés  
**RG-STOCK-006** : Transfert : stock source ≥ quantité transférée  
**RG-STOCK-007** : Alerte si stock < minimum  

---

## 4.4 Gestion des Ventes

### Fonctionnalités Principales

**FP-VENTE-001 : Devis**
- Création devis
- Sélection client
- Numérotation auto (DEV-YYYY-XXXXX)
- Ajout lignes produits
- Calculs automatiques (HT, TVA, TTC)
- Remises (ligne et globale)
- Date validité (30 jours par défaut)
- Notes client et internes
- Conditions générales
- Génération PDF professionnel
- Envoi email client

**FP-VENTE-002 : Workflow Devis**
- États :
  - Brouillon
  - Envoyé
  - Accepté
  - Refusé
  - Expiré
  - Annulé
- Relances automatiques (J+7, J+15)
- Versioning si modification après envoi
- Historique versions

**FP-VENTE-003 : Commandes**
- Création depuis devis ou manuelle
- Numérotation auto (CMD-YYYY-XXXXX)
- Vérifications :
  - Stock disponible
  - Crédit client
  - Client actif
- Réservation stock automatique
- Dates livraison (demandée/promis/réelle)
- Adresse livraison
- Instructions livraison

**FP-VENTE-004 : Workflow Commandes**
- États :
  - Brouillon
  - Confirmée
  - En préparation
  - Prête
  - Expédiée
  - Livrée
  - Facturée
  - Annulée
- Traçabilité changements
- Livraisons partielles possibles
- Facturation partielle possible

**FP-VENTE-005 : Préparation Commandes**
- Ordre de picking généré
- Par zone/emplacement
- Scanner code-barres
- Bon de livraison
- Étiquettes expédition
- Tracking transporteur

**FP-VENTE-006 : Documents**
- Devis PDF
- Confirmation commande PDF
- Bon de livraison PDF
- Templates personnalisables
- Logo entreprise
- Mentions légales

### Règles de Gestion

**RG-VENTE-001** : Au moins une ligne produit  
**RG-VENTE-002** : Quantité > 0  
**RG-VENTE-003** : Prix ≥ 0  
**RG-VENTE-004** : Remise ≤ 100%  
**RG-VENTE-005** : Date expiration > date devis  
**RG-VENTE-006** : Conversion commande uniquement si devis accepté  
**RG-VENTE-007** : Blocage si crédit insuffisant (paramétrable)  
**RG-VENTE-008** : Alerte si stock insuffisant  
**RG-VENTE-009** : Annulation commande libère stock réservé  
**RG-VENTE-010** : Remise exceptionnelle (>15%) nécessite validation  

---

## 4.5 Facturation

### Fonctionnalités Principales

**FP-FACT-001 : Génération Factures**
- Création depuis commande
- Numérotation légale (FA-YYYY-XXXXX)
- Séquentielle sans trou
- Sélection lignes à facturer
- Facturation partielle
- Calculs automatiques

**FP-FACT-002 : Informations Obligatoires**
- Numéro unique
- Date facture et échéance
- Identité émetteur complète
- Identité client complète
- Détail lignes (qté, PU, TVA)
- Total HT, TVA, TTC
- Conditions paiement
- Pénalités retard
- Indemnité forfaitaire (40€)
- Mentions légales

**FP-FACT-003 : Avoirs**
- Création avoir
- Lien facture d'origine
- Raison avoir obligatoire
- Montant total ou partiel
- Numérotation séparée (AV-YYYY-XXXXX)

**FP-FACT-004 : États Facture**
- Brouillon
- Validée
- Envoyée
- Partiellement payée
- Payée
- Échue (impayée)
- Annulée (via avoir)

**FP-FACT-005 : Envoi et Export**
- Génération PDF conforme
- Envoi email automatique
- Export comptable (FEC, CSV)
- Archivage légal

### Règles de Gestion

**RG-FACT-001** : Numérotation strictement séquentielle  
**RG-FACT-002** : Pas de trou dans numérotation  
**RG-FACT-003** : Facture validée non modifiable  
**RG-FACT-004** : Annulation uniquement par avoir  
**RG-FACT-005** : Conservation 10 ans minimum  
**RG-FACT-006** : Date facture ≤ aujourd'hui  
**RG-FACT-007** : Échéance selon délai paiement client  
**RG-FACT-008** : Quantités facturées ≤ quantités livrées  

---

## 4.6 Paiements

### Fonctionnalités Principales

**FP-PAY-001 : Enregistrement Paiements**
- Saisie manuelle
- Import relevé bancaire
- Modes paiement :
  - Espèces
  - Chèque
  - Virement
  - Carte bancaire
  - Prélèvement
- Affectation sur facture(s)
- Paiement partiel possible

**FP-PAY-002 : Rapprochement Bancaire**
- Import relevés bancaires
- Rapprochement automatique
- Rapprochement manuel
- Lettrage factures

**FP-PAY-003 : Relances**
- Niveaux de relance (1, 2, 3)
- Automatisation :
  - J+7 après échéance
  - J+15 après échéance
  - J+30 après échéance
- Templates emails
- Lettres de relance PDF
- Historique relances

**FP-PAY-004 : Suivi Impayés**
- Liste factures échues
- Groupement par ancienneté (0-30j, 30-60j, 60-90j, >90j)
- Montants
- Dashboard impayés
- Alertes

### Règles de Gestion

**RG-PAY-001** : Montant paiement > 0  
**RG-PAY-002** : Montant paiement ≤ reste à payer  
**RG-PAY-003** : Date paiement ≥ date facture  
**RG-PAY-004** : Facture payée non modifiable  
**RG-PAY-005** : Relance si échéance dépassée  
**RG-PAY-006** : Libération crédit client après paiement  

---

## 4.7 Achats

### Fonctionnalités Principales

**FP-ACH-001 : Demandes d'Achat**
- Création manuelle
- Génération automatique (si stock < minimum)
- Validation workflow
- Conversion en commande fournisseur

**FP-ACH-002 : Commandes Fournisseurs**
- Création
- Sélection fournisseur
- Ajout lignes produits
- Calculs automatiques
- Numérotation (BCA-YYYY-XXXXX)
- Envoi email fournisseur
- Suivi statuts

**FP-ACH-003 : Réceptions**
- Depuis commande fournisseur
- Vérification quantités
- Contrôle qualité (optionnel)
- Génération mouvement stock
- Bon de réception
- Écarts quantités

**FP-ACH-004 : Factures Fournisseurs**
- Saisie facture
- Rapprochement avec BC/réception
- Contrôle (3-way matching)
- Validation paiement
- Échéancier

### Règles de Gestion

**RG-ACH-001** : Demande validée avant conversion commande  
**RG-ACH-002** : Réception partielle autorisée  
**RG-ACH-003** : Écart réception > 10% nécessite validation  
**RG-ACH-004** : Facture ≤ commande (montant)  
**RG-ACH-005** : Mise à jour coût produit après réception  

---

# 5. EXIGENCES TECHNIQUES

## 5.1 Exigences de Performance

**PERF-001** : Temps de réponse
- Pages < 2 secondes (95% des cas)
- Recherches < 1 seconde pour 10 000 enregistrements
- Rapports < 5 secondes pour 12 mois de données

**PERF-002** : Charge utilisateurs
- Support 50 utilisateurs simultanés minimum
- Support 100 utilisateurs simultanés cible

**PERF-003** : Volume de données
- 100 000 produits minimum
- 50 000 clients minimum
- 1 000 000 documents/an minimum
- 10 000 000 lignes de documents/an minimum

**PERF-004** : Disponibilité
- Disponibilité 99,5% (43h downtime/an max)
- Fenêtre maintenance : nuit ou weekend
- Notification préalable maintenance programmée

## 5.2 Exigences de Compatibilité

**COMPAT-001** : Navigateurs Web
- Chrome 100+
- Firefox 100+
- Edge 100+
- Safari 15+

**COMPAT-002** : Systèmes d'exploitation
- Serveur : Linux (Ubuntu/Debian) ou Windows Server
- Client : Windows 10+, macOS 12+, Linux
- Mobile : iOS 15+, Android 11+

**COMPAT-003** : Résolution écran
- Desktop : 1366×768 minimum, 1920×1080 recommandé
- Tablette : 768×1024 minimum
- Mobile : 360×640 minimum

**COMPAT-004** : Bases de données
- PostgreSQL 14+ (recommandé)
- SQL Server 2019+ (alternative)
- MySQL 8+ (alternative)

## 5.3 Exigences d'Évolutivité

**SCAL-001** : Architecture modulaire
- Modules indépendants
- Ajout de modules sans impact existant
- API RESTful pour extensions

**SCAL-002** : Croissance
- Support croissance ×10 volume sur 5 ans
- Scalabilité horizontale possible

**SCAL-003** : Multi-tenant
- Support optionnel multi-entreprises
- Isolation données par tenant
- Gestion centralisée

## 5.4 Exigences de Sécurité

**SEC-001** : Authentification
- Authentification forte
- Mot de passe complexité minimale
- Double authentification (2FA) optionnelle
- Expiration session inactivité (30 min)
- Verrouillage compte après 5 tentatives échouées

**SEC-002** : Autorisation
- Gestion rôles et permissions
- RBAC (Role-Based Access Control)
- Permissions granulaires par module/fonction
- Héritage permissions
- Audit des accès

**SEC-003** : Chiffrement
- HTTPS obligatoire (TLS 1.2+)
- Chiffrement données sensibles en base
- Chiffrement sauvegardes

**SEC-004** : Audit et Traçabilité
- Log toutes les actions utilisateurs
- Horodatage et utilisateur
- Conservation logs 1 an minimum
- Non répudiation

**SEC-005** : Protection données
- Conformité RGPD
- Droit à l'oubli
- Portabilité données
- Consentement explicite

**SEC-006** : Sauvegardes
- Sauvegarde automatique quotidienne
- Sauvegarde incrémentale horaire (optionnel)
- Rétention 30 jours minimum
- Test restauration trimestriel
- Stockage sauvegardes hors site

## 5.5 Exigences d'Ergonomie

**ERGO-001** : Interface utilisateur
- Design moderne et intuitif
- Responsive (desktop/tablette/mobile)
- Navigation cohérente
- Messages d'erreur explicites
- Aide contextuelle

**ERGO-002** : Accessibilité
- Conformité WCAG 2.1 niveau AA
- Navigation clavier
- Lecteurs d'écran supportés
- Contrastes suffisants

**ERGO-003** : Internationalisation
- Support multi-langues (FR, AR, EN minimum)
- Support multi-devises
- Formats date/nombre localisés
- RTL supporté (arabe)

**ERGO-004** : Productivité
- Raccourcis clavier
- Actions en masse (sélection multiple)
- Recherche globale
- Favoris/Raccourcis personnalisables

---

# 6. ARCHITECTURE SYSTÈME

## 6.1 Architecture Applicative

### Architecture en Couches (Recommandée)

```
┌─────────────────────────────────────┐
│      PRÉSENTATION (UI)              │
│  Web App / Mobile App / API         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      APPLICATION (Business)         │
│  Use Cases / Services / DTOs        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      DOMAINE (Core)                 │
│  Entities / Business Rules          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      INFRASTRUCTURE (Data)          │
│  Database / Files / External APIs   │
└─────────────────────────────────────┘
```

**Principes :**
- Séparation des responsabilités (SoC)
- Inversion de dépendances (DIP)
- Indépendance du framework
- Testabilité maximale

### Pattern Recommandé

**Clean Architecture** ou **Onion Architecture**
- Domaine au centre
- Infrastructure en périphérie
- Dépendances vers l'intérieur uniquement

## 6.2 Architecture Technique

### Stack Technologique .NET

**Backend :**
- Framework : ASP.NET Core 8.0 ou .NET 9
- Langage : C# 12
- ORM : Entity Framework Core 8.0
- API : RESTful + Swagger/OpenAPI
- Cache : Redis (distributed) + IMemoryCache
- Jobs : Hangfire ou Quartz.NET
- Messaging : RabbitMQ ou Azure Service Bus (si microservices)

**Base de Données :**
- Principale : PostgreSQL 16 (recommandé) ou SQL Server 2022
- Cache : Redis 7
- Recherche : Elasticsearch (optionnel, si volumes importants)

**Frontend (3 options) :**

**Option 1 - Blazor WebAssembly** (Recommandé si équipe .NET)
- UI Components : MudBlazor ou Radzen
- State : Fluxor
- Charts : ApexCharts.Blazor

**Option 2 - React + TypeScript** (Recommandé si équipe polyvalente)
- Framework : React 18 + Next.js 14
- UI : Material-UI (MUI) ou Ant Design
- State : Redux Toolkit + React Query
- Charts : Recharts

**Option 3 - Angular** (Entreprise stricte)
- Framework : Angular 17+
- UI : Angular Material
- State : NgRx

**Mobile (Optionnel) :**
- .NET MAUI (C# partagé)
- ou Flutter (si besoin UI riche)

## 6.3 Architecture Données

### Modèle Relationnel

**Schémas principaux :**
- Products (Produits)
- Customers (Clients)
- Sales (Ventes)
- Inventory (Stock)
- Purchasing (Achats)
- Billing (Facturation)
- Security (Sécurité)
- Common (Commun)

### Bases de Données

**Base Principale :**
- Toutes les données transactionnelles
- PostgreSQL ou SQL Server
- Schéma normalisé (3NF minimum)

**Base Analytics** (Optionnel) :
- Data Warehouse pour reporting
- Schéma dimensionnel (star schema)
- Rafraîchissement quotidien

**Cache Redis :**
- Sessions utilisateurs
- Données fréquemment lues
- Résultats recherches

## 6.4 Architecture Déploiement

### Option 1 : Monolithe (Recommandé MVP)

```
┌──────────────────────────────────┐
│       Load Balancer (Nginx)      │
└────────┬────────┬────────────────┘
         │        │
    ┌────▼────┐  │
    │ Web App │  │
    │ Backend │◄─┤
    └────┬────┘  │
         │       │
    ┌────▼────┐  │
    │Database │◄─┘
    │(Primary)│
    └─────────┘
```

**Avantages :**
- Simple à développer
- Simple à déployer
- Performances excellentes
- Pas de complexité réseau

### Option 2 : Microservices (Si scale)

```
┌────────────────────────────────────┐
│         API Gateway                │
│      (Ocelot ou YARP)             │
└─┬────┬────┬────┬────┬────────────┘
  │    │    │    │    │
  │ Products Service
  │    │ Orders Service
  │    │    │ Inventory Service
  │    │    │    │ Billing Service
  │    │    │    │    │
  └────┴────┴────┴────┴──────►
       Message Bus (RabbitMQ)
```

**Avantages :**
- Scalabilité indépendante
- Déploiements indépendants
- Technos différentes possibles
- Résilience (isolation des pannes)

**Inconvénients :**
- Complexité accrue
- Gestion réseau
- Transactions distribuées
- Coût infrastructure

**Recommandation :** Commencer monolithe modulaire, migrer microservices si nécessaire.

## 6.5 Architecture Sécurité

### Couches de Sécurité

**Niveau 1 : Réseau**
- Firewall
- VPN si accès distant
- DDoS protection
- Rate limiting

**Niveau 2 : Application**
- HTTPS/TLS obligatoire
- CORS configuré
- Headers sécurité (CSP, HSTS, etc.)
- Anti-CSRF tokens
- Validation entrées
- Échappement sorties

**Niveau 3 : Authentification**
- ASP.NET Core Identity
- JWT Tokens
- Refresh tokens
- 2FA optionnel
- OAuth 2.0 / OpenID Connect

**Niveau 4 : Autorisation**
- Policy-based
- Claims-based
- RBAC
- Permissions granulaires

**Niveau 5 : Données**
- Chiffrement au repos
- Chiffrement en transit
- Masquage données sensibles
- Audit trail complet

---

# 7. INTERFACES ET INTÉGRATIONS

## 7.1 Intégrations Obligatoires

**INT-001 : Comptabilité**
- Export FEC (Fichier Écritures Comptables)
- Export format Sage, Cegid, EBP
- Export CSV/Excel personnalisable
- Fréquence : Quotidienne ou à la demande

**INT-002 : Banque**
- Import relevés bancaires (CSV, OFX, CFONB)
- Rapprochement automatique
- Export virements SEPA
- Fréquence : Quotidienne

**INT-003 : Email**
- SMTP pour envois
- Templates personnalisables
- Pièces jointes (PDF)
- Suivi envois

## 7.2 Intégrations Optionnelles

**INT-004 : Transporteurs**
- API Chronopost, Colissimo, DHL, UPS, FedEx
- Génération étiquettes
- Tracking
- Calcul tarifs

**INT-005 : E-commerce**
- Synchronisation catalogue
- Import commandes web
- Mise à jour stock temps réel
- Synchronisation clients

**INT-006 : CRM Externe**
- Salesforce, HubSpot (si existant)
- Synchronisation contacts
- Synchronisation opportunités

**INT-007 : ERP Externe**
- SAP, Dynamics (si coexistence)
- Échange données master
- Synchronisation transactions

**INT-008 : Paiement en Ligne**
- Stripe, PayPal, Lydia
- Paiement sécurisé
- Callback confirmation

**INT-009 : BI / Analytics**
- Power BI, Tableau, Qlik
- Export données
- API données

## 7.3 APIs à Exposer

**API Publique (Externe) :**
- Authentification OAuth 2.0
- Rate limiting
- Documentation OpenAPI/Swagger
- Versioning (/api/v1/)

**Endpoints principaux :**
- GET /api/products : Liste produits
- GET /api/products/{id} : Détail produit
- POST /api/orders : Créer commande
- GET /api/orders/{id} : Détail commande
- GET /api/customers : Liste clients
- POST /api/invoices : Créer facture

**API Interne :**
- Pour applications internes
- Authentification JWT
- Pas de rate limiting

## 7.4 Webhooks

Notification d'événements vers systèmes externes :
- order.created
- order.shipped
- invoice.created
- invoice.paid
- stock.low

---

# 8. SÉCURITÉ ET CONFORMITÉ

## 8.1 RGPD

**RGPD-001 : Consentement**
- Consentement explicite collecte données
- Possibilité de retrait consentement
- Information claire sur usage données

**RGPD-002 : Droits des Personnes**
- Droit d'accès (export données personnelles)
- Droit de rectification
- Droit à l'oubli (suppression données)
- Droit à la portabilité
- Droit d'opposition

**RGPD-003 : Sécurité**
- Chiffrement données sensibles
- Pseudonymisation
- Minimisation des données
- Conservation limitée

**RGPD-004 : Documentation**
- Registre des traitements
- Politique de confidentialité
- Procédures violation données
- DPO désigné (si applicable)

## 8.2 Conformité Légale France

**CONF-001 : Facturation**
- Conformité article 289 du CGI
- Numérotation chronologique sans trou
- Mentions obligatoires complètes
- Conservation 10 ans
- Inaltérabilité, sécurisation, conservation (si dématérialisation)

**CONF-002 : Archivage Fiscal**
- Conservation factures 10 ans
- Conservation documents comptables 10 ans
- Format PDF/A recommandé
- Horodatage qualifié (optionnel)

**CONF-003 : Données Personnelles**
- Déclaration CNIL (si applicable)
- DPO (si > 250 salariés ou traitement sensible)
- Analyse d'impact (DPIA) si risque

## 8.3 Normes et Standards

**NORM-001 : ISO 27001** (Optionnel)
- Système management sécurité information
- Certification possible

**NORM-002 : PCI-DSS** (Si paiement carte)
- Protection données cartes bancaires
- Conformité si traitement CB

**NORM-003 : Accessibilité**
- WCAG 2.1 niveau AA minimum
- RGAA (référentiel français)

---

# 9. ORGANISATION ET PLANNING

## 9.1 Organisation Projet

### Équipe Projet Recommandée

**Côté Client :**
- Chef de Projet Fonctionnel (1)
- Product Owner (1)
- Utilisateurs Clés par module (5-10)
- Sponsor Direction (1)

**Côté Développement :**
- Chef de Projet Technique (1)
- Architecte Logiciel (1)
- Développeurs Backend .NET (2-4)
- Développeur Frontend (1-2)
- Développeur Mobile (1) - si applicable
- DevOps (1)
- Testeur QA (1)
- UX/UI Designer (1)

### Méthodologie

**Approche : Agile Scrum**
- Sprints de 2 semaines
- Réunions quotidiennes (daily)
- Démonstrations fin de sprint
- Rétrospectives
- Planification sprint

**Outils :**
- Gestion projet : Jira, Azure DevOps, ou Trello
- Documentation : Confluence ou Notion
- Code : GitHub, GitLab, ou Azure Repos
- Communication : Slack ou Teams

## 9.2 Planning Détaillé

### PHASE 1 : PRÉPARATION (4 semaines)

**Semaine 1-2 : Cadrage**
- Validation cahier des charges
- Ateliers utilisateurs
- Maquettes écrans
- Validation architecture

**Semaine 3-4 : Setup**
- Configuration environnements (Dev/Test/Prod)
- Mise en place CI/CD
- Configuration outils (Git, Jira, etc.)
- Recrutement équipe si nécessaire

**Livrables :**
- Cahier des charges validé
- Maquettes approuvées
- Environnements prêts
- Équipe constituée

---

### PHASE 2 : MVP (16 semaines)

**Sprint 1-2 (Semaines 1-4) : Fondations**
- Architecture projet
- Base de données (schéma initial)
- Authentification/Autorisation
- CRUD Produits
- CRUD Clients

**Sprint 3-4 (Semaines 5-8) : Stock & Ventes**
- Gestion Stock (mouvements basiques)
- Emplacements
- Devis (CRUD + workflow)
- Commandes (CRUD)

**Sprint 5-6 (Semaines 9-12) : Intégration**
- Conversion Devis → Commande
- Réservation stock
- Dashboard MVP
- Reporting basique

**Sprint 7-8 (Semaines 13-16) : Finalisation MVP**
- Tests complets
- Corrections bugs
- Formation utilisateurs pilotes
- Documentation utilisateur
- Déploiement pilote

**Livrables Phase 2 :**
- Application MVP fonctionnelle
- Tests validés
- Documentation
- Pilote lancé

**Critères de Sortie Phase 2 :**
- ✅ 100% fonctionnalités MVP développées
- ✅ Tests unitaires >80% couverture
- ✅ Tests d'intégration OK
- ✅ Tests utilisateurs OK
- ✅ Performance conforme
- ✅ Sécurité validée

---

### PHASE 3 : COMPLET (16 semaines)

**Sprint 9-10 (Semaines 17-20) : Facturation**
- Module facturation
- Numérotation légale
- Génération PDF
- Avoirs
- Envoi emails

**Sprint 11-12 (Semaines 21-24) : Paiements & Achats**
- Gestion paiements
- Relances automatiques
- Module achats
- Commandes fournisseurs
- Réceptions

**Sprint 13-14 (Semaines 25-28) : Multi-Emplacements & Reporting**
- Gestion multi-sites
- Transferts inter-sites
- Reporting avancé
- Export Excel/PDF
- Analytics

**Sprint 15-16 (Semaines 29-32) : Finalisation**
- Tests complets
- Optimisations performance
- Corrections bugs
- Formation complète
- Migration données
- Déploiement production

**Livrables Phase 3 :**
- Application complète
- Migration données OK
- Formation effectuée
- Production lancée

---

### PHASE 4 : AVANCÉ (16 semaines) - Optionnel

**Sprint 17-20 : POS**
- Interface caisse tactile
- Gestion sessions
- Paiements multiples
- Tickets

**Sprint 21-24 : CRM**
- Gestion prospects
- Pipeline
- Opportunités
- Suivi commercial

**Sprint 25-28 : E-commerce**
- Catalogue en ligne
- Panier
- Paiement
- Synchronisation

**Sprint 29-32 : Mobile**
- Application iOS/Android
- Fonctionnalités essentielles
- Mode hors-ligne
- Publication stores

---

## 9.3 Jalons et Points de Contrôle

| Jalon | Date | Livrables | Critères Validation |
|-------|------|-----------|-------------------|
| **J0** | S0 | Kick-off | Équipe mobilisée, planning validé |
| **J1** | S4 | Fin préparation | Environnements OK, maquettes validées |
| **J2** | S8 | Modules core | Produits + Clients fonctionnels |
| **J3** | S12 | Stock + Ventes | Workflow devis→commande OK |
| **J4** | S16 | MVP | Pilote lancé |
| **J5** | S24 | Facturation + Achats | Modules complets |
| **J6** | S32 | Go-Live | Production lancée |
| **J7** | S40 | POS + CRM | Modules avancés |
| **J8** | S48 | Mobile | Applications publiées |

---

# 10. BUDGET ET RESSOURCES

## 10.1 Estimation des Coûts (Développement Interne)

### Option 1 : Équipe Interne

**Ressources Humaines (32 semaines = 8 mois) :**

| Rôle | Nb | TJ Mensuel | Durée | Coût Total |
|------|-----|------------|-------|------------|
| Chef Projet Tech | 1 | 20j | 8 mois | 80 000 € |
| Architecte | 1 | 10j | 8 mois | 50 000 € |
| Dev Backend Senior | 2 | 40j | 8 mois | 160 000 € |
| Dev Frontend | 1 | 20j | 8 mois | 60 000 € |
| DevOps | 1 | 10j | 8 mois | 40 000 € |
| Testeur QA | 1 | 15j | 6 mois | 30 000 € |
| UX/UI Designer | 1 | 5j | 4 mois | 15 000 € |
| **Total RH** | | | | **435 000 €** |

**Infrastructure (8 mois + 1 an prod) :**

| Élément | Coût Mensuel | Durée | Total |
|---------|--------------|-------|-------|
| Serveurs Cloud Dev/Test | 300 € | 8 mois | 2 400 € |
| Serveurs Cloud Prod | 500 € | 12 mois | 6 000 € |
| Bases données | 200 € | 20 mois | 4 000 € |
| Monitoring/Logs | 100 € | 20 mois | 2 000 € |
| CI/CD | 100 € | 20 mois | 2 000 € |
| Stockage/CDN | 100 € | 20 mois | 2 000 € |
| **Total Infra** | | | **18 400 €** |

**Licences et Outils :**

| Élément | Coût Annuel | Nb | Total |
|---------|-------------|-----|-------|
| Visual Studio Enterprise | 5 000 € | 5 | 25 000 € |
| JetBrains | 200 € | 7 | 1 400 € |
| Jira/Confluence | 100 € | 10 | 1 000 € |
| GitHub/GitLab | 100 € | 1 | 100 € |
| **Total Licences** | | | **27 500 €** |

**Divers :**
- Formation équipe : 15 000 €
- Support/Conseil externe : 20 000 €
- Contingence (10%) : 51 600 €

**TOTAL PHASE MVP + COMPLET : 567 500 €**

---

### Option 2 : Prestation Externe (Forfait)

| Phase | Durée | Coût Estimé |
|-------|-------|-------------|
| MVP (Phase 1-2) | 4 mois | 120 000 - 180 000 € |
| Complet (Phase 3) | 4 mois | 100 000 - 150 000 € |
| Avancé (Phase 4) | 4 mois | 80 000 - 120 000 € |
| **Total Complet** | 8 mois | **220 000 - 330 000 €** |
| **Total avec Avancé** | 12 mois | **300 000 - 450 000 €** |

**Avantages Prestation :**
- Pas de recrutement
- Expertise immédiate
- Délais maîtrisés
- Garantie résultat

**Inconvénients :**
- Coût unitaire plus élevé
- Dépendance prestataire
- Transfer knowledge nécessaire

---

### Option 3 : Hybride (Interne + Prestation)

**Recommandation :**
- Core Team interne : Chef Projet + 1-2 Dev
- Renfort externe : 2-3 Dev + DevOps
- Coût : 350 000 - 450 000 €

**Avantages :**
- Équilibre coût/expertise
- Montée en compétence interne
- Flexibilité

---

## 10.2 Coûts Récurrents (Année 2+)

**Infrastructure Cloud (Annuel) :**
- Hébergement : 6 000 - 12 000 €
- Bases données : 3 000 - 6 000 €
- CDN/Stockage : 1 000 - 2 000 €
- Monitoring : 1 000 - 2 000 €
- **Total : 11 000 - 22 000 €/an**

**Maintenance et Évolution :**
- Corrections bugs : 20 000 - 30 000 €/an
- Évolutions mineures : 30 000 - 50 000 €/an
- Évolutions majeures : Budget projet séparé
- **Total : 50 000 - 80 000 €/an**

**Support et Formation :**
- Support utilisateurs : 15 000 - 25 000 €/an
- Formations nouvelles fonctionnalités : 5 000 - 10 000 €/an
- **Total : 20 000 - 35 000 €/an**

**TOTAL RÉCURRENT ANNUEL : 81 000 - 137 000 €/an**

---

## 10.3 Comparaison Développement vs Achat

| Critère | Développement Sur-Mesure | Solution du Marché (ex: Odoo) |
|---------|-------------------------|-------------------------------|
| **Coût Initial** | 220 000 - 567 000 € | 35 000 - 100 000 € |
| **Délai** | 8-12 mois | 3-6 mois |
| **Personnalisation** | ⭐⭐⭐⭐⭐ Totale | ⭐⭐⭐ Limitée |
| **Évolutivité** | ⭐⭐⭐⭐⭐ Totale | ⭐⭐⭐ Dépend éditeur |
| **Indépendance** | ⭐⭐⭐⭐⭐ Totale | ⭐⭐ Dépendance éditeur |
| **Coût Annuel** | 81 000 - 137 000 € | 10 000 - 20 000 € (licences) + évolutions |
| **Expertise** | ⭐⭐ Recrutement nécessaire | ⭐⭐⭐⭐ Partenaires disponibles |
| **Risque** | ⭐⭐⭐ Moyen-Élevé | ⭐⭐ Faible-Moyen |
| **Time-to-Market** | ⭐⭐ Long | ⭐⭐⭐⭐ Rapide |

**Quand développer sur-mesure ?**
- ✅ Besoins très spécifiques
- ✅ Processus uniques non standards
- ✅ Indépendance stratégique importante
- ✅ Budget et ressources disponibles
- ✅ Horizon long terme (5-10 ans)

**Quand acheter une solution ?**
- ✅ Processus standards
- ✅ Budget limité
- ✅ Besoin rapidité
- ✅ Pas d'expertise interne
- ✅ Horizon court-moyen terme

---

# 11. CRITÈRES DE VALIDATION

## 11.1 Critères Fonctionnels

**CF-001 : Complétude Fonctionnelle**
- [ ] 100% des fonctionnalités MVP implémentées
- [ ] 100% des user stories validées
- [ ] Tous les modules opérationnels

**CF-002 : Qualité Fonctionnelle**
- [ ] 0 bug bloquant
- [ ] < 5 bugs majeurs
- [ ] Bugs mineurs documentés et planifiés

**CF-003 : Ergonomie**
- [ ] Navigation fluide et intuitive
- [ ] Temps apprentissage < 2h par module
- [ ] Satisfaction utilisateurs > 80%

## 11.2 Critères Techniques

**CT-001 : Performance**
- [ ] Temps réponse pages < 2s (95%)
- [ ] Support 50+ utilisateurs simultanés
- [ ] Pas de dégradation performance sur 12 mois

**CT-002 : Qualité Code**
- [ ] Couverture tests unitaires > 80%
- [ ] Couverture tests intégration > 60%
- [ ] Dette technique < 10%
- [ ] Code review systématique
- [ ] Documentation code complète

**CT-003 : Sécurité**
- [ ] Aucune faille critique (OWASP Top 10)
- [ ] Tests pénétration passés
- [ ] Chiffrement données sensibles
- [ ] Audit sécurité validé

**CT-004 : Disponibilité**
- [ ] Uptime > 99,5% sur 3 mois
- [ ] Plan reprise activité testé
- [ ] Sauvegardes validées

## 11.3 Critères Projet

**CP-001 : Respect Planning**
- [ ] Écart < 15% sur durée totale
- [ ] Jalons majeurs respectés
- [ ] Communication régulière

**CP-002 : Respect Budget**
- [ ] Écart < 10% sur budget total
- [ ] Pas de dépassement sans validation
- [ ] Reporting financier régulier

**CP-003 : Documentation**
- [ ] Documentation utilisateur complète
- [ ] Documentation technique complète
- [ ] Vidéos formation disponibles
- [ ] FAQ constituée

**CP-004 : Formation**
- [ ] 100% utilisateurs formés
- [ ] Support niveau 1 autonome
- [ ] Satisfaction formation > 75%

## 11.4 Critères de Recette

### Recette Fonctionnelle

**RF-001 : Tests Unitaires**
- Chaque module testé individuellement
- Scénarios nominaux et alternatifs
- Gestion erreurs

**RF-002 : Tests d'Intégration**
- Workflows complets bout-en-bout
- Intégrations validées
- Cohérence données

**RF-003 : Tests Utilisateurs (UAT)**
- Tests par utilisateurs métier
- Scénarios réels
- Validation ergonomie

### Recette Technique

**RT-001 : Tests Performance**
- Tests charge (50+ users)
- Tests stress (limite système)
- Tests endurance (12h+)

**RT-002 : Tests Sécurité**
- Scan vulnérabilités
- Tests pénétration
- Audit code sécurité

**RT-003 : Tests Compatibilité**
- Navigateurs supportés
- Résolutions écran
- Systèmes d'exploitation

### Recette de Migration

**RM-001 : Migration Données**
- Données importées complètes
- Intégrité données validée
- Pas de perte données
- Performances migration acceptables

---

# 12. ANNEXES

## 12.1 Glossaire

| Terme | Définition |
|-------|------------|
| **MVP** | Minimum Viable Product - Version minimale fonctionnelle |
| **CRUD** | Create, Read, Update, Delete |
| **B2B** | Business to Business - Commerce entre entreprises |
| **B2C** | Business to Consumer - Commerce vers particuliers |
| **SKU** | Stock Keeping Unit - Référence produit unique |
| **TTC** | Toutes Taxes Comprises |
| **HT** | Hors Taxes |
| **FIFO** | First In First Out - Premier entré, premier sorti |
| **AVCO** | Average Cost - Coût moyen pondéré |
| **KPI** | Key Performance Indicator - Indicateur clé de performance |
| **API** | Application Programming Interface |
| **REST** | Representational State Transfer |
| **JWT** | JSON Web Token |
| **RGPD** | Règlement Général sur la Protection des Données |
| **CI/CD** | Continuous Integration / Continuous Deployment |
| **POS** | Point of Sale - Point de vente |
| **CRM** | Customer Relationship Management |
| **ERP** | Enterprise Resource Planning |

## 12.2 Références

**Normes et Standards :**
- ISO 27001 - Sécurité de l'information
- WCAG 2.1 - Accessibilité web
- RGPD - Protection des données
- Article 289 CGI - Facturation France

**Technologies :**
- ASP.NET Core : https://dotnet.microsoft.com/
- PostgreSQL : https://www.postgresql.org/
- React : https://react.dev/
- Blazor : https://dotnet.microsoft.com/apps/aspnet/web-apps/blazor

**Méthodologies :**
- Scrum : https://www.scrum.org/
- Clean Architecture : https://blog.cleancoder.com/

## 12.3 Templates Documents

**À fournir :**
- Template fiche produit
- Template fiche client
- Template devis (PDF)
- Template facture (PDF)
- Template bon de livraison
- Import produits Excel
- Import clients Excel

## 12.4 Contacts

**Équipe Projet :**
- Chef de Projet Fonctionnel : [Nom] - [Email]
- Chef de Projet Technique : [Nom] - [Email]
- Sponsor : [Nom] - [Email]

**Support :**
- Email : support@projet.com
- Téléphone : [Numéro]
- Horaires : Lun-Ven 9h-18h

---

## SIGNATURES ET VALIDATIONS

| Rôle | Nom | Signature | Date |
|------|-----|-----------|------|
| **Sponsor** | | | |
| **Chef Projet Fonctionnel** | | | |
| **Chef Projet Technique** | | | |
| **Utilisateur Clé Commercial** | | | |
| **Utilisateur Clé Logistique** | | | |
| **Utilisateur Clé Comptabilité** | | | |

---

**FIN DU CAHIER DES CHARGES**

Document créé le : 15 Novembre 2025  
Version : 1.0  
Statut : Draft - À valider

Ce cahier des charges est un document évolutif qui pourra être amendé en fonction des retours et besoins identifiés durant le projet.
