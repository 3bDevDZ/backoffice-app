# 📦 Service Stock - Explication

## 🎯 Qu'est-ce qu'un Service dans l'Architecture DDD/CQRS ?

Dans une architecture **Domain-Driven Design (DDD)** avec **CQRS**, on distingue plusieurs couches :

1. **Domain Models** (`app/domain/models/`) : Contiennent la logique métier de base d'un agrégat
2. **Command/Query Handlers** (`app/application/*/handlers.py`) : Gèrent les opérations CRUD simples
3. **Services** (`app/services/`) : Contiennent la **logique métier complexe** qui dépasse un seul agrégat

## 🔍 Pourquoi un Service Stock ?

### Ce qui existe déjà dans les Handlers

Les handlers de commandes gèrent déjà :
- ✅ Création de mouvements de stock simples
- ✅ Réservation/relâchement de stock (via `StockItem.reserve()` / `StockItem.release()`)
- ✅ Ajustements de stock simples

### Ce qui manque et nécessite un Service

Un **Service Stock** est nécessaire pour gérer des opérations **complexes** qui :

1. **Impliquent plusieurs agrégats** (StockItem, StockMovement, Location, Product, Order)
2. **Requièrent des règles métier transversales** (RG-STOCK-001 à RG-STOCK-007)
3. **Nécessitent des calculs complexes** (valorisation FIFO/AVCO, disponibilité multi-emplacement)
4. **Gèrent des workflows complexes** (réservation pour commande avec vérifications multiples)

## 📋 Exemples de Fonctionnalités du Service Stock

### 1. Validation Complexe des Mouvements

```python
# Dans un handler simple, on fait :
movement = StockMovement.create(...)
session.add(movement)

# Dans le service, on valide AVANT de créer :
def validate_movement(self, movement_data):
    # RG-STOCK-003 : Mouvement nécessite emplacement source ET/OU destination
    # RG-STOCK-004 : Lot/Série obligatoire si produit tracé
    # RG-STOCK-005 : Inventaire bloque mouvements sur produits concernés
    # RG-STOCK-006 : Transfert : stock source ≥ quantité transférée
    # Vérifier si un inventaire est en cours pour ce produit
    # Vérifier si le produit nécessite un lot/série
    # Vérifier les capacités des emplacements
    # etc.
```

### 2. Réservation Multi-Emplacement

```python
# Le handler actuel ne gère qu'un seul emplacement
# Le service peut gérer :
def reserve_stock_for_order(self, order_id, order_lines):
    """
    Réserve du stock pour une commande en cherchant dans plusieurs emplacements.
    Stratégie :
    1. Chercher dans l'emplacement principal
    2. Si insuffisant, chercher dans les emplacements secondaires
    3. Optimiser pour minimiser les transferts
    4. Créer des réservations partielles si nécessaire
    """
    reservations = []
    for line in order_lines:
        # Logique complexe de recherche multi-emplacement
        # Gestion des priorités d'emplacement
        # Calcul des transferts nécessaires
        pass
    return reservations
```

### 3. Calcul de Disponibilité Globale

```python
def get_global_availability(self, product_id, variant_id=None):
    """
    Calcule la disponibilité totale d'un produit sur TOUS les emplacements.
    Utile pour :
    - Afficher le stock total dans le catalogue
    - Décider si on peut créer une commande
    - Calculer les besoins de réapprovisionnement
    """
    # Agrège les stocks de tous les emplacements
    # Soustrait les réservations
    # Retourne un résumé par emplacement
    pass
```

### 4. Validation des Règles Métier Transversales

```python
def validate_stock_rules(self, stock_item, operation):
    """
    Valide toutes les règles métier (RG-STOCK-001 à RG-STOCK-007)
    """
    # RG-STOCK-001 : Stock physique ≥ 0
    if stock_item.physical_quantity < 0:
        raise ValueError("Stock physique ne peut pas être négatif")
    
    # RG-STOCK-002 : Stock réservé ≤ stock physique
    if stock_item.reserved_quantity > stock_item.physical_quantity:
        raise ValueError("Stock réservé ne peut pas dépasser le stock physique")
    
    # RG-STOCK-005 : Inventaire bloque mouvements
    if self.is_inventory_in_progress(stock_item.product_id):
        raise ValueError("Un inventaire est en cours pour ce produit")
    
    # etc.
```

### 5. Calcul de Valorisation (FIFO, AVCO)

```python
def calculate_stock_value(self, stock_item, method='fifo'):
    """
    Calcule la valeur du stock selon la méthode choisie.
    - FIFO (First In, First Out) : utilise les mouvements d'entrée
    - AVCO (Average Cost) : moyenne pondérée
    - Standard : coût standard du produit
    """
    if method == 'fifo':
        # Analyse les mouvements d'entrée dans l'ordre chronologique
        # Calcule la valeur selon les coûts d'entrée
        pass
    elif method == 'avco':
        # Calcule la moyenne pondérée des coûts d'entrée
        pass
    # etc.
```

