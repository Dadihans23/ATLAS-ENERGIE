# Guide de Déploiement — Atlas Énergies

## Stack de production

| Composant | Détail |
|-----------|--------|
| Serveur | VPS Contabo (Ubuntu) |
| IP | 79.143.190.190 |
| Domaine | atlasenergies.net |
| Base de données | PostgreSQL |
| Serveur WSGI | Gunicorn (3 workers) |
| Reverse proxy | Nginx |
| Process manager | systemd |
| CI/CD | GitHub Actions |

---

## 1. Prérequis sur le VPS

### Connexion SSH
```bash
ssh hans@79.143.190.190
```

### Structure du projet
```
/home/hans/ATLAS-ENERGIE/
├── venv/               # Environnement virtuel Python
├── logs/               # Logs Django (créé manuellement)
│   ├── django_errors.log
│   └── security.log
├── staticfiles/        # Fichiers statiques collectés
├── media/              # Fichiers uploadés
├── .env                # Variables d'environnement (jamais committé)
└── atlas.sock          # Socket Gunicorn (généré automatiquement)
```

---

## 2. Premier déploiement (setup initial)

### 2.1 Cloner le projet
```bash
git clone https://github.com/Dadihans23/ATLAS-ENERGIE.git
cd ATLAS-ENERGIE
git checkout prod
```

### 2.2 Créer le venv et installer les dépendances
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements/base.txt
```

### 2.3 Créer le fichier .env
```bash
nano .env
```

Contenu :
```env
SECRET_KEY=une-cle-secrete-longue-et-aleatoire
DEBUG=False
ALLOWED_HOSTS=79.143.190.190,atlasenergies.net,www.atlasenergies.net

DATABASE_URL=postgres://USER:PASSWORD@localhost:5432/NOM_BD

MEDIA_ROOT=media
MEDIA_URL=/media/
STATIC_ROOT=staticfiles
STATIC_URL=/static/
SITE_ID=1

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=email@gmail.com
EMAIL_HOST_PASSWORD=app-password-gmail
EMAIL_USE_SSL=False
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=Atlas Energies <email@gmail.com>

TAUX_EUR_XOF=655.957
TAUX_USD_XOF=605.00
MAX_UPLOAD_SIZE_MB=10

CSRF_TRUSTED_ORIGINS=http://atlasenergies.net,http://www.atlasenergies.net,http://79.143.190.190
```

### 2.4 Créer le dossier logs
```bash
mkdir -p logs
touch logs/django_errors.log logs/security.log
```

### 2.5 Migrations et données initiales
```bash
DJANGO_SETTINGS_MODULE=atlas_energies.settings.prod python manage.py migrate
DJANGO_SETTINGS_MODULE=atlas_energies.settings.prod python manage.py createsuperuser
DJANGO_SETTINGS_MODULE=atlas_energies.settings.prod python manage.py collectstatic --noinput
```

---

## 3. Configuration Gunicorn (systemd)

### Créer le service
```bash
sudo nano /etc/systemd/system/atlas.service
```

Contenu :
```ini
[Unit]
Description=Atlas Énergies – Gunicorn
After=network.target

[Service]
User=hans
Group=www-data
WorkingDirectory=/home/hans/ATLAS-ENERGIE
Environment="DJANGO_SETTINGS_MODULE=atlas_energies.settings.prod"
ExecStart=/home/hans/ATLAS-ENERGIE/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/home/hans/ATLAS-ENERGIE/atlas.sock \
          atlas_energies.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

### Activer et démarrer
```bash
sudo systemctl daemon-reload
sudo systemctl enable atlas
sudo systemctl start atlas
sudo systemctl status atlas
```

---

## 4. Configuration Nginx

### Installer Nginx
```bash
sudo apt update && sudo apt install nginx -y
```

### Créer le fichier de config
```bash
sudo nano /etc/nginx/sites-available/atlas
```

Contenu :
```nginx
server {
    listen 80;
    server_name 79.143.190.190 atlasenergies.net www.atlasenergies.net;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /home/hans/ATLAS-ENERGIE/staticfiles/;
    }

    location /media/ {
        alias /home/hans/ATLAS-ENERGIE/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/hans/ATLAS-ENERGIE/atlas.sock;
    }
}
```

### Activer le site
```bash
sudo ln -s /etc/nginx/sites-available/atlas /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Permissions socket
```bash
sudo chmod 755 /home/hans
sudo usermod -aG www-data hans
sudo chown -R hans:www-data /home/hans/ATLAS-ENERGIE
sudo chmod -R 750 /home/hans/ATLAS-ENERGIE
```

---

## 5. Firewall

### UFW (sur le VPS)
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Contabo (panneau réseau)
Dans my.contabo.com → Firewall → ajouter les règles :
- TCP port 22 — Any IPv4
- TCP port 80 — Any IPv4
- TCP port 443 — Any IPv4

Assigner le firewall au VPS via l'onglet **Active VPS/VDS**.

---

## 6. DNS (LWS)

Dans le panneau cPanel LWS → Zone Editor → atlasenergies.net :

| Type | Nom | Valeur |
|------|-----|--------|
| A | @ | 79.143.190.190 |
| A | www | 79.143.190.190 |

Supprimer les enregistrements AAAA pointant vers LWS.

Propagation DNS : 1 à 4 heures.

---

## 7. Commandes utiles

```bash
# Statut des services
sudo systemctl status atlas
sudo systemctl status nginx

# Redémarrer
sudo systemctl restart atlas
sudo systemctl restart nginx

# Logs Gunicorn
sudo journalctl -u atlas -f

# Logs Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Logs Django
tail -f logs/django_errors.log
tail -f logs/security.log
```

---

## 8. SSL (HTTPS) avec Let's Encrypt ✅

### 8.1 Installer Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 8.2 Générer le certificat

```bash
sudo certbot --nginx -d atlasenergies.net -d www.atlasenergies.net
```

> Certbot configure Nginx automatiquement et met en place le renouvellement automatique du certificat (valable 90 jours, renouvelé via un timer systemd).

### 8.3 Mettre à jour le .env

```bash
nano ~/ATLAS-ENERGIE/.env
```

Modifier `CSRF_TRUSTED_ORIGINS` :

```env
CSRF_TRUSTED_ORIGINS=https://atlasenergies.net,https://www.atlasenergies.net
```

### 8.4 Mettre à jour prod.py

Dans `atlas_energies/settings/prod.py`, activer toutes les options HTTPS :

```python
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

CSRF_TRUSTED_ORIGINS = [
    'https://atlasenergies.net',
    'https://www.atlasenergies.net',
]
```

### 8.5 Redémarrer

```bash
sudo systemctl restart atlas
sudo systemctl restart nginx
```

### 8.6 Vérifier le renouvellement automatique

```bash
sudo certbot renew --dry-run
```

> Si la commande affiche `Congratulations, all simulated renewals succeeded`, le renouvellement automatique est opérationnel.

---

## Résumé final — État de production

| Élément | Statut | Détail |
|---------|--------|--------|
| Domaine | ✅ | atlasenergies.net |
| HTTPS | ✅ | Let's Encrypt, renouvellement auto |
| PostgreSQL | ✅ | cabinet_db / hans23 |
| Gunicorn | ✅ | 3 workers, systemd |
| Nginx | ✅ | Reverse proxy + SSL |
| CI/CD | ✅ | GitHub Actions → push prod |
