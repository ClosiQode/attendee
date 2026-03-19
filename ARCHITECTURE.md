# ARCHITECTURE.md — Attendee

> Cartographie complète des fonctionnalités, relations et fichiers critiques du projet Attendee.

---

## 1. Arbre des fonctionnalités

```
[CORE] Infrastructure Django
├─ [CORE] Authentication & Users (accounts/)
│  ├─ [FEATURE] Email-based login → utilise django-allauth
│  │  ├─ [SUB] Google OAuth provider → utilisé par Login flow
│  │  ├─ [SUB] Email verification → déclenche auto-login invited users
│  │  └─ [HOOK] pre_save User → déclenche création Organization + Project
│  ├─ [FEATURE] Signup control → dépend de DISABLE_SIGNUP env
│  │  ├─ [SUB] StandardAccountAdapter → autorise inscriptions publiques
│  │  └─ [SUB] NoNewUsersAccountAdapter → bloque inscriptions
│  ├─ [FEATURE] Organization management
│  │  ├─ [SUB] Credit system (centicredits) → utilisé par Billing
│  │  ├─ [SUB] Feature flags (webhooks, async_transcription, app_sessions)
│  │  └─ [SUB] Autopay Stripe → déclenche autopay_charge task
│  └─ [FEATURE] User roles (Admin / Regular) → utilisé par Permissions
│
├─ [CORE] Project system (bots/models.py)
│  ├─ [FEATURE] Multi-project support → dépend de Organization
│  ├─ [FEATURE] API Key management → utilisé par API Authentication
│  │  └─ [SUB] SHA-256 hashed keys → persiste dans ApiKey
│  ├─ [FEATURE] Credentials vault → utilisé par Bot adapters, Transcription, AI Summary
│  │  └─ [SUB] Fernet encryption → persiste dans Credentials (13 types)
│  ├─ [FEATURE] Webhook subscriptions → déclenche deliver_webhook task
│  │  ├─ [SUB] 10 trigger types (bot_state, transcript, chat, participants, calendar, etc.)
│  │  ├─ [SUB] HMAC-SHA256 signature → dépend de WebhookSecret
│  │  └─ [SUB] Delivery tracking → persiste dans WebhookDeliveryAttempt
│  └─ [FEATURE] Project access control → dépend de ProjectAccess + UserRole
│
├─ [CORE] Bot engine (bots/bot_controller/, bots/*_bot_adapter/)
│  ├─ [FEATURE] Bot lifecycle state machine
│  │  ├─ [SUB] States: READY → SCHEDULED → STAGED → JOINING → JOINED → LEAVING → POST_PROCESSING → ENDED
│  │  ├─ [SUB] BotEventManager → persiste dans BotEvent (19 event types, 28 sub-types)
│  │  ├─ [HOOK] State transitions → déclenche webhooks
│  │  ├─ [HOOK] POST_PROCESSING_COMPLETED → déclenche generate_ai_summary_task
│  │  └─ [HOOK] Fatal error → déclenche send_slack_alert task
│  │
│  ├─ [FEATURE] Bot Controller (bot_controller.py)
│  │  ├─ [SUB] Recording orchestration → utilise ScreenAndAudioRecorder
│  │  ├─ [SUB] File upload → utilise S3FileUploader / AzureFileUploader
│  │  ├─ [SUB] Streaming upload → utilise StreamingUploader
│  │  ├─ [SUB] Audio chunk upload → utilise AudioChunkUploader
│  │  ├─ [SUB] Heartbeat monitoring → persiste dans Bot
│  │  └─ [SUB] Credit deduction → persiste dans CreditTransaction
│  │
│  ├─ [FEATURE] Bot Adapter hierarchy
│  │  ├─ [SUB] BotAdapter (base) → interface abstraite
│  │  ├─ [SUB] WebBotAdapter → dépend de Chrome/Selenium, PulseAudio, GStreamer
│  │  │  ├─ [SUB] Auto-leave system → dépend de AutomaticLeaveConfiguration
│  │  │  │  ├─ [UTIL] Silence detection (600s timeout)
│  │  │  │  ├─ [UTIL] Only participant detection (60s)
│  │  │  │  ├─ [UTIL] Waiting room timeout (900s)
│  │  │  │  ├─ [UTIL] Max uptime enforcement
│  │  │  │  └─ [UTIL] Bot keyword detection → utilise automatic_leave_utils
│  │  │  └─ [SUB] Recording pause/resume
│  │  ├─ [SUB] GoogleMeetBotAdapter → dépend de WebBotAdapter
│  │  │  ├─ [SUB] UI methods (Selenium) → google_meet_ui_methods.py
│  │  │  ├─ [SUB] ChromeDriver JS payload → google_meet_chromedriver_payload.js
│  │  │  └─ [SUB] Bot login groups → dépend de GoogleMeetBotLogin
│  │  ├─ [SUB] TeamsBotAdapter → dépend de WebBotAdapter
│  │  │  └─ [SUB] SAML SSO login → dépend de pysaml2
│  │  ├─ [SUB] ZoomBotAdapter → dépend de zoom-meeting-sdk (natif)
│  │  └─ [SUB] ZoomWebBotAdapter → dépend de WebBotAdapter
│  │
│  ├─ [FEATURE] Participant tracking
│  │  ├─ [SUB] Join/Leave events → persiste dans ParticipantEvent
│  │  ├─ [SUB] Speech start/stop → persiste dans ParticipantEvent
│  │  └─ [HOOK] Events → déclenche webhooks (PARTICIPANT_EVENTS_*)
│  │
│  └─ [FEATURE] Chat messages
│     ├─ [SUB] Capture chat → persiste dans ChatMessage
│     ├─ [SUB] Send chat → persiste dans BotChatMessageRequest
│     └─ [HOOK] New message → déclenche webhook (CHAT_MESSAGES_UPDATE)
│
├─ [CORE] Recording & Transcription
│  ├─ [FEATURE] Recording management
│  │  ├─ [SUB] State machine: NOT_STARTED → IN_PROGRESS → COMPLETE/FAILED
│  │  ├─ [SUB] Formats: MP4, WEBM, MP3, NONE
│  │  ├─ [SUB] Views: SPEAKER_VIEW, GALLERY_VIEW, SPEAKER_VIEW_NO_SIDEBAR
│  │  ├─ [SUB] Storage backends → dépend de S3 / Azure / Local
│  │  └─ [SUB] Shared recording links → persiste dans SharedRecordingLink
│  │
│  ├─ [FEATURE] Real-time transcription
│  │  ├─ [SUB] Audio capture → persiste dans AudioChunk
│  │  ├─ [SUB] Utterance processing → déclenche process_utterance task
│  │  └─ [SUB] 7 providers: Deepgram, OpenAI, Gladia, AssemblyAI, Sarvam, ElevenLabs, Kyutai
│  │
│  ├─ [FEATURE] Async transcription (post-meeting)
│  │  ├─ [SUB] AsyncTranscription model → déclenche process_async_transcription task
│  │  ├─ [SUB] Grouped utterance processing (AssemblyAI)
│  │  └─ [HOOK] Completion → déclenche generate_ai_summary_task
│  │
│  └─ [FEATURE] Platform closed captions
│     └─ [SUB] Per-platform language config → dépend de TranscriptionSettings
│
├─ [CORE] AI Summary system
│  ├─ [FEATURE] AI Summary generation
│  │  ├─ [SUB] Provider abstraction → utilise ai_summary_providers.py
│  │  │  ├─ [SUB] OpenAI (GPT-5.x, o1, o3) → avec reasoning_effort conditionnel
│  │  │  ├─ [SUB] Anthropic (Claude) → claude-sonnet-4-20250514 par défaut
│  │  │  └─ [SUB] Mistral → mistral-large-latest par défaut
│  │  ├─ [SUB] Celery task → generate_ai_summary_task (soft_time_limit=300s)
│  │  └─ [SUB] Status tracking → persiste dans Recording (ai_summary, ai_summary_status)
│  │
│  └─ [FEATURE] AI Summary settings (per project)
│     ├─ [SUB] Enable/Disable toggle
│     ├─ [SUB] Provider selection
│     ├─ [SUB] Custom system prompt
│     ├─ [SUB] Model selection
│     └─ [SUB] Reasoning effort config
│
├─ [CORE] REST API (bots/bots_api_views.py)
│  ├─ [FEATURE] Bot CRUD → /api/v1/bots/
│  │  ├─ [SUB] Create bot → valide credentials, concurrency, calendar
│  │  ├─ [SUB] List bots → cursor pagination, filtrage par state/url/date
│  │  ├─ [SUB] Bot actions: leave, pause, resume, delete_data
│  │  └─ [SUB] Throttling → dépend de ProjectPostThrottle
│  ├─ [FEATURE] Recording API → /api/v1/bots/<id>/recording
│  ├─ [FEATURE] Transcript API → /api/v1/bots/<id>/transcript
│  │  └─ [SUB] Async transcription creation (POST)
│  ├─ [FEATURE] Chat API → /api/v1/bots/<id>/chat_messages, send_chat_message
│  ├─ [FEATURE] Media output API → speech, output_audio, output_image, output_video
│  ├─ [FEATURE] Participant API → participants, participant_events
│  ├─ [FEATURE] Calendar API → /api/v1/calendars/
│  ├─ [FEATURE] Zoom OAuth API → /api/v1/zoom_oauth_connections/
│  └─ [FEATURE] App Sessions API → /api/v1/app_sessions/ (Zoom RTMS)
│
├─ [CORE] Web Dashboard (bots/projects_views.py)
│  ├─ [FEATURE] Bot management UI → HTMX + Bootstrap 5
│  │  ├─ [SUB] Bot list with filters → project_bots.html
│  │  ├─ [SUB] Bot detail (7 tabs) → project_bot_detail.html
│  │  ├─ [SUB] Recording player + transcription → partials/project_bot_recordings.html
│  │  ├─ [SUB] AI Summary tab → partials/project_bot_ai_summary.html
│  │  │  ├─ [UTIL] Markdown rendering (marked.js)
│  │  │  ├─ [UTIL] JSON rendering
│  │  │  ├─ [UTIL] Email preview + copy block
│  │  │  └─ [UTIL] HTMX polling (every 3s during generation)
│  │  └─ [SUB] Speaker timeline visualization
│  ├─ [FEATURE] Settings pages
│  │  ├─ [SUB] Credentials management (14 types)
│  │  ├─ [SUB] AI Summary settings
│  │  ├─ [SUB] API keys
│  │  ├─ [SUB] Webhooks
│  │  └─ [SUB] Project settings
│  ├─ [FEATURE] Team management → invite, roles, delete
│  ├─ [FEATURE] Calendar management
│  └─ [FEATURE] Billing → Stripe integration
│
├─ [CORE] Celery async tasks (bots/tasks/)
│  ├─ [FEATURE] run_bot → exécution principale du bot (4h timeout)
│  ├─ [FEATURE] run_bot_in_ephemeral_container → lancement Docker isolé
│  ├─ [FEATURE] process_utterance → transcription temps réel (7 providers)
│  ├─ [FEATURE] process_async_transcription → transcription post-meeting
│  ├─ [FEATURE] generate_ai_summary_task → synthèse IA (3 providers)
│  ├─ [FEATURE] deliver_webhook → livraison webhooks (3 retries, backoff)
│  ├─ [FEATURE] sync_calendar → sync Google/Microsoft calendars (24h)
│  ├─ [FEATURE] sync_zoom_oauth_connection → sync Zoom meetings (7 jours)
│  ├─ [FEATURE] refresh_zoom_oauth_connection → refresh tokens (30 jours)
│  ├─ [FEATURE] launch_scheduled_bot → lancement bots planifiés
│  ├─ [FEATURE] restart_bot_pod → restart pods K8s
│  ├─ [FEATURE] autopay_charge → facturation Stripe auto
│  └─ [FEATURE] send_slack_alert → alertes Slack
│
└─ [CORE] Infrastructure & Config
   ├─ [FEATURE] Storage backends
   │  ├─ [SUB] AWS S3 → boto3, django-storages
   │  ├─ [SUB] Azure Blob Storage → azure-storage-blob
   │  └─ [SUB] Local filesystem → /recordings
   ├─ [FEATURE] Docker deployment
   │  ├─ [SUB] 5 services: app, worker, scheduler, postgres, redis
   │  ├─ [SUB] Optional: webpage-streamer
   │  └─ [SUB] Chrome 134 + ChromeDriver 134
   ├─ [FEATURE] Kubernetes support → restart_bot_pod, ephemeral containers
   ├─ [FEATURE] Scheduler daemon → run_scheduler (polling, pas Celery Beat)
   ├─ [FEATURE] Sentry monitoring → errors, traces, profiles
   └─ [FEATURE] White-label → PLATFORM_NAME configurable
```

