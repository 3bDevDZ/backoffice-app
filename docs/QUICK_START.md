# Guide de Démarrage Rapide - CommerceFlow

**Temps estimé** : 15 minutes

---

## 🚀 Démarrage en 5 Étapes

### 1. Installation (5 min)

```bash
# Cloner le dépôt
git clone https://github.com/votre-repo/commerceflow.git
cd commerceflow

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Configuration (2 min)

Créez un fichier `.env` :

```env
FLASK_ENV=development
SECRET_KEY=changez-moi-en-production
JWT_SECRET_KEY=changez-moi-en-production
DATABASE_URL=sqlite:///gmflow.db
STOCK_MANAGEMENT_MODE=simple
```

### 3. Initialisation (3 min)

```bash
# Créer la base de données
python app/scripts/create_tables.py

# Créer l'utilisateur admin
python app/scripts/seed_admin.py

# Compiler les traductions
flask babel compile -d app/translations
```

### 4. Lancer (1 min)

```bash
python run.py
```

### 5. Accéder (1 min)

Ouvrez votre navigateur : `http://localhost:5000`

**Identifiants** :
- Username : `admin`
- Password : `admin`

---

## 📝 Première Configuration

### Étape 1 : Configurer l'Entreprise

1. Connectez-vous
2. Allez dans **Paramètres → Application**
3. Remplissez :
   - Nom de l'entreprise
   - Adresse
   - SIRET, TVA (si applicable)
   - Logo (optionnel)

### Étape 2 : Créer un Emplacement

1. Allez dans **Inventaire → Entrepôts**
2. Cliquez sur **"Nouvel Emplacement"**
3. Remplissez :
   - Code : `ENTREPOT-01`
   - Nom : `Entrepôt Principal`
   - Type : `Warehouse`
4. Cliquez sur **"Enregistrer"**

### Étape 3 : Importer/Créer des Produits

**Option A : Import Excel**
1. Allez dans **Catalogue → Produits**
2. Cliquez sur **"Importer"**
3. Téléchargez le modèle Excel
4. Remplissez avec vos produits
5. Importez

**Option B : Création manuelle**
1. Cliquez sur **"Nouveau Produit"**
2. Remplissez le formulaire
3. Enregistrez

### Étape 4 : Créer un Client

1. Allez dans **Ventes → Clients**
2. Cliquez sur **"Nouveau Client"**
3. Choisissez **B2B** ou **B2C**
4. Remplissez les informations
5. Enregistrez

---

## ✅ Vérification

Testez le workflow complet :

1. **Créer un devis** : Ventes → Devis → Nouveau Devis
2. **Convertir en commande** : Ouvrir le devis → Convertir en Commande
3. **Confirmer la commande** : Ouvrir la commande → Confirmer
4. **Réceptionner un achat** : Achats → Réceptions → Nouvelle Réception

Si tout fonctionne, vous êtes prêt ! 🎉

---

## 📚 Prochaines Étapes

- Lisez le [Guide Utilisateur Complet](USER_GUIDE.md)
- Consultez le [Guide d'Installation](INSTALLATION_GUIDE.md) pour la production
- Explorez les [Rapports](USER_GUIDE.md#rapports-et-analyses)

---

**Besoin d'aide ?** Consultez la [FAQ](USER_GUIDE.md#faq) ou contactez le support.

