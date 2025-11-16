# 📋 Règles Métier d'Application des Remises

## 🎯 Vue d'ensemble

Ce document définit les règles métier et bonnes pratiques pour l'application des remises (discounts) dans le système CommerceFlow, en tenant compte des interactions avec les listes de prix, les prix promotionnels, et les prix dégressifs.

---

## 1. 🔍 Principes Fondamentaux

### 1.1. Distinction entre Prix et Remise

**Règle fondamentale :** Un **prix** est une valeur monétaire fixe. Une **remise** est une réduction appliquée sur un prix de référence.

| Type | Nature | Est-ce une remise ? |
|------|--------|---------------------|
| **Prix de base** | Prix standard du produit | ❌ Non |
| **Price List** | Prix négocié pour un client | ❌ Non - C'est un prix différent |
| **Volume Pricing** | Prix dégressif selon quantité | ❌ Non - C'est un prix différent |
| **Promotional Price** | Prix promotionnel temporaire | ❌ Non - C'est un prix différent |
| **Customer Discount** | Réduction % sur le prix de référence | ✅ Oui - C'est une vraie remise |

### 1.2. Ordre de Priorité des Prix

L'ordre de priorité est **strict** et **non cumulatif** :

```
1. PRIORITÉ 1 : Promotional Price (PRIORITÉ MAXIMALE)
   - Prix promotionnel actif
   - Source: 'promotional_price'
   - ❌ N'est PAS une remise

2. PRIORITÉ 2 : Volume Pricing
   - Prix dégressif selon quantité
   - Source: 'volume_pricing'
   - ❌ N'est PAS une remise

3. PRIORITÉ 3 : Price List
   - Prix négocié pour le client
   - Source: 'price_list'
   - ❌ N'est PAS une remise

4. PRIORITÉ 4 : Customer Discount
   - Réduction % sur prix de base
   - Source: 'customer_discount'
   - ✅ C'est une VRAIE remise
```

**Règle importante :** Un seul mécanisme de prix s'applique à la fois. Si un prix promotionnel existe, il remplace tout le reste.

---

## 2. 📐 Règles d'Application des Remises

### 2.1. Remise Client (Customer Discount)

#### Règle 1 : Application uniquement sur le prix de base

**Règle métier :** La remise client (`default_discount_percent`) s'applique **uniquement** si :
- Aucun prix promotionnel n'est actif
- Aucun volume pricing ne s'applique
- Aucune price list n'est assignée au client
- Le prix utilisé est le **prix de base** du produit

**Exemple :**
```
Produit : 100€ (prix de base)
Client : 10% de remise par défaut

✅ CORRECT : 100€ - 10% = 90€
```

#### Règle 2 : Pas de remise sur les price lists

**Règle métier :** Si un client a une price list assignée, la remise client **ne s'applique PAS**.

**Exemple :**
```
Produit : 100€ (prix de base)
Price List : 90€ (prix négocié)
Client : 10% de remise par défaut

✅ CORRECT : Prix utilisé = 90€ (price list)
❌ INCORRECT : 90€ - 10% = 81€ (ne pas appliquer la remise)
```

**Justification :** Le prix de la price list est déjà un prix négocié. Appliquer une remise supplémentaire serait une double réduction.

#### Règle 3 : Pas de remise sur les prix promotionnels

**Règle métier :** Si un prix promotionnel est actif, la remise client **ne s'applique PAS**.

**Exemple :**
```
Produit : 100€ (prix de base)
Prix promotionnel : 75€ (actif)
Client : 10% de remise par défaut

✅ CORRECT : Prix utilisé = 75€ (promotional price)
❌ INCORRECT : 75€ - 10% = 67.50€ (ne pas appliquer la remise)
```

**Justification :** Le prix promotionnel est déjà un prix réduit. Appliquer une remise supplémentaire serait une double réduction.

#### Règle 4 : Pas de remise sur les volume pricing

**Règle métier :** Si un volume pricing s'applique, la remise client **ne s'applique PAS**.

**Exemple :**
```
Produit : 100€ (prix de base)
Volume pricing (≥10 unités) : 85€
Client : 10% de remise par défaut
Quantité : 10 unités

✅ CORRECT : Prix utilisé = 85€ (volume pricing)
❌ INCORRECT : 85€ - 10% = 76.50€ (ne pas appliquer la remise)
```