---

## 2. Table des relations

| From | Relation | To | Description |
|------|----------|----|-------------|
| **Organization** | contient | Project[] | Un org = N projets |
| **Organization** | contient | User[] | Un org = N utilisateurs |
| **Organization** | persiste dans | CreditTransaction[] | Historique facturation |
| **User** | appartient à | Organization | via FK |
| **User** | a accès à | Project[] | via ProjectAccess ou role Admin |
| **Project** | contient | Bot[] | Un projet = N bots |
| **Project** | contient | Credentials[] | Credentials chiffrés (unique par type) |
| **Project** | contient | ApiKey[] | Clés API hashées SHA-256 |
| **Project** | contient | WebhookSubscription[] | Abonnements webhook |
| **Project** | contient | Calendar[] | Calendriers synchronisés |
| **Project** | contient | GoogleMeetBotLoginGroup[] | Groupes login Google Meet |
| **Project** | contient | ZoomOAuthApp[] | Apps Zoom OAuth |
| **Project** | a un | AISummarySettings | Config synthèse IA (OneToOne) |
| **Bot** | appartient à | Project | via FK |
| **Bot** | a N | BotEvent[] | Événements lifecycle |
| **Bot** | a N | Recording[] | Enregistrements |
| **Bot** | a N | Participant[] | Participants de la réunion |
| **Bot** | a N | ChatMessage[] | Messages chat capturés |
| **Bot** | a N | BotMediaRequest[] | Requêtes média (audio/video/image) |
| **Bot** | a N | BotChatMessageRequest[] | Messages envoyés |
| **Bot** | a N | BotLogEntry[] | Logs applicatifs |
| **Bot** | a N | BotResourceSnapshot[] | Snapshots ressources |
| **Bot** | optionnel | CalendarEvent | Lien vers événement calendrier |
| **Bot** | déclenche | run_bot task | Exécution principale |
| **Bot** | déclenche | run_bot_in_ephemeral_container | Alternative Docker |
| **Recording** | appartient à | Bot | via FK |
| **Recording** | a N | Utterance[] | Segments transcrits |
| **Recording** | a N | AudioChunk[] | Chunks audio bruts |
| **Recording** | a N | AsyncTranscription[] | Transcriptions post-meeting |
| **Recording** | a N | SharedRecordingLink[] | Liens de partage |
| **Recording** | stocké dans | S3 / Azure / Local | Fichier media |
| **Recording** | déclenche | generate_ai_summary_task | Après transcription complète |
| **Utterance** | appartient à | Recording | via FK |
| **Utterance** | référence | Participant | Qui parle |
| **Utterance** | référence | AudioChunk | Source audio |
| **Utterance** | déclenche | process_utterance task | Transcription |
| **AsyncTranscription** | appartient à | Recording | via FK |
| **AsyncTranscription** | déclenche | process_async_transcription task | Orchestration |
| **AsyncTranscription** | déclenche | generate_ai_summary_task | Après complétion |
| **BotEvent** | appartient à | Bot | via FK |
| **BotEvent** | déclenche | deliver_webhook task | Sur changement d'état |
| **BotEvent** | a N | BotDebugScreenshot[] | Screenshots debug |
| **Calendar** | appartient à | Project | via FK |
| **Calendar** | a N | CalendarEvent[] | Événements synchronisés |
| **Calendar** | a N | CalendarNotificationChannel[] | Push notifications |
| **Calendar** | déclenche | sync_calendar task | Synchronisation périodique |
| **CalendarEvent** | déclenche | launch_scheduled_bot task | Si bot planifié |
| **ZoomOAuthApp** | appartient à | Project | via FK |
| **ZoomOAuthApp** | a N | ZoomOAuthConnection[] | Connexions utilisateurs |
| **ZoomOAuthConnection** | déclenche | sync_zoom_oauth_connection task | Sync meetings |
| **ZoomOAuthConnection** | déclenche | refresh_zoom_oauth_connection task | Refresh tokens |
| **WebhookSubscription** | appartient à | Project | via FK |
| **WebhookSubscription** | optionnel | Bot | Webhook spécifique à un bot |
| **WebhookDeliveryAttempt** | appartient à | WebhookSubscription | via FK |
| **WebhookDeliveryAttempt** | déclenche | deliver_webhook task | Livraison HTTP |
| **AISummarySettings** | appartient à | Project | OneToOne |
| **AISummarySettings** | utilise | Credentials | Clé API du provider LLM |
| **AISummarySettings** | configure | generate_ai_summary_task | Provider, modèle, prompt |
| **Scheduler daemon** | déclenche | launch_scheduled_bot | Bots planifiés |
| **Scheduler daemon** | déclenche | sync_calendar | Toutes les 24h |
| **Scheduler daemon** | déclenche | sync_zoom_oauth_connection | Tous les 7 jours |
| **Scheduler daemon** | déclenche | refresh_zoom_oauth_connection | Tous les 30 jours |
| **Scheduler daemon** | déclenche | autopay_charge | Quand crédits < seuil |

