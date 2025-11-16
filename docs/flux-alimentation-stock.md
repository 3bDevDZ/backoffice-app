# 📦 Flux d'Alimentation du Stock

## Vue d'ensemble

Le système alimente automatiquement le stock lorsqu'une commande d'achat est marquée comme reçue. Ce processus est entièrement automatisé via les **Domain Events** et respecte l'architecture DDD + CQRS.

---

## 🔄 Flux Complet d'Alimentation

```
1. Création Commande d'Achat (Purchase Order)
   ↓
2. Ajout de Lignes (Produits + Quantités)
   ↓
3. Confirmation de la Commande
   ↓
4. Réception des Marchandises
   ├─ Marquer ligne comme reçue (quantity_received)
   └─ Appel: ReceivePurchaseOrderLineCommand
   ↓
5. Mise à jour du Statut de la Commande
   ├─ Si toutes les lignes reçues → status = "received"
   └─ Sinon → status = "partially_received"
   ↓
6. Déclenchement Domain Event
   └─ PurchaseOrderReceivedDomainEvent (si status = "received")
   ↓
7. Handler Automatique
   └─ PurchaseOrderReceivedDomainEventHandler
   ↓
8. Création Automatique des Mouvements de Stock
   ├─ Pour chaque ligne avec quantity_received > 0
   ├─ Création StockItem si n'existe pas
   ├─ Création StockMovement (type: "entry")
   └─ Mise à jour physical_quantity du StockItem
   ↓
9. Stock Alimenté ✅
```

---

## 📋 Détails Techniques

### 1. Réception d'une Ligne de Commande

**Commande :** `ReceivePurchaseOrderLineCommand`

```python
command = ReceivePurchaseOrderLineCommand(
    purchase_order_id=1,
    line_id=5,
    quantity_received=Decimal("100.0"),
    location_id=1  # Optionnel: location spécifique
)

line = mediator.dispatch(command)
```

**Handler :** `ReceivePurchaseOrderLineHandler`
- Valide la quantité reçue (≤ quantité commandée)
- Met à jour `line.quantity_received`
- Appelle `order.mark_received()` qui vérifie si toutes les lignes sont reçues

### 2. Mise à Jour du Statut de la Commande

**Méthode du domaine :** `PurchaseOrder.mark_received()`

```python
def mark_received(self):
    # Vérifie si toutes les lignes sont complètement reçues
    for line in self.lines:
        if line.quantity_received < line.quantity:
            self.status = 'partially_received'
            return
    
    # Toutes les lignes sont reçues
    self.status = 'received'
    self.received_date = date.today()
    
    # Déclenche le domain event
    self.raise_domain_event(PurchaseOrderReceivedDomainEvent(
        purchase_order_id=self.id,
        purchase_order_number=self.number
    ))
```

### 3. Handler d'Événement Domaine

**Handler :** `PurchaseOrderReceivedDomainEventHandler`

**Fichier :** `app/application/purchases/events/purchase_order_received_handler.py`

**Fonctionnement :**

1. **Récupère la commande d'achat** avec toutes ses lignes
2. **Trouve la location par défaut** (premier entrepôt actif)
3. **Pour chaque ligne avec `quantity_received > 0`** :
   - Vérifie si un `StockItem` existe pour ce produit à cette location
   - Si non, crée un nouveau `StockItem` avec `physical_quantity = 0`
   - Crée un `StockMovement` de type `"entry"` avec :
     - `quantity` = `line.quantity_received` (positif)
     - `movement_type` = `"entry"`
     - `reason` = `"Réception commande d'achat {order.number}"`
     - `related_document_type` = `"purchase_order"`
     - `related_document_id` = `order.id`
   - Met à jour `stock_item.physical_quantity += quantity_received`
   - Met à jour `stock_item.last_movement_at`

### 4. Création du Mouvement de Stock

**Handler de mouvement :** `CreateStockMovementHandler`

Lorsqu'un `StockMovement` de type `"entry"` est créé :

```python
# Dans CreateStockMovementHandler
if command.movement_type == 'entry':
    stock_item.physical_quantity += command.quantity
    stock_item.last_movement_at = movement.created_at
```

Le `physical_quantity` est automatiquement augmenté.

---

## 🎯 Exemple Concret

### Scénario : Réception d'une commande d'achat

