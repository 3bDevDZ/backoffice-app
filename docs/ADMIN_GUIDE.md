# Guide Administrateur - CommerceFlow

**Version**: 1.0  
**Date**: 2025-11-21

---

## 📋 Table des Matières

1. [Gestion des Utilisateurs](#gestion-des-utilisateurs)
2. [Sauvegarde et Restauration](#sauvegarde-et-restauration)
3. [Maintenance](#maintenance)
4. [Sécurité](#sécurité)
5. [Performance](#performance)
6. [Monitoring](#monitoring)
7. [Dépannage Avancé](#dépannage-avancé)

---

## Gestion des Utilisateurs

### Créer un Utilisateur

Actuellement, la création d'utilisateurs se fait via script Python :

```bash
python app/scripts/create_user.py
```

Ou directement en base de données :

```sql
INSERT INTO users (username, password_hash, role, locale)
VALUES ('nouvel_utilisateur', 'hash_du_mot_de_passe', 'commercial', 'fr');
```

> **Note** : Une interface d'administration des utilisateurs sera disponible dans une future version.

### Rôles et Permissions

| Rôle | Accès |
|------|------|
| **admin** | Accès complet à tous les modules |
| **direction** | Dashboard, rapports, factures, paiements |
| **commercial** | Clients, devis, commandes, produits, promotions |
| **magasinier** | Stock, emplacements, réceptions, transferts, mouvements |
| **comptable** | Factures, paiements, rapprochement bancaire |

### Changer le Mot de Passe d'un Utilisateur

```python
from app.domain.models.user import User
from app.infrastructure.db import get_session

with get_session() as session:
    user = session.query(User).filter_by(username='nom_utilisateur').first()
    user.set_password('nouveau_mot_de_passe')
    session.commit()
```

---

## Sauvegarde et Restauration

### Sauvegarde de la Base de Données

#### PostgreSQL

```bash
# Sauvegarde complète
pg_dump -U gmflow_user gmflow_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Sauvegarde compressée
pg_dump -U gmflow_user gmflow_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Sauvegarde avec format personnalisé (recommandé)
pg_dump -U gmflow_user -F c gmflow_db > backup_$(date +%Y%m%d_%H%M%S).dump
```

#### SQLite

```bash
# Copier le fichier
cp gmflow.db backup_$(date +%Y%m%d_%H%M%S).db
```

### Script de Sauvegarde Automatique

Créez `/opt/commerceflow/scripts/backup.sh` :

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/commerceflow"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql"

mkdir -p $BACKUP_DIR

# Sauvegarde PostgreSQL
pg_dump -U gmflow_user gmflow_db > $BACKUP_FILE

# Compresser
gzip $BACKUP_FILE

# Garder seulement les 30 derniers jours
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Sauvegarde terminée : $BACKUP_FILE.gz"
```

Ajoutez au crontab :

```bash
# Sauvegarde quotidienne à 2h du matin
0 2 * * * /opt/commerceflow/scripts/backup.sh
```

### Restauration

#### PostgreSQL

```bash
# Depuis un fichier SQL
psql -U gmflow_user gmflow_db < backup_20251121_020000.sql

# Depuis un dump compressé
gunzip < backup_20251121_020000.sql.gz | psql -U gmflow_user gmflow_db

# Depuis un format personnalisé
pg_restore -U gmflow_user -d gmflow_db backup_20251121_020000.dump
```

#### SQLite

```bash
# Remplacer le fichier
cp backup_20251121_020000.db gmflow.db
```

> **⚠️ ATTENTION** : La restauration écrase toutes les données existantes. Faites une sauvegarde avant !

---

## Maintenance

### Nettoyage des Logs

```bash
# Nettoyer les logs anciens (> 30 jours)
find /var/log/commerceflow -name "*.log" -mtime +30 -delete

# Rotation des logs (configuré dans Supervisor)
```

### Optimisation de la Base de Données

#### PostgreSQL

```sql
-- Analyser les tables
ANALYZE;

-- VACUUM (nettoyage)
VACUUM;

-- VACUUM FULL (reconstruction, nécessite un verrou exclusif)
VACUUM FULL;
```

#### Script d'Optimisation

```bash
#!/bin/bash
# Optimisation hebdomadaire
psql -U gmflow_user -d gmflow_db -c "VACUUM ANALYZE;"
```

### Nettoyage des Sessions Expirées

Les sessions Flask expirent automatiquement après 24h. Aucune action nécessaire.

### Nettoyage des Fichiers Temporaires

```bash
# Nettoyer les fichiers PDF temporaires (> 7 jours)
find /tmp -name "commerceflow_*.pdf" -mtime +7 -delete
```

---

## Sécurité

### Changer les Mots de Passe par Défaut

**CRITIQUE** : Changez immédiatement les mots de passe par défaut :

```python
# Script pour changer le mot de passe admin
python -c "
from app.domain.models.user import User
from app.infrastructure.db import get_session

with get_session() as session:
    user = session.query(User).filter_by(username='admin').first()
    user.set_password('NOUVEAU_MOT_DE_PASSE_SECURISE')
    session.commit()
    print('Mot de passe changé avec succès')
"
```

### Configuration HTTPS

1. **Obtenir un certificat SSL** (Let's Encrypt recommandé)
2. **Configurer Nginx** pour HTTPS
3. **Forcer HTTPS** dans l'application

Voir [Guide d'Installation - SSL](INSTALLATION_GUIDE.md#étape-11--configurer-ssl-https)

### Firewall

```bash
# Autoriser seulement les ports nécessaires
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Mises à Jour de Sécurité

```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Mettre à jour Python packages
pip install --upgrade pip
pip list --outdated
pip install --upgrade <package>
```

---

## Performance

### Optimisation PostgreSQL

#### Indexes

Créez une migration pour ajouter des indexes :

```python
# migrations/versions/XXXX_add_performance_indexes.py
def upgrade():
    op.create_index('idx_orders_customer_id', 'orders', ['customer_id'])
    op.create_index('idx_orders_status', 'orders', ['status'])
    op.create_index('idx_stock_items_product_id', 'stock_items', ['product_id'])
    op.create_index('idx_stock_items_location_id', 'stock_items', ['location_id'])
    op.create_index('idx_invoices_customer_id', 'invoices', ['customer_id'])
    op.create_index('idx_invoices_status', 'invoices', ['status'])
```

#### Configuration PostgreSQL

Éditez `/etc/postgresql/14/main/postgresql.conf` :

```conf
# Mémoire
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 16MB

# Connexions
max_connections = 100

# Performance
random_page_cost = 1.1  # Pour SSD
effective_io_concurrency = 200  # Pour SSD
```

Redémarrer PostgreSQL :

```bash
sudo systemctl restart postgresql
```

### Cache Redis

Pour améliorer les performances, activez le cache Redis :

```python
# Dans app/config.py
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379/1'
```

### Optimisation des Requêtes

Vérifiez les requêtes lentes :

```sql
-- Activer le logging des requêtes lentes
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 1 seconde
SELECT pg_reload_conf();
```

---

## Monitoring

### Health Check

Créez un endpoint de health check :

```python
# app/routes/health.py
@health_bp.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'database': check_database(),
        'redis': check_redis()
    })
```

### Logs

#### Logs Application

```bash
# Suivre les logs en temps réel
tail -f /var/log/commerceflow/app.log

# Filtrer les erreurs
grep ERROR /var/log/commerceflow/app.log
```

#### Logs Nginx

```bash
# Logs d'accès
tail -f /var/log/nginx/access.log

# Logs d'erreur
tail -f /var/log/nginx/error.log
```

### Métriques

Surveillez :
- **CPU** : `top`, `htop`
- **Mémoire** : `free -h`
- **Disque** : `df -h`
- **Base de données** : Taille, connexions actives

---

## Dépannage Avancé

### Problème : Application Lente

**Diagnostic** :
1. Vérifier les logs : `tail -f /var/log/commerceflow/app.log`
2. Vérifier les requêtes lentes PostgreSQL
3. Vérifier la charge CPU/mémoire

**Solutions** :
- Augmenter le nombre de workers Gunicorn
- Optimiser les requêtes SQL
- Ajouter des indexes
- Activer le cache Redis

### Problème : Erreurs 500

**Diagnostic** :
1. Vérifier les logs : `grep ERROR /var/log/commerceflow/app.log`
2. Vérifier les logs Nginx : `tail -f /var/log/nginx/error.log`

**Solutions courantes** :
- Vérifier les permissions fichiers
- Vérifier la connexion base de données
- Vérifier les variables d'environnement

### Problème : Celery Ne Fonctionne Pas

**Diagnostic** :
```bash
# Vérifier Redis
redis-cli ping

# Vérifier les workers
sudo supervisorctl status commerceflow_celery
```

**Solutions** :
- Redémarrer Redis : `sudo systemctl restart redis`
- Redémarrer Celery : `sudo supervisorctl restart commerceflow_celery`

### Problème : Migrations Échouent

**Diagnostic** :
```bash
# Vérifier l'état des migrations
alembic current
alembic history
```

**Solutions** :
- Vérifier les permissions base de données
- Vérifier la connexion
- Restaurer depuis sauvegarde si nécessaire

---

## Commandes Utiles

### Gestion des Processus

```bash
# Status
sudo supervisorctl status

# Redémarrer
sudo supervisorctl restart commerceflow

# Logs
sudo supervisorctl tail commerceflow
```

### Base de Données

```bash
# Connexion
psql -U gmflow_user -d gmflow_db

# Taille de la base
psql -U gmflow_user -d gmflow_db -c "SELECT pg_size_pretty(pg_database_size('gmflow_db'));"

# Tables les plus volumineuses
psql -U gmflow_user -d gmflow_db -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;"
```

### Traductions

```bash
# Extraire les nouvelles chaînes
flask babel extract -F babel.cfg -k _l -o messages.pot .

# Mettre à jour les fichiers .po
flask babel update -i messages.pot -d app/translations

# Compiler
flask babel compile -d app/translations
```

---

## Support

Pour toute question d'administration :
- **Email** : admin@commerceflow.com
- **Documentation** : https://docs.commerceflow.com
- **GitHub Issues** : https://github.com/votre-repo/commerceflow/issues

---

**Fin du Guide Administrateur**