---

## 3. Fichiers critiques par fonctionnalité

### Authentication & Users
| Fichier | Rôle |
|---------|------|
| `accounts/models.py` | User, Organization, UserRole |
| `accounts/adapters.py` | Signup control, email verification |
| `accounts/views.py` | Home redirect |
| `accounts/templates/account/` | Login, signup, password reset |

### Bot Engine
| Fichier | Rôle |
|---------|------|
| `bots/models.py` | Bot, BotEvent, BotStates, BotEventManager (~137K) |
| `bots/bot_adapter.py` | Interface abstraite BotAdapter |
| `bots/bot_controller/bot_controller.py` | Logique principale (~100K) |
| `bots/bot_controller/s3_file_uploader.py` | Upload S3 |
| `bots/bot_controller/azure_file_uploader.py` | Upload Azure |
| `bots/bot_controller/screen_and_audio_recorder.py` | Enregistrement GStreamer |
| `bots/bot_controller/streaming_uploader.py` | Upload streaming |
| `bots/bot_controller/audio_chunk_uploader.py` | Upload chunks audio |
| `bots/web_bot_adapter/web_bot_adapter.py` | Base bots navigateur (Chrome/Selenium) |
| `bots/google_meet_bot_adapter/google_meet_bot_adapter.py` | Adaptateur Google Meet |
| `bots/google_meet_bot_adapter/google_meet_ui_methods.py` | Méthodes UI Selenium (~40K) |
| `bots/google_meet_bot_adapter/google_meet_chromedriver_payload.js` | Payload JS injecté (~87K) |
| `bots/teams_bot_adapter/` | Adaptateur Microsoft Teams |
| `bots/zoom_bot_adapter/` | Adaptateur Zoom SDK natif |
| `bots/zoom_web_bot_adapter/` | Adaptateur Zoom navigateur |
| `bots/automatic_leave_configuration.py` | Config timeouts auto-leave |
| `bots/automatic_leave_utils.py` | Détection bots par mots-clés |

