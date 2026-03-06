# Guide d'installation Attendee (Self-Hosting)

Ce guide explique comment installer et configurer Attendee sur votre propre serveur.

## Prerequis

- **Linux amd64** (obligatoire pour Chrome/ChromeDriver)
- **Docker** + **Docker Compose** installes
- **Un domaine** pointant vers le serveur (ex: `bot.votredomaine.com`)
- Un reverse proxy (Nginx/Caddy) pour le SSL (recommande)

## 1. Cloner le repo

```bash
git clone https://github.com/ClosiQode/attendee.git
cd attendee
```

## 2. Build de l'image Docker

```bash
docker compose -f dev.docker-compose.yaml build
```

Cette etape prend environ 5 minutes au premier build.

## 3. Creer le fichier .env

Generez les cles automatiquement :

```bash
docker compose -f dev.docker-compose.yaml run --rm attendee-app-local python init_env.py > .env
```

Puis editez le fichier `.env` avec vos parametres :

```env
# Cles (deja generees automatiquement)
CREDENTIALS_ENCRYPTION_KEY=...
DJANGO_SECRET_KEY=...

# ============================================
# HOSTING - OBLIGATOIRE
# ============================================
# Domaine de votre instance (sans https://)
SITE_DOMAIN=bot.votredomaine.com

# Hosts autorises (separes par des virgules, sans espaces)
ALLOWED_HOSTS=bot.votredomaine.com,localhost

# Origines CSRF autorisees (avec https://)
CSRF_TRUSTED_ORIGINS=https://bot.votredomaine.com

# Mode debug (false en production)
DJANGO_DEBUG=false

# SSL : true si votre reverse proxy gere le HTTPS
# false si vous accedez directement en HTTP
DJANGO_SSL_REQUIRE=false

# ============================================
# STOCKAGE
# ============================================
# Option A : Stockage local (filesystem)
STORAGE_PROTOCOL=local
LOCAL_RECORDING_STORAGE_PATH=/recordings
LOCAL_AUDIO_CHUNK_STORAGE_PATH=/audio_chunks

# Option B : AWS S3 (decommentez et remplissez)
# STORAGE_PROTOCOL=s3
# AWS_RECORDING_STORAGE_BUCKET_NAME=mon-bucket
# AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
# AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# AWS_DEFAULT_REGION=eu-west-3
# AWS_ENDPOINT_URL=  # Optionnel, pour MinIO ou S3-compatible

# Option C : Azure Blob Storage (decommentez et remplissez)
# STORAGE_PROTOCOL=azure
# AZURE_RECORDING_STORAGE_CONTAINER_NAME=recordings
# AZURE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...

# ============================================
# BOT
# ============================================
# Duree max d'un bot en meeting (en secondes, defaut: 14400 = 4h)
BOT_SOFT_TIME_LIMIT_SECONDS=14400

# ============================================
# BASE DE DONNEES (optionnel)
# ============================================
# Par defaut, utilise le PostgreSQL du docker-compose.
# Decommentez pour utiliser une base externe :
# DATABASE_URL=postgresql://user:password@host:5432/attendee

# ============================================
# EMAIL (optionnel, pour la production)
# ============================================
# Par defaut, les emails sont affiches dans les logs.
# Decommentez pour envoyer de vrais emails :
# EMAIL_HOST=smtp.mailgun.org
# EMAIL_HOST_USER=postmaster@mail.votredomaine.com
# EMAIL_HOST_PASSWORD=votre-mot-de-passe-smtp
# DEFAULT_FROM_EMAIL=noreply@votredomaine.com
```

## 4. Demarrer les services

```bash
docker compose -f dev.docker-compose.yaml up -d
```

Verifiez que tout tourne :

```bash
docker compose -f dev.docker-compose.yaml ps
```

Vous devriez voir 5 services en cours d'execution :
- `attendee-app-local` : Serveur Django (port 8000)
- `attendee-worker-local` : Worker Celery (execute les bots)
- `attendee-scheduler-local` : Planificateur de taches
- `postgres` : Base de donnees
- `redis` : Cache et message broker

## 5. Appliquer les migrations

```bash
docker compose -f dev.docker-compose.yaml exec attendee-app-local python manage.py migrate
```

## 6. Creer un compte

Ouvrez votre navigateur sur `http://bot.votredomaine.com:8000` (ou `http://localhost:8000` en local) et creez un compte.

Le lien de confirmation par email apparait dans les logs du serveur :

```bash
docker compose -f dev.docker-compose.yaml logs -f attendee-app-local
```

Cherchez une ligne comme :
```
http://bot.votredomaine.com:8000/accounts/confirm-email/XXXXX/
```

Collez ce lien dans votre navigateur pour confirmer votre compte.

## 7. Obtenir une cle API

1. Connectez-vous a l'interface web
2. Allez dans la section **API Keys** dans le menu lateral
3. Creez une nouvelle cle API

## 8. Reverse proxy (recommande pour la production)

### Nginx

