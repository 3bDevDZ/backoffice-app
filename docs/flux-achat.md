# 📦 Flux d'Achat - Documentation Complète

## Vue d'ensemble

Le module achat permet de gérer le cycle complet d'achat de marchandises auprès des fournisseurs, depuis la création d'un fournisseur jusqu'à la réception des marchandises et la mise à jour du stock.

---

## 🔄 Workflow Complet

```
1. Création Fournisseur
   ↓
2. Création Commande d'Achat (Purchase Order)
   ↓
3. Ajout de Lignes (Produits + Quantités + Prix)
   ↓
4. Confirmation de la Commande
   ↓
5. Envoi au Fournisseur (optionnel - statut "sent")
   ↓
6. Réception Partielle ou Totale
   ↓
7. Mise à Jour du Stock (via StockMovement)
   ↓
8. Commande Marquée "Received"
```

---

## 📋 Étapes Détaillées

### **Étape 1 : Gestion des Fournisseurs (Suppliers)**

#### Entité : `Supplier`

**Informations de base :**
- Code unique (auto-généré : `FOUR-XXXXXX`)
- Nom, email, téléphone
- Informations entreprise (SIRET, TVA, RCS, forme juridique)
- Catégorie (Primary, Secondary, Backup)
- Statut (active, inactive, archived, blocked)

**Relations :**
- **Adresses** (`SupplierAddress`) : Siège, entrepôt, facturation, livraison
- **Contacts** (`SupplierContact`) : Personnes à contacter (nom, fonction, email, téléphone)
- **Conditions Commerciales** (`SupplierConditions`) :
  - Délais de paiement (jours)
  - Remise par défaut (%)
  - Montant minimum de commande
  - Délai de livraison typique (jours)

**Exemple de création :**
```python
supplier = Supplier.create(
    name="Fournisseur ABC",
    email="contact@fournisseur-abc.fr",
    company_name="ABC SARL",
    siret="12345678901234",
    payment_terms_days=30,
    default_discount_percent=Decimal("5.00"),
    minimum_order_amount=Decimal("500.00"),
    delivery_lead_time_days=7
)
```

---

### **Étape 2 : Création d'une Commande d'Achat (Purchase Order)**

#### Entité : `PurchaseOrder`

**Informations :**
- Numéro unique (auto-généré : `PO-YYYY-XXXXX`)
- Fournisseur (référence)
- Date de commande
- Date de livraison prévue
- Notes (visibles par le fournisseur)
- Notes internes (non visibles)

**Statuts possibles :**
1. **`draft`** : Brouillon (peut être modifié)
2. **`sent`** : Envoyée au fournisseur
3. **`confirmed`** : Confirmée par le fournisseur
4. **`partially_received`** : Partiellement reçue
5. **`received`** : Totalement reçue
6. **`cancelled`** : Annulée

**Workflow de statut :**
```
draft → sent → confirmed → partially_received → received
  ↓
cancelled (peut être annulée à tout moment sauf si "received")
```

**Exemple de création :**
```python
purchase_order = PurchaseOrder.create(
    supplier_id=1,
    created_by=user_id,
    expected_delivery_date=date(2025, 12, 1),
    notes="Livraison urgente",
    internal_notes="Commande pour réapprovisionnement"
)
```

---

### **Étape 3 : Ajout de Lignes à la Commande**

#### Entité : `PurchaseOrderLine`

**Informations par ligne :**
- Produit (référence)
- Quantité commandée
- Prix unitaire d'achat
- Remise (%) sur la ligne
- Taux de TVA (%)
- Quantité reçue (initialement 0)
- Notes

**Calculs automatiques :**
- `line_total_ht` = (quantité × prix unitaire) - remise
- `line_total_ttc` = `line_total_ht` × (1 + TVA/100)

**Exemple d'ajout de ligne :**
```python
line = purchase_order.add_line(
    product_id=10,
    quantity=Decimal("100"),
    unit_price=Decimal("15.50"),
    discount_percent=Decimal("5.0"),  # 5% de remise
    tax_rate=Decimal("20.0"),  # 20% TVA
    notes="Produit fragile"
)
```

**Règles métier :**
- ✅ Les lignes ne peuvent être ajoutées/modifiées que si le statut est `draft`
- ✅ La quantité doit être > 0
- ✅ Le prix unitaire doit être ≥ 0
- ✅ La remise doit être entre 0% et 100%

---

### **Étape 4 : Confirmation de la Commande**

**Action :** `purchase_order.confirm(user_id)`

**Ce qui se passe :**
1. Vérification que le statut est `draft` ou `sent`
2. Vérification qu'il y a au moins une ligne
3. Changement du statut à `confirmed`
4. Enregistrement de l'utilisateur qui confirme
5. Enregistrement de la date de confirmation
6. Émission d'un événement domaine : `PurchaseOrderConfirmedDomainEvent`

**Règles :**
- ❌ Impossible de confirmer une commande sans lignes
- ❌ Impossible de confirmer si déjà `received` ou `cancelled`

**Exemple :**
```python
purchase_order.confirm(user_id=current_user.id)
```

---

### **Étape 5 : Réception des Marchandises**

#### Processus de Réception

