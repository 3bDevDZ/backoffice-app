# Bonnes Pratiques Pharmaceutiques - Guide de Configuration Flexible

**Version**: 1.0  
**Date**: 2025-11-21  
**Contexte**: Application flexible pour gestion pharmaceutique

---

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Standards Réglementaires](#standards-réglementaires)
3. [Gestion Flexible des Spécifications Produits](#gestion-flexible-des-spécifications-produits)
4. [Gestion par Lots et Traçabilité](#gestion-par-lots-et-traçabilité)
5. [Gestion des Dates d'Expiration](#gestion-des-dates-dexpiration)
6. [Configuration Flexible par Type d'Établissement](#configuration-flexible-par-type-détablissement)
7. [Sérialisation et Agrégation](#sérialisation-et-agrégation)
8. [Conditions de Stockage](#conditions-de-stockage)
9. [Alertes et Rappels](#alertes-et-rappels)
10. [Architecture Recommandée](#architecture-recommandée)

---

## Vue d'ensemble

Dans le contexte pharmaceutique, l'application doit être **ultra-flexible** pour s'adapter à :
- Différents types d'établissements (pharmacies, laboratoires, grossistes)
- Différentes réglementations (France, Europe, International)
- Différents types de produits (médicaments, dispositifs médicaux, produits de santé)
- Évolutions réglementaires fréquentes

### Principes Clés

1. **Flexibilité maximale** : Configuration sans modification de code
2. **Traçabilité complète** : Chaque mouvement doit être tracé
3. **Conformité réglementaire** : Respect des BPF, BPD, ISO
4. **Sécurité** : Protection des données sensibles
5. **Auditabilité** : Historique complet de toutes les opérations

---

## Standards Réglementaires

### Bonnes Pratiques de Fabrication (BPF / GMP)

**Exigences clés** :
- Documentation rigoureuse de tous les processus
- Contrôle qualité à chaque étape
- Traçabilité complète des lots
- Validation des processus critiques
- Formation continue du personnel

**Impact sur l'application** :
- Journal d'audit complet (qui, quoi, quand, pourquoi)
- Validation des données à chaque étape
- Blocage des opérations non conformes
- Rapports de conformité

### Bonnes Pratiques de Distribution (BPD / GDP)

**Exigences clés** :
- Conditions de stockage appropriées (température, humidité)
- Traçabilité du transport
- Sécurité de la chaîne d'approvisionnement
- Gestion des retours et rappels

**Impact sur l'application** :
- Enregistrement des conditions de stockage
- Suivi des transferts entre sites
- Gestion des rappels de produits
- Alertes sur conditions de stockage

### ISO 15378 (Emballages Primaires)

**Exigences clés** :
- Traçabilité des lots d'emballage
- Maîtrise des conditions environnementales
- Validation des processus critiques

**Impact sur l'application** :
- Gestion des lots d'emballage
- Enregistrement des conditions environnementales
- Historique de validation

---

## Gestion Flexible des Spécifications Produits

### Approche JSONB dans PostgreSQL

**Avantages** :
- Flexibilité totale sans migration de schéma
- Indexation possible sur les clés JSONB
- Recherche avancée sur les valeurs
- Adaptabilité aux évolutions réglementaires

### Structure Recommandée

#### Spécifications Standard (Tous Produits)

```json
{
  "regulatory": {
    "atc_code": "A10BB01",
    "cis_code": "12345678",
    "amm_number": "AMM-12345",
    "pharmaceutical_form": "Comprimé",
    "dosage": "500mg",
    "active_ingredient": "Metformine",
    "regulatory_status": "Autorisé",
    "marketing_authorization_holder": "Laboratoire XYZ"
  },
  "storage": {
    "temperature_min": 2,
    "temperature_max": 8,
    "humidity_max": 60,
    "light_sensitive": true,
    "storage_conditions": "Conserver au réfrigérateur (2°C - 8°C)"
  },
  "safety": {
    "controlled_substance": false,
    "narcotic": false,
    "psychotropic": false,
    "prescription_required": true,
    "pharmacovigilance": true
  }
}
```

#### Spécifications Personnalisées (Par Type de Produit)

**Médicaments** :
```json
{
  "medication": {
    "therapeutic_class": "Antidiabétique",
    "indication": "Diabète de type 2",
    "contraindications": ["Insuffisance rénale", "Grossesse"],
    "side_effects": ["Nausées", "Diarrhée"],
    "interactions": ["Alcool", "Contraste iodé"],
    "pregnancy_category": "B",
    "breastfeeding_compatible": false
  }
}
```

**Dispositifs Médicaux** :
```json
{
  "medical_device": {
    "ce_marking": "CE-1234",
    "class": "IIa",
    "sterile": true,
    "single_use": true,
    "implantable": false
  }
}
```

**Produits de Santé** :
```json
{
  "health_product": {
    "category": "Complément alimentaire",
    "composition": "Vitamine D, Calcium",
    "target_population": "Personnes âgées"
  }
}
```

### Configuration Flexible par Type d'Établissement

**Table de Configuration** : `product_specification_templates`

| Champ | Type | Description |
|-------|------|-------------|
| `id` | INT | Identifiant unique |
| `establishment_type` | VARCHAR | Type d'établissement (pharmacy, lab, wholesaler) |
| `product_category` | VARCHAR | Catégorie de produit |
| `specification_schema` | JSONB | Schéma JSON des champs requis |
| `validation_rules` | JSONB | Règles de validation |
| `is_active` | BOOLEAN | Template actif |

**Exemple de Schéma** :
```json
{
  "required_fields": ["regulatory.atc_code", "regulatory.cis_code"],
  "optional_fields": ["medication.indication", "medication.contraindications"],
  "validation": {
    "regulatory.cis_code": {
      "pattern": "^[0-9]{8}$",
      "message": "Le code CIS doit contenir 8 chiffres"
    },
    "storage.temperature_min": {
      "type": "number",
      "min": -20,
      "max": 25
    }
  }
}
```

### Interface de Configuration

**Pour l'Administrateur** :
1. Accéder à **Paramètres → Configuration Produits**
2. Sélectionner le type d'établissement
3. Définir les champs requis/optionnels
4. Configurer les règles de validation
5. Activer le template

**Résultat** : Les formulaires produits s'adaptent automatiquement selon le type d'établissement.

---

## Gestion par Lots et Traçabilité

### Structure de Données Recommandée

#### Table `stock_lots`

| Colonne | Type | Description | Obligatoire |
|---------|------|-------------|-------------|
| `id` | INT | Identifiant unique | Oui |
| `product_id` | INT | Produit | Oui |
| `location_id` | INT | Emplacement | Oui |
| `lot_number` | VARCHAR(50) | Numéro de lot (unique) | Oui |
| `batch_number` | VARCHAR(50) | Numéro de batch | Optionnel |
| `serial_number` | VARCHAR(100) | Numéro de série (sérialisation) | Optionnel |
| `manufacturing_date` | DATE | Date de fabrication | Oui |
| `expiration_date` | DATE | Date d'expiration | Oui |
| `quantity` | DECIMAL | Quantité totale | Oui |
| `reserved_quantity` | DECIMAL | Quantité réservée | Oui |
| `available_quantity` | DECIMAL | Quantité disponible | Oui |
| `cost` | DECIMAL | Coût unitaire | Oui |
| `supplier_id` | INT | Fournisseur | Optionnel |
| `purchase_order_id` | INT | Commande d'achat | Optionnel |
| `manufacturer_lot` | VARCHAR(50) | Lot fabricant | Optionnel |
| `country_of_origin` | VARCHAR(3) | Pays d'origine (ISO) | Optionnel |
| `certificate_of_analysis` | TEXT | Certificat d'analyse | Optionnel |
| `quarantine_status` | VARCHAR(20) | Statut quarantaine | Optionnel |
| `quarantine_reason` | TEXT | Raison quarantaine | Optionnel |
| `released_date` | DATE | Date de libération | Optionnel |
| `released_by` | INT | Libéré par (user_id) | Optionnel |
| `created_at` | TIMESTAMP | Date de création | Oui |
| `updated_at` | TIMESTAMP | Date de mise à jour | Oui |

#### Table `stock_movements` (Extension)

Ajouter les colonnes :
- `lot_id` : INT (Foreign Key vers `stock_lots`)
- `serial_number` : VARCHAR(100) (pour sérialisation)
- `movement_reason` : VARCHAR(100) (raison du mouvement)
- `validated_by` : INT (user_id qui a validé)
- `validated_at` : TIMESTAMP (date de validation)

### Numérotation des Lots

#### Configuration Flexible

**Table** : `lot_numbering_config`

| Champ | Type | Description |
|-------|------|-------------|
| `establishment_id` | INT | Établissement (NULL = global) |
| `product_category` | VARCHAR | Catégorie produit |
| `format` | VARCHAR | Format de numérotation |
| `prefix` | VARCHAR | Préfixe (ex: "LOT") |
| `include_date` | BOOLEAN | Inclure la date |
| `include_sequence` | BOOLEAN | Inclure séquence |
| `sequence_length` | INT | Longueur séquence |

**Exemples de Formats** :
- `LOT-YYYY-XXXXX` : LOT-2025-00001
- `YYYYMMDD-XXX` : 20251121-001
- `PROD-YY-XXXX` : PROD-25-0001
- `MANUFACTURER-LOT` : Utiliser le numéro du fabricant

### Traçabilité Complète

#### Historique d'un Lot

Pour chaque lot, enregistrer :
1. **Réception** :
   - Date et heure
   - Fournisseur
   - Quantité reçue
   - Conditions de réception (température, etc.)
   - Certificat d'analyse
   - Validé par (user_id)

2. **Stockage** :
   - Emplacement
   - Conditions de stockage
   - Vérifications périodiques

3. **Quarantaine/Libération** :
   - Date de mise en quarantaine
   - Raison
   - Date de libération
   - Libéré par (user_id)

4. **Sortie** :
   - Date et heure
   - Destination (client, transfert, destruction)
   - Quantité
   - Validé par (user_id)

5. **Rappel** :
   - Date de rappel
   - Raison
   - Quantité rappelée
   - Statut (en cours, terminé)

#### Table `lot_history`

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | INT | Identifiant unique |
| `lot_id` | INT | Lot concerné |
| `event_type` | VARCHAR | Type d'événement |
| `event_data` | JSONB | Données de l'événement |
| `user_id` | INT | Utilisateur |
| `timestamp` | TIMESTAMP | Date/heure |
| `ip_address` | VARCHAR | Adresse IP |
| `device_info` | JSONB | Informations appareil |

---

## Gestion des Dates d'Expiration

### Méthode FEFO (First Expired, First Out)

**Obligatoire en pharmaceutique** : Toujours sortir les produits les plus proches de l'expiration en premier.

### Algorithme de Sortie

1. **Sélectionner les lots disponibles** pour le produit
2. **Trier par date d'expiration croissante** (plus proche en premier)
3. **Débiter les lots dans l'ordre** jusqu'à satisfaction de la quantité demandée
4. **Alerter si** :
   - Lot expirant dans < 30 jours
   - Lot expirant dans < 7 jours
   - Lot expiré

### Alertes d'Expiration

#### Configuration Flexible

**Table** : `expiration_alert_config`

| Champ | Type | Description |
|-------|------|-------------|
| `establishment_id` | INT | Établissement |
| `alert_days_before` | INT[] | Jours avant expiration (ex: [7, 30, 60]) |
| `alert_frequency` | VARCHAR | Fréquence (daily, weekly) |
| `notification_method` | VARCHAR[] | Méthodes (email, sms, in_app) |
| `recipients` | JSONB | Destinataires |

#### Types d'Alertes

1. **Alerte Préventive** (60 jours avant) : Information
2. **Alerte Attention** (30 jours avant) : Action recommandée
3. **Alerte Urgente** (7 jours avant) : Action immédiate
4. **Alerte Expiré** : Blocage automatique des sorties

### Blocage Automatique

**Règles configurables** :
- Bloquer les sorties de lots expirés : Oui/Non
- Autoriser sortie avec validation : Oui/Non
- Délai de grâce après expiration : X jours

---

## Configuration Flexible par Type d'Établissement

### Types d'Établissements

1. **Pharmacie d'Officine**
   - Gestion par lots : Oui
   - Sérialisation : Optionnel
   - Quarantaine : Optionnel
   - Conditions de stockage : Basiques

2. **Pharmacie Hospitalière**
   - Gestion par lots : Oui (obligatoire)
   - Sérialisation : Recommandé
   - Quarantaine : Oui
   - Conditions de stockage : Strictes

3. **Grossiste-Répartiteur**
   - Gestion par lots : Oui (obligatoire)
   - Sérialisation : Oui (obligatoire)
   - Quarantaine : Oui
   - Conditions de stockage : Très strictes
   - Agrégation : Oui

4. **Laboratoire Pharmaceutique**
   - Gestion par lots : Oui (obligatoire)
   - Sérialisation : Oui (obligatoire)
   - Quarantaine : Oui (obligatoire)
   - Conditions de stockage : Très strictes
   - Certificats d'analyse : Obligatoires

### Table de Configuration

**Table** : `establishment_config`

| Champ | Type | Description |
|-------|------|-------------|
| `establishment_type` | VARCHAR | Type d'établissement |
| `lot_management_required` | BOOLEAN | Lots obligatoires |
| `serialization_required` | BOOLEAN | Sérialisation obligatoire |
| `quarantine_required` | BOOLEAN | Quarantaine obligatoire |
| `temperature_monitoring` | BOOLEAN | Monitoring température |
| `coa_required` | BOOLEAN | Certificat d'analyse requis |
| `fefo_enforced` | BOOLEAN | FEFO obligatoire |
| `expiration_blocking` | BOOLEAN | Blocage lots expirés |
| `custom_fields` | JSONB | Champs personnalisés |

### Activation par Établissement

Lors de la configuration d'un établissement :
1. Sélectionner le type d'établissement
2. Le système charge la configuration par défaut
3. Personnaliser si nécessaire
4. Valider

**Résultat** : L'interface et les workflows s'adaptent automatiquement.

---

## Sérialisation et Agrégation

### Sérialisation (Numéro de Série Unique)

**Obligatoire pour** :
- Médicaments soumis à sérialisation (Europe, USA)
- Dispositifs médicaux de classe III
- Produits à haut risque

**Structure** :
- **Table** : `product_serials`
- **Relation** : Un lot peut avoir plusieurs numéros de série
- **Format** : GTIN + Numéro de série (GS1 standard)

### Agrégation (Hiérarchie d'Emballage)

**Niveaux** :
1. **Unité** : Boîte individuelle
2. **Carton** : Contient N unités
3. **Palette** : Contient N cartons

**Structure** :
- **Table** : `product_aggregation`
- **Relation parent-enfant** : Unité → Carton → Palette
- **Traçabilité** : Remonter/descendre la hiérarchie

### Configuration

**Table** : `serialization_config`

| Champ | Type | Description |
|-------|------|-------------|
| `product_id` | INT | Produit |
| `serialization_required` | BOOLEAN | Sérialisation requise |
| `aggregation_required` | BOOLEAN | Agrégation requise |
| `gtin` | VARCHAR | GTIN du produit |
| `serial_format` | VARCHAR | Format numéro de série |
| `aggregation_levels` | JSONB | Niveaux d'agrégation |

---

## Conditions de Stockage

### Enregistrement des Conditions

**Table** : `storage_conditions_log`

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | INT | Identifiant unique |
| `location_id` | INT | Emplacement |
| `temperature` | DECIMAL | Température enregistrée |
| `humidity` | DECIMAL | Humidité enregistrée |
| `timestamp` | TIMESTAMP | Date/heure |
| `sensor_id` | VARCHAR | ID capteur (si automatique) |
| `alert_triggered` | BOOLEAN | Alerte déclenchée |

### Alertes sur Conditions

**Configuration** :
- Température min/max par produit
- Humidité max par produit
- Délai d'alerte (dépassement > X minutes)

**Actions automatiques** :
- Alerte immédiate si dépassement
- Blocage des sorties si conditions non conformes
- Quarantaine automatique si dépassement prolongé

---

## Alertes et Rappels

### Types d'Alertes

1. **Expiration** : Lots expirant bientôt
2. **Conditions de stockage** : Dépassement température/humidité
3. **Quarantaine** : Lots en quarantaine
4. **Stock minimum** : Rupture de stock
5. **Rappel produit** : Rappel réglementaire

### Configuration Flexible

**Table** : `alert_config`

| Champ | Type | Description |
|-------|------|-------------|
| `alert_type` | VARCHAR | Type d'alerte |
| `establishment_id` | INT | Établissement |
| `thresholds` | JSONB | Seuils configurables |
| `notification_methods` | JSONB | Méthodes de notification |
| `recipients` | JSONB | Destinataires |
| `frequency` | VARCHAR | Fréquence |

### Rappels de Produits

**Table** : `product_recalls`

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | INT | Identifiant unique |
| `product_id` | INT | Produit |
| `lot_numbers` | VARCHAR[] | Numéros de lots concernés |
| `recall_reason` | TEXT | Raison du rappel |
| `recall_date` | DATE | Date du rappel |
| `status` | VARCHAR | Statut (active, closed) |
| `affected_quantity` | DECIMAL | Quantité concernée |
| `recalled_quantity` | DECIMAL | Quantité rappelée |

**Workflow** :
1. Créer un rappel
2. Identifier les lots concernés
3. Bloquer automatiquement les sorties
4. Notifier les clients
5. Suivre les retours
6. Clôturer le rappel

---

## Architecture Recommandée

### Tables Principales

1. **`products`** : Produits avec `additional_specs` (JSONB)
2. **`stock_lots`** : Gestion des lots
3. **`product_serials`** : Sérialisation
4. **`product_aggregation`** : Agrégation
5. **`storage_conditions_log`** : Conditions de stockage
6. **`lot_history`** : Historique complet
7. **`product_recalls`** : Rappels
8. **`establishment_config`** : Configuration par établissement
9. **`product_specification_templates`** : Templates de spécifications
10. **`alert_config`** : Configuration des alertes

### Index Recommandés

```sql
-- Lots
CREATE INDEX idx_stock_lots_product_expiration ON stock_lots(product_id, expiration_date);
CREATE INDEX idx_stock_lots_lot_number ON stock_lots(lot_number);
CREATE INDEX idx_stock_lots_location ON stock_lots(location_id);

-- Spécifications produits (JSONB)
CREATE INDEX idx_products_specs_gin ON products USING GIN(additional_specs);
CREATE INDEX idx_products_specs_atc ON products((additional_specs->>'regulatory'->>'atc_code'));

-- Conditions de stockage
CREATE INDEX idx_storage_conditions_location_time ON storage_conditions_log(location_id, timestamp);

-- Historique
CREATE INDEX idx_lot_history_lot ON lot_history(lot_id, timestamp);
```

### Workflows Configurables

**Table** : `workflow_config`

| Champ | Type | Description |
|-------|------|-------------|
| `workflow_type` | VARCHAR | Type de workflow |
| `establishment_type` | VARCHAR | Type d'établissement |
| `steps` | JSONB | Étapes du workflow |
| `validation_rules` | JSONB | Règles de validation |
| `approval_required` | BOOLEAN | Approbation requise |

**Exemple - Réception** :
```json
{
  "steps": [
    {"name": "Saisie", "required": true},
    {"name": "Vérification lot", "required": true},
    {"name": "Vérification certificat", "required": true, "conditional": "coa_required"},
    {"name": "Contrôle température", "required": true, "conditional": "temperature_monitoring"},
    {"name": "Mise en quarantaine", "required": true, "conditional": "quarantine_required"},
    {"name": "Validation", "required": true, "approval": true}
  ]
}
```

---

## Implémentation Progressive

### Phase 1 : Fondations (2 semaines)
- Ajouter colonne `additional_specs` (JSONB) à `products`
- Créer table `stock_lots`
- Créer table `establishment_config`
- Créer index GIN sur JSONB

### Phase 2 : Lots et Expiration (2 semaines)
- Implémenter gestion par lots
- Implémenter FEFO
- Système d'alertes expiration
- Blocage lots expirés

### Phase 3 : Traçabilité (2 semaines)
- Table `lot_history`
- Enregistrement complet des mouvements
- Rapports de traçabilité
- Gestion des rappels

### Phase 4 : Conditions de Stockage (1 semaine)
- Table `storage_conditions_log`
- Alertes sur conditions
- Blocage si non conforme

### Phase 5 : Sérialisation (2 semaines)
- Table `product_serials`
- Agrégation
- Conformité GS1

### Phase 6 : Configuration Flexible (1 semaine)
- Templates de spécifications
- Configuration par établissement
- Workflows configurables

---

## Checklist de Conformité

### BPF/GMP
- [ ] Traçabilité complète des lots
- [ ] Journal d'audit complet
- [ ] Validation des processus
- [ ] Contrôle qualité à chaque étape
- [ ] Documentation rigoureuse

### BPD/GDP
- [ ] Conditions de stockage enregistrées
- [ ] Traçabilité du transport
- [ ] Gestion des rappels
- [ ] Sécurité de la chaîne

### ISO 15378
- [ ] Traçabilité emballages
- [ ] Conditions environnementales
- [ ] Validation processus

---

## Support

Pour toute question sur les bonnes pratiques pharmaceutiques :
- **Email** : pharma-support@commerceflow.com
- **Documentation réglementaire** : https://ansm.sante.fr
- **Standards ISO** : https://www.iso.org

---

**Fin du Guide des Bonnes Pratiques Pharmaceutiques**

