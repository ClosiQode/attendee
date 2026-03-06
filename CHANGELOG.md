# Changelog

Toutes les modifications notables de ce projet sont documentees dans ce fichier.
Format base sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

## [Non publie]

### Ajoute
- Support du stockage local filesystem via `STORAGE_PROTOCOL=local` comme alternative a S3 et Azure
- Nouveau `LocalFileUploader` pour copier les enregistrements vers le filesystem local
- Volumes Docker pour le stockage local des recordings et audio chunks
- Systeme de partage de video par lien public avec tracking des acces
- Modeles `SharedRecordingLink` et `SharedRecordingAccess` pour gerer les liens de partage
- Page de visualisation HTML5 pour les videos partagees
- Endpoints API pour creer, lister et desactiver les liens de partage
- Support du telechargement et du streaming pour le stockage local

### Modifie
- Rendu le `soft_time_limit` Celery de la tache `run_bot` configurable via la variable d'environnement `BOT_SOFT_TIME_LIMIT_SECONDS` (defaut: 14400s = 4h, ancien: 3600s = 1h)
