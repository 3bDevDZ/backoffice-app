# Guide Utilisateur - CommerceFlow

**Version**: 1.0  
**Date**: 2025-11-21  
**Langue**: Français

---

## 📋 Table des Matières

1. [Introduction](#introduction)
2. [Premiers Pas](#premiers-pas)
3. [Gestion des Produits](#gestion-des-produits)
4. [Gestion des Clients](#gestion-des-clients)
5. [Gestion du Stock](#gestion-du-stock)
6. [Gestion des Ventes](#gestion-des-ventes)
7. [Gestion des Achats](#gestion-des-achats)
8. [Facturation et Paiements](#facturation-et-paiements)
9. [Rapports et Analyses](#rapports-et-analyses)
10. [Configuration](#configuration)
11. [FAQ](#faq)
12. [Dépannage](#dépannage)

---

## Introduction

### Qu'est-ce que CommerceFlow ?

CommerceFlow est un système de gestion commerciale complet qui vous permet de gérer l'ensemble de votre activité : produits, clients, stocks, ventes, achats et facturation, le tout dans une interface moderne et intuitive.

### À qui s'adresse CommerceFlow ?

- **Petits grossistes** : Un seul entrepôt, gestion simple
- **PME multi-sites** : Plusieurs entrepôts, gestion avancée
- **Entreprises B2B et B2C** : Gestion des deux types de clients

### Fonctionnalités Principales

✅ **Gestion Produits** : Catalogue complet avec variantes, prix multiples, catégories  
✅ **Gestion Clients** : Fiches clients B2B/B2C, adresses, contacts, conditions commerciales  
✅ **Gestion Stock** : Suivi temps réel, multi-emplacements, alertes, inventaires  
✅ **Gestion Ventes** : Devis, commandes, workflow complet, PDF automatiques  
✅ **Gestion Achats** : Commandes fournisseurs, réceptions, factures fournisseurs  
✅ **Facturation** : Factures conformes, paiements, rapprochement bancaire  
✅ **Rapports** : Analyses de ventes, marges, stocks, clients, prévisions  

---

## Premiers Pas

### Connexion

1. Accédez à l'URL de votre application CommerceFlow
2. Entrez vos identifiants :
   - **Nom d'utilisateur** : Votre nom d'utilisateur
   - **Mot de passe** : Votre mot de passe
3. Cliquez sur **"Se connecter"**

> **Note** : Les identifiants par défaut sont `admin` / `admin` (à changer immédiatement en production)

### Interface Principale

L'interface se compose de :

- **Menu latéral gauche** : Navigation entre les modules
- **Zone de contenu principale** : Affichage des données et formulaires
- **Barre supérieure** : Notifications, date, profil utilisateur

### Navigation

#### Page Modules

Après connexion, vous arrivez sur la **page Modules** qui présente tous les modules disponibles :

- 📊 **Dashboard** : Vue d'ensemble de l'activité
- 💼 **Ventes** : Clients, devis, commandes, factures, paiements
- 🛒 **Achats** : Fournisseurs, demandes d'achat, commandes, réceptions
- 📦 **Inventaire** : Stock, emplacements, transferts, mouvements, alertes
- 🏷️ **Catalogue** : Produits, listes de prix
- 📈 **Rapports** : Analyses et prévisions
- ⚙️ **Paramètres** : Configuration de l'application

#### Menu Latéral

Lorsque vous entrez dans un module, le menu latéral affiche les sous-modules spécifiques.

**Exemple - Module Ventes** :
- Clients
- Devis
- Commandes
- Promotions
- Factures
- Paiements
- Dashboard Paiements

### Changement de Langue

Le système supporte **3 langues** :
- 🇫🇷 **Français** (FR)
- 🇬🇧 **English** (EN)
- 🇸🇦 **العربية** (AR)

Pour changer la langue :
1. Cliquez sur l'icône de langue dans la barre supérieure
2. Sélectionnez la langue souhaitée

> **Note** : La langue est sauvegardée dans votre profil et sera utilisée lors de vos prochaines connexions.

---

## Gestion des Produits

### Vue d'ensemble

Le module **Catalogue** permet de gérer votre catalogue produits avec variantes, prix multiples et catégorisation.

### Créer un Produit

1. Accédez à **Catalogue → Produits**
2. Cliquez sur **"Nouveau Produit"**
3. Remplissez le formulaire :

#### Informations Générales
- **Nom** : Nom du produit (obligatoire)
- **Code** : Code unique (auto-généré si vide)
- **Référence** : Référence interne
- **Catégorie** : Sélectionnez une catégorie
- **Description** : Description détaillée

#### Informations Techniques
- **Unité de vente** : Unité, kg, L, m², etc.
- **Poids** : Poids unitaire
- **Dimensions** : Longueur, largeur, hauteur

#### Prix
- **Prix de vente HT** : Prix unitaire hors taxes
- **Taux de TVA** : Taux de TVA applicable (20%, 10%, 5.5%, etc.)
- **Prix de revient** : Coût d'achat (pour calcul des marges)

#### Stock
- **Gestion du stock** : Activer/désactiver la gestion du stock
- **Stock minimum** : Seuil d'alerte
- **Stock maximum** : Niveau maximum recommandé

4. Cliquez sur **"Enregistrer"**

### Variantes de Produit

Pour créer des variantes (couleur, taille, etc.) :

1. Créez d'abord le produit principal
2. Dans la fiche produit, section **"Variantes"**
3. Cliquez sur **"Ajouter une variante"**
4. Remplissez :
   - **Nom de la variante** : Ex. "Rouge - Taille L"
   - **Code SKU** : Code unique de la variante
   - **Prix** : Prix spécifique (optionnel)
   - **Stock** : Stock spécifique

### Listes de Prix

Les listes de prix permettent d'appliquer des prix différents selon le type de client.

#### Créer une Liste de Prix

1. Accédez à **Catalogue → Listes de Prix**
2. Cliquez sur **"Nouvelle Liste de Prix"**
3. Remplissez :
   - **Nom** : Ex. "Prix Grossiste"
   - **Description** : Description de la liste
   - **Statut** : Active/Inactive
4. Cliquez sur **"Enregistrer"**

#### Ajouter des Produits à une Liste

1. Ouvrez la liste de prix
2. Section **"Produits"**
3. Cliquez sur **"Ajouter un produit"**
4. Sélectionnez le produit et entrez le prix
5. Cliquez sur **"Enregistrer"**

### Prix Dégressifs (Volume Pricing)

Pour appliquer des remises selon la quantité :

1. Dans la fiche produit, section **"Prix Dégressifs"**
2. Cliquez sur **"Ajouter un palier"**
3. Remplissez :
   - **Quantité minimum** : Ex. 10
   - **Prix unitaire** : Ex. 8.50€ (au lieu de 10€)
4. Cliquez sur **"Enregistrer"**

**Exemple** :
- 1-9 unités : 10€
- 10-49 unités : 8.50€ (-15%)
- 50+ unités : 7.50€ (-25%)

### Catégories

#### Créer une Catégorie

1. Accédez à **Catalogue → Produits**
2. Dans le filtre, cliquez sur **"Gérer les catégories"**
3. Cliquez sur **"Nouvelle Catégorie"**
4. Remplissez :
   - **Nom** : Nom de la catégorie
   - **Catégorie parente** : Pour créer une sous-catégorie
   - **Description** : Description de la catégorie

### Import/Export

#### Exporter les Produits

1. Accédez à **Catalogue → Produits**
2. Cliquez sur **"Exporter"**
3. Le fichier Excel sera téléchargé

#### Importer les Produits

1. Accédez à **Catalogue → Produits**
2. Cliquez sur **"Importer"**
3. Sélectionnez votre fichier Excel/CSV
4. Vérifiez le prévisualisation
5. Cliquez sur **"Importer"**

**Format du fichier** :
- Colonnes requises : `nom`, `code`, `prix_vente_ht`, `taux_tva`
- Colonnes optionnelles : `description`, `categorie`, `poids`, `unite`

---

## Gestion des Clients

### Vue d'ensemble

Le module **Ventes → Clients** permet de gérer vos clients B2B et B2C avec leurs informations complètes.

### Créer un Client

1. Accédez à **Ventes → Clients**
2. Cliquez sur **"Nouveau Client"**
3. Sélectionnez le type : **B2B** ou **B2C**

#### Client B2B

**Informations Entreprise** :
- **Nom** : Nom commercial (obligatoire)
- **Raison sociale** : Nom légal
- **SIRET** : Numéro SIRET (14 chiffres)
- **TVA** : Numéro de TVA intracommunautaire
- **RCS** : Numéro RCS
- **Forme juridique** : SARL, SAS, etc.

**Informations Contact** :
- **Email** : Email principal
- **Téléphone** : Téléphone fixe
- **Mobile** : Téléphone portable

**Conditions Commerciales** :
- **Délais de paiement** : Nombre de jours (ex. 30, 60)
- **Remise par défaut** : Remise automatique (%)
- **Limite de crédit** : Montant maximum autorisé
- **Liste de prix** : Liste de prix spécifique

#### Client B2C

**Informations Personnelles** :
- **Prénom** : Prénom
- **Nom** : Nom de famille
- **Date de naissance** : Date de naissance (optionnel)
- **Email** : Email
- **Téléphone** : Téléphone

**Conditions Commerciales** :
- **Délais de paiement** : Généralement 0 (paiement immédiat)
- **Remise par défaut** : Remise automatique (%)

4. Cliquez sur **"Enregistrer"**

### Adresses

Pour ajouter une adresse :

1. Ouvrez la fiche client
2. Section **"Adresses"**
3. Cliquez sur **"Ajouter une adresse"**
4. Remplissez :
   - **Type** : Siège, Facturation, Livraison, Autre
   - **Adresse** : Rue et numéro
   - **Code postal** : Code postal
   - **Ville** : Ville
   - **Pays** : Pays
5. Cliquez sur **"Enregistrer"**

### Contacts

Pour ajouter un contact :

1. Ouvrez la fiche client
2. Section **"Contacts"**
3. Cliquez sur **"Ajouter un contact"**
4. Remplissez :
   - **Nom** : Nom complet
   - **Fonction** : Poste occupé
   - **Email** : Email du contact
   - **Téléphone** : Téléphone
5. Cliquez sur **"Enregistrer"**

### Vue Client

La vue client affiche :
- **Informations générales** : Type, statut, coordonnées
- **Commandes en attente** : Liste des commandes non livrées
- **Factures non payées** : Liste des factures avec montant restant

Pour accéder à la vue client :
1. Accédez à **Ventes → Clients**
2. Cliquez sur l'icône **👁️ (Voir)** à côté du client

---

## Gestion du Stock

### Vue d'ensemble

Le module **Inventaire** permet de gérer votre stock en temps réel avec support multi-emplacements.

### Modes de Gestion

CommerceFlow propose **2 modes** :

#### Mode Simple
- **Un seul entrepôt** : Tous les produits dans un emplacement par défaut
- **Interface simplifiée** : Pas de sélection de site lors de la réception
- **Idéal pour** : Petits grossistes avec un seul entrepôt

#### Mode Avancé
- **Multi-sites** : Plusieurs entrepôts/sites
- **Emplacements détaillés** : Structure hiérarchique (Site → Zone → Allée → Étagère)
- **Transfers inter-sites** : Transferts de stock entre sites
- **Idéal pour** : Entreprises avec plusieurs entrepôts

> **Note** : Le mode est configuré dans **Paramètres → Application → Mode de gestion du stock**

### Vue Stock

1. Accédez à **Inventaire → Stock**
2. Vous voyez :
   - **Valeur totale du stock** : Valeur globale
   - **Nombre de produits** : Nombre de produits en stock
   - **Tableau détaillé** : Produit, emplacement, quantités, valeur

### Emplacements (Locations)

Les emplacements permettent d'organiser votre stock physiquement.

#### Créer un Emplacement

1. Accédez à **Inventaire → Entrepôts**
2. Cliquez sur **"Nouvel Emplacement"**
3. Remplissez :
   - **Code** : Code unique (ex. "ZONE-A-01")
   - **Nom** : Nom de l'emplacement (ex. "Zone A - Allée 1")
   - **Type** : Warehouse, Zone, Aisle, Shelf, Level, Virtual
   - **Site** : Site parent (mode avancé uniquement)
   - **Emplacement parent** : Pour créer une hiérarchie
4. Cliquez sur **"Enregistrer"**

**Exemple de hiérarchie** :
```
Entrepôt Principal (Warehouse)
  └── Zone A (Zone)
      └── Allée 1 (Aisle)
          └── Étagère 2 (Shelf)
              └── Niveau 3 (Level)
```

### Sites (Mode Avancé)

Les sites représentent vos différents entrepôts.

#### Créer un Site

1. Accédez à **Inventaire → Sites**
2. Cliquez sur **"Nouveau Site"**
3. Remplissez :
   - **Code** : Code unique (ex. "PARIS-NORD")
   - **Nom** : Nom du site (ex. "Entrepôt Paris Nord")
   - **Adresse** : Adresse complète
   - **Responsable** : Responsable du site
4. Cliquez sur **"Enregistrer"**

### Mouvements de Stock

Les mouvements permettent de suivre toutes les entrées et sorties.

#### Types de Mouvements

- **Réception** : Entrée de marchandises (depuis achat)
- **Sortie** : Sortie de marchandises (vers vente)
- **Transfert** : Transfert entre emplacements
- **Ajustement** : Correction d'inventaire
- **Inventaire** : Mouvement d'inventaire

#### Consulter les Mouvements

1. Accédez à **Inventaire → Mouvements**
2. Filtrez par :
   - **Date** : Période
   - **Type** : Type de mouvement
   - **Produit** : Produit spécifique
   - **Emplacement** : Emplacement spécifique

### Alertes Stock

Le système génère automatiquement des alertes pour :
- **Rupture de stock** : Stock = 0
- **Stock minimum atteint** : Stock ≤ seuil minimum
- **Stock maximum dépassé** : Stock > seuil maximum

#### Consulter les Alertes

1. Accédez à **Inventaire → Alertes**
2. Vous voyez la liste des produits en alerte
3. Cliquez sur un produit pour voir les détails

### Transferts Inter-Sites (Mode Avancé)

Pour transférer du stock entre sites :

1. Accédez à **Inventaire → Transferts**
2. Cliquez sur **"Nouveau Transfert"**
3. Remplissez :
   - **Site source** : Site d'origine
   - **Site destination** : Site de destination
   - **Produits** : Ajoutez les produits à transférer
4. Cliquez sur **"Créer"**
5. **Expédier** : Quand le transfert est prêt, cliquez sur "Expédier"
6. **Réceptionner** : Sur le site destination, cliquez sur "Réceptionner"

---

## Gestion des Ventes

### Vue d'ensemble

Le module **Ventes** gère le cycle complet de vente : devis, commandes, factures, paiements.

### Devis

#### Créer un Devis

1. Accédez à **Ventes → Devis**
2. Cliquez sur **"Nouveau Devis"**
3. Sélectionnez le **client**
4. Ajoutez les **produits** :
   - Recherchez le produit
   - Entrez la **quantité**
   - Le **prix** est calculé automatiquement selon la liste de prix du client
5. Ajustez si nécessaire :
   - **Remise globale** : Remise sur le total
   - **Notes** : Notes internes ou pour le client
6. Cliquez sur **"Enregistrer"**

#### Envoyer un Devis

1. Ouvrez le devis
2. Cliquez sur **"Envoyer"**
3. Le devis est envoyé par email au client
4. Le statut passe à **"Envoyé"**

#### Accepter un Devis

1. Le client accepte le devis (via lien email ou manuellement)
2. Le statut passe à **"Accepté"**
3. Vous pouvez **convertir en commande** :
   - Cliquez sur **"Convertir en Commande"**
   - Une commande est créée automatiquement

### Commandes

#### Créer une Commande

**Depuis un devis accepté** :
1. Ouvrez le devis accepté
2. Cliquez sur **"Convertir en Commande"**

**Création manuelle** :
1. Accédez à **Ventes → Commandes**
2. Cliquez sur **"Nouvelle Commande"**
3. Sélectionnez le **client**
4. Ajoutez les **produits**
5. Cliquez sur **"Enregistrer"**

#### Workflow de Commande

```
Brouillon (draft)
  ↓
Confirmée (confirmed) → Stock réservé automatiquement
  ↓
En préparation (in_preparation)
  ↓
Prête (ready) → Bon de livraison généré
  ↓
Expédiée (shipped) → Stock débité
  ↓
Livrée (delivered)
```

#### Confirmer une Commande

1. Ouvrez la commande en statut **"Brouillon"**
2. Cliquez sur **"Confirmer"**
3. Le système :
   - Vérifie le stock disponible
   - Vérifie le crédit client
   - Réserve automatiquement le stock
   - Change le statut à **"Confirmée"**

#### Mettre en Préparation

1. Ouvrez la commande **"Confirmée"**
2. Cliquez sur **"Mettre en Préparation"**
3. Le statut passe à **"En préparation"**

#### Marquer comme Prête

1. Ouvrez la commande **"En préparation"**
2. Cliquez sur **"Marquer comme Prête"**
3. Le système :
   - Génère le bon de livraison (PDF)
   - Change le statut à **"Prête"**

#### Expédier

1. Ouvrez la commande **"Prête"**
2. Cliquez sur **"Expédier"**
3. Le système :
   - Débite le stock réservé
   - Change le statut à **"Expédiée"**
   - Envoie le bon de livraison par email (optionnel)

#### Livrer

1. Ouvrez la commande **"Expédiée"**
2. Cliquez sur **"Marquer comme Livrée"**
3. Le statut passe à **"Livrée"**

### Promotions

Les promotions permettent d'appliquer des remises automatiques.

#### Créer une Promotion

1. Accédez à **Ventes → Promotions**
2. Cliquez sur **"Nouvelle Promotion"**
3. Remplissez :
   - **Nom** : Nom de la promotion
   - **Type** : Pourcentage ou montant fixe
   - **Valeur** : Valeur de la remise
   - **Période** : Date de début et fin
   - **Produits** : Produits concernés
   - **Clients** : Clients concernés (ou tous)
4. Cliquez sur **"Enregistrer"**

---

## Gestion des Achats

### Vue d'ensemble

Le module **Achats** gère le cycle complet d'achat : fournisseurs, demandes d'achat, commandes, réceptions, factures.

### Fournisseurs

#### Créer un Fournisseur

1. Accédez à **Achats → Fournisseurs**
2. Cliquez sur **"Nouveau Fournisseur"**
3. Remplissez les informations (similaire aux clients)
4. Cliquez sur **"Enregistrer"**

### Demandes d'Achat

Les demandes d'achat permettent de demander l'approbation avant de commander.

#### Créer une Demande d'Achat

1. Accédez à **Achats → Demandes d'Achat**
2. Cliquez sur **"Nouvelle Demande"**
3. Remplissez :
   - **Raison** : Pourquoi cet achat
   - **Produits** : Produits à acheter
4. Cliquez sur **"Soumettre"**
5. La demande passe en statut **"En attente d'approbation"**

#### Approuver une Demande

1. Ouvrez la demande
2. Cliquez sur **"Approuver"**
3. Vous pouvez **convertir en commande** :
   - Cliquez sur **"Créer Commande d'Achat"**

### Commandes d'Achat

#### Créer une Commande d'Achat

1. Accédez à **Achats → Commandes d'Achat**
2. Cliquez sur **"Nouvelle Commande"**
3. Sélectionnez le **fournisseur**
4. Ajoutez les **produits** avec quantités et prix
5. Cliquez sur **"Enregistrer"**

#### Confirmer une Commande

1. Ouvrez la commande
2. Cliquez sur **"Confirmer"**
3. Le statut passe à **"Confirmée"**
4. Vous pouvez **envoyer au fournisseur** :
   - Cliquez sur **"Envoyer"** (email automatique)

### Réceptions

Quand les marchandises arrivent, enregistrez la réception :

1. Accédez à **Achats → Réceptions**
2. Cliquez sur **"Nouvelle Réception"**
3. Sélectionnez la **commande d'achat**
4. Pour chaque produit :
   - **Quantité reçue** : Quantité réellement reçue
   - **Emplacement** : Où stocker (mode avancé : Site + Location)
5. Cliquez sur **"Valider la Réception"**
6. Le système :
   - Met à jour le stock automatiquement
   - Met à jour le coût des produits (AVCO)
   - Met à jour le statut de la commande

> **Note** : En mode simple, l'emplacement est automatique (entrepôt par défaut)

### Factures Fournisseurs

#### Créer une Facture Fournisseur

1. Accédez à **Achats → Factures Fournisseurs**
2. Cliquez sur **"Nouvelle Facture"**
3. Sélectionnez la **commande d'achat** (optionnel)
4. Remplissez les informations
5. Cliquez sur **"Enregistrer"**

#### Rapprochement Automatique

Si vous créez la facture depuis une réception validée :
1. Le système fait le **3-way matching** automatique :
   - Commande d'achat
   - Réception
   - Facture fournisseur
2. Les montants sont validés automatiquement

---

## Facturation et Paiements

### Vue d'ensemble

Le module **Ventes → Factures** gère la facturation client et les paiements.

### Factures

#### Créer une Facture depuis une Commande

1. Ouvrez la commande **"Livrée"**
2. Cliquez sur **"Créer une Facture"**
3. Le système pré-remplit :
   - Produits livrés
   - Quantités livrées
   - Prix
4. Ajustez si nécessaire
5. Cliquez sur **"Enregistrer"**

#### Valider une Facture

1. Ouvrez la facture en statut **"Brouillon"**
2. Vérifiez les informations
3. Cliquez sur **"Valider"**
4. Le système :
   - Génère le numéro de facture (FA-YYYY-XXXXX)
   - Change le statut à **"Validée"**
   - Génère le PDF automatiquement

#### Envoyer une Facture

1. Ouvrez la facture **"Validée"**
2. Cliquez sur **"Envoyer"**
3. La facture est envoyée par email au client
4. Le statut passe à **"Envoyée"**

### Paiements

#### Enregistrer un Paiement

1. Accédez à **Ventes → Paiements**
2. Cliquez sur **"Nouveau Paiement"**
3. Remplissez :
   - **Client** : Client concerné
   - **Montant** : Montant payé
   - **Méthode** : Espèces, Chèque, Virement, Carte
   - **Date** : Date du paiement
   - **Référence** : Numéro de chèque, référence virement, etc.
4. **Allocation automatique** :
   - Cochez **"Allocation automatique"**
   - Sélectionnez la stratégie : Plus anciennes, Plus récentes, Par montant
5. **Allocation manuelle** :
   - Décochez l'allocation automatique
   - Sélectionnez les factures à payer
6. Cliquez sur **"Enregistrer"**

#### Rapprochement Bancaire

1. Accédez à **Ventes → Paiements**
2. Cliquez sur **"Rapprochement"**
3. Importez votre relevé bancaire (CSV)
4. Le système propose des correspondances automatiques
5. Validez les correspondances
6. Cliquez sur **"Valider le Rapprochement"**

### Dashboard Paiements

Le dashboard paiements affiche :
- **Total à recevoir** : Montant total des factures non payées
- **Factures en retard** : Factures avec date d'échéance dépassée
- **Top 10 clients** : Clients avec le plus de créances
- **Échéancier** : Calendrier des échéances

---

## Rapports et Analyses

### Vue d'ensemble

Le module **Rapports** fournit des analyses détaillées de votre activité.

### Rapport de Ventes

1. Accédez à **Rapports → Rapport de Ventes**
2. Sélectionnez la **période** :
   - Date de début
   - Date de fin
   - Groupement : Jour, Semaine, Mois, Année
3. Cliquez sur **"Appliquer les Filtres"**

**Données affichées** :
- **Revenu total** : CA sur la période
- **Total commandes** : Nombre de commandes
- **Panier moyen** : CA moyen par commande
- **Tendance revenus** : Graphique d'évolution
- **Tendance commandes** : Graphique d'évolution
- **Top produits** : Produits les plus vendus
- **Top clients** : Clients avec le plus de CA

### Rapport de Marge

1. Accédez à **Rapports → Rapport de Marge**
2. Sélectionnez la **période**
3. Cliquez sur **"Appliquer les Filtres"**

**Données affichées** :
- **Marge totale** : Marge globale
- **Coût total** : Coût total
- **Marge %** : Pourcentage de marge
- **Détails par produit** : Marge par produit

### Rapport Stock

1. Accédez à **Rapports → Rapport de Stock**
2. Le rapport affiche :
   - **Valeur totale du stock** : Valeur globale
   - **Nombre de produits** : Produits en stock
   - **Détails par produit** : Produit, emplacement, quantités, valeur

### Rapport Clients

1. Accédez à **Rapports → Rapport Clients**
2. Sélectionnez la **période**
3. Cliquez sur **"Appliquer les Filtres"**

**Données affichées** :
- **Revenu total** : CA total
- **Total commandes** : Nombre de commandes
- **Panier moyen** : CA moyen
- **Détails par client** : CA, nombre de commandes, dernière commande

### Prévisions

1. Accédez à **Rapports → Prévisions**
2. Sélectionnez le type : **Prévisions Ventes** ou **Prévisions Stock**

**Prévisions Ventes** :
- Prédiction des ventes futures basée sur l'historique
- Tendance et intervalle de confiance

**Prévisions Stock** :
- Sélectionnez un produit
- Le système calcule :
  - Stock actuel
  - Demande prévue
  - Jours jusqu'à rupture
  - Quantité de réapprovisionnement recommandée

### Export des Rapports

Tous les rapports peuvent être exportés :
1. Dans le rapport, cliquez sur **"Exporter"**
2. Sélectionnez le format : **Excel** ou **PDF**
3. Le fichier est téléchargé

---

## Configuration

### Paramètres de l'Application

1. Accédez à **Paramètres → Application**
2. Configurez :

#### Informations Entreprise
- **Nom** : Nom de l'entreprise
- **Raison sociale** : Nom légal
- **SIRET** : Numéro SIRET
- **TVA** : Numéro de TVA
- **Adresse** : Adresse complète
- **Logo** : Logo de l'entreprise

#### Gestion du Stock
- **Mode** : Simple ou Avancé
  - **Simple** : Un seul entrepôt
  - **Avancé** : Multi-sites

#### Localisation
- **Langue par défaut** : Français, English, العربية
- **Devise** : EUR, USD, MAD, DZD, TND, etc.
- **Format de date** : Format d'affichage des dates

### Utilisateurs et Rôles

#### Rôles Disponibles

- **Admin** : Accès complet à tous les modules
- **Direction** : Accès aux rapports et dashboard
- **Commercial** : Accès aux ventes, clients, produits
- **Magasinier** : Accès au stock, réceptions, transferts
- **Comptable** : Accès aux factures et paiements

> **Note** : La gestion des utilisateurs est actuellement limitée. Contactez l'administrateur pour créer/modifier des utilisateurs.

---

## FAQ

### Questions Générales

**Q : Comment changer mon mot de passe ?**  
R : Contactez l'administrateur système. La fonctionnalité de changement de mot de passe sera disponible dans une future version.

**Q : Puis-je utiliser CommerceFlow sur mobile ?**  
R : L'interface est responsive et fonctionne sur tablette. Une application mobile dédiée est prévue.

**Q : Combien d'utilisateurs peuvent utiliser le système simultanément ?**  
R : Le système supporte 50+ utilisateurs simultanés. Pour plus d'utilisateurs, contactez le support.

### Questions Produits

**Q : Puis-je importer mes produits depuis Excel ?**  
R : Oui, utilisez la fonction **"Importer"** dans le module Produits. Le format est détaillé dans la section Import/Export.

**Q : Comment gérer les variantes (couleur, taille) ?**  
R : Créez d'abord le produit principal, puis ajoutez des variantes dans la fiche produit.

**Q : Les prix peuvent-ils changer automatiquement ?**  
R : Oui, via les listes de prix et les prix dégressifs. Les prix promotionnels peuvent avoir des dates de début/fin.

### Questions Stock

**Q : Quelle est la différence entre mode Simple et Avancé ?**  
R : Le mode Simple est pour un seul entrepôt. Le mode Avancé permet de gérer plusieurs sites avec transferts inter-sites.

**Q : Comment changer de mode ?**  
R : Allez dans **Paramètres → Application → Mode de gestion du stock**. Les données existantes sont conservées.

**Q : Le stock est-il mis à jour en temps réel ?**  
R : Oui, toutes les opérations (réceptions, ventes, transferts) mettent à jour le stock immédiatement.

### Questions Ventes

**Q : Puis-je créer une facture sans passer par une commande ?**  
R : Oui, créez directement une facture dans **Ventes → Factures → Nouvelle Facture**.

**Q : Comment annuler une commande ?**  
R : Ouvrez la commande et cliquez sur **"Annuler"**. Le stock réservé sera libéré automatiquement.

**Q : Les devis expirent-ils automatiquement ?**  
R : Oui, les devis expirent après 30 jours (configurable). Des relances automatiques sont envoyées.

### Questions Achats

**Q : Que faire si la quantité reçue est différente de la commande ?**  
R : Entrez la quantité réellement reçue lors de la réception. Si l'écart est > 10%, une validation est requise.

**Q : Comment gérer les retours fournisseurs ?**  
R : Créez un mouvement de stock de type **"Ajustement"** avec quantité négative.

---

## Dépannage

### Problèmes de Connexion

**Problème** : "Nom d'utilisateur ou mot de passe invalide"  
**Solution** :
1. Vérifiez que vous utilisez les bons identifiants
2. Vérifiez que le CAPS LOCK n'est pas activé
3. Contactez l'administrateur pour réinitialiser le mot de passe

**Problème** : "Session expirée"  
**Solution** : Reconnectez-vous. Les sessions expirent après 24h d'inactivité.

### Problèmes de Stock

**Problème** : "Stock insuffisant" lors de la confirmation d'une commande  
**Solution** :
1. Vérifiez le stock disponible dans **Inventaire → Stock**
2. Réceptionnez les commandes d'achat en attente
3. Ajustez le stock si nécessaire (mouvement d'ajustement)

**Problème** : "Stock négatif"  
**Solution** :
1. Vérifiez les mouvements de stock dans **Inventaire → Mouvements**
2. Créez un ajustement pour corriger
3. Contactez le support si le problème persiste

### Problèmes de Facturation

**Problème** : "Impossible de créer une facture"  
**Solution** :
1. Vérifiez que la commande est en statut **"Livrée"**
2. Vérifiez que des quantités ont été livrées (quantité_delivered > 0)
3. Contactez le support si le problème persiste

**Problème** : "Numéro de facture incorrect"  
**Solution** : Les numéros de facture suivent le format FA-YYYY-XXXXX et sont générés automatiquement. Contactez le support si vous voyez un doublon.

### Problèmes d'Affichage

**Problème** : "L'interface est en anglais alors que j'ai sélectionné français"  
**Solution** :
1. Vérifiez votre langue dans la barre supérieure
2. Videz le cache du navigateur (Ctrl+F5)
3. Vérifiez les paramètres de langue dans **Paramètres → Application**

**Problème** : "Les graphiques ne s'affichent pas"  
**Solution** :
1. Vérifiez votre connexion internet (Chart.js est chargé depuis CDN)
2. Vérifiez que JavaScript est activé dans votre navigateur
3. Essayez un autre navigateur

### Problèmes de Performance

**Problème** : "L'application est lente"  
**Solution** :
1. Vérifiez votre connexion internet
2. Fermez les onglets inutiles
3. Videz le cache du navigateur
4. Contactez le support si le problème persiste

### Support

Pour toute question ou problème non résolu :
- **Email** : support@commerceflow.com
- **Téléphone** : +33 X XX XX XX XX
- **Horaires** : Lundi-Vendredi, 9h-18h

---

## Annexes

### Codes de Statut

#### Commandes
- **Brouillon** : Commande en cours de création
- **Confirmée** : Commande validée, stock réservé
- **En préparation** : Commande en cours de préparation
- **Prête** : Commande prête à être expédiée
- **Expédiée** : Commande expédiée, stock débité
- **Livrée** : Commande livrée au client
- **Annulée** : Commande annulée

#### Factures
- **Brouillon** : Facture en cours de création
- **Validée** : Facture validée, numéro attribué
- **Envoyée** : Facture envoyée au client
- **Partiellement payée** : Facture partiellement payée
- **Payée** : Facture entièrement payée
- **En retard** : Facture avec date d'échéance dépassée

#### Devis
- **Brouillon** : Devis en cours de création
- **Envoyé** : Devis envoyé au client
- **Accepté** : Devis accepté par le client
- **Refusé** : Devis refusé par le client
- **Expiré** : Devis expiré (30 jours)

### Raccourcis Clavier

- **Ctrl + S** : Enregistrer (dans les formulaires)
- **Ctrl + F** : Rechercher (dans les listes)
- **Echap** : Fermer les modales

### Formats de Fichiers Supportés

- **Import** : Excel (.xlsx, .xls), CSV (.csv)
- **Export** : Excel (.xlsx), PDF (.pdf)
- **Images** : JPG, PNG, GIF (pour logos et images produits)

---

**Fin du Guide Utilisateur**

Pour toute question, consultez la FAQ ou contactez le support.

