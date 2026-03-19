# CLAUDE.md

Ce fichier guide Claude Code lors du travail sur le projet Attendee.

## REGLE ESSENTIELLE - A RESPECTER ABSOLUMENT

**AVANT de modifier un fichier, vous DEVEZ lire au moins 3 fichiers** afin de comprendre comment assurer la coherence du processus.

Ceci est **OBLIGATOIRE**. Ne negligez cette etape sous aucun pretexte. La lecture des fichiers existants garantit :
- La coherence du code avec les modeles du projet
- Une bonne comprehension des conventions
- Le respect de l'architecture etablie
- L'evitement des modifications incompatibles

**Types de fichiers a lire absolument :**

1. **ARCHITECTURE.md** : Consultez la table des relations et les fichiers critiques pour comprendre l'impact de votre modification. Identifiez les dependants et les dependances. Si votre modification touche un fichier critique, verifiez que les systemes dependants ne seront pas casses.
2. **Fichiers similaires** : Lisez les fichiers aux fonctionnalites similaires pour comprendre les modeles et les conventions.
3. **Dependances importees** : Lisez la definition/l'implementation des importations dont vous n'etes pas certain de l'utilisation ; comprenez leur API, leurs types et leurs cas d'utilisation.

**Etapes a suivre :**

1. Consultez ARCHITECTURE.md pour identifier les impacts potentiels de votre modification
2. Lisez au moins 3 fichiers existants pertinents (fichiers dependants + dependances importees)
3. Comprenez les modeles, les conventions et l'utilisation de l'API
4. Procedez ensuite a la creation/modification des fichiers
5. Si la modification est structurelle, mettez a jour ARCHITECTURE.md

## CHANGELOG - OBLIGATOIRE

**A chaque modification du projet, vous DEVEZ mettre a jour le fichier CHANGELOG.md.**

- Si le fichier `CHANGELOG.md` n'existe pas, **creez-le immediatement**
- Documentez chaque modification avec : date, description, fichiers impactes
- Utilisez le format [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/)

## ARCHITECTURE - OBLIGATOIRE

**A chaque modification structurelle du projet, vous DEVEZ mettre a jour le fichier ARCHITECTURE.md.**

- Si le fichier `ARCHITECTURE.md` n'existe pas, **creez-le** en analysant le projet complet
- Mettez a jour lors de : ajout/suppression de fonctionnalite, modification de schema BDD, changement de dependances entre systemes, ajout de fichier critique
- Ne PAS mettre a jour pour : corrections de bugs, changements CSS, modifications de texte

## WORKFLOW OBLIGATOIRE - SWARM / EQUIPES D'AGENTS PARALLELES

**REGLE NON NEGOCIABLE : Utiliser `/swarm` (equipes d'agents paralleles) comme mode de travail PAR DEFAUT pour TOUTE tache.**

Le swarm n'est PAS une option — c'est le workflow standard. Travailler seul en sequentiel est l'EXCEPTION, pas la norme.

### Pourquoi c'est obligatoire

Les equipes d'agents (swarm) :
- Accelerent le travail de 3x a 5x en parallelisant les taches
- Produisent un code plus coherent grace a la specialisation des agents
- Reduisent les erreurs en isolant les responsabilites
- Permettent recherche + implementation en simultane

### QUAND UTILISER SWARM (= presque toujours)

**Utiliser `/swarm` des que la tache implique :**
- 2 fichiers ou plus a modifier
- Une recherche/exploration + une implementation
- Plusieurs etapes logiques (meme si elles semblent simples)
- Du frontend + du backend
- Des tests + du code
- De la documentation + du code
- Un refactoring, meme partiel
- Une nouvelle fonctionnalite, meme petite
- Un bug fix qui touche plusieurs fichiers

### Les SEULES exceptions (ne PAS utiliser swarm)

- Correction d'une faute de frappe dans UN seul fichier
- Modification d'UNE seule ligne de configuration
- Question simple de l'utilisateur (pas d'implementation)
- Lecture/exploration pure sans modification

### Comment structurer le swarm

1. **Toujours decomposer** la tache en sous-taches independantes
2. **Creer des agents specialises** : un par responsabilite (ex: `db-agent`, `api-agent`, `ui-agent`, `test-agent`)
3. **Paralleliser au maximum** : lancer les agents independants en meme temps
4. **Un agent = une responsabilite claire** : pas d'agent "fourre-tout"

### Regle d'or