### Recording & Transcription
| Fichier | Rôle |
|---------|------|
| `bots/models.py` | Recording, Utterance, AudioChunk, AsyncTranscription |
| `bots/storage.py` | StorageAlias, remote_storage_url |
| `bots/tasks/process_utterance_task.py` | Transcription 7 providers |
| `bots/tasks/process_async_transcription_task.py` | Orchestration post-meeting |
| `bots/tasks/process_utterance_group_for_async_transcription_task.py` | Batch AssemblyAI |

### AI Summary
| Fichier | Rôle |
|---------|------|
| `bots/models.py` | AISummarySettings, Recording.ai_summary_* |
| `bots/ai_summary_providers.py` | Abstraction OpenAI/Anthropic/Mistral |
| `bots/tasks/generate_ai_summary_task.py` | Tâche Celery génération |
| `bots/templates/projects/partials/project_bot_ai_summary.html` | Rendu Markdown/JSON + email copiable |
| `bots/templates/projects/project_ai_summary_settings.html` | Page settings |

### REST API
| Fichier | Rôle |
|---------|------|
| `bots/bots_api_views.py` | Endpoints API bots (~71K) |
| `bots/serializers.py` | Serializers DRF (~95K) |
| `bots/bots_api_utils.py` | Utilitaires création/validation bots |
| `bots/bots_api_urls.py` | Routes API bots |
| `bots/calendars_api_views.py` | Endpoints calendriers |
| `bots/app_session_api_views.py` | Endpoints app sessions |
| `bots/zoom_oauth_connections_api_views.py` | Endpoints Zoom OAuth |
| `bots/authentication.py` | ApiKeyAuthentication |
| `bots/throttling.py` | Rate limiting |

