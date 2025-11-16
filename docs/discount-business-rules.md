# 📋 Règles Métier et Bonnes Pratiques pour les Discounts

## 🎯 Vue d'ensemble

Ce document définit les règles métier et bonnes pratiques pour la gestion des discounts (remises) dans le système CommerceFlow.

---

## 1. 🔍 Distinction entre Prix et Discounts

### ⚠️ Règle fondamentale : **Prix ≠ Discount**

Un **discount** est une **réduction appliquée sur un prix de référence**. Il ne faut PAS confondre :

| Type | Nature | Est-ce un discount ? |
|------|--------|---------------------|
| **Prix de base** | Prix standard du produit | ❌ Non |
| **Price List** | Prix négocié pour un client | ❌ Non - C'est un prix différent |
| **Volume Pricing** | Prix dégressif selon quantité | ❌ Non - C'est un prix différent |
| **Promotional Price** | Prix promotionnel temporaire | ❌ Non - C'est un prix différent |
| **Customer Discount** | Réduction % sur le prix de base | ✅ Oui - C'est un vrai discount |

### 📊 Exemple concret :

```
Produit : 100€ (prix de base)

Scénario 1 : Price List
- Client a une price list : 90€
- ❌ Ce n'est PAS un discount de 10%
- ✅ C'est un prix négocié de 90€

Scénario 2 : Customer Discount
- Client a 10% de discount par défaut
- Prix calculé : 100€ - 10% = 90€
- ✅ C'est un discount de 10% sur le prix de base
```

---

## 2. 📐 Règles de Validation des Discounts

### 2.1. Plage de valeurs

```python
# ✅ VALIDE
discount_percent >= 0 AND discount_percent <= 100

# ❌ INVALIDE
discount_percent < 0        # Discount négatif = augmentation de prix
discount_percent > 100      # Discount > 100% = prix négatif
```

**Implémentation actuelle :** ✅ Respectée
- `QuoteLine.create()` : Validation 0-100%
- `Quote.create()` : Validation 0-100%
- `PricingService.validate_price_rules()` : Validation 0-100%

### 2.2. Prix minimum après discount

```python
# ✅ RÈGLE MÉTIER
final_price = base_price * (1 - discount_percent / 100)
assert final_price >= 0  # Le prix final ne peut pas être négatif
```

**Implémentation actuelle :** ⚠️ Partiellement implémentée
- Validation du prix minimum existe dans `validate_minimum_price()` mais pas encore complète

### 2.3. Discounts cumulatifs

**Règle métier :** Les discounts peuvent être appliqués à deux niveaux :

1. **Discount au niveau ligne** (`QuoteLine.discount_percent`)
   - Appliqué sur le prix unitaire de la ligne
   - Calcul : `line_total_ht = (quantity * unit_price) * (1 - discount_percent / 100)`

2. **Discount au niveau document** (`Quote.discount_percent`)
   - Appliqué sur le sous-total HT après les discounts de lignes
   - Calcul : `subtotal = lines_subtotal * (1 - discount_percent / 100)`

**⚠️ Attention :** Les discounts ne sont PAS cumulatifs entre eux, ils sont appliqués séquentiellement :
- D'abord le discount de ligne
- Ensuite le discount de document sur le total des lignes

**Implémentation actuelle :** ✅ Correcte
```python
# QuoteLine.calculate_totals()
subtotal = self.quantity * self.unit_price
discount_amount = subtotal * (self.discount_percent / Decimal(100))
self.line_total_ht = subtotal - discount_amount

# Quote.calculate_totals()
lines_subtotal = sum(line.line_total_ht for line in self.lines)
self.discount_amount = lines_subtotal * (self.discount_percent / Decimal(100))
self.subtotal = lines_subtotal - self.discount_amount
```

---

## 3. 🎯 Ordre de Priorité des Prix

### 3.1. Hiérarchie des prix (PricingService)

