# EasyCook

EasyCook est une application Django permettant de créer automatiquement des recettes à partir de vidéos courtes (comme les Reels Instagram). Le projet combine du scraping, de la transcription audio et l’utilisation d’OpenAI pour générer une recette structurée.

## Fonctionnalités principales

- Suivi des influenceurs et de leurs vidéos
- Extraction de l’audio d’une vidéo et transcription
- Génération d’une recette (ingrédients, quantités, étapes, tags)
- Interface web basée sur Django pour consulter et modifier les recettes
- Commandes de gestion pour importer des ingrédients ou analyser des vidéos

## Endpoints

- **GET /health** — vérifie que le serveur fonctionne. Répond :

```json
{"status": "healthy"}
```

## Lancement en local

1. Créer un environnement virtuel Python 3 et l’activer.
2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

3. Appliquer les migrations et lancer le serveur :

```bash
python manage.py migrate
python manage.py runserver
```

## Structure du projet

```
api_auth/       – vues d’authentification et endpoint de santé
application/    – modèles, vues et commandes pour les vidéos et recettes
customtools/    – mixins et vues génériques réutilisables
templates/      – templates HTML (base.html, navigation.html, etc.)
static/         – fichiers statiques (JS, CSS, images)
easycook/       – configuration Django (settings, urls, wsgi)
```

### Commandes utiles

- `python manage.py analyse_video <uuid_video>` : analyse une vidéo existante et crée une recette.
- `python manage.py scrapp_ingredients` : importe des ingrédients depuis différentes sources.

Pour un démarrage en production, le dépôt fournit un `Procfile` qui lance `gunicorn` après avoir appliqué les migrations et collecté les fichiers statiques.
