# Analyse : Conformité Produits au CDC et Compatibilité Achats/Stock

**Date**: 2025-01-27  
**Objectif**: Vérifier si l'implémentation actuelle des produits répond au CDC et est compatible avec la gestion des achats/stock

---

## Résumé Exécutif

### ✅ Conforme au CDC
- Prix de vente standard (FP-PROD-002, FP-PROD-003)
- Coût produit (FP-PROD-002)
- Modification avec historique (partiel - via events, pas de table dédiée)

### ❌ Non Conforme au CDC
- **Historique des prix** (FP-PROD-003) - NON IMPLÉMENTÉ
- **Listes de prix multiples** (FP-PROD-003) - NON IMPLÉMENTÉ
- **Prix dégressifs par quantité** (FP-PROD-003) - NON IMPLÉMENTÉ
- **Prix promotionnels (dates validité)** (FP-PROD-003) - NON IMPLÉMENTÉ
- **Mise à jour coût produit après réception** (RG-ACH-005) - NON IMPLÉMENTÉ

---

## Analyse Détaillée

### 1. FP-PROD-003 : Gestion Prix

#### ✅ Prix de vente standard
**CDC**: "Prix de vente standard"  
**Implémentation**: ✅ **CONFORME**
- `Product.price` (Numeric(12, 2), nullable=False, default=0)
- Validation : prix ≥ 0
- Stocké dans la table `products`

**Fichier**: `app/domain/models/product.py:54`

#### ❌ Listes de prix multiples
**CDC**: "Listes de prix multiples"  
**Implémentation**: ❌ **NON CONFORME**

**État actuel**:
- Champ `price_list_id` dans `CommercialConditions` mais marqué "future" (ligne 247)
- `PricingService` a un TODO pour les listes de prix (ligne 123)
- Pas de modèle `PriceList` ou `ProductPriceList`

**Fichiers concernés**:
- `app/domain/models/customer.py:247` - `price_list_id` (future)
- `app/services/pricing_service.py:123` - TODO comment

**Impact**: Impossible d'avoir plusieurs listes de prix (ex: Prix Standard, Prix VIP, Prix Gros)

#### ❌ Prix dégressifs par quantité
**CDC**: "Prix dégressifs par quantité"  
**Implémentation**: ❌ **NON CONFORME**

**État actuel**:
- Pas de modèle pour les prix dégressifs
- `PricingService.get_price_for_customer()` a un paramètre `quantity` mais ne l'utilise pas (ligne 87-88)
- Pas de table `product_volume_pricing` ou similaire

**Fichier**: `app/services/pricing_service.py:83-137`

**Impact**: Impossible d'avoir des prix qui diminuent selon la quantité commandée (ex: 1-10 unités = 100€, 11-50 = 95€, 51+ = 90€)

#### ❌ Prix promotionnels (dates validité)
**CDC**: "Prix promotionnels (dates validité)"  
**Implémentation**: ❌ **NON CONFORME**

**État actuel**:
- Pas de modèle pour les prix promotionnels
- Pas de table `product_promotional_prices` ou similaire
- Pas de logique pour appliquer automatiquement les prix promotionnels selon les dates

**Impact**: Impossible de définir des prix promotionnels avec dates de début/fin

#### ❌ Historique des prix
**CDC**: "Historique des prix"  
**Implémentation**: ❌ **NON CONFORME**

**État actuel**:
- Les changements de prix sont trackés dans `ProductUpdatedDomainEvent` avec `changes['price']` (ligne 177)
- Mais cet historique n'est **pas persisté** en base de données
- Pas de table `product_price_history` ou similaire
- L'événement est dispatché mais pas stocké pour consultation historique

**Fichiers concernés**:
- `app/domain/models/product.py:173-178` - Tracking dans event
- `app/application/products/events/product_updated_handler.py` - Handler qui ne persiste pas l'historique

**Impact**: Impossible de consulter l'historique des prix d'un produit (ex: voir que le prix était 100€ le 01/01/2024, puis 110€ le 15/03/2024)

---

### 2. RG-ACH-005 : Mise à jour coût produit après réception

**CDC**: "Mise à jour coût produit après réception"  
**Implémentation**: ❌ **NON CONFORME**

**État actuel**:
- Lors de la réception d'une commande d'achat, le handler `PurchaseOrderLineReceivedDomainEventHandler` :
  - ✅ Crée un mouvement de stock (entry)
  - ✅ Met à jour `StockItem.physical_quantity`
  - ❌ **NE MET PAS À JOUR** `Product.cost`

**Fichier**: `app/application/purchases/events/purchase_order_line_received_handler.py:42-115`

**Code actuel** (lignes 94-115):
```python
# Create stock movement entry for the incremental quantity received
movement = StockMovement.create(...)
session.add(movement)
session.flush()

# Update stock item quantity (entry increases physical quantity)
stock_item.physical_quantity += event.quantity_received
stock_item.last_movement_at = movement.created_at

session.commit()
```

**Manque**:
```python
# TODO: Update product cost based on purchase price
# This should calculate AVCO (Average Cost) or use the purchase price
product = session.get(Product, event.product_id)
if product:
    # Calculate new cost (AVCO method)
    # new_cost = (old_cost * old_stock + purchase_price * quantity_received) / (old_stock + quantity_received)
    # product.cost = new_cost
```

**Impact**: 
- Le coût produit n'est pas mis à jour automatiquement après réception
- Les marges calculées seront incorrectes
- Impossible de suivre l'évolution du coût d'achat