**Justification :** Le volume pricing est déjà un prix réduit basé sur la quantité. Appliquer une remise supplémentaire serait une double réduction.

---

## 3. 💼 Bonnes Pratiques B2B

### 3.1. Négociation Commerciale

**Principe :** Dans le commerce B2B, les prix sont généralement négociés individuellement avec chaque client.

**Pratiques courantes :**

1. **Price Lists (Listes de Prix)**
   - Prix négociés par produit
   - Valables pour une période déterminée
   - Peuvent être différentes selon les clients
   - **Ne doivent PAS avoir de remise supplémentaire**

2. **Remises Client (Customer Discounts)**
   - Remise globale par défaut pour un client
   - S'applique uniquement sur les prix de base
   - Peut être modifiée manuellement sur chaque ligne
   - **Ne s'applique PAS si une price list existe**

3. **Remises Ligne (Line Discounts)**
   - Remise spécifique à une ligne de commande/devis
   - Peut être négociée au cas par cas
   - S'applique sur le prix unitaire de la ligne
   - **Peut être combinée avec le prix de base + remise client**

### 3.2. Transparence et Traçabilité

**Règle métier :** Toutes les remises doivent être :
- **Visibles** : Affichées clairement sur les documents (devis, commandes)
- **Traçables** : Enregistrées avec qui, quand, pourquoi
- **Justifiables** : Raison documentée pour chaque remise exceptionnelle

---

## 4. 🔄 Scénarios d'Application

### Scénario 1 : Client avec Price List

```
Produit : 100€ (prix de base)
Price List : 90€ (assignée au client)
Client : 10% de remise par défaut

Résultat :
- Prix utilisé : 90€ (price list)
- Remise appliquée : 0%
- Total HT : 90€
```

**Règle :** La price list remplace le prix de base. Pas de remise supplémentaire.

### Scénario 2 : Client avec Remise par Défaut (sans Price List)

```
Produit : 100€ (prix de base)
Client : 10% de remise par défaut
Pas de price list assignée

Résultat :
- Prix utilisé : 100€ (prix de base)
- Remise appliquée : 10%
- Discount amount : 10€
- Total HT : 90€
```

**Règle :** La remise client s'applique sur le prix de base.

### Scénario 3 : Client avec Price List + Remise Manuelle

```
Produit : 100€ (prix de base)
Price List : 90€ (assignée au client)
Remise manuelle sur ligne : 5%

Résultat :
- Prix utilisé : 90€ (price list)
- Remise appliquée : 5% (manuelle)
- Discount amount : 4.50€
- Total HT : 85.50€
```

**Règle :** Une remise manuelle peut être appliquée même avec une price list, mais c'est une décision commerciale explicite.

### Scénario 4 : Prix Promotionnel Actif

```
Produit : 100€ (prix de base)
Prix promotionnel : 75€ (actif)
Client : 10% de remise par défaut

Résultat :
- Prix utilisé : 75€ (promotional price)
- Remise appliquée : 0%
- Total HT : 75€
```

**Règle :** Le prix promotionnel a la priorité maximale. Pas de remise supplémentaire.

### Scénario 5 : Volume Pricing + Price List

```
Produit : 100€ (prix de base)
Price List : 90€ (assignée au client)
Volume pricing (≥10 unités) : 85€
Quantité : 10 unités

Résultat :
- Prix utilisé : 85€ (volume pricing - priorité sur price list)
- Remise appliquée : 0%
- Total HT : 850€ (10 × 85€)
```

**Règle :** Le volume pricing a la priorité sur la price list. Pas de remise supplémentaire.

---

## 5. ⚠️ Cas d'Erreur à Éviter

### ❌ Erreur 1 : Double Application de Remise

```python
# ❌ MAUVAIS
price_result = pricing_service.get_price_for_customer(...)
# price_result.final_price = 90€ (déjà avec remise de 10%)
unit_price = price_result.final_price  # 90€
discount_percent = price_result.applied_discount_percent  # 10%
# Résultat : 90€ - 10% = 81€ (double réduction !)
```

