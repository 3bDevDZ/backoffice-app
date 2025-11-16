# 📋 Meilleures Pratiques : Réceptions Partielles de Commandes d'Achat

## 🎯 Vue d'Ensemble

Ce document présente les meilleures pratiques pour gérer les réceptions partielles de commandes d'achat et la mise à jour du stock dans un système de gestion commerciale.

---

## ✅ Approche Recommandée : **Mise à Jour Immédiate du Stock**

### Principe
**Le stock doit être mis à jour immédiatement dès qu'une quantité est reçue, même partiellement.**

### Avantages

1. **Disponibilité Immédiate** ✅
   - Les produits reçus sont disponibles immédiatement pour la vente
   - Pas d'attente jusqu'à la réception complète de la commande
   - Améliore la rotation des stocks

2. **Traçabilité Complète** ✅
   - Chaque réception partielle crée un mouvement de stock distinct
   - Historique détaillé de toutes les réceptions
   - Facilite l'audit et la conformité

3. **Gestion des Erreurs** ✅
   - Plus facile de corriger une réception partielle spécifique
   - Possibilité d'annuler une réception partielle sans affecter les autres
   - Meilleure granularité dans la gestion des erreurs

4. **Performance Opérationnelle** ✅
   - Les équipes peuvent utiliser le stock immédiatement
   - Réduction des délais de traitement
   - Meilleure réactivité aux besoins clients

5. **Conformité Comptable** ✅
   - Chaque réception peut être facturée séparément
   - Meilleure gestion des écarts de réception
   - Traçabilité pour les audits

### Inconvénients

1. **Complexité** ⚠️
   - Plus de mouvements de stock à gérer
   - Nécessite une gestion des corrections plus sophistiquée

2. **Performance Base de Données** ⚠️
   - Plus d'insertions dans la table `stock_movements`
   - Nécessite une indexation appropriée

---

## 🔄 Architecture Implémentée

### 1. Domain Events pour Granularité

```python
# Event déclenché à chaque réception partielle
PurchaseOrderLineReceivedDomainEvent
  - purchase_order_id
  - line_id
  - product_id
  - quantity_received (incrémentale)
  - location_id
```

**Avantages :**
- Séparation des responsabilités (DDD)
- Traçabilité fine
- Facilite les corrections futures

### 2. Mouvements de Stock Incrémentaux

Chaque réception partielle crée un mouvement de stock séparé :

```
Réception 1: 50 unités → StockMovement #1 (50 unités)
Réception 2: 30 unités → StockMovement #2 (30 unités)
Réception 3: 20 unités → StockMovement #3 (20 unités)
Total: 100 unités avec 3 mouvements distincts
```

**Avantages :**
- Historique complet
- Facilite les corrections
- Meilleure traçabilité

### 3. Gestion des Doublons

Le handler vérifie les quantités déjà traitées pour éviter les doublons :

```python
# Calcul de la quantité incrémentale
incremental_quantity = new_quantity_received - old_quantity_received

# Seule la quantité incrémentale est traitée
if incremental_quantity > 0:
    # Créer mouvement de stock
```

---

## 🛡️ Gestion des Cas Limites

### 1. Correction d'une Réception Partielle

**Scénario :** Une réception partielle a été saisie incorrectement.

**Solution :**
- Créer un mouvement de stock inverse (adjustment)
- Corriger la quantité reçue
- Créer un nouveau mouvement avec la quantité corrigée

**Exemple :**
```
Réception incorrecte: 50 unités
Correction: -50 (adjustment)
Nouvelle réception: 30 unités
Résultat: Stock correct avec traçabilité complète
```

### 2. Annulation d'une Réception Partielle

**Scénario :** Une réception partielle doit être annulée.

**Solution :**
- Créer un mouvement de stock inverse (exit ou adjustment)
- Réduire `quantity_received` sur la ligne
- Mettre à jour le statut de la commande

### 3. Réception Supérieure à la Commande

**Scénario :** Plus de produits reçus que commandés.

**Solution :**
- Valider la quantité reçue (peut dépasser la commandée)
- Créer un mouvement de stock pour la quantité totale
- Marquer la commande comme "over-received"
- Optionnel: Créer une commande d'achat supplémentaire pour l'excédent

### 4. Réception à Plusieurs Emplacements

**Scénario :** Les produits sont reçus dans différents entrepôts.

**Solution :**
- Chaque réception partielle peut spécifier un `location_id`
- Créer des mouvements de stock séparés par emplacement
- Gérer le stock par emplacement individuellement

---

## 📊 Comparaison des Approches

### Approche 1 : Mise à Jour Immédiate (✅ Recommandée)

| Critère | Note | Commentaire |
|---------|------|-------------|
| Disponibilité | ⭐⭐⭐⭐⭐ | Stock disponible immédiatement |
| Traçabilité | ⭐⭐⭐⭐⭐ | Historique complet |
| Performance | ⭐⭐⭐⭐ | Plus de mouvements mais meilleure réactivité |
| Complexité | ⭐⭐⭐ | Plus complexe mais plus flexible |
| Conformité | ⭐⭐⭐⭐⭐ | Meilleure pour les audits |

### Approche 2 : Mise à Jour Différée (❌ Non Recommandée)