**En cas de doute sur l'utilisation du swarm → UTILISER LE SWARM.** Il vaut mieux utiliser un swarm pour une tache simple que de ne pas l'utiliser pour une tache qui l'aurait merite.

## Presentation du projet

**Attendee** est une API open source pour gerer des meeting bots sur Zoom, Google Meet et Microsoft Teams. Le bot rejoint une reunion, enregistre l'audio/video et transcrit via des fournisseurs comme Deepgram.

- **Repository** : attendee (licence open source)
- **Site** : attendee.dev
- **Documentation** : docs.attendee.dev

## Stack technique

- **Framework** : Django 5.1 + Django REST Framework 3.15
- **Python** : 3.10
- **Base de donnees** : PostgreSQL 15 (via psycopg2)
- **Cache / Message broker** : Redis 7
- **Taches asynchrones** : Celery 5.4 (scheduler custom, pas Celery Beat)
- **Stockage** : django-storages (S3 via boto3 + Azure Blob Storage + Local filesystem)
- **Authentification** : django-allauth (email, Google OAuth) + SAML SSO (pysaml2)
- **API docs** : drf-spectacular (OpenAPI / Swagger / Redoc)
- **Linter/Formatter** : Ruff (pre-commit hooks)
- **Navigateur automatise** : Selenium + Chrome/ChromeDriver 134
- **Audio/Video** : GStreamer, PulseAudio, FFmpeg, OpenCV, PyVirtualDisplay, aiortc (WebRTC)
- **Transcription** : Deepgram, OpenAI, Gladia, AssemblyAI, Sarvam, ElevenLabs, Kyutai
- **Synthese IA** : OpenAI (GPT-5.x), Anthropic (Claude), Mistral
- **Paiements** : Stripe (checkout, autopay)
- **Frontend** : Django templates + HTMX 2.0.3 + Bootstrap 5.3
- **Deploiement** : Docker (Ubuntu 22.04 amd64), Kubernetes (optionnel)
- **Monitoring** : Sentry (Django, Celery, Redis integrations)

## Commandes de developpement

```bash
# Build de l'image Docker (~5 min)
make build
# ou: docker compose -f dev.docker-compose.yaml build

# Demarrer tous les services en arriere-plan
make up
# ou: docker compose -f dev.docker-compose.yaml up -d

# Arreter les services
make down

# Voir les logs
make logs

# Appliquer les migrations
make migrate
# ou: docker compose -f dev.docker-compose.yaml exec attendee-app-local python manage.py migrate

# Linter et formater le code
make lint
# ou: ruff check --fix && ruff format

# Creer les variables d'environnement locales
docker compose -f dev.docker-compose.yaml run --rm attendee-app-local python init_env.py > .env

# Lancer les tests
docker compose -f dev.docker-compose.yaml exec attendee-app-local python manage.py test bots.tests

# Lancer un test specifique
docker compose -f dev.docker-compose.yaml exec attendee-app-local python manage.py test bots.tests.test_google_meet_bot
```

## Architecture du projet

### Structure des dossiers

