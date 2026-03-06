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
- Bouton "Share" dans l'interface web (onglet Recordings) pour creer et gerer les liens de partage
- Option "Never expires" pour les liens de partage qui n'expirent jamais
- Route Django pour servir les fichiers locaux (recordings et audio chunks) avec authentification
- Configuration SMTP email configurable via `.env` (`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, etc.)
- Variable `DISABLE_SIGNUP` pour desactiver les inscriptions publiques
- Variables `EMAIL_PORT` et `EMAIL_USE_SSL` ajoutees au fichier .env

- Champ `title` personnalisable pour les liens de partage
- Affichage de la taille des fichiers d'enregistrement
- Bouton de suppression des enregistrements
- Bouton de suppression des membres d'equipe avec confirmation
- Marque blanche : `PLATFORM_NAME` configurable via `.env` pour remplacer "Attendee"
- Masquage du lien "Creer un compte" quand `DISABLE_SIGNUP=true`
- Les utilisateurs invites n'ont plus besoin de verifier leur email (email marque comme verifie automatiquement, lien de configuration du mot de passe envoye directement)

### Modifie
- Traduction complete de l'interface en francais : pages d'authentification, sidebar, dashboard, detail bot, calendriers, equipe, partage de videos
- Rendu le `soft_time_limit` Celery de la tache `run_bot` configurable via la variable d'environnement `BOT_SOFT_TIME_LIMIT_SECONDS` (defaut: 14400s = 4h, ancien: 3600s = 1h)
- Ajout de `base_url` aux backends de stockage local pour generer des URLs correctes
- Page de partage en marque blanche (suppression du footer "Powered by Attendee")
