# Réservation de Stock et Génération de Bons de Livraison

## 1. Mécanisme de Réservation de Stock via Domain Events

### Architecture Découplée avec Domain Events

Le système utilise des **Domain Events** pour découpler les opérations de réservation/libération de stock du modèle `Order`. Cela suit les principes DDD et permet une meilleure extensibilité.

### Processus de Réservation (via Domain Event)

Quand une commande est **confirmée**, le flux suit ce pattern :

#### Étape 1 : Confirmation de la Commande
```python
order.confirm(user_id)
```

#### Étape 2 : Validation (dans le modèle Order)
- ✅ Validation du stock disponible (`validate_stock()`)
- ✅ Validation du crédit client (`validate_credit()`)
- ✅ Mise à jour du statut à `"confirmed"`

#### Étape 3 : Émission du Domain Event
Le modèle `Order` émet `OrderConfirmedDomainEvent` :
```python
self.raise_domain_event(OrderConfirmedDomainEvent(
    order_id=self.id,
    order_number=self.number,
    customer_id=self.customer_id,
    confirmed_by=user_id
))
```

#### Étape 4 : Handler Automatique (OrderConfirmedDomainEventHandler)
Le handler `OrderConfirmedDomainEventHandler` est déclenché automatiquement :

1. **Récupère la commande** avec ses lignes
2. **Vérifie les réservations existantes** (évite les doublons)
3. **Pour chaque ligne de commande** :
   - Trouve les `StockItem` disponibles pour le produit/variant
   - Trie par quantité disponible décroissante
   - Réserve depuis plusieurs emplacements si nécessaire
4. **Crée des `StockReservation`** :
   - Une réservation par `StockItem` utilisé
   - Lien vers `order_id`, `order_line_id`, `stock_item_id`
   - Quantité réservée
   - Statut : `"reserved"`
5. **Met à jour `StockItem.reserved_quantity`** :
   - Incrémente la quantité réservée
   - Réduit la quantité disponible

#### Exemple de Réservation Multi-Emplacements

Si une commande nécessite 100 unités d'un produit :
- Emplacement A : 60 unités disponibles → Réserve 60
- Emplacement B : 50 unités disponibles → Réserve 40
- Total réservé : 100 unités (2 réservations)

### Libération du Stock (via Domain Event)

Quand une commande est **annulée** :

1. Le modèle `Order` émet `OrderCanceledDomainEvent`
2. Le handler `OrderCanceledDomainEventHandler` est déclenché automatiquement :
   - Récupère toutes les réservations avec statut `"reserved"`
   - Pour chaque réservation :
     - Décrémente `StockItem.reserved_quantity`
     - Met à jour le statut de la réservation à `"released"`
     - Enregistre `released_at`

### Avantages de cette Architecture

✅ **Découplage** : Le modèle `Order` ne connaît pas les détails de la réservation  
✅ **Extensibilité** : Facile d'ajouter d'autres handlers (notifications, logs, etc.)  
✅ **Testabilité** : Chaque handler peut être testé indépendamment  
✅ **Cohérence** : Suit le même pattern que `PurchaseOrderReceivedDomainEvent`

## 2. Génération de Bons de Livraison via Domain Event

### Quand Générer un Bon de Livraison ?

Un bon de livraison (BL) est généré quand :
- La commande passe au statut **"ready"** (prête à être expédiée)
- Le modèle `Order` émet `OrderReadyDomainEvent`
- Le handler `OrderReadyDomainEventHandler` peut déclencher la génération (actuellement placeholder)

### Flux avec Domain Event

1. **Commande passe à "ready"** :
   ```python
   order.mark_ready()
   ```

2. **Émission du Domain Event** :
   ```python
   self.raise_domain_event(OrderReadyDomainEvent(
       order_id=self.id,
       order_number=self.number,
       customer_id=self.customer_id
   ))
   ```

3. **Handler peut déclencher la génération** :
   - Actuellement : placeholder pour futures améliorations
   - Peut être étendu pour :
     - Générer le PDF automatiquement
     - Envoyer une notification au service logistique
     - Créer un enregistrement de bon de livraison

### Contenu du Bon de Livraison

Le bon de livraison contient :
- **En-tête** :
  - Numéro de bon de livraison (BL-YYYY-XXXXX)
  - Numéro de commande
  - Date de livraison
  - Informations client et adresse de livraison
- **Lignes de livraison** :
  - Produits livrés
  - Quantités livrées (peut être partielle)
  - Emplacements de stock utilisés
- **Totaux** :
  - Quantités totales livrées
  - Instructions de livraison

### Workflow

```
Commande "confirmed" 
  ↓
Mise en préparation "in_preparation"
  ↓
Prête "ready" → Génération BL
  ↓
Expédiée "shipped" → BL envoyé
  ↓
Livrée "delivered"
```

## 3. Implémentation Technique

### Modèle StockReservation

Chaque réservation stocke :
- `order_id` : Commande concernée
- `order_line_id` : Ligne de commande
- `stock_item_id` : Emplacement de stock
- `quantity` : Quantité réservée
- `status` : `"reserved"`, `"fulfilled"`, `"released"`

### Service PDF

Le service `PDFService` génère les bons de livraison de la même manière que les devis, avec :
- Template spécifique pour les BL
- Informations de livraison
- Liste des produits avec emplacements

