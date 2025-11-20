# Guide d'utilisation i18n Frontend

Ce guide explique comment utiliser le système d'internationalisation (i18n) dans le frontend JavaScript.

## Vue d'ensemble

Le système i18n frontend fournit :
- **Traduction de chaînes** : Fonction `t()` pour traduire les messages
- **Formatage de nombres** : Formatage selon la locale
- **Formatage de dates** : Formatage selon la locale
- **Formatage de devises** : Formatage monétaire selon la locale
- **Support RTL** : Application automatique de la direction du texte
- **Changement de langue** : Changement de langue avec rechargement

## API Endpoint

### GET `/api/i18n/translations`
Récupère les traductions pour la locale actuelle.

**Réponse :**
```json
{
  "success": true,
  "locale": "fr",
  "direction": "ltr",
  "translations": {
    "Loading...": "Chargement...",
    "Error": "Erreur",
    "Success": "Succès",
    ...
  }
}
```

### GET `/api/i18n/translations/<locale>`
Récupère les traductions pour une locale spécifique (`fr` ou `ar`).

## Utilisation en JavaScript

### 1. Traduction basique

```javascript
// Utiliser la fonction t()
const message = window.i18n.t('Loading...');
console.log(message); // "Chargement..." (si locale = 'fr')

// Ou utiliser l'alias _
const error = window.i18n._('An error occurred');
```

### 2. Traduction avec paramètres

```javascript
// Support des placeholders {{key}}
const welcome = window.i18n.t('Welcome, {{name}}!', { name: 'John' });
// Résultat: "Bienvenue, John!" (si locale = 'fr')
```

### 3. Formatage de nombres

```javascript
// Formatage simple
const formatted = window.i18n.formatNumber(1234.56);
// Résultat: "1 234,56" (fr) ou "1,234.56" (en)

// Avec options
const formatted = window.i18n.formatNumber(1234.56, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
});
```

### 4. Formatage de dates

```javascript
// Formatage simple
const date = window.i18n.formatDate(new Date());
// Résultat: "27/01/2025" (fr) ou "01/27/2025" (en)

// Avec options
const date = window.i18n.formatDate(new Date(), {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
});
// Résultat: "27 janvier 2025" (fr)
```

### 5. Formatage de devises

```javascript
// Formatage EUR par défaut
const price = window.i18n.formatCurrency(1234.56);
// Résultat: "1 234,56 €" (fr)

// Avec devise spécifique
const price = window.i18n.formatCurrency(1234.56, 'USD');
// Résultat: "$1,234.56" (en)
```

### 6. Obtenir la direction du texte

```javascript
const direction = window.i18n.getTextDirection();
// Résultat: "rtl" (ar) ou "ltr" (fr)
```

### 7. Changer de langue

```javascript
// Changer vers l'arabe
window.i18n.switchLanguage('ar');

// Changer vers le français
window.i18n.switchLanguage('fr');
```

### 8. Obtenir la locale actuelle

```javascript
const locale = window.i18n.getCurrentLocale();
// Résultat: "fr" ou "ar"
```

## Intégration avec les composants

### Toast Notifications

Les composants `showToast`, `showSuccessToast`, etc. utilisent automatiquement i18n :

```javascript
// Le message sera automatiquement traduit
window.CommerceFlowComponents.showSuccessToast('Operation successful');
// Affiche: "Opération réussie" (si locale = 'fr')
```

### Loading Spinner

```javascript
// Le message sera automatiquement traduit
window.CommerceFlowComponents.showLoading('Please wait...');
// Affiche: "Veuillez patienter..." (si locale = 'fr')
```

## Événements

### `i18n:ready`

Déclenché lorsque les traductions sont chargées :

```javascript
document.addEventListener('i18n:ready', function(event) {
    console.log('Locale:', event.detail.locale);
    console.log('Translations:', event.detail.translations);
    
    // Votre code ici
    const message = window.i18n.t('Loading...');
});
```

## Exemples d'utilisation

### Validation de formulaire

```javascript
function validateForm() {
    const errors = [];
    
    if (!email.value) {
        errors.push(window.i18n.t('Required field'));
    }
    
    if (errors.length > 0) {
        window.CommerceFlowComponents.showErrorToast(
            window.i18n.t('Please fill in all required fields')
        );
        return false;
    }
    
    return true;
}
```

### Mise à jour dynamique de contenu

```javascript
function updateButtonText(buttonId, textKey) {
    const button = document.getElementById(buttonId);
    if (button && window.i18n) {
        button.textContent = window.i18n.t(textKey);
    }
}

// Utilisation
updateButtonText('save-btn', 'Save');
```

### Gestion d'erreurs API

```javascript
async function handleAPIError(error) {
    const errorMessage = window.i18n.t('An error occurred');
    const details = error.message || window.i18n.t('Unknown error');
    
    window.CommerceFlowComponents.showErrorToast(
        `${errorMessage}: ${details}`
    );
}
```

## Traductions disponibles

Les traductions suivantes sont disponibles par défaut :

- **Général** : Loading..., Error, Success, Warning, Info, Cancel, Save, Delete, Edit, View, Create, Update, Submit, Back, Next, Previous, Search, Filter, Reset, Close, Confirm, Yes, No, OK
- **Messages** : Are you sure?, This action cannot be undone., Please wait..., Operation successful, Operation failed, An error occurred, Invalid input, Required field
- **Statuts** : Active, Inactive, Draft, Confirmed, Cancelled, Completed, Pending
- **Actions** : Add, Remove, Select, Choose, Upload, Download, Export, Import, Print
- **Dates** : Date, From, To, Today, Yesterday, This week, This month, This year
- **Pagination** : Page, of, Showing, to, results, No results found
- **Validation** : Please fill in all required fields, Invalid email address, Invalid phone number, Value must be greater than 0, Value must be a number

## Ajouter de nouvelles traductions

Pour ajouter de nouvelles traductions, modifiez `app/api/i18n.py` et ajoutez les clés dans le dictionnaire `common_translations`.

Ensuite, utilisez `flask babel extract` et `flask babel update` pour mettre à jour les fichiers de traduction.

## Notes importantes

1. **Chargement asynchrone** : Les traductions sont chargées de manière asynchrone. Utilisez l'événement `i18n:ready` si vous avez besoin que les traductions soient disponibles.

2. **Cache** : Les traductions sont mises en cache pour améliorer les performances.

3. **Fallback** : Si une traduction n'est pas trouvée, le texte original est retourné.

4. **Locale** : La locale est détectée depuis :
   - Le paramètre URL `?locale=fr`
   - La variable `window.__LOCALE__` (définie par le serveur)
   - Par défaut : `'fr'`