### Web Dashboard
| Fichier | Rôle |
|---------|------|
| `bots/projects_views.py` | Vues Django template |
| `bots/projects_urls.py` | Routes dashboard |
| `templates/base.html` | Template racine (Bootstrap 5, HTMX) |
| `bots/templates/projects/sidebar.html` | Navigation sidebar |
| `bots/templates/projects/project_bot_detail.html` | Page détail bot (7 tabs) |
| `bots/templates/projects/project_bots.html` | Liste bots + filtres |
| `bots/templates/projects/project_credentials.html` | Gestion credentials |
| `bots/templates/projects/partials/project_bot_recordings.html` | Player + transcription |
| `bots/templatetags/bot_filters.py` | Filtres custom (couleurs, dates) |

### Celery Tasks
| Fichier | Rôle |
|---------|------|
| `attendee/celery.py` | Configuration Celery + SSL |
| `bots/tasks/__init__.py` | Exports + autodiscovery |
| `bots/tasks/run_bot_task.py` | Exécution bot (4h timeout) |
| `bots/tasks/run_bot_in_ephemeral_container_task.py` | Docker isolé |
| `bots/tasks/deliver_webhook_task.py` | Livraison webhooks |
| `bots/tasks/launch_scheduled_bot_task.py` | Bots planifiés |
| `bots/tasks/sync_calendar_task.py` | Sync calendriers (Google/Microsoft) |
| `bots/tasks/autopay_charge_task.py` | Facturation Stripe |
| `bots/tasks/send_slack_alert_task.py` | Alertes Slack |
| `bots/management/commands/run_scheduler.py` | Daemon scheduler (polling) |

