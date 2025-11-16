# Analyse : Gestion des Variantes Produit

**Date**: 2025-01-27  
**Objectif**: Analyser comment les variantes produit sont gérées et vérifier la conformité au CDC

---

## Résumé Exécutif

### ✅ Implémenté
- Modèle `ProductVariant` avec code unique, prix, coût, barcode
- Support variantes dans `QuoteLine` et `OrderLine` (champ `variant_id`)
- Support variantes dans `StockItem` et `StockMovement` (champ `variant_id`)

### ⚠️ Partiellement Implémenté
- **Frontend** : Pas d'interface visible pour gérer/sélectionner les variantes
- **Stock** : Commentaires "For future use" suggèrent que ce n'est pas encore actif
- **Réservation stock** : Utilise `variant_id` mais pas testé

### ❌ Manquant
- Interface CRUD pour créer/modifier les variantes
- Sélection de variante dans les formulaires devis/commandes
- Affichage des variantes dans les listes
- Validation que la variante appartient au produit

---

## Analyse Détaillée

### 1. Modèle de Domaine : ProductVariant

#### ✅ Structure du Modèle
**Fichier**: `app/domain/models/product.py:264-378`

**Champs**:
- `id` (Integer, PK)
- `product_id` (Integer, FK to products.id) - Produit parent
- `code` (String(50), unique) - Code unique par variante ✅
- `name` (String(200)) - Nom de la variante
- `attributes` (Text, JSON) - Attributs (couleur, taille, etc.) ✅
- `price` (Numeric(12,2), nullable) - Prix override si différent du parent ✅
- `cost` (Numeric(12,2), nullable) - Coût override si différent du parent ✅
- `barcode` (String(50), unique, nullable) - Code-barres unique ✅
- `status` (String(20)) - active/archived

**Conformité CDC (FP-PROD-004)**:
- ✅ Produit parent (`product_id`)
- ✅ Variantes multiples (relation one-to-many)
- ✅ Code unique par variante (`code` unique)
- ✅ Prix par variante (`price` override)
- ✅ Coût par variante (`cost` override)

**Méthodes**:
- `create()` - Factory method avec validation
- `update_details()` - Mise à jour des détails
- `archive()` / `activate()` - Gestion du statut

**Note**: Le modèle est bien conçu et conforme au CDC.

---

### 2. Utilisation dans Devis (Quotes)

#### ✅ Support Technique
**Fichier**: `app/domain/models/quote.py:75`

**Champ**: `variant_id` (Integer, nullable) dans `QuoteLine`

**Relation**: 
```python
variant = relationship("ProductVariant", foreign_keys=[variant_id])
```

**Méthode `create()`**: Accepte `variant_id` (ligne 108)

#### ⚠️ Utilisation Réelle
- Le champ existe mais **pas d'interface frontend** pour sélectionner une variante
- Pas de validation que `variant_id` appartient au `product_id` sélectionné
- Pas d'affichage de la variante dans les listes de devis

**Impact**: Les variantes peuvent être stockées mais ne sont pas utilisables par les utilisateurs.

---

### 3. Utilisation dans Commandes (Orders)

#### ✅ Support Technique
**Fichier**: `app/domain/models/order.py:79`

**Champ**: `variant_id` (Integer, nullable) dans `OrderLine`

**Relation**: 
```python
variant = relationship("ProductVariant", foreign_keys=[variant_id])
```

**Réservation Stock**: 
- `StockReservation` utilise `variant_id` (ligne 319 dans `order.py`)
- Filtre par `variant_id` lors de la réservation

#### ⚠️ Utilisation Réelle
- Même problème que pour les devis : pas d'interface frontend
- La réservation stock fonctionne théoriquement mais n'est pas testée avec variantes

---

### 4. Utilisation dans Stock

#### ⚠️ Support Partiel
**Fichier**: `app/domain/models/stock.py:99, 251`

**Champs**:
- `StockItem.variant_id` (ligne 99) - **Commentaire**: "For future use (product_variants table not yet created)"
- `StockMovement.variant_id` (ligne 251) - **Commentaire**: "For future use"

**Contrainte Unique**: 
```python
UniqueConstraint('product_id', 'variant_id', 'location_id', name='uq_stock_item_product_location')
```
✅ La contrainte permet d'avoir un stock séparé par variante

**Problème**: Les commentaires suggèrent que les variantes ne sont pas encore activées dans le stock, mais le modèle existe.

#### ❌ Incohérence
- Le modèle `ProductVariant` existe
- Les champs `variant_id` existent dans `StockItem` et `StockMovement`
- Mais les commentaires disent "For future use"
- **Conclusion**: Le support technique existe mais n'est pas activé/utilisé

---

### 5. Frontend / Interface Utilisateur

#### ❌ Pas d'Interface
**Recherche effectuée**: Aucun template ne gère les variantes

**Manque**:
- Formulaire pour créer/modifier des variantes
- Sélection de variante dans les formulaires devis/commandes
- Affichage des variantes dans les listes produits
- Gestion des variantes dans le formulaire produit

**Impact**: Les utilisateurs ne peuvent pas utiliser les variantes même si le modèle existe.

---

### 6. Handlers et Services

#### ⚠️ Support Partiel
**Recherche effectuée**: Les handlers acceptent `variant_id` mais ne le valident pas