```nginx
server {
    listen 80;
    server_name bot.votredomaine.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name bot.votredomaine.com;

    ssl_certificate /etc/letsencrypt/live/bot.votredomaine.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bot.votredomaine.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 500M;
    }
}
```

Si vous utilisez Nginx avec SSL, mettez `DJANGO_SSL_REQUIRE=true` dans votre `.env`.

### Caddy (alternative plus simple)

```
bot.votredomaine.com {
    reverse_proxy localhost:8000
}
```

Caddy gere automatiquement les certificats SSL via Let's Encrypt.

## 9. Tester votre installation

### Health check

```bash
curl https://bot.votredomaine.com/health/
# Doit retourner un statut 200
```

### Envoyer un bot dans un meeting

```bash
curl -X POST https://bot.votredomaine.com/api/v1/bots \
  -H 'Authorization: Token VOTRE_CLE_API' \
  -H 'Content-Type: application/json' \
  -d '{
    "meeting_url": "https://meet.google.com/xxx-xxxx-xxx",
    "bot_name": "Mon Bot"
  }'
```

### Verifier l'etat du bot

```bash
curl https://bot.votredomaine.com/api/v1/bots/BOT_ID \
  -H 'Authorization: Token VOTRE_CLE_API'
```

### Recuperer la transcription

```bash
curl https://bot.votredomaine.com/api/v1/bots/BOT_ID/transcript \
  -H 'Authorization: Token VOTRE_CLE_API'
```

### Partager une video

```bash
# Creer un lien de partage (expire dans 48h, telechargement autorise)
curl -X POST https://bot.votredomaine.com/api/v1/bots/BOT_ID/recording/share \
  -H 'Authorization: Token VOTRE_CLE_API' \
  -H 'Content-Type: application/json' \
  -d '{"expires_in_hours": 48, "allow_download": true}'

# Reponse : {"token": "...", "share_url": "https://bot.votredomaine.com/share/TOKEN/", ...}
# Le share_url est accessible sans authentification
```

## Commandes utiles

```bash
# Voir les logs en temps reel
docker compose -f dev.docker-compose.yaml logs -f

# Voir les logs d'un service specifique
docker compose -f dev.docker-compose.yaml logs -f attendee-worker-local

# Arreter les services
docker compose -f dev.docker-compose.yaml down

# Redemarrer les services
docker compose -f dev.docker-compose.yaml restart

# Acceder au shell Django
docker compose -f dev.docker-compose.yaml exec attendee-app-local python manage.py shell

# Lancer les migrations apres une mise a jour
docker compose -f dev.docker-compose.yaml exec attendee-app-local python manage.py migrate
```

## Mise a jour

```bash
git pull origin main
docker compose -f dev.docker-compose.yaml build
docker compose -f dev.docker-compose.yaml down
docker compose -f dev.docker-compose.yaml up -d
docker compose -f dev.docker-compose.yaml exec attendee-app-local python manage.py migrate
```

## Migration depuis le repo officiel Attendee

Si vous avez deja une instance Attendee qui tourne depuis le repo officiel (`attendee-team/attendee`) et que vous souhaitez passer sur ce fork avec les fonctionnalites supplementaires (stockage local, timeout configurable, partage video), voici la procedure.

**Vos donnees sont preservees** : comptes, cles API, bots, recordings, tout reste intact. Les nouvelles migrations s'ajoutent apres les existantes sans conflit.

### Etape 1 : Changer le remote Git

```bash
# Sur votre serveur, dans le dossier attendee existant
cd /chemin/vers/attendee

# Sauvegarder l'ancien remote (optionnel)
git remote rename origin upstream

# Ajouter le fork comme nouveau remote
git remote add origin https://github.com/ClosiQode/attendee.git

# Recuperer les modifications du fork
git fetch origin
git pull origin main
```

Si vous avez des modifications locales, sauvegardez-les d'abord :

```bash
git stash
git pull origin main
git stash pop
```

### Etape 2 : Mettre a jour le fichier .env

Ajoutez les nouvelles variables a votre `.env` existant. Les anciennes variables restent valides.

```bash
# Ajouter les nouvelles variables (ne touche pas aux existantes)
cat >> .env << 'EOF'

# === Nouvelles fonctionnalites (fork ClosiQode) ===

# Timeout bot configurable (defaut: 14400s = 4h, ancien: 3600s = 1h)
BOT_SOFT_TIME_LIMIT_SECONDS=14400

# Stockage local (decommentez pour remplacer S3)
# STORAGE_PROTOCOL=local
# LOCAL_RECORDING_STORAGE_PATH=/recordings
# LOCAL_AUDIO_CHUNK_STORAGE_PATH=/audio_chunks

# Hosting (ajustez avec votre domaine)
# SITE_DOMAIN=bot.votredomaine.com
# ALLOWED_HOSTS=bot.votredomaine.com,localhost
# CSRF_TRUSTED_ORIGINS=https://bot.votredomaine.com
EOF
```