```
attendee/                    # Projet Django principal
  settings/                  # Configurations par environnement
    base.py                  # Settings communs (stockage, apps, etc.)
    development.py           # Dev local
    production.py            # Production
    test.py                  # Tests
  urls.py                    # Routage principal
  celery.py                  # Configuration Celery

accounts/                    # App Django - Gestion des utilisateurs et organisations
  models.py                  # User, Organization, UserRole

bots/                        # App Django principale - Coeur du projet
  models.py                  # Modeles principaux (~137K) : Project, Bot, BotEvent, etc.
  serializers.py             # Serializers DRF (~95K)
  bots_api_views.py          # Vues API REST pour les bots (~71K)
  bots_api_utils.py          # Utilitaires API bots
  projects_views.py          # Vues Django dashboard (HTMX)
  projects_urls.py           # Routes dashboard web
  bot_adapter.py             # Classe de base abstraite pour les adaptateurs de bot
  ai_summary_providers.py    # Abstraction OpenAI/Anthropic/Mistral pour synthese IA
  storage.py                 # Abstraction stockage (StorageAlias, remote_storage_url)
  authentication.py          # ApiKeyAuthentication (Token-based)
  throttling.py              # Rate limiting API (ProjectPostThrottle)
  webhook_utils.py           # Declenchement webhooks + payload construction
  automatic_leave_configuration.py  # Config auto-leave (timeouts)
  automatic_leave_utils.py   # Detection de bots par mots-cles

  bot_controller/            # Controleur principal du bot
    bot_controller.py         # Logique principale (~100K) : enregistrement, upload, events
    s3_file_uploader.py       # Upload vers AWS S3
    azure_file_uploader.py    # Upload vers Azure Blob Storage
    screen_and_audio_recorder.py  # Enregistrement ecran + audio via GStreamer
    streaming_uploader.py     # Upload en streaming
    audio_chunk_uploader.py   # Upload des chunks audio

  google_meet_bot_adapter/   # Adaptateur Google Meet (herite de WebBotAdapter)
    google_meet_bot_adapter.py
    google_meet_ui_methods.py       # Methodes UI Selenium (~40K)
    google_meet_chromedriver_payload.js  # Payload JS injecte dans Chrome (~87K)

  web_bot_adapter/           # Adaptateur de base pour bots web (Google Meet, Teams)
    web_bot_adapter.py        # Gestion Chrome/Selenium, auto-leave, audio/video

  zoom_bot_adapter/          # Adaptateur Zoom (SDK natif)
  zoom_web_bot_adapter/      # Adaptateur Zoom via navigateur
  teams_bot_adapter/         # Adaptateur Microsoft Teams
  webpage_streamer/          # Streaming de pages web dans les reunions

  tasks/                     # Taches Celery asynchrones (un fichier par tache)
    __init__.py               # IMPORTANT: toute nouvelle tache doit etre importee ici
    run_bot_task.py           # Tache principale de lancement de bot (4h timeout)
    run_bot_in_ephemeral_container_task.py  # Lancement dans conteneur Docker ephemere
    deliver_webhook_task.py   # Livraison des webhooks (3 retries, backoff)
    process_utterance_task.py # Transcription temps reel (7 providers)
    process_async_transcription_task.py  # Transcription asynchrone post-meeting
    generate_ai_summary_task.py  # Generation synthese IA (OpenAI/Anthropic/Mistral)
    sync_calendar_task.py     # Sync calendriers Google/Microsoft (24h)
    launch_scheduled_bot_task.py  # Lancement bots planifies
    autopay_charge_task.py    # Facturation Stripe automatique
    send_slack_alert_task.py  # Alertes Slack sur erreurs fatales

  templates/projects/        # Templates Django (HTMX)
    sidebar.html              # Navigation principale
    project_bot_detail.html   # Detail bot (7 onglets)
    project_bots.html         # Liste bots + filtres
    partials/                 # Fragments HTMX (recordings, AI summary, credentials)

  templatetags/bot_filters.py  # Filtres custom (couleurs participants, dates)

  management/commands/
    run_scheduler.py          # Daemon scheduler (polling, PAS Celery Beat)

  tests/                     # Suite de tests (~47 fichiers)
  migrations/                # Migrations Django (~80+ fichiers)
```

### Modeles principaux (bots/models.py)

- **Project** : Projet contenant des bots, lie a une Organization
- **Bot** : Entite principale - un bot qui rejoint une reunion (19 etats possibles)
- **BotEvent** : Evenements du cycle de vie du bot (19 types, 28 sous-types)
- **Recording** : Enregistrement media (S3/Azure/Local) avec etats et transcription
- **Utterance** : Segment transcrit (audio → texte via providers)
- **AudioChunk** : Chunk audio brut (PCM/MP3, par participant ou mixe)
- **AsyncTranscription** : Transcription post-meeting (orchestre process_utterance tasks)
- **Participant** : Participant de reunion (UUID, nom, evenements join/leave)
- **Credentials** : Credentials chiffres Fernet (13 types: Deepgram, OpenAI, Anthropic, Mistral, etc.)
- **AISummarySettings** : Config synthese IA par projet (provider, modele, prompt, reasoning_effort)
- **Calendar** / **CalendarEvent** : Integration calendrier Google/Microsoft
- **ZoomOAuthApp** / **ZoomOAuthConnection** : Gestion OAuth Zoom
- **WebhookSubscription** / **WebhookDeliveryAttempt** : Systeme de webhooks (10 triggers)
- **ApiKey** : Cles API hashees SHA-256
- **CreditTransaction** : Historique facturation (centicredits)
- **SharedRecordingLink** : Liens de partage public des enregistrements
- **GoogleMeetBotLoginGroup** : Groupes de login pour bots Google Meet

### API REST

