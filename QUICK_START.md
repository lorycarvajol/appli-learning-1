# 🚀 Quick Start Guide - Environnement Docker

Ce guide vous permet de démarrer rapidement la plateforme d'apprentissage avec Docker.

## 📋 Prérequis

- Docker Desktop installé et lancé
- Docker Compose (inclus avec Docker Desktop)
- Git

## 🏗️ Architecture Docker

Le projet est entièrement dockerisé avec les services suivants :

- **postgres** : Base de données PostgreSQL 15
- **redis** : Cache et message broker Redis 7
- **backend** : API REST Django (port 8000)
- **daphne** : WebSocket ASGI Django Channels (port 8001)
- **celery** : Workers pour tâches asynchrones
- **celery-beat** : Scheduler pour tâches périodiques
- **frontend** : Application React avec Vite (port 5173)
- **nginx** : Reverse proxy (optionnel, port 80)

## 🚀 Démarrage Rapide

### 1. Cloner le projet (si pas déjà fait)

```bash
cd "C:\Users\loryc\OneDrive\Desktop\appli learning"
```

### 2. Lancer tous les services

```bash
docker-compose up -d
```

Cette commande va :
- Télécharger toutes les images Docker nécessaires
- Construire les images pour backend et frontend
- Créer les conteneurs
- Démarrer tous les services

### 3. Créer les migrations et le superuser

```bash
# Créer les migrations
docker-compose exec backend python manage.py makemigrations

# Appliquer les migrations
docker-compose exec backend python manage.py migrate

# Créer un superuser
docker-compose exec backend python manage.py createsuperuser
```

Exemple de superuser :
- Email: `admin@example.com`
- Password: `admin123`

### 4. Accéder à l'application

- **Frontend React** : http://localhost:5173
- **API Backend** : http://localhost:8000/api
- **Admin Django** : http://localhost:8000/admin
- **WebSocket** : ws://localhost:8001

## 📝 Utilisation

### S'inscrire et se connecter

1. Ouvrir http://localhost:5173
2. Cliquer sur "S'inscrire"
3. Remplir le formulaire :
   - Email: `test@example.com`
   - Prénom: `Test`
   - Nom: `User`
   - Mot de passe: `testpass123`
4. Vous serez automatiquement connecté et redirigé vers le dashboard

### Tester l'authentification

L'authentification JWT est fonctionnelle :
- Les tokens sont stockés dans localStorage
- Le refresh automatique fonctionne en cas de token expiré
- La déconnexion blacklist le refresh token

## 🔧 Commandes Utiles

### Voir les logs

```bash
# Tous les services
docker-compose logs -f

# Un service spécifique
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Arrêter les services

```bash
# Arrêter sans supprimer
docker-compose stop

# Arrêter et supprimer les conteneurs
docker-compose down

# Tout supprimer (conteneurs + volumes)
docker-compose down -v
```

### Redémarrer un service

```bash
docker-compose restart backend
docker-compose restart frontend
```

### Accéder au shell d'un conteneur

```bash
# Backend Django shell
docker-compose exec backend python manage.py shell

# Bash dans le backend
docker-compose exec backend sh

# Bash dans le frontend
docker-compose exec frontend sh
```

### Installer des dépendances

```bash
# Backend - ajouter un package Python
docker-compose exec backend pip install package-name
docker-compose exec backend pip freeze > requirements/base.txt

# Frontend - ajouter un package npm
docker-compose exec frontend npm install package-name
```

### Reconstruire les images

```bash
# Reconstruire tout
docker-compose build

# Reconstruire un service spécifique
docker-compose build backend
docker-compose build frontend

# Forcer la reconstruction
docker-compose build --no-cache
```

## 🧪 Tests

### Tests Backend

```bash
# Lancer tous les tests
docker-compose exec backend pytest

# Tests avec couverture
docker-compose exec backend pytest --cov=apps

# Tests d'une app spécifique
docker-compose exec backend pytest apps/accounts/tests/
```

### Tests Frontend (à venir)

```bash
docker-compose exec frontend npm run test
```

## 🗄️ Base de Données

### Accéder à PostgreSQL

```bash
# Via docker-compose
docker-compose exec postgres psql -U postgres -d learning_platform

# Via psql local (si installé)
psql -h localhost -U postgres -d learning_platform
```

### Réinitialiser la base de données

```bash
# Supprimer et recréer
docker-compose down -v
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

## 🐛 Troubleshooting

### Les conteneurs ne démarrent pas

```bash
# Vérifier les logs
docker-compose logs

# Vérifier l'état des services
docker-compose ps

# Redémarrer proprement
docker-compose down
docker-compose up -d
```

### Port déjà utilisé

Si vous avez une erreur "port already allocated" :

```bash
# Windows - identifier le processus sur le port 8000
netstat -ano | findstr :8000

# Arrêter le processus (remplacer PID)
taskkill /PID <PID> /F
```

### Problème de permissions (Linux/Mac)

```bash
# Donner les permissions sur le dossier
sudo chown -R $USER:$USER .
```

### Celery ne traite pas les tâches

```bash
# Vérifier que Redis fonctionne
docker-compose exec redis redis-cli ping

# Redémarrer Celery
docker-compose restart celery
```

### Le frontend ne se connecte pas au backend

1. Vérifier que le backend est démarré : http://localhost:8000/api/
2. Vérifier les variables d'environnement dans `frontend/.env`
3. Vérifier les logs CORS dans le backend

## 📦 Structure des Volumes Docker

Les données persistantes sont stockées dans des volumes Docker :

- `postgres_data` : Données PostgreSQL
- `redis_data` : Données Redis
- `static_volume` : Fichiers statiques Django
- `media_volume` : Fichiers média uploadés

## 🔄 Hot Reload

Le hot reload fonctionne automatiquement :

- **Backend** : Gunicorn avec `--reload`
- **Frontend** : Vite avec hot module replacement

Modifiez le code et les changements seront visibles immédiatement.

## 🚀 Prochaines Étapes

Maintenant que l'environnement fonctionne :

1. ✅ Authentification JWT complète
2. 📚 Créer les modèles pour les Chapitres et Leçons
3. 📝 Créer les endpoints API REST
4. 🎨 Développer l'interface React
5. 🔌 Intégrer le WebSocket pour le temps réel

Consultez le **[ROADMAP](./01_ROADMAP.md)** pour le plan complet.

## 📞 Aide

Pour plus d'informations, consultez :
- **[CLAUDE.md](./CLAUDE.md)** - Guide technique complet
- **[04_ARCHITECTURE_TECHNIQUE.md](./04_ARCHITECTURE_TECHNIQUE.md)** - Architecture détaillée
- **[05_GUIDE_DEVELOPPEMENT_INITIAL.md](./05_GUIDE_DEVELOPPEMENT_INITIAL.md)** - Guide de développement

---

**Statut actuel** : ✅ Infrastructure Docker complète et fonctionnelle