L'ordre de priorité actuel est **correct** :

```
1. PRIORITÉ 1 : Promotional Price (PRIORITÉ MAXIMALE)
   - Prix promotionnel actif
   - Source: 'promotional_price'
   - ❌ N'est PAS un discount

2. PRIORITÉ 2 : Volume Pricing
   - Prix dégressif selon quantité
   - Source: 'volume_pricing'
   - ❌ N'est PAS un discount

3. PRIORITÉ 3 : Price List
   - Prix négocié pour le client
   - Source: 'price_list'
   - ❌ N'est PAS un discount

4. PRIORITÉ 4 : Customer Discount
   - Réduction % sur prix de base
   - Source: 'customer_discount'
   - ✅ C'est un VRAI discount
```

### 3.2. Règle métier : Un seul prix à la fois

**Règle :** Un seul mécanisme de prix s'applique à la fois. Si un prix promotionnel existe, il remplace tout le reste.

**Implémentation actuelle :** ✅ Correcte
- Utilisation de `elif` et `if source == 'base'` pour éviter les conflits

---

## 4. 💰 Calcul des Discounts

### 4.1. Discount au niveau ligne

```python
# ✅ FORMULE CORRECTE
subtotal = quantity * unit_price
discount_amount = subtotal * (discount_percent / 100)
line_total_ht = subtotal - discount_amount
```

**Implémentation actuelle :** ✅ Correcte dans `QuoteLine.calculate_totals()`

### 4.2. Discount au niveau document

```python
# ✅ FORMULE CORRECTE
lines_subtotal = sum(line.line_total_ht for line in lines)
document_discount_amount = lines_subtotal * (discount_percent / 100)
subtotal = lines_subtotal - document_discount_amount
```

**Implémentation actuelle :** ✅ Correcte dans `Quote.calculate_totals()`

### 4.3. ⚠️ Règle importante : Ne pas calculer de discount pour les price lists

**Règle métier :** Si le prix vient d'une price list, d'un prix promotionnel ou d'un volume pricing, il ne faut **PAS** calculer de `discount_amount` car ce n'est pas un discount.

**Exemple incorrect :**
```python
# ❌ MAUVAIS
base_price = 100€
price_list_price = 90€
discount_amount = 100€ - 90€ = 10€  # ❌ FAUX ! Ce n'est pas un discount
```

**Exemple correct :**
```python
# ✅ BON
base_price = 100€
price_list_price = 90€
discount_amount = 0€  # ✅ Correct : pas de discount, juste un prix différent
applied_discount_percent = 0%  # ✅ Correct
```

**Implémentation actuelle :** ✅ Corrigée dans `PricingService.get_price_for_customer()`
```python
# Only calculate discount_amount if we actually applied a discount (customer_discount)
discount_amount = Decimal(0)
if source == 'customer_discount':
    discount_amount = base_price - final_price
```

---

## 5. 🔐 Règles de Sécurité et Contrôle

### 5.1. Autorisation pour appliquer des discounts

**Règle métier :** Seuls les utilisateurs avec les rôles appropriés peuvent :
- Modifier les discounts de lignes
- Modifier les discounts de document
- Dépasser les discounts par défaut du client

**Implémentation actuelle :** ✅ Vérifiée via `@require_roles_or_redirect('admin', 'commercial')`

### 5.2. Limites de discount

**Règle métier recommandée :** 
- Discount par défaut client : Limité par les conditions commerciales
- Discount manuel : Peut nécessiter une approbation si > seuil (ex: > 20%)

**Implémentation actuelle :** ⚠️ Pas encore implémentée
- TODO: Ajouter validation de seuil maximum de discount

### 5.3. Traçabilité

**Règle métier :** Tous les discounts doivent être traçables :
- Qui a appliqué le discount ?
- Quand ?
- Pourquoi (notes internes) ?