### Webhooks
| Fichier | Rôle |
|---------|------|
| `bots/models.py` | WebhookSubscription, WebhookDeliveryAttempt, WebhookSecret |
| `bots/webhook_utils.py` | trigger_webhook(), payload construction |
| `bots/tasks/deliver_webhook_task.py` | HTTP delivery + HMAC signing |

### Infrastructure & Config
| Fichier | Rôle |
|---------|------|
| `attendee/settings/base.py` | Settings partagés (storage, apps, Celery) |
| `attendee/settings/development.py` | Dev local (PostgreSQL, console email) |
| `attendee/settings/production.py` | Prod (DATABASE_URL, SSL, gunicorn) |
| `attendee/urls.py` | Routage principal |
| `dev.docker-compose.yaml` | Services Docker (5 containers) |
| `Dockerfile` | Image Ubuntu 22.04 + Chrome 134 |
| `requirements.txt` | 105 dépendances Python |
| `attendee/sentry.py` | Monitoring Sentry |

### Billing & Payments
| Fichier | Rôle |
|---------|------|
| `accounts/models.py` | Organization.centicredits, autopay_* |
| `bots/models.py` | CreditTransaction, CreditTransactionManager |
| `bots/tasks/autopay_charge_task.py` | Stripe PaymentIntent |
| `bots/projects_views.py` | ProjectBillingView, CheckoutSession |