Toutes les routes API sont sous `/api/v1/` :
- `/api/v1/bots/` - CRUD et gestion des bots
- `/api/v1/calendars/` - Integration calendrier
- `/api/v1/zoom_oauth_connections/` - Connexions OAuth Zoom
- `/api/v1/app_sessions/` - Sessions applicatives

Interface admin Django disponible sur `/admin/` (desactivable via `DISABLE_ADMIN`).

### Systeme de stockage

Le stockage est configure via `STORAGE_PROTOCOL` (env var) :
- `"s3"` (defaut) : AWS S3 via boto3 + django-storages
- `"azure"` : Azure Blob Storage
- `"local"` : Systeme de fichiers local (/recordings)

Configuration dans `attendee/settings/base.py`.
Point d'extension principal : `bot_controller.py:get_file_uploader()`.

Les uploaders suivent une interface commune :
- `upload_file(file_path, callback=None)`
- `wait_for_upload()`
- `delete_file(file_path)`

### Systeme de synthese IA

Configure via le modele `AISummarySettings` (OneToOne avec Project) :
- **Providers** : OpenAI (1), Anthropic (2), Mistral (3)
- **Declenchement** : automatique apres POST_PROCESSING_COMPLETED ou manuellement via UI
- **Provider abstraction** : `ai_summary_providers.py` (reasoning_effort conditionnel pour GPT-5.x/o1/o3)
- **Tache Celery** : `generate_ai_summary_task` (soft_time_limit=300s, max_retries=2)
- **Credentials** : utilise le vault Credentials du projet (type correspondant au provider)
- **Rendu** : Markdown (marked.js) ou JSON, avec bloc email HTML copiable

### Systeme de webhooks

- 10 types de triggers (bot_state, transcript, chat, participants, calendar, etc.)
- Signature HMAC-SHA256 via WebhookSecret
- Livraison via task Celery `deliver_webhook` (3 retries, exponential backoff)
- Tracking: WebhookDeliveryAttempt avec idempotency_key

### Systeme d'auto-leave

Defini dans `automatic_leave_configuration.py` avec ces timeouts :
- `silence_timeout_seconds` : 600s (10 min de silence)
- `silence_activate_after_seconds` : 1200s (active apres 20 min)
- `only_participant_in_meeting_timeout_seconds` : 60s
- `wait_for_host_to_start_meeting_timeout_seconds` : 600s
- `waiting_room_timeout_seconds` : 900s
- `max_uptime_seconds` : None (infini par defaut)

Logique implementee dans `web_bot_adapter.py:check_auto_leave_conditions()` (ligne 939) et `zoom_bot_adapter.py` (ligne 1144).

## Conventions de code

### Style (Ruff)

- **Indentation** : 4 espaces
- **Quotes** : doubles (`"`)
- **Longueur de ligne** : pas de limite stricte (line-length = 999)
- **Imports** : tries automatiquement par Ruff (isort integre)
- **Regles** : pycodestyle (E), Pyflakes (F), import sorting (I)
- **Ignores** : E501 (ligne trop longue), E722 (bare except), E402 (import position), F403 (wildcard import)

### Nommage

- **Fichiers** : snake_case (ex: `bot_controller.py`, `s3_file_uploader.py`)
- **Classes** : PascalCase (ex: `BotController`, `S3FileUploader`, `GoogleMeetBotAdapter`)
- **Fonctions/methodes** : snake_case (ex: `get_file_uploader`, `check_auto_leave_conditions`)
- **Variables** : snake_case
- **Constantes/Enums** : UPPER_SNAKE_CASE (ex: `LEAVE_REASON`, `AUTO_LEAVE_SILENCE`)
- **Object IDs** : prefixes courts + random (ex: `bot_`, `proj_`, `gbg_`)

### Patterns du projet

- **Adaptateurs de bot** : Heritage hierarchique `BotAdapter` > `WebBotAdapter` > `GoogleMeetBotAdapter`/`TeamsBotAdapter`
- **Uploaders de fichiers** : Interface commune (duck typing), instancies dans `get_file_uploader()`
- **Taches Celery** : Un fichier par tache dans `bots/tasks/`, decorateur `@shared_task`. **IMPORTANT** : toute nouvelle tache doit etre importee dans `bots/tasks/__init__.py` et ajoutee a `__all__` sinon Celery ne la decouvre pas
- **Serializers** : Serializers DRF avec schemas OpenAPI personnalises
- **Concurrence** : `IntegerVersionField` pour l'optimistic locking
- **Chiffrement** : Fernet pour les credentials sensibles
- **Callbacks** : Pattern callback largement utilise dans les adaptateurs de bot

