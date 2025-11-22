# Guide d'Installation - CommerceFlow

**Version**: 1.0  
**Date**: 2025-11-21

---

## 📋 Table des Matières

1. [Prérequis](#prérequis)
2. [Installation Locale (Développement)](#installation-locale-développement)
3. [Installation Production](#installation-production)
4. [Configuration](#configuration)
5. [Initialisation](#initialisation)
6. [Vérification](#vérification)
7. [Mise à Jour](#mise-à-jour)
8. [Dépannage Installation](#dépannage-installation)

---

## Prérequis

### Logiciels Requis

#### Développement
- **Python** : 3.11 ou supérieur
- **Git** : Pour cloner le dépôt
- **SQLite** : Inclus avec Python (pour développement)

#### Production
- **Python** : 3.11 ou supérieur
- **PostgreSQL** : 14 ou supérieur
- **Redis** : 6.0 ou supérieur (pour Celery)
- **Nginx** : 1.18 ou supérieur (reverse proxy)
- **Supervisor** : Pour gérer les processus (optionnel)

### Système d'Exploitation

- **Linux** : Ubuntu 20.04+, Debian 11+, CentOS 8+
- **Windows** : Windows 10/11, Windows Server 2019+
- **macOS** : macOS 11+ (pour développement uniquement)

### Espace Disque

- **Minimum** : 2 GB (développement)
- **Recommandé** : 10 GB (production avec données)

### Mémoire RAM

- **Minimum** : 2 GB
- **Recommandé** : 4 GB (production)
- **Optimal** : 8 GB+ (production avec charge)

---

## Installation Locale (Développement)

### Étape 1 : Cloner le Dépôt

```bash
git clone https://github.com/votre-repo/commerceflow.git
cd commerceflow
```

### Étape 2 : Créer un Environnement Virtuel

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Étape 3 : Installer les Dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Étape 4 : Configuration

Créez un fichier `.env` à la racine du projet :

```env
# Environnement
FLASK_ENV=development
DEBUG=True

# Sécurité
SECRET_KEY=votre-cle-secrete-tres-longue-et-aleatoire
JWT_SECRET_KEY=votre-cle-jwt-secrete

# Base de données (SQLite pour développement)
DATABASE_URL=sqlite:///gmflow.db

# i18n
BABEL_DEFAULT_LOCALE=fr
BABEL_SUPPORTED_LOCALES=en,fr,ar

# Gestion du stock
STOCK_MANAGEMENT_MODE=simple

# Celery (optionnel pour développement)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

> **Important** : Générez des clés secrètes aléatoires pour `SECRET_KEY` et `JWT_SECRET_KEY` :
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### Étape 5 : Initialiser la Base de Données

```bash
# Créer les tables
python app/scripts/create_tables.py

# Créer l'utilisateur admin
python app/scripts/seed_admin.py
```

**Identifiants par défaut** :
- Username : `admin`
- Password : `admin`

> **⚠️ IMPORTANT** : Changez le mot de passe immédiatement en production !

### Étape 6 : Initialiser les Traductions

```bash
# Extraire les chaînes traduisibles
flask babel extract -F babel.cfg -k _l -o messages.pot .

# Compiler les traductions existantes
flask babel compile -d app/translations
```

### Étape 7 : Lancer l'Application

```bash
python run.py
```

L'application sera accessible sur : `http://localhost:5000`

### Étape 8 : Lancer Celery (Optionnel)

Pour les tâches asynchrones (emails, rappels) :

```bash
# Terminal 1 : Worker
celery -A app.tasks.celery_config worker --loglevel=info

# Terminal 2 : Beat (scheduler)
celery -A app.tasks.celery_config beat --loglevel=info
```

---

## Installation Production

### Étape 1 : Préparer le Serveur

#### Sur Ubuntu/Debian

```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer Python et dépendances
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql-14 redis-server nginx supervisor git

# Installer PostgreSQL
sudo apt install -y postgresql-14 postgresql-contrib-14
```

#### Sur CentOS/RHEL

```bash
# Installer EPEL
sudo yum install -y epel-release

# Installer Python et dépendances
sudo yum install -y python3.11 python3-pip postgresql14-server redis nginx supervisor git
```

### Étape 2 : Configurer PostgreSQL

```bash
# Démarrer PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Créer la base de données
sudo -u postgres psql
```

Dans PostgreSQL :

```sql
-- Créer l'utilisateur
CREATE USER gmflow_user WITH PASSWORD 'votre-mot-de-passe-securise';

-- Créer la base de données
CREATE DATABASE gmflow_db OWNER gmflow_user;

-- Donner les permissions
GRANT ALL PRIVILEGES ON DATABASE gmflow_db TO gmflow_user;

-- Quitter
\q
```

### Étape 3 : Configurer Redis

```bash
# Démarrer Redis
sudo systemctl start redis
sudo systemctl enable redis

# Vérifier
redis-cli ping
# Devrait répondre : PONG
```

### Étape 4 : Déployer l'Application

```bash
# Créer le répertoire
sudo mkdir -p /opt/commerceflow
sudo chown $USER:$USER /opt/commerceflow

# Cloner le dépôt
cd /opt/commerceflow
git clone https://github.com/votre-repo/commerceflow.git .

# Créer l'environnement virtuel
python3.11 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

### Étape 5 : Configuration Production

Créez `/opt/commerceflow/.env` :

```env
# Environnement
FLASK_ENV=production
DEBUG=False

# Sécurité (GÉNÉREZ DES CLÉS UNIQUES !)
SECRET_KEY=votre-cle-secrete-production-tres-longue
JWT_SECRET_KEY=votre-cle-jwt-production-tres-longue

# Base de données PostgreSQL
DATABASE_URL=postgresql+psycopg2://gmflow_user:votre-mot-de-passe@localhost:5432/gmflow_db

# i18n
BABEL_DEFAULT_LOCALE=fr
BABEL_SUPPORTED_LOCALES=en,fr,ar

# Gestion du stock
STOCK_MANAGEMENT_MODE=advanced

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email (SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=votre-email@gmail.com
MAIL_PASSWORD=votre-mot-de-passe-app

# URL de l'application
APPLICATION_URL=https://votre-domaine.com
```

### Étape 6 : Initialiser la Base de Données

```bash
cd /opt/commerceflow
source venv/bin/activate

# Exécuter les migrations
alembic upgrade head

# Créer l'utilisateur admin
python app/scripts/seed_admin.py
```

### Étape 7 : Compiler les Traductions

```bash
flask babel compile -d app/translations
```

### Étape 8 : Configurer Gunicorn

Créez `/opt/commerceflow/gunicorn_config.py` :

```python
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
```

### Étape 9 : Configurer Supervisor

Créez `/etc/supervisor/conf.d/commerceflow.conf` :

```ini
[program:commerceflow]
command=/opt/commerceflow/venv/bin/gunicorn -c /opt/commerceflow/gunicorn_config.py "app:create_app()"
directory=/opt/commerceflow
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/commerceflow/app.log

[program:commerceflow_celery]
command=/opt/commerceflow/venv/bin/celery -A app.tasks.celery_config worker --loglevel=info
directory=/opt/commerceflow
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/commerceflow/celery.log

[program:commerceflow_celery_beat]
command=/opt/commerceflow/venv/bin/celery -A app.tasks.celery_config beat --loglevel=info
directory=/opt/commerceflow
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/commerceflow/celery_beat.log
```

```bash
# Créer le répertoire de logs
sudo mkdir -p /var/log/commerceflow
sudo chown www-data:www-data /var/log/commerceflow

# Recharger Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start commerceflow
sudo supervisorctl start commerceflow_celery
sudo supervisorctl start commerceflow_celery_beat
```

### Étape 10 : Configurer Nginx

Créez `/etc/nginx/sites-available/commerceflow` :

```nginx
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;

    # Redirection HTTPS (si certificat SSL configuré)
    # return 301 https://$server_name$request_uri;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/commerceflow/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/commerceflow /etc/nginx/sites-enabled/

# Tester la configuration
sudo nginx -t

# Redémarrer Nginx
sudo systemctl restart nginx
```

### Étape 11 : Configurer SSL (HTTPS)

#### Avec Let's Encrypt (Recommandé)

```bash
# Installer Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtenir le certificat
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com

# Renouvellement automatique
sudo certbot renew --dry-run
```

---

## Configuration

### Variables d'Environnement

| Variable | Description | Exemple |
|----------|-------------|---------|
| `FLASK_ENV` | Environnement (development/production) | `production` |
| `DEBUG` | Mode debug (True/False) | `False` |
| `SECRET_KEY` | Clé secrète Flask | Générer avec `secrets.token_hex(32)` |
| `JWT_SECRET_KEY` | Clé secrète JWT | Générer avec `secrets.token_hex(32)` |
| `DATABASE_URL` | URL de connexion DB | `postgresql+psycopg2://user:pass@localhost/db` |
| `STOCK_MANAGEMENT_MODE` | Mode stock (simple/advanced) | `advanced` |
| `BABEL_DEFAULT_LOCALE` | Langue par défaut | `fr` |
| `CELERY_BROKER_URL` | URL Redis pour Celery | `redis://localhost:6379/0` |
| `MAIL_SERVER` | Serveur SMTP | `smtp.gmail.com` |
| `MAIL_PORT` | Port SMTP | `587` |
| `MAIL_USE_TLS` | Utiliser TLS | `True` |
| `MAIL_USERNAME` | Email SMTP | `votre-email@gmail.com` |
| `MAIL_PASSWORD` | Mot de passe SMTP | `votre-mot-de-passe` |

### Configuration de l'Application

Accédez à **Paramètres → Application** pour configurer :
- Informations entreprise
- Logo
- Langue par défaut
- Devise
- Mode de gestion du stock

---

## Initialisation

### Première Utilisation

1. **Connectez-vous** avec les identifiants admin
2. **Changez le mot de passe** (via admin système)
3. **Configurez l'entreprise** :
   - Allez dans **Paramètres → Application**
   - Remplissez les informations entreprise
   - Uploadez le logo
4. **Créez les emplacements** :
   - Allez dans **Inventaire → Entrepôts**
   - Créez au moins un emplacement de type "Warehouse"
5. **Importez vos produits** :
   - Allez dans **Catalogue → Produits**
   - Cliquez sur **"Importer"**
6. **Créez vos clients** :
   - Allez dans **Ventes → Clients**
   - Créez vos premiers clients

---

## Vérification

### Vérifier l'Installation

1. **Accédez à l'application** : `http://votre-domaine.com`
2. **Connectez-vous** avec les identifiants admin
3. **Vérifiez les modules** : Tous les modules doivent être accessibles
4. **Testez une fonctionnalité** :
   - Créez un produit
   - Créez un client
   - Créez une commande

### Vérifier les Services

```bash
# PostgreSQL
sudo systemctl status postgresql

# Redis
sudo systemctl status redis

# Nginx
sudo systemctl status nginx

# Supervisor (processus CommerceFlow)
sudo supervisorctl status
```

### Vérifier les Logs

```bash
# Application
tail -f /var/log/commerceflow/app.log

# Celery
tail -f /var/log/commerceflow/celery.log

# Nginx
sudo tail -f /var/log/nginx/error.log
```

---

## Mise à Jour

### Procédure de Mise à Jour

1. **Sauvegarder la base de données** :
```bash
pg_dump -U gmflow_user gmflow_db > backup_$(date +%Y%m%d).sql
```

2. **Arrêter l'application** :
```bash
sudo supervisorctl stop commerceflow
sudo supervisorctl stop commerceflow_celery
sudo supervisorctl stop commerceflow_celery_beat
```

3. **Mettre à jour le code** :
```bash
cd /opt/commerceflow
git pull origin main
```

4. **Mettre à jour les dépendances** :
```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

5. **Exécuter les migrations** :
```bash
alembic upgrade head
```

6. **Compiler les traductions** :
```bash
flask babel compile -d app/translations
```

7. **Redémarrer l'application** :
```bash
sudo supervisorctl start commerceflow
sudo supervisorctl start commerceflow_celery
sudo supervisorctl start commerceflow_celery_beat
```

---

## Dépannage Installation

### Problème : "Module not found"

**Solution** :
```bash
# Vérifier que l'environnement virtuel est activé
source venv/bin/activate

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Problème : "Database connection failed"

**Solution** :
1. Vérifier que PostgreSQL est démarré : `sudo systemctl status postgresql`
2. Vérifier les identifiants dans `.env`
3. Tester la connexion : `psql -U gmflow_user -d gmflow_db`

### Problème : "Port 5000 already in use"

**Solution** :
```bash
# Trouver le processus
sudo lsof -i :5000

# Tuer le processus
sudo kill -9 <PID>

# Ou changer le port dans gunicorn_config.py
```

### Problème : "Permission denied"

**Solution** :
```bash
# Donner les permissions
sudo chown -R www-data:www-data /opt/commerceflow
sudo chmod -R 755 /opt/commerceflow
```

### Problème : "Celery not working"

**Solution** :
1. Vérifier que Redis est démarré : `sudo systemctl status redis`
2. Vérifier la configuration Celery dans `.env`
3. Vérifier les logs : `tail -f /var/log/commerceflow/celery.log`

---

## Support

Pour toute question d'installation :
- **Email** : support@commerceflow.com
- **Documentation** : https://docs.commerceflow.com
- **GitHub Issues** : https://github.com/votre-repo/commerceflow/issues

---

**Fin du Guide d'Installation**