---

## Compatibilité avec Achats/Stock

### ✅ Compatible
1. **Prix d'achat dans PurchaseOrderLine**
   - `PurchaseOrderLine.unit_price` stocke le prix d'achat (ligne 67)
   - Utilisé pour calculer les totaux de la commande

2. **Stock mis à jour après réception**
   - `PurchaseOrderLineReceivedDomainEventHandler` crée les mouvements de stock
   - `StockItem.physical_quantity` est mis à jour

3. **Prix de vente utilisé dans devis/commandes**
   - `Product.price` est utilisé dans `QuoteLine` et `OrderLine`
   - `PricingService` peut appliquer des remises client

### ❌ Incompatibilités

1. **Coût produit non mis à jour**
   - Le coût d'achat (`PurchaseOrderLine.unit_price`) n'est pas propagé vers `Product.cost`
   - Impact sur le calcul des marges

2. **Pas d'historique des coûts d'achat**
   - Impossible de voir l'évolution des coûts d'achat
   - Impossible de calculer des moyennes pondérées (AVCO) correctement

3. **Prix d'achat vs Prix de vente**
   - Pas de lien automatique entre le prix d'achat et le prix de vente
   - Pas de suggestion de prix de vente basé sur le coût d'achat + marge

---

## Recommandations

### Priorité 1 : Critique pour Phase 2

#### 1. Mise à jour coût produit après réception (RG-ACH-005)
**Action**: Modifier `PurchaseOrderLineReceivedDomainEventHandler` pour mettre à jour `Product.cost`

**Méthode recommandée**: AVCO (Average Cost - Coût Moyen Pondéré)
```python
# Dans handle_internal() après la mise à jour du stock
product = session.get(Product, event.product_id)
if product:
    # Récupérer le prix d'achat depuis la ligne
    purchase_line = session.get(PurchaseOrderLine, event.line_id)
    purchase_price = purchase_line.unit_price
    
    # Calculer AVCO
    old_cost = product.cost or Decimal(0)
    old_stock = stock_item.physical_quantity - event.quantity_received
    new_stock = stock_item.physical_quantity
    
    if new_stock > 0:
        new_cost = (old_cost * old_stock + purchase_price * event.quantity_received) / new_stock
        product.cost = new_cost
```

**Fichier à modifier**: `app/application/purchases/events/purchase_order_line_received_handler.py`

#### 2. Historique des prix (FP-PROD-003)
**Action**: Créer une table `product_price_history` et persister les changements

**Modèle à créer**:
```python
class ProductPriceHistory(Base):
    __tablename__ = "product_price_history"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    old_price = Column(Numeric(12, 2), nullable=True)
    new_price = Column(Numeric(12, 2), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime, nullable=False, server_default=func.now())
    reason = Column(String(200), nullable=True)
```

**Handler à modifier**: `app/application/products/events/product_updated_handler.py` pour persister l'historique

### Priorité 2 : Important pour Phase 2

#### 3. Listes de prix multiples (FP-PROD-003)
**Action**: Créer les modèles `PriceList` et `ProductPriceList`

**Modèles à créer**:
```python
class PriceList(Base):
    __tablename__ = "price_lists"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

class ProductPriceList(Base):
    __tablename__ = "product_price_lists"
    
    id = Column(Integer, primary_key=True)
    price_list_id = Column(Integer, ForeignKey("price_lists.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
```

**Service à modifier**: `app/services/pricing_service.py` pour utiliser les listes de prix

### Priorité 3 : Amélioration future

#### 4. Prix dégressifs par quantité (FP-PROD-003)
**Action**: Créer le modèle `ProductVolumePricing`

#### 5. Prix promotionnels (FP-PROD-003)
**Action**: Créer le modèle `ProductPromotionalPrice`

---

## Plan d'Action

### Sprint 1 (Immédiat)
- [ ] T335 [US9] Implémenter mise à jour coût produit après réception (RG-ACH-005)
- [ ] T336 [US7] Créer modèle `ProductPriceHistory` pour historique des prix
- [ ] T337 [US7] Modifier `ProductUpdatedDomainEventHandler` pour persister l'historique

### Sprint 2 (Phase 2)
- [ ] T338 [US7] Créer modèles `PriceList` et `ProductPriceList`
- [ ] T339 [US7] Modifier `PricingService` pour utiliser les listes de prix
- [ ] T340 [US7] Créer API endpoints pour gestion des listes de prix

### Sprint 3 (Future)
- [ ] T341 [US7] Créer modèle `ProductVolumePricing` pour prix dégressifs
- [ ] T342 [US7] Créer modèle `ProductPromotionalPrice` pour prix promotionnels
- [ ] T343 [US7] Modifier `PricingService` pour appliquer prix dégressifs et promotionnels

---

## Conclusion

**État actuel**: L'implémentation des produits est **partiellement conforme** au CDC.

**Points forts**:
- ✅ Prix de vente standard fonctionnel
- ✅ Coût produit stocké (mais pas mis à jour automatiquement)
- ✅ Compatible avec achats/stock pour les mouvements

**Points faibles**:
- ❌ Historique des prix non persisté
- ❌ Listes de prix multiples non implémentées
- ❌ Prix dégressifs/promotionnels non implémentés
- ❌ **CRITIQUE**: Coût produit non mis à jour après réception

**Recommandation**: Prioriser la mise à jour du coût produit (RG-ACH-005) car c'est critique pour la Phase 2 (Achats) et impacte directement les calculs de marge.