**1. Commande d'achat créée :**
```
Purchase Order: PO-2025-00001
├─ Ligne 1: Produit A, Quantité commandée: 100
└─ Ligne 2: Produit B, Quantité commandée: 50
```

**2. Réception partielle :**
```python
# Marquer la ligne 1 comme reçue (100 unités)
mediator.dispatch(ReceivePurchaseOrderLineCommand(
    purchase_order_id=1,
    line_id=1,
    quantity_received=Decimal("100.0")
))
```

**Résultat :**
- `line.quantity_received = 100`
- `order.status = "partially_received"` (ligne 2 pas encore reçue)
- **Aucun mouvement de stock créé** (commande pas encore complètement reçue)

**3. Réception complète :**
```python
# Marquer la ligne 2 comme reçue (50 unités)
mediator.dispatch(ReceivePurchaseOrderLineCommand(
    purchase_order_id=1,
    line_id=2,
    quantity_received=Decimal("50.0")
))
```

**Résultat :**
- `line.quantity_received = 50`
- `order.status = "received"` (toutes les lignes reçues)
- **Domain Event déclenché :** `PurchaseOrderReceivedDomainEvent`
- **Handler automatique exécuté :**
  - Crée `StockMovement` pour Produit A (100 unités, type: "entry")
  - Crée `StockMovement` pour Produit B (50 unités, type: "entry")
  - Met à jour `StockItem.physical_quantity` pour chaque produit

**4. Stock mis à jour :**
```
StockItem (Produit A, Location: Entrepôt Principal)
├─ physical_quantity: 0 → 100 ✅
└─ StockMovement créé (entry, 100, PO-2025-00001)

StockItem (Produit B, Location: Entrepôt Principal)
├─ physical_quantity: 0 → 50 ✅
└─ StockMovement créé (entry, 50, PO-2025-00001)
```

---

## 🔧 Points Techniques Importants

### 1. Transaction Atomique

Tout se passe dans une **même transaction** :
- Mise à jour de `quantity_received`
- Mise à jour du statut de la commande
- Création des mouvements de stock
- Mise à jour des quantités de stock

Si une erreur survient, **tout est annulé** (rollback).

### 2. Domain Events (Événements Domaine)

- **Synchrones** : Exécutés dans la même transaction
- **Interne** : Communication entre agrégats du même contexte
- **Automatiques** : Déclenchés par les méthodes du domaine (`mark_received()`)

### 3. Location par Défaut

Pour l'instant, le handler utilise le **premier entrepôt actif** trouvé. 

**Amélioration future :**
- Utiliser la location de livraison du fournisseur
- Permettre de spécifier la location lors de la réception
- Gérer plusieurs locations (multi-entrepôts)

### 4. Création Automatique de StockItem

Si un `StockItem` n'existe pas pour un produit à une location :
- Il est **créé automatiquement** avec `physical_quantity = 0`
- Puis la quantité reçue est ajoutée

---

## 📊 Résumé

| Étape | Action | Résultat |
|-------|--------|----------|
| 1 | Marquer ligne comme reçue | `quantity_received` mis à jour |
| 2 | Vérifier toutes les lignes | Statut → `"received"` ou `"partially_received"` |
| 3 | Domain Event déclenché | `PurchaseOrderReceivedDomainEvent` (si `"received"`) |
| 4 | Handler automatique | Parcourt toutes les lignes avec `quantity_received > 0` |
| 5 | Création StockItem | Si n'existe pas, création automatique |
| 6 | Création StockMovement | Mouvement d'entrée créé pour chaque ligne |
| 7 | Mise à jour stock | `physical_quantity` augmenté automatiquement |

---

## ✅ Avantages de cette Architecture

1. **Automatisation** : Pas besoin d'appeler manuellement la création de mouvements
2. **Cohérence** : Impossible d'oublier de mettre à jour le stock
3. **Traçabilité** : Chaque mouvement est lié à la commande d'achat
4. **Transaction** : Tout ou rien (pas de stock partiellement mis à jour)
5. **Évolutivité** : Facile d'ajouter d'autres handlers (notifications, etc.)

---

## 🔮 Améliorations Futures

- [ ] Gestion de plusieurs locations (spécifier location par ligne)
- [ ] Réception partielle avec mise à jour progressive du stock
- [ ] Validation qualité avant mise en stock
- [ ] Mise à jour automatique du coût d'achat du produit
- [ ] Notifications automatiques (email, SMS) lors de réception