**Option A : Réception Partielle**
- Mise à jour de `quantity_received` sur chaque ligne
- Le statut passe automatiquement à `partially_received` si toutes les lignes ne sont pas complètes

**Option B : Réception Totale**
- Toutes les lignes ont `quantity_received == quantity`
- Le statut passe à `received`
- La date de réception est enregistrée
- Émission d'un événement domaine : `PurchaseOrderReceivedDomainEvent`

**Exemple de réception :**
```python
# Réception partielle d'une ligne
line.quantity_received = Decimal("50")  # Sur 100 commandés

# Vérification automatique du statut
purchase_order.mark_received()  # Passe à "partially_received" ou "received"
```

---

### **Étape 6 : Mise à Jour du Stock**

#### Intégration avec le Module Stock

**Quand une commande est reçue :**
1. Création d'un `StockMovement` de type `entry`
2. Mise à jour du `StockItem` (augmentation de `physical_quantity`)
3. Mise à jour du coût d'achat du produit (si nécessaire)

**Exemple de mouvement de stock :**
```python
# Créer un mouvement d'entrée pour chaque ligne reçue
stock_movement = StockMovement.create(
    product_id=line.product_id,
    location_id=default_location_id,
    quantity=line.quantity_received,
    type='entry',
    reason=f'Réception commande {purchase_order.number}',
    user_id=current_user.id,
    related_document_type='purchase_order',
    related_document_id=purchase_order.id
)
```

**Note :** Cette intégration sera implémentée dans le module Stock (User Story 3).

---

## 🔗 Relations entre Entités

```
Supplier (Fournisseur)
  ├── SupplierAddress (Adresses)
  ├── SupplierContact (Contacts)
  ├── SupplierConditions (Conditions commerciales)
  └── PurchaseOrder (Commandes d'achat)
        └── PurchaseOrderLine (Lignes de commande)
              └── Product (Produit)
                    └── StockItem (Stock)
                          └── StockMovement (Mouvement d'entrée)
```

---

## 📊 Exemple de Scénario Complet

### Scénario : Réapprovisionnement d'un produit

**1. Création du fournisseur (si nouveau)**
```
POST /api/suppliers
{
  "name": "Grossiste Plomberie Pro",
  "email": "contact@gpp.fr",
  "company_name": "GPP SARL",
  "siret": "12345678901234",
  "payment_terms_days": 30,
  "default_discount_percent": 5.0,
  "minimum_order_amount": 500.00
}
```

**2. Création de la commande d'achat**
```
POST /api/purchase-orders
{
  "supplier_id": 1,
  "expected_delivery_date": "2025-12-01",
  "notes": "Livraison urgente - stock critique"
}
→ Retourne: { "id": 1, "number": "PO-2025-00001", "status": "draft" }
```

**3. Ajout de lignes**
```
POST /api/purchase-orders/1/lines
{
  "product_id": 10,
  "quantity": 100,
  "unit_price": 15.50,
  "discount_percent": 5.0,
  "tax_rate": 20.0
}
```

**4. Confirmation de la commande**
```
POST /api/purchase-orders/1/confirm
→ Statut passe à "confirmed"
```

**5. Réception des marchandises**
```
PUT /api/purchase-orders/1/lines/1
{
  "quantity_received": 100  // Réception complète
}
→ Statut passe automatiquement à "received"
```

**6. Mise à jour du stock (automatique via événement domaine)**
```
StockMovement créé automatiquement:
- Type: "entry"
- Quantité: 100
- Produit: ID 10
- Raison: "Réception commande PO-2025-00001"
```

---

## 🎯 Points Clés

### ✅ Avantages du Design

1. **Traçabilité complète** : Chaque mouvement de stock est lié à une commande d'achat
2. **Flexibilité** : Réception partielle possible
3. **Séparation des responsabilités** : Module Achat indépendant du module Stock
4. **Événements domaine** : Intégration future facilitée via événements
5. **Workflow clair** : Statuts bien définis avec règles métier

### ⚠️ Limitations Actuelles

1. **Pas encore intégré avec Stock** : Les mouvements de stock ne sont pas créés automatiquement (à implémenter dans US3)
2. **Pas de factures fournisseurs** : Module facturation fournisseur non implémenté (Phase 2)
3. **Pas de gestion des retours** : Retours fournisseur non gérés

### 🔮 Évolutions Futures

1. **Intégration Stock** : Création automatique de `StockMovement` lors de la réception
2. **Factures Fournisseurs** : Lien entre commande d'achat et facture fournisseur
3. **Réceptions Multi-Emplacements** : Réception directe dans différents entrepôts
4. **Workflow d'Approbation** : Validation hiérarchique pour commandes importantes
5. **Alertes** : Notifications pour commandes en retard, réceptions attendues

---

## 📝 Résumé

Le flux d'achat suit un cycle clair :
1. **Fournisseur** → Création et gestion
2. **Commande** → Création en brouillon
3. **Lignes** → Ajout de produits
4. **Confirmation** → Validation de la commande
5. **Réception** → Enregistrement des quantités reçues
6. **Stock** → Mise à jour automatique (à implémenter)

Chaque étape respecte les règles métier et maintient la cohérence des données.