### Calendar Integration
| Fichier | Rôle |
|---------|------|
| `bots/models.py` | Calendar, CalendarEvent, CalendarNotificationChannel |
| `bots/tasks/sync_calendar_task.py` | Google Calendar API + Microsoft Graph |
| `bots/calendars_api_views.py` | REST API calendriers |

### Zoom Integration
| Fichier | Rôle |
|---------|------|
| `bots/models.py` | ZoomOAuthApp, ZoomOAuthConnection, ZoomMeetingMapping |
| `bots/tasks/sync_zoom_oauth_connection_task.py` | Sync meetings Zoom |
| `bots/tasks/refresh_zoom_oauth_connection_task.py` | Refresh OAuth tokens |
| `bots/tasks/validate_zoom_oauth_connections_task.py` | Validation connexions |
| `bots/zoom_bot_adapter/` | SDK natif Zoom |
| `bots/zoom_web_bot_adapter/` | Zoom via navigateur |

### Shared Recordings
| Fichier | Rôle |
|---------|------|
| `bots/models.py` | SharedRecordingLink, SharedRecordingAccess |
| `bots/templates/shared_recording.html` | Vue publique enregistrement |
| `bots/projects_views.py` | Create/Delete share links |

---

## 4. Services Docker

```
┌─────────────────────────────────────────────────────────┐
│                    attendee_network                       │
│                                                           │
│  ┌──────────────────┐  ┌──────────────────────────────┐  │
│  │   postgres:15     │  │         redis:7               │  │
│  │   :5432           │  │         :6379                  │  │
│  └────────┬─────────┘  └──────────┬───────────────────┘  │
│           │                        │                      │
│  ┌────────┴────────────────────────┴───────────────────┐ │
│  │              attendee-app-local :8000                │ │
│  │              (Django runserver)                       │ │
│  └──────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              attendee-worker-local                    │ │
│  │              (Celery worker + Chrome + GStreamer)     │ │
│  └──────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              attendee-scheduler-local                 │ │
│  │              (Polling daemon, pas Celery Beat)        │ │
│  └──────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         attendee-webpage-streamer-local :8001         │ │
│  │         (Optionnel, profil webpage-streamer)          │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Variables d'environnement critiques

| Variable | Obligatoire | Description |
|----------|:-----------:|-------------|
| `DJANGO_SECRET_KEY` | **Oui** | Clé secrète Django |
| `CREDENTIALS_ENCRYPTION_KEY` | **Oui** | Clé Fernet chiffrement credentials |
| `POSTGRES_HOST` / `DATABASE_URL` | **Oui** | Connexion PostgreSQL |
| `REDIS_URL` | **Oui** | Connexion Redis (broker + cache) |
| `STORAGE_PROTOCOL` | Non | `s3` (défaut), `azure`, ou `local` |
| `PLATFORM_NAME` | Non | Nom marque blanche (défaut: Attendee) |
| `DISABLE_SIGNUP` | Non | Bloquer inscriptions publiques |
| `DISABLE_ADMIN` | Non | Masquer /admin/ |
| `SENTRY_DSN` | Non | Monitoring erreurs |
| `CHARGE_CREDITS_FOR_BOTS` | Non | Déduire crédits par bot |

---

*Généré automatiquement à partir de l'analyse du codebase le 2026-03-19.*