### 6. Gestion des Transferts Complexes

```python
def transfer_stock(self, from_location_id, to_location_id, product_id, quantity):
    """
    Gère un transfert de stock avec toutes les validations :
    1. Vérifie que le stock source est suffisant
    2. Vérifie la capacité de l'emplacement destination
    3. Crée le mouvement de sortie
    4. Crée le mouvement d'entrée
    5. Met à jour les deux StockItems
    6. Gère les erreurs (rollback si échec)
    """
    # Logique complexe de transfert atomique
    pass
```

### 7. Calcul des Besoins de Réapprovisionnement

```python
def calculate_reorder_needs(self, location_id=None):
    """
    Calcule les besoins de réapprovisionnement pour tous les produits
    selon les seuils (reorder_point, min_stock).
    """
    # Analyse tous les StockItems
    # Compare physical_quantity avec reorder_point
    # Suggère des quantités à commander (reorder_quantity)
    # Priorise selon l'urgence
    pass
```

## 🏗️ Structure Proposée du Service Stock

```python
# app/services/stock_service.py

class StockService:
    """
    Service pour la gestion complexe du stock.
    Contient la logique métier qui dépasse un seul agrégat.
    """
    
    def __init__(self, session):
        self.session = session
    
    # Validation
    def validate_movement(self, movement_data) -> bool:
        """Valide un mouvement selon toutes les règles métier."""
        pass
    
    def validate_stock_rules(self, stock_item, operation) -> bool:
        """Valide les règles RG-STOCK-001 à RG-STOCK-007."""
        pass
    
    # Réservation complexe
    def reserve_stock_for_order(self, order_id, order_lines) -> List[Reservation]:
        """Réserve du stock pour une commande (multi-emplacement)."""
        pass
    
    def release_stock_for_order(self, order_id) -> None:
        """Libère toutes les réservations d'une commande."""
        pass
    
    # Disponibilité
    def get_global_availability(self, product_id, variant_id=None) -> AvailabilitySummary:
        """Calcule la disponibilité globale d'un produit."""
        pass
    
    def check_availability(self, product_id, quantity, location_id=None) -> bool:
        """Vérifie si une quantité est disponible."""
        pass
    
    # Transferts
    def transfer_stock(self, from_location, to_location, product_id, quantity) -> TransferResult:
        """Gère un transfert de stock complexe."""
        pass
    
    # Valorisation
    def calculate_stock_value(self, stock_item, method='standard') -> Decimal:
        """Calcule la valeur du stock selon la méthode."""
        pass
    
    # Réapprovisionnement
    def calculate_reorder_needs(self, location_id=None) -> List[ReorderNeed]:
        """Calcule les besoins de réapprovisionnement."""
        pass
    
    # Inventaire
    def is_inventory_in_progress(self, product_id) -> bool:
        """Vérifie si un inventaire est en cours pour un produit."""
        pass
```

## 🔄 Utilisation dans les Handlers

Les handlers utilisent le service pour les opérations complexes :

```python
# app/application/stock/commands/handlers.py

class CreateStockMovementHandler(CommandHandler):
    def handle(self, command: CreateStockMovementCommand) -> StockMovement:
        with get_session() as session:
            # Utiliser le service pour validation complexe
            stock_service = StockService(session)
            stock_service.validate_movement({
                'type': command.movement_type,
                'quantity': command.quantity,
                'location_from_id': command.location_from_id,
                'location_to_id': command.location_to_id,
                'product_id': command.product_id
            })
            
            # Créer le mouvement (logique simple reste dans le handler)
            movement = StockMovement.create(...)
            session.add(movement)
            session.commit()
            return movement
```

## 📊 Comparaison : Handler vs Service

| Aspect | Handler | Service |
|--------|---------|---------|
| **Portée** | Un seul agrégat | Plusieurs agrégats |
| **Complexité** | Opérations simples (CRUD) | Logique métier complexe |
| **Exemples** | Créer un mouvement, réserver du stock | Réservation multi-emplacement, calcul FIFO |
| **Règles métier** | Validations simples | Règles transversales (RG-STOCK-*) |
| **Réutilisabilité** | Spécifique à une commande | Réutilisable par plusieurs handlers |

## ✅ Résumé

Le **Service Stock** est nécessaire pour :
- ✅ Centraliser la logique métier complexe
- ✅ Valider les règles métier transversales (RG-STOCK-*)
- ✅ Gérer les opérations multi-agrégats
- ✅ Calculer des valeurs complexes (FIFO, AVCO)
- ✅ Optimiser les réservations et transferts
- ✅ Faciliter les tests (logique isolée)

**Sans service** : La logique complexe serait dispersée dans plusieurs handlers, rendant le code difficile à maintenir et tester.

**Avec service** : La logique est centralisée, testable indépendamment, et réutilisable.

