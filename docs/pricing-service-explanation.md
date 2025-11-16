# 💰 Service Pricing - Explication

## 🎯 Qu'est-ce qu'un Pricing Service ?

Un **Pricing Service** est un service applicatif qui centralise toute la logique de **calcul de prix, remises et tarification** dans l'application. Il encapsule les règles métier complexes liées à la tarification qui dépassent le simple calcul arithmétique.

## 🔍 Différence avec les calculs dans les modèles de domaine

### Ce qui existe déjà (dans Quote/QuoteLine)

Actuellement, les calculs de prix sont dans les modèles de domaine :

```python
# Dans QuoteLine.calculate_totals()
subtotal = self.quantity * self.unit_price
discount_amount = subtotal * (self.discount_percent / Decimal(100))
self.line_total_ht = subtotal - discount_amount
self.line_total_ttc = self.line_total_ht * (Decimal(1) + self.tax_rate / Decimal(100))

# Dans Quote.calculate_totals()
lines_subtotal = sum(line.line_total_ht for line in self.lines)
self.discount_amount = lines_subtotal * (self.discount_percent / Decimal(100))
self.subtotal = lines_subtotal - self.discount_amount
self.tax_amount = sum(line.line_total_ttc - line.line_total_ht for line in self.lines)
self.total = self.subtotal + self.tax_amount
```

**Ces calculs sont corrects** pour des cas simples, mais ils ne gèrent pas :

### Ce qu'un Pricing Service apporterait

Un **Pricing Service** gérerait des **règles métier complexes** comme :

#### 1. **Tarification dynamique basée sur le client**

```python
def get_price_for_customer(self, product_id: int, customer_id: int, quantity: Decimal) -> Decimal:
    """
    Calcule le prix d'un produit pour un client spécifique.
    - Utilise la grille tarifaire du client (CommercialConditions.price_list_id)
    - Applique les remises volume (ex: -5% si quantité > 100)
    - Applique les remises fidélité
    - Vérifie les prix négociés spécifiques
    """
    # Logique complexe qui nécessite :
    # - Product
    # - Customer + CommercialConditions
    # - PriceList (future table)
    # - VolumeDiscountRules (future table)
    # - NegotiatedPrices (future table)
```

#### 2. **Calcul de remises complexes**

```python
def calculate_discounts(self, quote_lines: List[QuoteLine], customer_id: int) -> Dict:
    """
    Calcule les remises en appliquant plusieurs règles :
    - Remise client par défaut (CommercialConditions.default_discount_percent)
    - Remise volume globale (ex: -2% si total > 1000€)
    - Remise produit spécifique (ex: -10% sur catégorie "Promo")
    - Remise saisonnière (ex: -5% en janvier)
    - Remise fidélité (ex: -3% si client depuis > 2 ans)
    """
    # Logique qui combine plusieurs sources de remises
```

#### 3. **Gestion des grilles tarifaires**

```python
def get_price_from_price_list(self, product_id: int, price_list_id: int, quantity: Decimal) -> Decimal:
    """
    Récupère le prix depuis une grille tarifaire.
    - Prix de base du produit
    - Prix dans la grille tarifaire du client
    - Prix dégressifs selon quantité
    """
    # Nécessite une table price_lists et price_list_items
```

#### 4. **Calcul de marges et rentabilité**

```python
def calculate_margin(self, quote: Quote) -> Dict:
    """
    Calcule la marge sur un devis.
    - Coût total (sum des product.cost * quantity)
    - Prix de vente total
    - Marge brute (prix - coût)
    - Marge nette (après frais)
    - Taux de marge (%)
    """
    # Nécessite product.cost pour chaque ligne
```

#### 5. **Validation des prix minimums**

```python
def validate_minimum_price(self, product_id: int, unit_price: Decimal) -> bool:
    """
    Valide qu'un prix respecte les règles :
    - Prix minimum du produit (product.min_price)
    - Prix minimum de la grille tarifaire
    - Prix minimum négocié avec le client
    """
    # Logique de validation complexe
```

#### 6. **Application automatique de remises**

```python
def suggest_discounts(self, quote: Quote) -> List[Dict]:
    """
    Suggère des remises applicables :
    - "Vous êtes à 50€ du seuil pour une remise de 5%"
    - "Commande de 100+ unités = -3% automatique"
    - "Client VIP = -2% supplémentaire"
    """
    # Analyse et suggestions intelligentes
```

## 📊 Exemple concret : Pourquoi c'est utile

### Scénario : Client avec grille tarifaire

**Sans Pricing Service** (actuel) :
```python
# L'utilisateur doit manuellement :
# 1. Chercher le prix dans la grille tarifaire du client
# 2. Calculer les remises volume
# 3. Appliquer les remises client
# 4. Vérifier les prix minimums
# Tout cela dans le handler ou le frontend
```

