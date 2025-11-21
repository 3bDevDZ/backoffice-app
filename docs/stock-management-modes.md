# Modes de Gestion du Stock

## Vue d'ensemble

Le système CommerceFlow propose deux modes de gestion du stock pour s'adapter à différents types d'entreprises :

- **Mode Simple** : Pour les petits grossistes avec un seul entrepôt
- **Mode Avancé** : Pour les entreprises avec plusieurs sites/entrepôts

## Configuration

Le mode est configuré via la variable d'environnement `STOCK_MANAGEMENT_MODE` :

```bash
# Mode simple (par défaut)
STOCK_MANAGEMENT_MODE=simple

# Mode avancé
STOCK_MANAGEMENT_MODE=advanced
```

## Mode Simple (`simple`)

### Caractéristiques

- **Un seul entrepôt** : Tous les produits sont stockés dans un emplacement par défaut
- **Interface simplifiée** : Pas de sélection de site ou d'emplacement lors de la réception
- **Gestion rapide** : Idéal pour les petits grossistes qui n'ont pas besoin de gérer plusieurs sites

### Fonctionnement

1. **Réception de marchandises** :
   - Les produits sont automatiquement reçus à l'emplacement par défaut (première Location de type `'warehouse'` active)
   - L'utilisateur n'a pas besoin de choisir un site ou un emplacement
   - L'interface affiche un message informatif indiquant l'emplacement par défaut utilisé

2. **Gestion du stock** :
   - Vue unique du stock par produit
   - Pas de distinction entre sites
   - Mouvements de stock simplifiés

### Exemple d'utilisation

Un petit grossiste avec un seul entrepôt à Paris :
- Tous les produits sont reçus automatiquement à "Entrepôt Principal"
- Pas besoin de gérer plusieurs sites
- Interface épurée et rapide

## Mode Avancé (`advanced`)

### Caractéristiques

- **Multi-sites** : Gestion de plusieurs entrepôts/sites
- **Emplacements détaillés** : Structure hiérarchique (Site → Location → Zone → Allée → Étagère)
- **Transfers inter-sites** : Possibilité de transférer du stock entre sites
- **Vue consolidée** : Vue globale du stock avec répartition par site

### Fonctionnement

1. **Réception de marchandises** :
   - L'utilisateur doit choisir le **Site** de réception
   - Puis choisir l'**Emplacement** (Location) spécifique dans ce site
   - Les emplacements sont filtrés automatiquement selon le site sélectionné

2. **Gestion du stock** :
   - Vue par site ou vue consolidée (multi-sites)
   - Transfers de stock entre sites
   - Suivi détaillé des mouvements par site

### Exemple d'utilisation

Une entreprise avec plusieurs entrepôts :
- Site 1 : "Entrepôt Paris Nord"
- Site 2 : "Entrepôt Lyon Sud"
- Site 3 : "Entrepôt Marseille"

Lors de la réception, l'utilisateur choisit :
- Site : "Entrepôt Paris Nord"
- Emplacement : "Zone A - Allée 1 - Étagère 2"

## Réception des Marchandises

### Mode Simple

```
┌─────────────────────────────────────┐
│  Bon de Réception                    │
├─────────────────────────────────────┤
│  Commande : PO-2024-00123           │
│  Date : 2024-01-15                   │
│                                     │
│  Produits :                          │
│  ┌─────────────────────────────────┐ │
│  │ Produit A │ Qté: 100 │ [Auto] │ │
│  │ Produit B │ Qté: 50  │ [Auto] │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ℹ️ Mode simple: Réception          │
│     automatique à "Entrepôt Principal"│
└─────────────────────────────────────┘
```

### Mode Avancé

```
┌─────────────────────────────────────┐
│  Bon de Réception                    │
├─────────────────────────────────────┤
│  Commande : PO-2024-00123           │
│  Date : 2024-01-15                   │
│                                     │
│  Produits :                          │
│  ┌─────────────────────────────────┐ │
│  │ Produit A │ Qté: 100            │ │
│  │ Site: [Entrepôt Paris Nord ▼]   │ │
│  │ Location: [Zone A - Allée 1 ▼] │ │
│  ├─────────────────────────────────┤ │
│  │ Produit B │ Qté: 50             │ │
│  │ Site: [Entrepôt Lyon Sud ▼]    │ │
│  │ Location: [Zone B - Allée 2 ▼] │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## Migration entre Modes

### De Simple vers Avancé

1. Configurer `STOCK_MANAGEMENT_MODE=advanced`
2. Créer les Sites dans l'interface (Stock → Sites)
3. Créer les Locations pour chaque site (Stock → Emplacements)
4. Le système utilisera automatiquement les sites et locations existants

### De Avancé vers Simple

1. Configurer `STOCK_MANAGEMENT_MODE=simple`
2. L'interface se simplifie automatiquement
3. Les données multi-sites restent en base mais ne sont plus affichées dans l'interface de réception

## Recommandations

### Choisir le Mode Simple si :
- ✅ Vous avez un seul entrepôt
- ✅ Vous êtes un petit grossiste
- ✅ Vous voulez une interface simple et rapide
- ✅ Vous n'avez pas besoin de gérer plusieurs sites

### Choisir le Mode Avancé si :
- ✅ Vous avez plusieurs entrepôts/sites
- ✅ Vous devez transférer du stock entre sites
- ✅ Vous avez besoin d'un suivi détaillé par site
- ✅ Vous gérez une structure logistique complexe

## Impact sur les Fonctionnalités

| Fonctionnalité | Mode Simple | Mode Avancé |
|----------------|-------------|-------------|
| Réception marchandises | Auto (emplacement par défaut) | Choix Site + Location |
| Vue stock | Vue unique | Vue par site ou consolidée |
| Transfers inter-sites | ❌ Non disponible | ✅ Disponible |
| Gestion Sites | ❌ Masquée | ✅ Disponible |
| Gestion Locations | ✅ Disponible | ✅ Disponible |
| Complexité interface | ⭐ Simple | ⭐⭐⭐ Avancée |

## Notes Techniques

- Le mode est défini dans `app/config.py` via `STOCK_MANAGEMENT_MODE`
- Les templates s'adaptent automatiquement selon le mode (`app/templates/purchases/receipts/form.html`)
- Le handler de réception (`PurchaseReceiptValidatedDomainEventHandler`) gère automatiquement les sites
- En mode simple, si aucune location par défaut n'existe, le système utilise la première location de type `'warehouse'` active