### Tests

- Framework : `django.test.TestCase`
- Emplacement : `bots/tests/`
- Nommage : `test_<module>.py`
- Les tests Google Meet : `test_google_meet_bot.py`, `test_google_meet_bot_2.py`

## Variables d'environnement importantes

```
# Obligatoires
DJANGO_SECRET_KEY              # Cle secrete Django
CREDENTIALS_ENCRYPTION_KEY     # Cle Fernet pour chiffrer les credentials
DJANGO_SETTINGS_MODULE         # Module settings (ex: attendee.settings.development)
POSTGRES_HOST                  # Dev: hostname PostgreSQL
DATABASE_URL                   # Prod: connexion complete via dj-database-url
REDIS_URL                      # Connexion Redis (broker + cache)

# Stockage
STORAGE_PROTOCOL               # "s3" (defaut), "azure" ou "local"
AWS_RECORDING_STORAGE_BUCKET_NAME
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION
AWS_ENDPOINT_URL               # Pour MinIO ou S3-compatible
AZURE_RECORDING_STORAGE_CONTAINER_NAME
AZURE_STORAGE_CONNECTION_STRING
LOCAL_RECORDING_STORAGE_PATH   # Defaut: /recordings (mode local)

# Branding / Acces
PLATFORM_NAME                  # Nom marque blanche (defaut: "Attendee")
DISABLE_SIGNUP                 # Bloquer inscriptions publiques (true/false)
DISABLE_ADMIN                  # Masquer /admin/

# Bot execution
BOT_MAX_EXECUTION_SECONDS      # Timeout conteneur (defaut: 14400 = 4h)
BOT_CPU_QUOTA                  # CPU quota conteneur (defaut: 100000 = 1 core)
CONCURRENT_BOTS_LIMIT          # Limite de bots simultanees (defaut: 2500)

# Monitoring
SENTRY_DSN                     # URL Sentry (optionnel)

# Email
EMAIL_HOST                     # Serveur SMTP (optionnel en dev)
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
EMAIL_PORT                     # Port SMTP
EMAIL_USE_SSL / EMAIL_USE_TLS
```

## Services Docker (dev)

- `attendee-app-local` : Serveur Django (port 8000)
- `attendee-worker-local` : Worker Celery
- `attendee-scheduler-local` : Scheduleur de taches
- `attendee-webpage-streamer-local` : Streamer de pages web (port 8001, profil optionnel)
- `postgres` : PostgreSQL 15
- `redis` : Redis 7

## Workflow de developpement

1. Creer une branche : `git switch -c feature/nom-de-la-feature`
2. Installer les pre-commit hooks : `pip install pre-commit && pre-commit install`
3. Faire les modifications en respectant les conventions Ruff
4. Lancer `make lint` avant de commiter
5. Lancer les tests pertinents
6. Creer une Pull Request avec description claire

## Fichiers et dossiers importants

| Fichier | Description |
|---------|-------------|
| `ARCHITECTURE.md` | Cartographie complete : arbre, relations, fichiers critiques |
| `bots/models.py` | Tous les modeles Django (~137K lignes) |
| `bots/bot_controller/bot_controller.py` | Logique principale du bot (~100K) |
| `bots/web_bot_adapter/web_bot_adapter.py` | Base des bots navigateur (Google Meet, Teams) |
| `bots/google_meet_bot_adapter/` | Adaptateur specifique Google Meet |
| `bots/storage.py` | Abstraction stockage |
| `bots/ai_summary_providers.py` | Abstraction OpenAI/Anthropic/Mistral |
| `bots/bot_controller/s3_file_uploader.py` | Upload S3 |
| `bots/bot_controller/azure_file_uploader.py` | Upload Azure |
| `bots/automatic_leave_configuration.py` | Configuration des timeouts auto-leave |
| `bots/tasks/__init__.py` | **Critique** : imports Celery (toute tache doit y etre) |
| `bots/projects_views.py` | Vues dashboard web (HTMX) |
| `bots/webhook_utils.py` | Declenchement et construction webhooks |
| `attendee/settings/base.py` | Settings Django principaux |
| `bots/serializers.py` | Serializers API (~95K) |
| `bots/bots_api_views.py` | Endpoints API des bots (~71K) |
| `bots/management/commands/run_scheduler.py` | Daemon scheduler (polling) |