**Implémentation actuelle :** ⚠️ Partiellement implémentée
- `created_by` existe sur Quote
- Pas de champ `discount_applied_by` ou `discount_reason`

---

## 6. 📊 Règles de Calcul de la TVA

### 6.1. TVA sur le prix après discount

**Règle métier :** La TVA est calculée sur le prix HT **après** application des discounts.

```python
# ✅ CORRECT
line_total_ht = (quantity * unit_price) * (1 - discount_percent / 100)
line_total_ttc = line_total_ht * (1 + tax_rate / 100)
```

**Implémentation actuelle :** ✅ Correcte dans `QuoteLine.calculate_totals()`

### 6.2. TVA sur discount document

**Règle métier :** Le discount document est appliqué **avant** le calcul de la TVA.

```python
# ✅ CORRECT
lines_subtotal = sum(line.line_total_ht for line in lines)
document_discount = lines_subtotal * (discount_percent / 100)
subtotal_ht = lines_subtotal - document_discount
tax_amount = sum(line.line_total_ttc - line.line_total_ht for line in lines)
total_ttc = subtotal_ht + tax_amount
```

**Implémentation actuelle :** ✅ Correcte dans `Quote.calculate_totals()`

---

## 7. ✅ Checklist de Validation

Avant de valider un discount, vérifier :

- [ ] Le discount est entre 0% et 100%
- [ ] Le prix final après discount est >= 0
- [ ] Le discount est appliqué au bon niveau (ligne ou document)
- [ ] La TVA est calculée sur le prix après discount
- [ ] Le discount est traçable (qui, quand, pourquoi)
- [ ] Le discount respecte les limites autorisées
- [ ] Le discount n'est pas confondu avec un prix différent (price list, etc.)

---

## 8. 🚨 Cas d'Erreur Courants à Éviter

### ❌ Erreur 1 : Confondre price list et discount
```python
# ❌ MAUVAIS
if price_list_price < base_price:
    discount = base_price - price_list_price  # ❌ FAUX !
```

### ❌ Erreur 2 : Appliquer discount sur un prix déjà réduit
```python
# ❌ MAUVAIS
promotional_price = 80€
customer_discount = 10%
final_price = 80€ - 10% = 72€  # ❌ FAUX ! Le discount ne s'applique pas sur prix promo
```

### ❌ Erreur 3 : Cumuler discounts de manière incorrecte
```python
# ❌ MAUVAIS
line_discount = 10%
document_discount = 5%
final_discount = 10% + 5% = 15%  # ❌ FAUX ! Les discounts ne s'additionnent pas
```

### ✅ Correct
```python
# ✅ BON
line_total = 100€ * (1 - 10%) = 90€
document_discount = 90€ * 5% = 4.50€
final_total = 90€ - 4.50€ = 85.50€
```

---

## 9. 📝 Recommandations Futures

### 9.1. Validation de seuil de discount
- Ajouter un champ `max_discount_percent` dans `CommercialConditions`
- Exiger approbation si discount > seuil

### 9.2. Historique des discounts
- Enregistrer chaque modification de discount
- Traçabilité complète (qui, quand, pourquoi)

### 9.3. Discounts conditionnels
- Discount selon montant total de commande
- Discount selon catégorie de produit
- Discount selon période (saisonnier)

### 9.4. Validation de marge minimum
- Vérifier que le discount ne fait pas passer la marge en dessous d'un seuil
- Alerter si marge < seuil minimum

---

## 10. ✅ Conclusion

Les corrections apportées respectent les bonnes pratiques :

1. ✅ **Distinction claire** entre prix et discounts
2. ✅ **Validation** des plages de valeurs (0-100%)
3. ✅ **Calcul correct** des discounts (ligne et document)
4. ✅ **Pas de confusion** entre price list et discount
5. ✅ **Ordre de priorité** respecté pour les prix

**Les changements sont prêts à être validés !** ✅