**Correction :**
```python
# ✅ BON
if price_result.source == 'customer_discount':
    unit_price = price_result.base_price  # 100€
    discount_percent = price_result.applied_discount_percent  # 10%
    # Résultat : 100€ - 10% = 90€ (réduction unique)
```

### ❌ Erreur 2 : Remise sur Price List

```python
# ❌ MAUVAIS
price_list_price = 90€
customer_discount = 10%
final_price = 90€ - 10% = 81€  # ❌ FAUX !
```

**Correction :**
```python
# ✅ BON
price_list_price = 90€
customer_discount = 10%
final_price = 90€  # Pas de remise sur price list
```

### ❌ Erreur 3 : Remise sur Prix Promotionnel

```python
# ❌ MAUVAIS
promotional_price = 75€
customer_discount = 10%
final_price = 75€ - 10% = 67.50€  # ❌ FAUX !
```

**Correction :**
```python
# ✅ BON
promotional_price = 75€
customer_discount = 10%
final_price = 75€  # Pas de remise sur prix promotionnel
```

---

## 6. 📊 Matrice de Décision

| Source du Prix | Remise Client | Remise Ligne | Résultat |
|----------------|---------------|--------------|----------|
| **Base Price** | ✅ Oui (10%) | ✅ Oui (5%) | Prix base - 10% - 5% |
| **Base Price** | ✅ Oui (10%) | ❌ Non (0%) | Prix base - 10% |
| **Base Price** | ❌ Non (0%) | ✅ Oui (5%) | Prix base - 5% |
| **Price List** | ❌ Non | ✅ Oui (5%) | Prix price list - 5% (manuelle) |
| **Price List** | ❌ Non | ❌ Non | Prix price list (pas de remise) |
| **Promotional** | ❌ Non | ❌ Non | Prix promotionnel (pas de remise) |
| **Volume Pricing** | ❌ Non | ❌ Non | Prix volume (pas de remise) |

**Légende :**
- ✅ Oui : La remise peut être appliquée
- ❌ Non : La remise ne doit PAS être appliquée automatiquement

---

## 7. 🎯 Règles Spécifiques par Type de Prix

### 7.1. Prix de Base (Base Price)

**Règles :**
- ✅ Remise client par défaut : **APPLIQUÉE**
- ✅ Remise ligne manuelle : **APPLIQUÉE**
- ✅ Remise document : **APPLIQUÉE**

**Exemple :**
```
Prix de base : 100€
Remise client : 10%
Remise ligne : 5%
Remise document : 2%

Calcul :
1. Prix après remise client : 100€ - 10% = 90€
2. Prix après remise ligne : 90€ - 5% = 85.50€
3. Total lignes : 85.50€
4. Total après remise document : 85.50€ - 2% = 83.79€
```

### 7.2. Price List

**Règles :**
- ❌ Remise client par défaut : **NON APPLIQUÉE** (sauf décision commerciale)
- ✅ Remise ligne manuelle : **APPLIQUÉE** (décision commerciale)
- ✅ Remise document : **APPLIQUÉE**

**Exemple :**
```
Prix price list : 90€
Remise client : 10% (ignorée)
Remise ligne : 5% (manuelle)
Remise document : 2%

Calcul :
1. Prix utilisé : 90€ (price list)
2. Prix après remise ligne : 90€ - 5% = 85.50€
3. Total lignes : 85.50€
4. Total après remise document : 85.50€ - 2% = 83.79€
```

### 7.3. Prix Promotionnel

**Règles :**
- ❌ Remise client par défaut : **NON APPLIQUÉE**
- ❌ Remise ligne manuelle : **NON APPLIQUÉE** (sauf décision commerciale exceptionnelle)
- ✅ Remise document : **APPLIQUÉE** (sur le total)

**Exemple :**
```
Prix promotionnel : 75€
Remise client : 10% (ignorée)
Remise ligne : 0% (ignorée)
Remise document : 2%

Calcul :
1. Prix utilisé : 75€ (promotional)
2. Total lignes : 75€
3. Total après remise document : 75€ - 2% = 73.50€
```

### 7.4. Volume Pricing