**Note** : Si vous souhaitez passer en stockage local, decommentez les lignes `STORAGE_PROTOCOL`, `LOCAL_RECORDING_STORAGE_PATH` et `LOCAL_AUDIO_CHUNK_STORAGE_PATH`, et commentez les variables `AWS_*`.

### Etape 3 : Rebuild et relancer

```bash
# Rebuild l'image Docker (les nouvelles dependances seront installees)
docker compose -f dev.docker-compose.yaml build

# Arreter les services
docker compose -f dev.docker-compose.yaml down

# Relancer
docker compose -f dev.docker-compose.yaml up -d

# Appliquer les nouvelles migrations (0078 pour le partage video, etc.)
docker compose -f dev.docker-compose.yaml exec attendee-app-local python manage.py migrate
```

### Etape 4 : Verifier

```bash
# Verifier que les services tournent
docker compose -f dev.docker-compose.yaml ps

# Verifier le health check
curl http://localhost:8000/health/

# Verifier les logs
docker compose -f dev.docker-compose.yaml logs --tail=20
```

### Ce qui change par rapport au repo officiel

| Fonctionnalite | Repo officiel | Fork ClosiQode |
|---------------|---------------|----------------|
| Timeout bot | 1h fixe | Configurable (defaut 4h) |
| Stockage | S3 ou Azure uniquement | S3, Azure, ou **local** |
| Partage video | Pas de lien public | Liens publics avec tracking |
| Hosting config | Hardcode | Configurable via `.env` |

### Revenir au repo officiel

Si vous souhaitez revenir au repo officiel :

```bash
git remote set-url origin https://github.com/attendee-team/attendee.git
git fetch origin
git pull origin main
# Note : les migrations ajoutees resteront dans la base mais ne causeront pas de probleme
```

## Depannage

### Le bot ne rejoint pas le meeting

- Verifiez que le serveur est bien **linux/amd64** (Chrome ne fonctionne pas en emulation ARM)
- Consultez les logs du worker : `docker compose -f dev.docker-compose.yaml logs attendee-worker-local`

### Erreur "Permission denied" sur /recordings

- Le Dockerfile cree les repertoires avec les bonnes permissions
- Si le probleme persiste : `docker compose -f dev.docker-compose.yaml exec -u root attendee-worker-local chown -R app:app /recordings /audio_chunks`

### Erreur CSRF ou "Forbidden"

- Verifiez que `CSRF_TRUSTED_ORIGINS` contient votre domaine avec `https://`
- Verifiez que `ALLOWED_HOSTS` contient votre domaine

### Les emails ne sont pas envoyes

- Par defaut, les emails s'affichent dans les logs (mode console)
- Pour de vrais emails, configurez les variables `EMAIL_*` dans le `.env`
- Consultez les logs : `docker compose -f dev.docker-compose.yaml logs attendee-app-local | grep confirm-email`

### Le bot quitte apres 1 heure

- Augmentez `BOT_SOFT_TIME_LIMIT_SECONDS` dans le `.env` (defaut: 14400 = 4h)

## Variables d'environnement - Reference complete

| Variable | Description | Defaut |
|----------|-------------|--------|
| `DJANGO_SECRET_KEY` | Cle secrete Django | (generee) |
| `CREDENTIALS_ENCRYPTION_KEY` | Cle Fernet pour les credentials | (generee) |
| `SITE_DOMAIN` | Domaine de l'instance | `app.attendee.dev` |
| `ALLOWED_HOSTS` | Hosts autorises (virgules) | `localhost` |
| `CSRF_TRUSTED_ORIGINS` | Origines CSRF (virgules) | (vide) |
| `DJANGO_DEBUG` | Mode debug | `true` |
| `DJANGO_SSL_REQUIRE` | Forcer SSL | `true` en prod |
| `STORAGE_PROTOCOL` | Backend stockage | `s3` |
| `LOCAL_RECORDING_STORAGE_PATH` | Chemin recordings locaux | `/recordings` |
| `LOCAL_AUDIO_CHUNK_STORAGE_PATH` | Chemin audio chunks locaux | `/audio_chunks` |
| `AWS_RECORDING_STORAGE_BUCKET_NAME` | Bucket S3 | (vide) |
| `AWS_ACCESS_KEY_ID` | Cle AWS | (vide) |
| `AWS_SECRET_ACCESS_KEY` | Secret AWS | (vide) |
| `AWS_DEFAULT_REGION` | Region AWS | `us-east-1` |
| `BOT_SOFT_TIME_LIMIT_SECONDS` | Timeout max bot | `14400` (4h) |
| `DATABASE_URL` | URL base de donnees externe | (PostgreSQL Docker) |
| `REDIS_URL` | URL Redis | `redis://redis:6379/5` |
| `EMAIL_HOST` | Serveur SMTP | `smtp.mailgun.org` |
| `EMAIL_HOST_USER` | Utilisateur SMTP | (vide) |
| `EMAIL_HOST_PASSWORD` | Mot de passe SMTP | (vide) |
| `DEFAULT_FROM_EMAIL` | Expediteur emails | `noreply@mail.attendee.dev` |