**Avec Pricing Service** :
```python
# Le service fait tout automatiquement :
pricing_service = PricingService(session)
price = pricing_service.get_price_for_customer(
    product_id=123,
    customer_id=456,
    quantity=Decimal('50')
)
# Retourne le prix final avec toutes les règles appliquées
```

## 🏗️ Structure proposée du Pricing Service

```python
class PricingService:
    """Service for complex pricing calculations and discount application."""
    
    def __init__(self, session: Session):
        self.session = session
    
    # Prix de base
    def get_base_price(self, product_id: int) -> Decimal
    def get_price_from_price_list(self, product_id: int, price_list_id: int, quantity: Decimal) -> Decimal
    def get_price_for_customer(self, product_id: int, customer_id: int, quantity: Decimal) -> Decimal
    
    # Remises
    def calculate_line_discount(self, line: QuoteLine, customer_id: int) -> Decimal
    def calculate_document_discount(self, quote: Quote, customer_id: int) -> Decimal
    def apply_volume_discounts(self, lines: List[QuoteLine], customer_id: int) -> Dict
    def suggest_discounts(self, quote: Quote) -> List[Dict]
    
    # Validation
    def validate_minimum_price(self, product_id: int, unit_price: Decimal, customer_id: int) -> bool
    def validate_price_rules(self, quote: Quote) -> List[str]  # Retourne les erreurs
    
    # Marges
    def calculate_margin(self, quote: Quote) -> Dict
    def calculate_profitability(self, quote: Quote) -> Dict
    
    # Tarification dynamique
    def apply_pricing_rules(self, quote: Quote) -> Quote  # Applique toutes les règles
```

## ✅ Avantages d'un Pricing Service

1. **Centralisation** : Toute la logique de prix au même endroit
2. **Réutilisabilité** : Utilisable pour Quotes, Orders, Invoices
3. **Testabilité** : Facile à tester indépendamment
4. **Évolutivité** : Facile d'ajouter de nouvelles règles
5. **Séparation des responsabilités** : Les modèles de domaine restent simples

## ❌ Inconvénients / Quand ne pas l'utiliser

- **Complexité inutile** : Si les règles de prix sont très simples
- **Over-engineering** : Si on n'a qu'un seul type de remise
- **Performance** : Ajoute une couche supplémentaire (mais négligeable)

## 🎯 Recommandation pour ce projet

### Option 1 : Ne pas créer le Pricing Service (actuel)

**Justification** :
- Les calculs actuels dans Quote/QuoteLine sont suffisants pour le MVP
- Pas de grilles tarifaires complexes dans les spécifications
- Pas de remises volume automatiques
- Les remises sont gérées manuellement par l'utilisateur

**Avantages** :
- Code plus simple
- Moins de couches
- Suffisant pour le MVP

### Option 2 : Créer un Pricing Service minimal

**Si vous voulez l'ajouter**, voici ce qu'il devrait contenir :

```python
class PricingService:
    """Service for price calculation and discount application."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_customer_price(self, product_id: int, customer_id: int) -> Decimal:
        """Get price for a product considering customer's default discount."""
        # 1. Get base product price
        # 2. Apply customer's default_discount_percent if exists
        # 3. Return final price
    
    def calculate_quote_totals(self, quote: Quote) -> Dict:
        """Calculate all totals for a quote with discounts."""
        # Centralise le calcul actuel de Quote.calculate_totals()
        # Mais permet d'ajouter des règles futures facilement
    
    def validate_price(self, product_id: int, unit_price: Decimal, customer_id: int) -> bool:
        """Validate that price meets minimum requirements."""
        # Vérifie product.min_price si existe
        # Vérifie customer price limits si existent
```

## 📝 Conclusion

**Pour le MVP actuel** : Le Pricing Service n'est **pas nécessaire** car :
- ✅ Les calculs sont simples (prix × quantité - remise + TVA)
- ✅ Pas de grilles tarifaires complexes
- ✅ Pas de remises automatiques complexes
- ✅ Les modèles de domaine gèrent déjà les calculs de base

**Pour l'avenir** : Le Pricing Service serait utile si vous ajoutez :
- 📊 Grilles tarifaires par client
- 📈 Remises volume automatiques
- 🎯 Prix négociés spécifiques
- 💰 Calculs de marge complexes
- 🔄 Synchronisation avec systèmes externes de tarification

**Recommandation** : **Garder les calculs dans les modèles de domaine pour le MVP**, et créer le Pricing Service plus tard si les besoins évoluent vers des règles de tarification plus complexes.

