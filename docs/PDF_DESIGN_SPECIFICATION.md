# Spécification de Design - PDF Commande Professionnel

**Date**: 2025-01-27  
**Document**: COMMANDE (Purchase Order)  
**Objectif**: Transformer le PDF basique en document professionnel d'entreprise

---

## 1. Document Header/Branding

### 1.1 Layout du Header

**Structure recommandée**:
- **Hauteur totale**: 80-100mm
- **Marges latérales**: 20mm (alignées avec le corps du document)
- **Marge supérieure**: 15mm (pour l'en-tête)
- **Marge inférieure du header**: 20mm (espace avant le contenu)

**Disposition**:
```
┌─────────────────────────────────────────────────┐
│ [LOGO]  COMMANDE                    [Numéro]    │
│         (Titre principal)            [Date]     │
│                                                 │
│ ─────────────────────────────────────────────  │
│ (Barre d'accent colorée - optionnelle)         │
└─────────────────────────────────────────────────┘
```

### 1.2 Logo Placement

- **Position**: Coin supérieur gauche
- **Taille**: 40-50mm de largeur (hauteur proportionnelle)
- **Espacement**: 10mm depuis le bord gauche, 10mm depuis le haut
- **Format**: PNG avec fond transparent recommandé
- **Alternative**: Si pas de logo, utiliser un texte stylisé du nom de l'entreprise

### 1.3 Titre "COMMANDE"

**Typographie**:
- **Police**: Helvetica-Bold ou Arial-Bold (sans-serif professionnel)
- **Taille**: 28-32pt
- **Couleur**: `#1a1a1a` (noir profond, pas pur #000 pour impression)
- **Position**: À droite du logo, aligné verticalement au centre
- **Espacement**: 15mm depuis le logo

**Style optionnel**:
- Peut être en majuscules: "COMMANDE"
- Ou avec casse mixte: "Commande" (plus moderne)

### 1.4 Numéro et Date (Coin supérieur droit)

**Layout**:
- **Alignement**: Droite
- **Police**: Helvetica ou Arial
- **Taille**: 10pt pour les labels, 12pt pour les valeurs
- **Couleur**: `#4a4a4a` (gris foncé)
- **Espacement vertical**: 4mm entre les lignes

**Format**:
```
N° Commande: CMD-2025-00001
Date: 27/01/2025
```

### 1.5 Barre d'Accent (Optionnelle)

- **Position**: Sous le header, pleine largeur
- **Hauteur**: 4-6mm
- **Couleur**: `#4CAF50` (vert professionnel) ou `#2563EB` (bleu moderne)
- **Style**: Pleine couleur ou dégradé subtil
- **Espacement**: 15mm depuis le bas du header

---

## 2. Company/Client Information Layout

### 2.1 Structure Deux Colonnes

**Layout**:
```
┌──────────────────────┬──────────────────────┐
│ EXPÉDITEUR           │ DESTINATAIRE         │
│                      │                      │
│ [Nom Entreprise]     │ [Nom Client]         │
│ [Adresse]            │ [Adresse Client]     │
│ [Code Postal Ville]  │ [Code Postal Ville]  │
│                      │                      │
│ Tél: [Numéro]        │ Code: [Code Client]  │
│ Email: [Email]       │                      │
└──────────────────────┴──────────────────────┘
```

### 2.2 Dimensions et Espacement

- **Largeur totale**: 170mm (A4 - marges)
- **Largeur par colonne**: 80mm chacune
- **Espacement entre colonnes**: 10mm
- **Hauteur**: 50-60mm
- **Marge supérieure**: 20mm depuis la barre d'accent
- **Marge inférieure**: 15mm avant la section suivante

### 2.3 Styling des Sections

**Titres de section** ("EXPÉDITEUR", "DESTINATAIRE"):
- **Police**: Helvetica-Bold
- **Taille**: 11pt
- **Couleur**: `#2d3748` (gris très foncé)
- **Espacement**: 6mm sous le titre

**Contenu**:
- **Police**: Helvetica
- **Taille**: 9-10pt
- **Couleur**: `#1a1a1a` (noir)
- **Espacement vertical**: 3mm entre les lignes

**Bordures**:
- **Style**: Ligne fine (0.5pt) sous les titres
- **Couleur**: `#e2e8f0` (gris très clair)
- **Longueur**: Pleine largeur de la colonne

### 2.4 Icônes (Optionnel)

Si espace disponible, petites icônes avant les informations:
- 📞 Téléphone
- ✉️ Email
- 📍 Adresse

**Taille icônes**: 8pt (si utilisées comme texte Unicode)

---

## 3. Order Details Section

### 3.1 Layout en Grille

**Structure**:
```
┌─────────────────────────────────────────────┐
│ Informations Commande                       │
├─────────────────────────────────────────────┤
│ Statut: [Badge]    │ Date livraison: [Date] │
│ N° Devis: [Ref]    │ Date promise: [Date]   │
└─────────────────────────────────────────────┘
```

### 3.2 Dimensions

- **Largeur**: Pleine largeur (170mm)
- **Hauteur**: 40-50mm
- **Marge supérieure**: 15mm
- **Marge inférieure**: 20mm avant le tableau

### 3.3 Badge de Statut

**Design**:
- **Forme**: Rectangle arrondi (border-radius: 4pt)
- **Largeur**: 30-40mm
- **Hauteur**: 12mm
- **Padding**: 3mm horizontal, 2mm vertical

**Couleurs par statut**:
- **Draft**: `#fbbf24` (jaune) - Fond: `#fef3c7`, Texte: `#92400e`
- **Confirmed**: `#10b981` (vert) - Fond: `#d1fae5`, Texte: `#065f46`
- **Ready**: `#3b82f6` (bleu) - Fond: `#dbeafe`, Texte: `#1e40af`
- **Shipped**: `#8b5cf6` (violet) - Fond: `#ede9fe`, Texte: `#5b21b6`
- **Delivered**: `#059669` (vert foncé) - Fond: `#a7f3d0`, Texte: `#064e3b`
- **Canceled**: `#ef4444` (rouge) - Fond: `#fee2e2`, Texte: `#991b1b`

**Typographie badge**:
- **Police**: Helvetica-Bold
- **Taille**: 9pt
- **Texte**: Uppercase (ex: "CONFIRMÉ")

### 3.4 Informations de Commande

**Layout en 2 colonnes**:
- **Colonne gauche**: Statut, N° Devis
- **Colonne droite**: Dates de livraison

**Styling**:
- **Labels**: Helvetica, 9pt, couleur `#6b7280` (gris moyen)
- **Valeurs**: Helvetica, 10pt, couleur `#1a1a1a` (noir)
- **Espacement**: 8mm entre les lignes

**Bordures**:
- **Conteneur**: Ligne fine (0.5pt) autour de la section
- **Couleur**: `#e5e7eb` (gris clair)
- **Padding interne**: 8mm

---

## 4. Product Table Design

### 4.1 Structure du Tableau

**Colonnes** (largeurs recommandées):
1. **Produit**: 70mm (nom + code)
2. **Qté**: 18mm (quantité)
3. **Prix unit.**: 25mm
4. **Remise %**: 18mm
5. **Total HT**: 25mm
6. **TVA**: 18mm
7. **Total TTC**: 28mm

**Total largeur**: 170mm (A4 - marges)

### 4.2 Header Row (Ligne d'en-tête)

**Styling**:
- **Fond**: `#4CAF50` (vert professionnel) ou `#2563EB` (bleu moderne)
- **Texte**: Blanc (`#ffffff`)
- **Police**: Helvetica-Bold
- **Taille**: 10pt
- **Padding**: 8mm vertical, 5mm horizontal
- **Alignement**: 
  - Produit: Gauche
  - Nombres: Droite

**Bordures**:
- **Bordure inférieure**: 1pt, couleur `#2d5016` (vert foncé) ou `#1e40af` (bleu foncé)

### 4.3 Data Rows (Lignes de données)

**Alternance de couleurs**:
- **Ligne paire**: Fond blanc (`#ffffff`)
- **Ligne impaire**: Fond `#f9fafb` (gris très clair)

**Styling**:
- **Police**: Helvetica
- **Taille**: 9pt
- **Couleur texte**: `#1a1a1a` (noir)
- **Padding**: 6mm vertical, 4mm horizontal
- **Hauteur minimale**: 12mm par ligne

**Bordures**:
- **Bordures verticales**: 0.3pt, couleur `#e5e7eb` (gris clair)
- **Bordure inférieure**: 0.3pt, couleur `#e5e7eb`
- **Pas de bordure supérieure** (sauf pour la première ligne)

### 4.4 Formatage des Cellules

**Produit**:
- **Nom produit**: Helvetica-Bold, 9pt, `#1a1a1a`
- **Code produit**: Helvetica, 7pt, `#6b7280` (gris moyen)
- **Espacement**: 2mm entre nom et code

**Nombres** (Qté, Prix, Totaux):
- **Alignement**: Droite
- **Police**: Helvetica (ou Helvetica-Bold pour totaux)
- **Taille**: 9pt
- **Format**: 
  - Quantité: `1.000` (3 décimales)
  - Prix: `145.40 €` (2 décimales + symbole)
  - Totaux: `169.25 €` (2 décimales + symbole)

**Remise %**:
- **Format**: `3.00%` ou `-` si aucune remise
- **Couleur**: `#6b7280` si aucune remise

### 4.5 Espacement et Séparation

- **Espacement avant tableau**: 10mm
- **Espacement après tableau**: 15mm
- **Espacement entre lignes**: 0mm (bordures seulement)

---

## 5. Totals Section

### 5.1 Layout

**Structure**:
```
┌─────────────────────────────────────┐
│                                     │
│  Sous-total HT:           141.04 € │
│  Total HT:                 141.04 € │
│  ─────────────────────────────────  │
│  TVA:                      28.21 € │
│  ─────────────────────────────────  │
│  TOTAL TTC:               169.25 € │
│                                     │
└─────────────────────────────────────┘
```

### 5.2 Dimensions

- **Largeur**: 100mm (aligné à droite)
- **Marge gauche**: Auto (70mm depuis la gauche)
- **Padding**: 12mm
- **Marge supérieure**: 10mm depuis le tableau

### 5.3 Styling

**Conteneur**:
- **Fond**: `#f9fafb` (gris très clair) ou blanc avec bordure
- **Bordure**: 1pt, couleur `#e5e7eb` (gris clair)
- **Border-radius**: 4pt (coins arrondis)

**Lignes de total**:
- **Police**: Helvetica
- **Taille**: 10pt pour les lignes normales
- **Couleur**: `#1a1a1a` (noir)
- **Espacement vertical**: 6mm entre les lignes

**Lignes de séparation**:
- **Style**: Ligne fine (0.5pt)
- **Couleur**: `#d1d5db` (gris moyen)
- **Longueur**: Pleine largeur du conteneur
- **Espacement**: 4mm avant et après

**TOTAL TTC** (ligne finale):
- **Police**: Helvetica-Bold
- **Taille**: 12pt
- **Couleur**: `#1a1a1a` (noir)
- **Fond**: `#ffffff` (blanc) ou `#f0f9ff` (bleu très clair)
- **Bordure supérieure**: 2pt, couleur `#2563EB` (bleu) ou `#4CAF50` (vert)
- **Padding**: 8mm vertical

**Alignement**:
- **Labels**: Gauche
- **Valeurs**: Droite
- **Espacement**: 20mm entre label et valeur

---

## 6. Color Scheme

### 6.1 Palette Professionnelle

**Option 1 - Vert Professionnel** (Recommandé pour commerce):
- **Primaire**: `#4CAF50` (vert professionnel)
- **Primaire foncé**: `#2d5016` (pour bordures)
- **Primaire clair**: `#d1fae5` (pour fonds légers)
- **Accent**: `#10b981` (vert émeraude)
- **Neutre foncé**: `#1a1a1a` (texte principal)
- **Neutre moyen**: `#6b7280` (texte secondaire)
- **Neutre clair**: `#e5e7eb` (bordures)
- **Neutre très clair**: `#f9fafb` (fonds alternés)

**Option 2 - Bleu Moderne** (Recommandé pour technologie):
- **Primaire**: `#2563EB` (bleu moderne)
- **Primaire foncé**: `#1e40af` (pour bordures)
- **Primaire clair**: `#dbeafe` (pour fonds légers)
- **Accent**: `#3b82f6` (bleu vif)
- **Neutre foncé**: `#1a1a1a` (texte principal)
- **Neutre moyen**: `#6b7280` (texte secondaire)
- **Neutre clair**: `#e5e7eb` (bordures)
- **Neutre très clair**: `#f9fafb` (fonds alternés)

### 6.2 Utilisation des Couleurs

**Primaire** (`#4CAF50` ou `#2563EB`):
- Header du tableau
- Barre d'accent (optionnelle)
- Bordure supérieure du TOTAL TTC
- Badges de statut (certains)

**Neutre foncé** (`#1a1a1a`):
- Texte principal (titres, contenu)
- Valeurs numériques

**Neutre moyen** (`#6b7280`):
- Labels secondaires
- Codes produits
- Texte de statut "aucune remise"

**Neutre clair** (`#e5e7eb`):
- Bordures de tableaux
- Lignes de séparation
- Bordures de sections

**Neutre très clair** (`#f9fafb`):
- Fonds alternés des lignes
- Fond de la section totaux

### 6.3 Print-Friendly

**Vérification**:
- Tous les contrastes respectent WCAG AA (ratio 4.5:1 minimum)
- Les couleurs fonctionnent en niveaux de gris
- Les bordures restent visibles en noir & blanc

---

## 7. Typography

### 7.1 Hiérarchie des Polices

**Titre principal** ("COMMANDE"):
- **Police**: Helvetica-Bold ou Arial-Bold
- **Taille**: 28-32pt
- **Poids**: Bold (700)

**Sections** ("EXPÉDITEUR", "DESTINATAIRE", "Lignes de commande", "Totaux"):
- **Police**: Helvetica-Bold ou Arial-Bold
- **Taille**: 12-14pt
- **Poids**: Bold (700)

**Sous-sections** (Labels dans les sections):
- **Police**: Helvetica-Bold ou Arial-Bold
- **Taille**: 10-11pt
- **Poids**: Bold (700)

**Corps de texte** (Contenu principal):
- **Police**: Helvetica ou Arial
- **Taille**: 9-10pt
- **Poids**: Regular (400)

**Texte secondaire** (Codes produits, notes):
- **Police**: Helvetica ou Arial
- **Taille**: 7-8pt
- **Poids**: Regular (400)

**Nombres** (Prix, totaux):
- **Police**: Helvetica ou Arial
- **Taille**: 9-10pt (12pt pour TOTAL TTC)
- **Poids**: Regular (400) ou Bold (700) pour totaux

### 7.2 Espacement des Caractères

- **Titre principal**: Letter-spacing: 2pt (plus aéré)
- **Labels**: Letter-spacing: 0.5pt
- **Corps**: Letter-spacing: 0pt (normal)

### 7.3 Hauteur de Ligne

- **Titre principal**: Line-height: 1.2
- **Sections**: Line-height: 1.3
- **Corps**: Line-height: 1.4
- **Tableau**: Line-height: 1.2 (plus compact)

---

## 8. Layout & Spacing

### 8.1 Marges Globales

- **Marge supérieure**: 15mm (pour header)
- **Marge inférieure**: 20mm (pour footer)
- **Marge gauche**: 20mm
- **Marge droite**: 20mm
- **Zone utilisable**: 170mm × 257mm (A4: 210mm × 297mm)

### 8.2 Espacement entre Sections

- **Header → Info Client**: 20mm
- **Info Client → Détails Commande**: 15mm
- **Détails Commande → Tableau**: 20mm
- **Tableau → Totaux**: 15mm
- **Totaux → Instructions**: 15mm
- **Instructions → Notes**: 15mm
- **Notes → Footer**: 20mm

### 8.3 Padding Interne

- **Sections avec bordures**: 8-12mm
- **Cellules de tableau**: 4-6mm vertical, 4mm horizontal
- **Section totaux**: 12mm

### 8.4 Utilisation de l'Espace Blanc

- **Minimum 10mm** entre chaque section majeure
- **Espacement vertical** dans les listes: 3-4mm
- **Espacement horizontal** dans les grilles: 10mm

---

## 9. Professional Touches

### 9.1 Watermark (Pour brouillons)

**Si statut = "draft"**:
- **Texte**: "BROUILLON" ou "DRAFT"
- **Position**: Centré, diagonal (45°)
- **Police**: Helvetica-Bold
- **Taille**: 72pt
- **Couleur**: `#f3f4f6` (gris très clair, 10% opacité)
- **Rotation**: 45 degrés
- **Z-index**: Derrière tout le contenu

### 9.2 Footer

**Contenu**:
```
┌─────────────────────────────────────────────┐
│ Page 1 sur 1                                 │
│                                              │
│ CommerceFlow - Système de Gestion Commercial │
│ www.commerceflow.com | contact@commerceflow.com │
│                                              │
│ Ce document est généré automatiquement.      │
└─────────────────────────────────────────────┘
```

**Styling**:
- **Hauteur**: 30-40mm
- **Police**: Helvetica
- **Taille**: 7-8pt
- **Couleur**: `#9ca3af` (gris moyen)
- **Alignement**: Centre
- **Bordure supérieure**: 0.5pt, couleur `#e5e7eb`
- **Padding**: 8mm vertical

### 9.3 Lignes de Séparation

**Utilisation**:
- **Sous les titres de section**: Ligne fine (0.5pt), couleur `#e2e8f0`
- **Entre sections majeures**: Ligne fine (0.5pt), couleur `#e5e7eb`
- **Dans les totaux**: Ligne fine (0.5pt), couleur `#d1d5db`

**Longueur**: Pleine largeur de la section

### 9.4 QR Code (Optionnel)

**Position**: Coin inférieur droit du footer
- **Taille**: 30mm × 30mm
- **Contenu**: URL de vérification de commande ou données JSON encodées
- **Espacement**: 10mm depuis les bords

**Exemple URL**: `https://commerceflow.com/orders/verify/CMD-2025-00001`

### 9.5 Signature Line (Pour commandes confirmées)

**Si statut = "confirmed" ou supérieur**:
```
┌─────────────────────────────────────────────┐
│                                              │
│  Approuvé par:                              │
│  ──────────────────────                      │
│  [Nom] - [Date]                              │
│                                              │
└─────────────────────────────────────────────┘
```

**Styling**:
- **Position**: Avant le footer
- **Largeur**: 80mm
- **Hauteur**: 30mm
- **Police**: Helvetica
- **Taille**: 9pt
- **Ligne de signature**: 1pt, couleur `#1a1a1a`, longueur 60mm

---

## 10. PDF Metadata

### 10.1 Document Title

**Format**: `Commande {number} - {customer_name}`

**Exemple**: `Commande CMD-2025-00001 - Sanitaires Express Lyon`

### 10.2 Filename Convention

**Format**: `commande-{number}-{date}.pdf`

**Exemple**: `commande-CMD-2025-00001-20250127.pdf`

**Caractères**: 
- Utiliser uniquement lettres, chiffres, tirets
- Pas d'espaces, pas de caractères spéciaux
- Date au format YYYYMMDD

### 10.3 Metadata PDF

- **Title**: Même que Document Title
- **Author**: Nom de l'entreprise (ex: "CommerceFlow")
- **Subject**: "Commande commerciale"
- **Keywords**: "commande, purchase order, {customer_name}, {date}"
- **Creator**: "CommerceFlow PDF Generator"
- **Producer**: "ReportLab"

---

## 11. Instructions de Livraison & Notes

### 11.1 Section Instructions de Livraison

**Si présentes**:
- **Titre**: "Instructions de livraison" (Helvetica-Bold, 12pt)
- **Conteneur**: Fond `#fff3cd` (jaune très clair), bordure `#ffc107` (jaune)
- **Padding**: 10mm
- **Police contenu**: Helvetica, 9pt
- **Couleur texte**: `#92400e` (marron foncé)
- **Espacement**: 15mm avant et après

### 11.2 Section Notes

**Si présentes**:
- **Titre**: "Notes" (Helvetica-Bold, 12pt)
- **Conteneur**: Fond `#f9fafb` (gris très clair), bordure `#4CAF50` (vert) ou sans bordure
- **Padding**: 15mm
- **Police contenu**: Helvetica, 9pt
- **Couleur texte**: `#1a1a1a` (noir)
- **Espacement**: 15mm avant et après

---

## 12. Multilingual Support

### 12.1 Labels Bilingues

**Structure recommandée**:
- Utiliser des clés de traduction dans le code
- Support FR/EN par défaut
- Format: `{label_fr} / {label_en}` ou sélection basée sur locale

**Exemples**:
- `COMMANDE / PURCHASE ORDER`
- `EXPÉDITEUR / FROM`
- `DESTINATAIRE / TO`
- `Lignes de commande / Order Lines`
- `Totaux / Totals`

### 12.2 Format des Dates

- **FR**: `27/01/2025` (DD/MM/YYYY)
- **EN**: `01/27/2025` (MM/DD/YYYY) ou `January 27, 2025`

### 12.3 Format des Nombres

- **FR**: `1 234,56 €` (espace pour milliers, virgule pour décimales)
- **EN**: `1,234.56 €` (virgule pour milliers, point pour décimales)

---

## 13. Checklist d'Implémentation

### 13.1 Éléments Obligatoires

- [ ] Header avec logo ou nom d'entreprise
- [ ] Titre "COMMANDE" stylisé
- [ ] Informations expéditeur/destinataire en deux colonnes
- [ ] Section détails commande avec badge de statut
- [ ] Tableau produits avec header coloré
- [ ] Lignes alternées dans le tableau
- [ ] Section totaux avec TOTAL TTC en évidence
- [ ] Footer avec informations entreprise
- [ ] Numérotation des pages

### 13.2 Éléments Optionnels

- [ ] Barre d'accent colorée sous le header
- [ ] Watermark pour brouillons
- [ ] QR code de vérification
- [ ] Ligne de signature
- [ ] Icônes dans les informations contact
- [ ] Instructions de livraison stylisées
- [ ] Notes stylisées

### 13.3 Tests à Effectuer

- [ ] Impression en couleur (vérifier les contrastes)
- [ ] Impression en noir & blanc (vérifier la lisibilité)
- [ ] Affichage sur écran (PDF viewer)
- [ ] Taille du fichier (optimisation)
- [ ] Métadonnées PDF correctes
- [ ] Nom de fichier conforme
- [ ] Support multilingue (FR/EN)

---

## 14. Exemple de Layout Complet

```
┌─────────────────────────────────────────────────┐
│ [LOGO]  COMMANDE                    CMD-2025-001│
│                                 27/01/2025      │
│ ─────────────────────────────────────────────  │
│                                                 │
│ ┌──────────────┬──────────────┐                │
│ │ EXPÉDITEUR   │ DESTINATAIRE │                │
│ │              │              │                │
│ │ CommerceFlow │ Client ABC   │                │
│ │ 123 Rue...   │ 456 Ave...   │                │
│ └──────────────┴──────────────┘                │
│                                                 │
│ ┌─────────────────────────────────────────────┐│
│ │ Statut: [CONFIRMÉ]  │ Dates: ...            ││
│ └─────────────────────────────────────────────┘│
│                                                 │
│ ┌─────────────────────────────────────────────┐│
│ │ Produit │ Qté │ Prix │ ... │ Total TTC     ││
│ ├─────────────────────────────────────────────┤│
│ │ Produit 1│ 1.0 │ 145€ │ ... │ 169.25 €     ││
│ │ Code-001 │     │      │     │              ││
│ └─────────────────────────────────────────────┘│
│                                                 │
│                    ┌─────────────────────┐     │
│                    │ Sous-total: 141.04 € │     │
│                    │ TVA:        28.21 € │     │
│                    │ ───────────────────  │     │
│                    │ TOTAL:     169.25 € │     │
│                    └─────────────────────┘     │
│                                                 │
│ ┌─────────────────────────────────────────────┐│
│ │ Page 1 sur 1                                 ││
│ │ CommerceFlow - www.commerceflow.com         ││
│ └─────────────────────────────────────────────┘│
└─────────────────────────────────────────────────┘
```

---

## 15. Notes Finales

### 15.1 Priorités

**Phase 1 - Essentiel**:
1. Header professionnel avec logo/titre
2. Layout deux colonnes pour expéditeur/destinataire
3. Tableau avec header coloré et lignes alternées
4. Section totaux stylisée
5. Footer basique

**Phase 2 - Améliorations**:
1. Badges de statut colorés
2. Barre d'accent
3. Instructions et notes stylisées
4. Watermark pour brouillons

**Phase 3 - Avancé**:
1. QR code
2. Ligne de signature
3. Support multilingue complet
4. Optimisations d'impression

### 15.2 Compatibilité

- **ReportLab**: Toutes les spécifications sont compatibles
- **Impression**: Optimisé pour A4 (210mm × 297mm)
- **Couleurs**: Print-friendly (fonctionne en niveaux de gris)
- **Polices**: Helvetica/Arial (standard, toujours disponibles)

---

**Document créé le**: 2025-01-27  
**Version**: 1.0  
**Auteur**: Design Specification for CommerceFlow PDF Orders

