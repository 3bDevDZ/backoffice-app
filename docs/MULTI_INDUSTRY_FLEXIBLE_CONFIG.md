# Configuration Flexible Multi-Industries

**Version**: 1.0  
**Date**: 2025-11-21  
**Objectif**: Rendre l'application adaptable à différents types de commerce

---

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Types de Commerce Supportés](#types-de-commerce-supportés)
3. [Architecture de Configuration Flexible](#architecture-de-configuration-flexible)
4. [Configuration par Secteur](#configuration-par-secteur)
5. [Modules Activables/Désactivables](#modules-activablesdésactivables)
6. [Spécifications Produits Flexibles](#spécifications-produits-flexibles)
7. [Gestion Stock Adaptative](#gestion-stock-adaptative)
8. [Workflows Configurables](#workflows-configurables)
9. [Règles Métier Configurables](#règles-métier-configurables)
10. [Implémentation Progressive](#implémentation-progressive)

---

## Vue d'ensemble

### Objectif

Rendre CommerceFlow **ultra-flexible** pour s'adapter à différents secteurs d'activité sans modification de code, uniquement par configuration.

### Principe Fondamental

**"Configuration over Code"** : Toutes les différences entre secteurs sont gérées par des tables de configuration, pas par du code conditionnel.

### Secteurs Ciblés

1. **Pharmaceutique** : Lots obligatoires, traçabilité complète, FEFO, sérialisation
2. **Électronique** : Numéros de série, garanties, compatibilité
3. **Informatique** : Licences, versions, compatibilité matériel/logiciel
4. **Quincaillerie** : Gestion simple, pas de lots, FIFO basique

---

## Types de Commerce Supportés

### 1. Grossiste Équipement Électronique

**Caractéristiques** :
- Numéros de série uniques par produit
- Garanties (1 an, 2 ans, etc.)
- Compatibilité entre produits (ex: chargeur compatible avec plusieurs modèles)
- Gestion des retours sous garantie
- Traçabilité des réparations

**Exigences** :
- Lots : Optionnel (pour certains produits)
- Sérialisation : Oui (obligatoire)
- Expiration : Non
- Quarantaine : Non
- Conditions stockage : Basiques (température normale)

### 2. Informatique

**Caractéristiques** :
- Licences logicielles (perpetual, subscription)
- Versions de logiciels
- Compatibilité matériel/logiciel
- Clés d'activation
- Support technique par produit

**Exigences** :
- Lots : Non
- Sérialisation : Oui (clés de licence)
- Expiration : Oui (pour licences avec date d'expiration)
- Quarantaine : Non
- Conditions stockage : Basiques

### 3. Quincaillerie

**Caractéristiques** :
- Gestion simple, pas de traçabilité complexe
- Pas de lots (sauf exceptions)
- FIFO basique suffisant
- Gestion des références multiples
- Compatibilité entre produits (vis, écrous, etc.)

**Exigences** :
- Lots : Non (sauf produits spécifiques)
- Sérialisation : Non
- Expiration : Non (sauf produits chimiques)
- Quarantaine : Non
- Conditions stockage : Basiques

### 4. Pharmaceutique

**Caractéristiques** :
- Lots obligatoires
- Traçabilité complète
- FEFO obligatoire
- Sérialisation (selon réglementation)
- Conditions de stockage strictes
- Certificats d'analyse

**Exigences** :
- Lots : Oui (obligatoire)
- Sérialisation : Oui (selon produit)
- Expiration : Oui (obligatoire)
- Quarantaine : Oui (selon établissement)
- Conditions stockage : Strictes (température, humidité)

---

## Architecture de Configuration Flexible

### Table Principale : `industry_config`

**Structure** :

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | INT | Identifiant unique |
| `industry_type` | VARCHAR(50) | Type d'industrie (pharmaceutical, electronics, it, hardware) |
| `industry_name` | VARCHAR(100) | Nom lisible |
| `description` | TEXT | Description |
| `features` | JSONB | Fonctionnalités activées |
| `stock_management` | JSONB | Configuration gestion stock |
| `product_specs_template` | JSONB | Template spécifications produits |
| `workflow_config` | JSONB | Configuration workflows |
| `business_rules` | JSONB | Règles métier |
| `is_active` | BOOLEAN | Configuration active |
| `created_at` | TIMESTAMP | Date création |
| `updated_at` | TIMESTAMP | Date mise à jour |

### Table : `establishment_industry`

**Lien entre établissement et industrie** :

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | INT | Identifiant unique |
| `establishment_id` | INT | Établissement (ou NULL pour global) |
| `industry_type` | VARCHAR(50) | Type d'industrie |
| `config_overrides` | JSONB | Surcharges de configuration |
| `is_active` | BOOLEAN | Active |

**Principe** :
- Un établissement peut avoir UNE industrie principale
- Possibilité de surcharger la configuration globale
- Configuration par défaut si non spécifiée

---

## Configuration par Secteur

### Structure JSONB `features`

**Exemple pour Pharmaceutique** :
```json
{
  "lot_management": {
    "enabled": true,
    "required": true,
    "quarantine": true,
    "coa_required": true
  },
  "serialization": {
    "enabled": true,
    "required": false,
    "aggregation": false
  },
  "expiration_management": {
    "enabled": true,
    "required": true,
    "fefo_enforced": true,
    "block_expired": true
  },
  "storage_conditions": {
    "enabled": true,
    "temperature_monitoring": true,
    "humidity_monitoring": true,
    "alert_on_deviation": true
  },
  "warranty_management": {
    "enabled": false
  },
  "license_management": {
    "enabled": false
  },
  "compatibility_management": {
    "enabled": false
  }
}
```

**Exemple pour Électronique** :
```json
{
  "lot_management": {
    "enabled": false,
    "required": false
  },
  "serialization": {
    "enabled": true,
    "required": true,
    "aggregation": false
  },
  "expiration_management": {
    "enabled": false,
    "required": false
  },
  "storage_conditions": {
    "enabled": false
  },
  "warranty_management": {
    "enabled": true,
    "warranty_periods": [12, 24, 36],
    "warranty_unit": "months"
  },
  "license_management": {
    "enabled": false
  },
  "compatibility_management": {
    "enabled": true,
    "compatibility_types": ["charger", "cable", "accessory"]
  }
}
```

**Exemple pour Informatique** :
```json
{
  "lot_management": {
    "enabled": false,
    "required": false
  },
  "serialization": {
    "enabled": true,
    "required": true,
    "aggregation": false
  },
  "expiration_management": {
    "enabled": true,
    "required": false,
    "fefo_enforced": false,
    "block_expired": false
  },
  "storage_conditions": {
    "enabled": false
  },
  "warranty_management": {
    "enabled": true
  },
  "license_management": {
    "enabled": true,
    "license_types": ["perpetual", "subscription", "trial"],
    "activation_keys": true,
    "version_tracking": true
  },
  "compatibility_management": {
    "enabled": true,
    "compatibility_types": ["hardware", "software", "os"]
  }
}
```

**Exemple pour Quincaillerie** :
```json
{
  "lot_management": {
    "enabled": false,
    "required": false
  },
  "serialization": {
    "enabled": false,
    "required": false
  },
  "expiration_management": {
    "enabled": false,
    "required": false
  },
  "storage_conditions": {
    "enabled": false
  },
  "warranty_management": {
    "enabled": false
  },
  "license_management": {
    "enabled": false
  },
  "compatibility_management": {
    "enabled": true,
    "compatibility_types": ["thread", "size", "material"]
  }
}
```

### Structure JSONB `stock_management`

**Exemple** :
```json
{
  "mode": "simple|advanced",
  "lot_required": true|false,
  "fifo_method": "FIFO|FEFO|LIFO",
  "serialization_required": true|false,
  "expiration_tracking": true|false,
  "quarantine_enabled": true|false,
  "temperature_monitoring": true|false,
  "multi_location": true|false,
  "transfer_between_locations": true|false
}
```

---

## Modules Activables/Désactivables

### Table : `module_config`

**Structure** :

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | INT | Identifiant unique |
| `module_name` | VARCHAR(50) | Nom du module |
| `industry_type` | VARCHAR(50) | Type d'industrie (NULL = tous) |
| `enabled` | BOOLEAN | Module activé |
| `required` | BOOLEAN | Module obligatoire |
| `config` | JSONB | Configuration spécifique |

### Modules Disponibles

1. **`lot_management`** : Gestion par lots
2. **`serialization`** : Sérialisation
3. **`expiration_tracking`** : Suivi expiration
4. **`quarantine`** : Quarantaine
5. **`storage_conditions`** : Conditions stockage
6. **`warranty`** : Gestion garanties
7. **`licenses`** : Gestion licences
8. **`compatibility`** : Compatibilité produits
9. **`certificates`** : Certificats (analyse, conformité)
10. **`recalls`** : Rappels produits

### Activation par Industrie

**Exemple de Requête** :
```sql
-- Modules activés pour pharmaceutique
SELECT module_name, enabled, required 
FROM module_config 
WHERE industry_type = 'pharmaceutical' AND enabled = true;
```

**Résultat** :
- `lot_management` : enabled=true, required=true
- `serialization` : enabled=true, required=false
- `expiration_tracking` : enabled=true, required=true
- `quarantine` : enabled=true, required=true
- `storage_conditions` : enabled=true, required=true
- `certificates` : enabled=true, required=true
- `recalls` : enabled=true, required=true

---

## Spécifications Produits Flexibles

### Table : `product_specification_templates`

**Structure** :

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | INT | Identifiant unique |
| `industry_type` | VARCHAR(50) | Type d'industrie |
| `product_category` | VARCHAR(50) | Catégorie produit (NULL = toutes) |
| `template_name` | VARCHAR(100) | Nom du template |
| `specification_schema` | JSONB | Schéma JSON des champs |
| `validation_rules` | JSONB | Règles de validation |
| `is_default` | BOOLEAN | Template par défaut |

### Exemples de Schémas

#### Pharmaceutique
```json
{
  "required_fields": [
    "regulatory.atc_code",
    "regulatory.cis_code",
    "storage.temperature_min",
    "storage.temperature_max"
  ],
  "optional_fields": [
    "regulatory.amm_number",
    "medication.indication",
    "medication.contraindications"
  ],
  "field_types": {
    "regulatory.atc_code": "string",
    "regulatory.cis_code": "string",
    "storage.temperature_min": "number",
    "storage.temperature_max": "number"
  }
}
```

#### Électronique
```json
{
  "required_fields": [
    "electronics.model",
    "electronics.brand",
    "warranty.duration"
  ],
  "optional_fields": [
    "electronics.power_consumption",
    "electronics.dimensions",
    "compatibility.compatible_with"
  ],
  "field_types": {
    "electronics.model": "string",
    "electronics.brand": "string",
    "warranty.duration": "number"
  }
}
```

#### Informatique
```json
{
  "required_fields": [
    "software.name",
    "software.version",
    "license.type"
  ],
  "optional_fields": [
    "software.publisher",
    "license.expiration_date",
    "compatibility.min_os",
    "compatibility.min_ram"
  ],
  "field_types": {
    "software.name": "string",
    "software.version": "string",
    "license.type": "enum:perpetual,subscription,trial"
  }
}
```

#### Quincaillerie
```json
{
  "required_fields": [
    "hardware.material",
    "hardware.size"
  ],
  "optional_fields": [
    "hardware.color",
    "hardware.weight",
    "compatibility.thread_size"
  ],
  "field_types": {
    "hardware.material": "string",
    "hardware.size": "string"
  }
}
```

### Utilisation dans `products.additional_specs`

Le champ `additional_specs` (JSONB) dans la table `products` stocke les spécifications selon le template de l'industrie.

**Exemple - Produit Électronique** :
```json
{
  "electronics": {
    "model": "iPhone 15 Pro",
    "brand": "Apple",
    "power_consumption": "20W",
    "dimensions": {
      "length": 15.9,
      "width": 7.6,
      "height": 0.83,
      "unit": "cm"
    }
  },
  "warranty": {
    "duration": 12,
    "unit": "months",
    "type": "manufacturer"
  },
  "compatibility": {
    "compatible_with": ["iPhone 14", "iPhone 13"],
    "charger_type": "USB-C"
  }
}
```

---

## Gestion Stock Adaptative

### Configuration par Industrie

**Table** : `stock_config` (ou dans `industry_config.stock_management`)

#### Pharmaceutique
```json
{
  "lot_management": {
    "enabled": true,
    "required": true,
    "quarantine": true
  },
  "method": "FEFO",
  "expiration_tracking": true,
  "temperature_monitoring": true,
  "multi_location": true
}
```

#### Électronique
```json
{
  "lot_management": {
    "enabled": false,
    "required": false
  },
  "method": "FIFO",
  "serialization": true,
  "expiration_tracking": false,
  "temperature_monitoring": false,
  "multi_location": true
}
```

#### Informatique
```json
{
  "lot_management": {
    "enabled": false,
    "required": false
  },
  "method": "FIFO",
  "serialization": true,
  "expiration_tracking": true,
  "temperature_monitoring": false,
  "multi_location": false
}
```

#### Quincaillerie
```json
{
  "lot_management": {
    "enabled": false,
    "required": false
  },
  "method": "FIFO",
  "serialization": false,
  "expiration_tracking": false,
  "temperature_monitoring": false,
  "multi_location": false
}
```

### Adaptation de l'Interface

**Selon la configuration** :
- Si `lot_management.enabled = false` : Masquer les champs "Lot" dans les formulaires
- Si `serialization.enabled = false` : Masquer les champs "Numéro de série"
- Si `expiration_tracking = false` : Masquer les champs "Date d'expiration"
- Si `temperature_monitoring = false` : Masquer les alertes température

---

## Workflows Configurables

### Table : `workflow_config`

**Structure** :

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | INT | Identifiant unique |
| `workflow_type` | VARCHAR(50) | Type (reception, sale, transfer) |
| `industry_type` | VARCHAR(50) | Type d'industrie |
| `steps` | JSONB | Étapes du workflow |
| `validation_rules` | JSONB | Règles de validation |
| `approval_required` | BOOLEAN | Approbation requise |

### Exemple - Workflow Réception

#### Pharmaceutique
```json
{
  "steps": [
    {
      "name": "Saisie réception",
      "required": true,
      "order": 1
    },
    {
      "name": "Vérification lot",
      "required": true,
      "order": 2,
      "conditional": "lot_management.enabled"
    },
    {
      "name": "Vérification certificat",
      "required": true,
      "order": 3,
      "conditional": "certificates.required"
    },
    {
      "name": "Contrôle température",
      "required": true,
      "order": 4,
      "conditional": "storage_conditions.temperature_monitoring"
    },
    {
      "name": "Mise en quarantaine",
      "required": true,
      "order": 5,
      "conditional": "quarantine.enabled"
    },
    {
      "name": "Validation",
      "required": true,
      "order": 6,
      "approval": true
    }
  ]
}
```

#### Électronique
```json
{
  "steps": [
    {
      "name": "Saisie réception",
      "required": true,
      "order": 1
    },
    {
      "name": "Enregistrement numéros de série",
      "required": true,
      "order": 2,
      "conditional": "serialization.enabled"
    },
    {
      "name": "Vérification garantie",
      "required": false,
      "order": 3,
      "conditional": "warranty.enabled"
    },
    {
      "name": "Validation",
      "required": true,
      "order": 4
    }
  ]
}
```

#### Quincaillerie
```json
{
  "steps": [
    {
      "name": "Saisie réception",
      "required": true,
      "order": 1
    },
    {
      "name": "Validation",
      "required": true,
      "order": 2
    }
  ]
}
```

---

## Règles Métier Configurables

### Table : `business_rules_config`

**Structure** :

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | INT | Identifiant unique |
| `rule_name` | VARCHAR(100) | Nom de la règle |
| `industry_type` | VARCHAR(50) | Type d'industrie |
| `rule_type` | VARCHAR(50) | Type (validation, calculation, workflow) |
| `rule_definition` | JSONB | Définition de la règle |
| `is_active` | BOOLEAN | Règle active |

### Exemples de Règles

#### Règle : Validation Réception Pharmaceutique
```json
{
  "rule_name": "validate_pharmaceutical_reception",
  "rule_type": "validation",
  "conditions": [
    {
      "field": "lot_number",
      "required": true,
      "message": "Le numéro de lot est obligatoire"
    },
    {
      "field": "expiration_date",
      "required": true,
      "message": "La date d'expiration est obligatoire"
    },
    {
      "field": "certificate_of_analysis",
      "required": true,
      "message": "Le certificat d'analyse est obligatoire",
      "conditional": "certificates.required"
    }
  ]
}
```

#### Règle : Calcul Garantie Électronique
```json
{
  "rule_name": "calculate_electronics_warranty",
  "rule_type": "calculation",
  "formula": "manufacturing_date + warranty_duration",
  "fields": {
    "warranty_end_date": "manufacturing_date + warranty_duration"
  }
}
```

#### Règle : FEFO Pharmaceutique
```json
{
  "rule_name": "fefo_sorting",
  "rule_type": "workflow",
  "condition": "expiration_tracking.enabled AND fefo_enforced",
  "action": "sort_by_expiration_date_ascending"
}
```

---

## Implémentation Progressive

### Phase 1 : Fondations (2 semaines)

1. **Créer tables de configuration** :
   - `industry_config`
   - `establishment_industry`
   - `module_config`
   - `product_specification_templates`

2. **Ajouter colonne `additional_specs` (JSONB)** à `products`

3. **Créer index GIN** sur JSONB

4. **Créer interface admin** pour configuration

### Phase 2 : Configuration par Industrie (2 semaines)

1. **Créer configurations par défaut** :
   - Pharmaceutique
   - Électronique
   - Informatique
   - Quincaillerie

2. **Adapter les formulaires** selon configuration

3. **Masquer/désactiver** champs selon modules activés

### Phase 3 : Workflows Configurables (2 semaines)

1. **Créer table `workflow_config`**

2. **Implémenter moteur de workflow** :
   - Lecture des étapes depuis config
   - Exécution conditionnelle
   - Validation selon règles

3. **Adapter workflows existants**

### Phase 4 : Règles Métier (2 semaines)

1. **Créer table `business_rules_config`**

2. **Implémenter moteur de règles** :
   - Évaluation des conditions
   - Exécution des actions
   - Messages d'erreur personnalisés

3. **Migrer règles existantes** vers configuration

### Phase 5 : Tests et Validation (1 semaine)

1. **Tests par industrie**
2. **Validation des configurations**
3. **Documentation**

---

## Utilisation dans l'Application

### Détection de l'Industrie

**Lors de la connexion** :
1. Récupérer l'établissement de l'utilisateur
2. Chercher dans `establishment_industry`
3. Charger la configuration correspondante
4. Stocker en session/cache

### Application de la Configuration

**Dans les formulaires** :
- Afficher/masquer champs selon `features`
- Valider selon `validation_rules`
- Appliquer workflows selon `workflow_config`

**Dans les requêtes** :
- Filtrer selon modules activés
- Appliquer règles métier
- Utiliser méthodes de tri (FIFO/FEFO) selon config

### Surcharge par Établissement

**Principe** :
- Configuration globale par industrie
- Possibilité de surcharger par établissement
- Merge des configurations (établissement > industrie > défaut)

---

## Exemples Concrets

### Scénario 1 : Réception Produit Pharmaceutique

1. **Détection** : Industrie = "pharmaceutical"
2. **Chargement config** : Lots obligatoires, certificat requis, quarantaine
3. **Formulaire** :
   - Afficher champ "Numéro de lot" (obligatoire)
   - Afficher champ "Date d'expiration" (obligatoire)
   - Afficher champ "Certificat d'analyse" (obligatoire)
   - Afficher champ "Température réception" (obligatoire)
   - Masquer champ "Numéro de série" (si sérialisation non activée)
4. **Validation** : Vérifier tous les champs obligatoires
5. **Workflow** : Exécuter étapes (saisie → vérification lot → certificat → température → quarantaine → validation)
6. **Stock** : Créer lot avec FEFO activé

### Scénario 2 : Réception Produit Électronique

1. **Détection** : Industrie = "electronics"
2. **Chargement config** : Sérialisation obligatoire, garantie
3. **Formulaire** :
   - Masquer champ "Numéro de lot"
   - Masquer champ "Date d'expiration"
   - Afficher champ "Numéro de série" (obligatoire)
   - Afficher champ "Date fabrication" (pour garantie)
   - Afficher champ "Durée garantie"
4. **Validation** : Vérifier numéro de série unique
5. **Workflow** : Exécuter étapes (saisie → enregistrement série → validation)
6. **Stock** : Créer entrée sans lot, avec numéro de série

### Scénario 3 : Réception Produit Quincaillerie

1. **Détection** : Industrie = "hardware"
2. **Chargement config** : Gestion simple, pas de lots
3. **Formulaire** :
   - Masquer tous les champs complexes
   - Afficher uniquement : Produit, Quantité, Emplacement
4. **Validation** : Vérifications basiques
5. **Workflow** : Exécuter étapes (saisie → validation)
6. **Stock** : Mise à jour simple, FIFO basique

---

## Avantages de cette Approche

### ✅ Flexibilité Maximale

- **Aucune modification de code** pour ajouter un nouveau secteur
- **Configuration pure** : tout est dans la base de données
- **Évolutif** : facile d'ajouter de nouvelles industries

### ✅ Maintenance Simplifiée

- **Un seul codebase** pour tous les secteurs
- **Tests centralisés** : un bug fix profite à tous
- **Évolutions partagées** : nouvelles fonctionnalités disponibles partout

### ✅ Performance

- **Configuration en cache** : chargée une fois par session
- **Index optimisés** : recherches rapides sur JSONB
- **Pas de surcharge** : modules non activés = pas de traitement

### ✅ Conformité

- **Respect des réglementations** par secteur
- **Traçabilité** selon exigences
- **Audit** complet des configurations

---

## Checklist d'Implémentation

### Phase 1 : Fondations
- [ ] Créer table `industry_config`
- [ ] Créer table `establishment_industry`
- [ ] Créer table `module_config`
- [ ] Créer table `product_specification_templates`
- [ ] Ajouter colonne `additional_specs` (JSONB) à `products`
- [ ] Créer index GIN sur JSONB

### Phase 2 : Configurations
- [ ] Créer config Pharmaceutique
- [ ] Créer config Électronique
- [ ] Créer config Informatique
- [ ] Créer config Quincaillerie
- [ ] Interface admin pour configuration

### Phase 3 : Adaptation Interface
- [ ] Masquer/afficher champs selon config
- [ ] Valider selon règles
- [ ] Adapter workflows

### Phase 4 : Tests
- [ ] Tests par industrie
- [ ] Tests de configuration
- [ ] Tests de performance

---

## Support

Pour toute question sur la configuration flexible :
- **Email** : config-support@commerceflow.com
- **Documentation** : https://docs.commerceflow.com/multi-industry

---

**Fin du Guide Configuration Flexible Multi-Industries**