**Règles :**
- ❌ Remise client par défaut : **NON APPLIQUÉE**
- ❌ Remise ligne manuelle : **NON APPLIQUÉE** (sauf décision commerciale exceptionnelle)
- ✅ Remise document : **APPLIQUÉE** (sur le total)

**Exemple :**
```
Prix volume (≥10 unités) : 85€
Quantité : 10 unités
Remise client : 10% (ignorée)
Remise ligne : 0% (ignorée)
Remise document : 2%

Calcul :
1. Prix utilisé : 85€ (volume pricing)
2. Total lignes : 850€ (10 × 85€)
3. Total après remise document : 850€ - 2% = 833€
```

---

## 8. 🔐 Règles de Sécurité et Contrôle

### 8.1. Autorisation pour Appliquer des Remises

**Règle métier :** Seuls les utilisateurs avec les rôles appropriés peuvent :
- Modifier les remises de lignes
- Modifier les remises de document
- Dépasser les remises par défaut du client

**Rôles autorisés :**
- `admin` : Toutes les remises
- `commercial` : Remises jusqu'à un seuil (ex: 20%)
- `direction` : Remises exceptionnelles (ex: > 20%)

### 8.2. Limites de Remise

**Règle métier recommandée :**
- Remise par défaut client : Limité par les conditions commerciales
- Remise manuelle ligne : Peut nécessiter une approbation si > seuil (ex: > 20%)
- Remise document : Peut nécessiter une approbation si > seuil (ex: > 15%)

**Implémentation actuelle :** ⚠️ Pas encore implémentée
- TODO: Ajouter validation de seuil maximum de remise

### 8.3. Traçabilité

**Règle métier :** Toutes les remises doivent être traçables :
- Qui a appliqué la remise ?
- Quand ?
- Pourquoi (notes internes) ?
- Quelle était la remise par défaut du client ?

**Implémentation actuelle :** ⚠️ Partiellement implémentée
- `created_by` existe sur Quote
- Pas de champ `discount_applied_by` ou `discount_reason`

---

## 9. 📝 Recommandations Futures

### 9.1. Remises Conditionnelles

**Fonctionnalités à implémenter :**
- Remise selon montant total de commande
- Remise selon catégorie de produit
- Remise selon période (saisonnier)
- Remise selon historique client (fidélité)

### 9.2. Remises Négociées

**Fonctionnalités à implémenter :**
- Remises négociées par produit pour un client spécifique
- Remises négociées par quantité
- Remises négociées avec date d'expiration

### 9.3. Validation de Marge Minimum

**Fonctionnalités à implémenter :**
- Vérifier que la remise ne fait pas passer la marge en dessous d'un seuil
- Alerter si marge < seuil minimum
- Bloquer la remise si marge < seuil critique

### 9.4. Historique des Remises

**Fonctionnalités à implémenter :**
- Enregistrer chaque modification de remise
- Traçabilité complète (qui, quand, pourquoi)
- Statistiques sur les remises appliquées

---

## 10. ✅ Checklist de Validation

Avant d'appliquer une remise, vérifier :

- [ ] La remise est entre 0% et 100%
- [ ] Le prix final après remise est >= 0
- [ ] La remise est appliquée au bon niveau (ligne ou document)
- [ ] La remise n'est pas appliquée sur un prix déjà réduit (price list, promo, volume)
- [ ] La remise respecte les limites autorisées
- [ ] La remise est traçable (qui, quand, pourquoi)
- [ ] La TVA est calculée sur le prix après remise
- [ ] La marge reste acceptable après remise

---

## 11. 📚 Références

- [Règles Métier Discounts](./discount-business-rules.md) : Règles générales sur les discounts
- [Pricing Service Documentation](../app/services/pricing_service.py) : Implémentation technique
- [Quote Handlers](../app/application/sales/quotes/commands/handlers.py) : Logique d'application des remises

---

## 12. ✅ Conclusion

Les règles métier d'application des remises sont :

1. ✅ **Claires** : Distinction entre prix et remises
2. ✅ **Cohérentes** : Pas de double application
3. ✅ **Sécurisées** : Contrôles et autorisations
4. ✅ **Traçables** : Historique et justification
5. ✅ **Flexibles** : Remises manuelles possibles

**Les règles sont documentées et prêtes à être implémentées !** ✅