**Problèmes identifiés**:
1. **Pas de validation** que `variant_id` appartient au `product_id`
2. **Pas de logique** pour utiliser le prix de la variante si elle a un prix override
3. **Pas de service** dédié à la gestion des variantes

**Exemple dans `AddQuoteLineHandler`**:
```python
# Le handler accepte variant_id mais ne vérifie pas que:
# - La variante existe
# - La variante appartient au produit sélectionné
# - Le prix de la variante doit être utilisé si présent
```

---

## Conformité au CDC

### FP-PROD-004 : Variantes

| Exigence CDC | État | Détails |
|--------------|------|---------|
| Produit parent | ✅ | `product_id` dans `ProductVariant` |
| Variantes multiples | ✅ | Relation one-to-many `Product.variants` |
| Code unique par variante | ✅ | `code` unique dans `ProductVariant` |
| Prix par variante | ✅ | `price` override dans `ProductVariant` |
| Stock par variante | ⚠️ | Support technique mais commentaires "For future use" |

**Verdict**: **Partiellement conforme** - Le modèle est conforme mais l'utilisation n'est pas complète.

---

## Problèmes Identifiés

### 1. ❌ Pas d'Interface Utilisateur
**Impact**: CRITIQUE  
**Description**: Les utilisateurs ne peuvent pas créer, modifier ou sélectionner des variantes.

**Solution**: Créer des interfaces pour :
- Gestion des variantes (CRUD)
- Sélection de variante dans devis/commandes
- Affichage des variantes dans les listes

### 2. ⚠️ Incohérence Stock
**Impact**: MOYEN  
**Description**: Les commentaires "For future use" suggèrent que les variantes ne sont pas activées dans le stock, mais le modèle existe.

**Solution**: 
- Retirer les commentaires "For future use"
- Activer l'utilisation des variantes dans le stock
- Tester la réservation stock avec variantes

### 3. ⚠️ Pas de Validation
**Impact**: MOYEN  
**Description**: Pas de validation que `variant_id` appartient au `product_id` sélectionné.

**Solution**: Ajouter validation dans les handlers :
```python
if variant_id:
    variant = session.get(ProductVariant, variant_id)
    if not variant or variant.product_id != product_id:
        raise ValueError("Variant does not belong to selected product")
```

### 4. ⚠️ Prix Variante Non Utilisé
**Impact**: MOYEN  
**Description**: Si une variante a un prix override, il n'est pas utilisé automatiquement.

**Solution**: Modifier les handlers pour utiliser `variant.price` si présent :
```python
if variant_id and variant.price is not None:
    unit_price = variant.price
else:
    unit_price = product.price
```

### 5. ❌ Pas de Service Variantes
**Impact**: FAIBLE  
**Description**: Pas de service dédié pour la gestion des variantes.

**Solution**: Créer `VariantService` pour centraliser la logique.

---

## Recommandations

### Priorité 1 : Interface Utilisateur (CRITIQUE)

#### T344 [US1] Créer interface gestion variantes
- Formulaire pour créer/modifier variantes
- Liste des variantes d'un produit
- Suppression/archivage de variantes

#### T345 [US4] Ajouter sélection variante dans devis
- Dropdown pour sélectionner variante après sélection produit
- Affichage nom variante dans les lignes
- Utilisation prix variante si présent

#### T346 [US5] Ajouter sélection variante dans commandes
- Même chose que pour devis
- Validation stock par variante

### Priorité 2 : Validation et Logique Métier

#### T347 [US1] Ajouter validation variant_id
- Vérifier que variant appartient au produit
- Dans tous les handlers (quotes, orders, stock)

#### T348 [US4] Utiliser prix variante automatiquement
- Si variante a prix override, l'utiliser
- Sinon utiliser prix produit parent

#### T349 [US3] Activer variantes dans stock
- Retirer commentaires "For future use"
- Tester réservation stock par variante
- Afficher stock par variante dans dashboard

### Priorité 3 : Améliorations

#### T350 [US1] Créer VariantService
- Centraliser logique variantes
- Méthodes: get_variants_for_product(), get_variant_price(), etc.

#### T351 [US1] Améliorer affichage variantes
- Afficher variantes dans liste produits
- Badge "X variantes" sur produit parent
- Filtre par variante dans recherche

---

## Plan d'Action

### Sprint 1 (Immédiat)
- [ ] T344 : Interface CRUD variantes
- [ ] T345 : Sélection variante dans devis
- [ ] T346 : Sélection variante dans commandes

### Sprint 2 (Court terme)
- [ ] T347 : Validation variant_id
- [ ] T348 : Utilisation prix variante
- [ ] T349 : Activer variantes dans stock

### Sprint 3 (Moyen terme)
- [ ] T350 : Créer VariantService
- [ ] T351 : Améliorer affichage variantes

---

## Conclusion

**État actuel**: Les variantes produit sont **partiellement implémentées**.

**Points forts**:
- ✅ Modèle de domaine complet et conforme au CDC
- ✅ Support technique dans devis, commandes, stock
- ✅ Code unique, prix, coût par variante

**Points faibles**:
- ❌ **CRITIQUE**: Pas d'interface utilisateur
- ⚠️ Incohérence dans le stock (commentaires "For future use")
- ⚠️ Pas de validation variant_id
- ⚠️ Prix variante non utilisé automatiquement

**Recommandation**: Prioriser l'interface utilisateur (T344-T346) car c'est le blocage principal. Sans interface, les variantes ne sont pas utilisables même si le modèle existe.