| Critère | Note | Commentaire |
|---------|------|-------------|
| Disponibilité | ⭐⭐ | Stock bloqué jusqu'à réception complète |
| Traçabilité | ⭐⭐⭐ | Moins de détails |
| Performance | ⭐⭐⭐⭐⭐ | Moins de mouvements |
| Complexité | ⭐⭐⭐⭐⭐ | Plus simple mais moins flexible |
| Conformité | ⭐⭐⭐ | Moins de détails pour les audits |

---

## 🔐 Bonnes Pratiques de Sécurité

### 1. Transactions Atomiques

```python
# Toute la réception doit être atomique
with get_session() as session:
    # 1. Mettre à jour quantity_received
    # 2. Créer mouvement de stock
    # 3. Mettre à jour physical_quantity
    # 4. Mettre à jour statut commande
    session.commit()  # Tout ou rien
```

### 2. Validation des Quantités

```python
# Vérifications avant traitement
- quantity_received >= 0
- quantity_received <= quantity_ordered
- location_id existe et est actif
- product_id existe et est actif
```

### 3. Gestion des Conflits

```python
# Utiliser le verrouillage de ligne pour éviter les race conditions
stock_item = session.query(StockItem).filter(
    StockItem.product_id == product_id,
    StockItem.location_id == location_id
).with_for_update().first()
```

### 4. Audit Trail Complet

Chaque mouvement de stock doit contenir :
- `user_id` : Qui a effectué la réception
- `created_at` : Quand la réception a eu lieu
- `reason` : Raison du mouvement (référence commande)
- `related_document_type` et `related_document_id` : Lien vers la commande

---

## 📈 Optimisations Recommandées

### 1. Indexation de la Base de Données

```sql
-- Index pour les requêtes fréquentes
CREATE INDEX idx_stock_movements_related_doc 
ON stock_movements(related_document_type, related_document_id);

CREATE INDEX idx_stock_movements_product_date 
ON stock_movements(product_id, created_at);
```

### 2. Agrégation des Mouvements

Pour les rapports, agréger les mouvements par période :

```python
# Au lieu de compter tous les mouvements
# Utiliser des vues matérialisées ou des agrégations
SELECT 
    product_id,
    SUM(quantity) as total_received,
    COUNT(*) as receipt_count
FROM stock_movements
WHERE related_document_type = 'purchase_order'
GROUP BY product_id
```

### 3. Cache des Niveaux de Stock

Pour améliorer les performances, mettre en cache les niveaux de stock :

```python
# Cache Redis pour les niveaux de stock fréquemment consultés
cache_key = f"stock:{product_id}:{location_id}"
redis.set(cache_key, stock_item.physical_quantity, ex=300)
```

---

## 🎓 Standards de l'Industrie

### ERP Standards (SAP, Oracle, Microsoft Dynamics)

Tous les ERP majeurs utilisent la **mise à jour immédiate** :

1. **SAP** : Les réceptions partielles mettent à jour le stock immédiatement
2. **Oracle EBS** : Chaque réception crée un mouvement de stock
3. **Microsoft Dynamics** : Stock mis à jour à chaque réception partielle

### Normes Comptables

- **IFRS** : Exige la traçabilité complète des mouvements de stock
- **GAAP** : Nécessite un historique détaillé pour les audits
- **ISO 9001** : Exige la traçabilité des réceptions

---

## ✅ Recommandations Finales

### ✅ À FAIRE

1. **Mettre à jour le stock immédiatement** à chaque réception partielle
2. **Créer un mouvement de stock distinct** pour chaque réception
3. **Utiliser des Domain Events** pour la séparation des responsabilités
4. **Valider toutes les quantités** avant traitement
5. **Maintenir un audit trail complet** avec user_id, timestamp, reason
6. **Gérer les corrections** avec des mouvements inverses
7. **Utiliser des transactions atomiques** pour garantir la cohérence

### ❌ À ÉVITER

1. ❌ Attendre la réception complète pour mettre à jour le stock
2. ❌ Agréger plusieurs réceptions en un seul mouvement
3. ❌ Permettre des quantités négatives sans validation
4. ❌ Oublier de mettre à jour le statut de la commande
5. ❌ Créer des mouvements de stock sans traçabilité
6. ❌ Ignorer les erreurs de réception partielle

---

## 🔄 Workflow Recommandé

```
1. Réception Partielle
   ↓
2. Validation (quantité, location, product)
   ↓
3. Mise à jour quantity_received
   ↓
4. Calcul quantité incrémentale
   ↓
5. Déclenchement Domain Event
   ↓
6. Création StockMovement (incrémental)
   ↓
7. Mise à jour StockItem.physical_quantity
   ↓
8. Mise à jour statut commande (partially_received/received)
   ↓
9. Commit transaction (atomique)
```

---

## 📝 Conclusion

L'approche de **mise à jour immédiate du stock** est la meilleure pratique pour :

- ✅ Disponibilité immédiate des produits
- ✅ Traçabilité complète
- ✅ Conformité comptable
- ✅ Flexibilité opérationnelle
- ✅ Standards de l'industrie

Cette approche est déjà implémentée dans le système et suit les meilleures pratiques de l'industrie.

