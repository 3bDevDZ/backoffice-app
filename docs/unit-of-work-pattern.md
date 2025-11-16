# Pattern Unit of Work avec SQLAlchemy

## Vue d'ensemble

**Oui, SQLAlchemy (l'ORM utilisé par Flask) supporte nativement le pattern Unit of Work.**

Le pattern Unit of Work maintient une liste des objets modifiés pendant une transaction et coordonne l'écriture des changements et la résolution des problèmes de concurrence.

## Implémentation dans notre projet

### 1. Session SQLAlchemy = Unit of Work

Dans SQLAlchemy, chaque **Session** est une instance du pattern Unit of Work :

```python
# app/infrastructure/db.py
@contextmanager
def get_session() -> Iterator[Session]:
    """
    Get a database session with automatic transaction management.
    Domain events are dispatched after commit.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()  # Unit of Work: commit toutes les modifications
    except Exception:
        session.rollback()  # Unit of Work: annule toutes les modifications
        raise
    finally:
        session.close()
```

### 2. Caractéristiques du pattern Unit of Work dans SQLAlchemy

#### a) **Identity Map**
La session maintient une **Identity Map** qui garantit qu'un objet avec un ID donné n'existe qu'une seule fois dans la session :

```python
# Premier accès : requête DB
order1 = session.get(PurchaseOrder, 1)

# Deuxième accès : retourne le même objet depuis l'Identity Map
order2 = session.get(PurchaseOrder, 1)
assert order1 is order2  # True - même instance
```

#### b) **Change Tracking (Suivi des modifications)**
SQLAlchemy suit automatiquement tous les changements sur les objets attachés à la session :

```python
with get_session() as session:
    order = session.get(PurchaseOrder, 1)
    order.status = 'confirmed'  # Changement détecté automatiquement
    order.notes = 'Updated'
    # Pas besoin d'appeler session.update() - SQLAlchemy le fait automatiquement
    session.commit()  # Tous les changements sont persistés
```

#### c) **Transaction Management**
Toutes les opérations dans une session font partie d'une seule transaction :

```python
with get_session() as session:
    # Créer une commande
    order = PurchaseOrder.create(...)
    session.add(order)
    
    # Ajouter des lignes
    line1 = PurchaseOrderLine(...)
    line2 = PurchaseOrderLine(...)
    session.add_all([line1, line2])
    
    # Tout est dans la même transaction
    session.commit()  # Soit tout est sauvegardé, soit rien
```

#### d) **Automatic Flush**
SQLAlchemy fait automatiquement un `flush` avant les requêtes pour garantir la cohérence :

```python
with get_session() as session:
    order = PurchaseOrder.create(...)
    session.add(order)
    session.flush()  # Génère l'ID mais ne commit pas
    
    # Maintenant on peut utiliser order.id
    line = PurchaseOrderLine(purchase_order_id=order.id, ...)
    session.add(line)
    session.commit()  # Commit tout
```

### 3. Utilisation dans nos handlers

Nos command handlers utilisent le pattern Unit of Work :

```python
# app/application/purchases/commands/handlers.py
class CreatePurchaseOrderHandler(CommandHandler):
    def handle(self, command: CreatePurchaseOrderCommand) -> PurchaseOrder:
        with get_session() as session:  # Démarre une Unit of Work
            # Créer l'agrégat
            order = PurchaseOrder.create(
                supplier_id=command.supplier_id,
                created_by=command.created_by,
                order_date=command.order_date,
                expected_delivery_date=command.expected_delivery_date
            )
            session.add(order)  # Ajouté à l'Unit of Work
            session.flush()  # Génère l'ID
            
            # Ajouter des lignes
            for line_cmd in command.lines:
                line = PurchaseOrderLine.create(...)
                order.add_line(line)  # Modifie l'agrégat
                session.add(line)  # Ajouté à l'Unit of Work
            
            # Calculer les totaux
            order.calculate_totals()  # Modifie l'agrégat
            
            # Tous les changements sont suivis automatiquement
            session.commit()  # Unit of Work: commit tout ou rien
            
            return order
```

### 4. Gestion des événements de domaine

Notre implémentation dispatch les événements de domaine **après** le commit de la transaction :

```python
# app/infrastructure/db.py
@event.listens_for(Session, "after_commit")
def dispatch_domain_events(session):
    """Dispatch domain events after transaction commit."""
    # Collect domain events from all tracked aggregates
    domain_events = []
    for obj in session.identity_map.values():
        if hasattr(obj, 'get_domain_events'):
            domain_events.extend(obj.get_domain_events())
            obj.clear_domain_events()
    
    # Dispatch all events
    if domain_events:
        domain_event_dispatcher.dispatch_all(domain_events)
```

Cela garantit que :
- Les événements ne sont dispatchés que si la transaction réussit
- Les événements ont accès aux IDs générés
- L'ordre des événements est préservé

### 5. Avantages du pattern Unit of Work

1. **Atomicité** : Toutes les modifications sont dans une seule transaction
2. **Cohérence** : L'Identity Map garantit qu'un objet n'existe qu'une fois
3. **Performance** : Les changements sont batchés et envoyés en une seule fois
4. **Simplicité** : Pas besoin de gérer manuellement les INSERT/UPDATE/DELETE
5. **Isolation** : Chaque session a sa propre copie des objets

### 6. Bonnes pratiques

#### ✅ Utiliser `get_session()` comme context manager
```python
with get_session() as session:
    # Votre code
    session.commit()  # Automatique
```

#### ✅ Ne pas mélanger les sessions
```python
# ❌ Mauvais
order = session1.get(PurchaseOrder, 1)
line = PurchaseOrderLine(...)
line.purchase_order = order  # Erreur : objets de sessions différentes

# ✅ Bon
with get_session() as session:
    order = session.get(PurchaseOrder, 1)
    line = PurchaseOrderLine(...)
    line.purchase_order = order  # OK : même session
```

#### ✅ Utiliser `session.refresh()` pour recharger depuis la DB
```python
with get_session() as session:
    order = session.get(PurchaseOrder, 1)
    # ... modifications dans une autre session ...
    session.refresh(order)  # Recharge depuis la DB
```

#### ✅ Utiliser `session.expunge()` pour détacher un objet
```python
with get_session() as session:
    order = session.get(PurchaseOrder, 1)
    session.expunge(order)  # Détache de la session
    # order peut maintenant être utilisé hors de la session
```

### 7. Comparaison avec d'autres patterns

| Pattern | SQLAlchemy | Notre implémentation |
|---------|-----------|---------------------|
| **Unit of Work** | ✅ Session | ✅ `get_session()` |
| **Identity Map** | ✅ Automatique | ✅ Via Session |
| **Repository** | ⚠️ Pas natif | ✅ Via Query Objects |
| **Change Tracking** | ✅ Automatique | ✅ Via Session |
| **Transaction** | ✅ Automatique | ✅ Via context manager |

## Conclusion

SQLAlchemy implémente nativement le pattern Unit of Work via les **Sessions**. Notre code utilise ce pattern de manière cohérente :

- ✅ Tous les handlers utilisent `get_session()` comme context manager
- ✅ Les transactions sont gérées automatiquement (commit/rollback)
- ✅ Les événements de domaine sont dispatchés après commit
- ✅ L'Identity Map garantit la cohérence des objets
- ✅ Le change tracking est automatique

C'est une implémentation solide et conforme aux bonnes pratiques DDD/CQRS.

