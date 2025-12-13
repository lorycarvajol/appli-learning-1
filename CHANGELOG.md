# Changelog

Historique des modifications du projet Learning Platform.

## [0.3.0] - 2025-12-13

### ✨ Ajouté

**Backend - App Progression:**
- Création de l'app `progression` avec 3 modèles:
  - `ChapterAccess`: Contrôle d'accès aux chapitres (débloqué par trainer)
  - `UserProgress`: Progression de l'utilisateur sur chaque leçon (status, attempts, score, time_spent, last_code)
  - `ActivityLog`: Historique des activités (LESSON_STARTED, LESSON_COMPLETED, EXERCISE_SUBMITTED, QUIZ_COMPLETED, CHAPTER_UNLOCKED, BADGE_EARNED)
- Serializers pour tous les modèles de progression
- ViewSets pour la gestion de la progression avec permissions basées sur les rôles
- Permission personnalisée `IsTrainerOrAdmin`
- Endpoints API:
  - POST `/api/progression/chapter-access/unlock_chapter/` - Débloquer un chapitre pour un apprenant
  - POST `/api/progression/chapter-access/lock_chapter/` - Verrouiller un chapitre
  - GET `/api/progression/chapter-access/my_access/` - Obtenir ses propres accès
  - POST `/api/progression/progress/mark_completed/` - Marquer une leçon comme complétée
  - GET `/api/progression/progress/my_progress/` - Obtenir sa propre progression
  - GET `/api/progression/activity/` - Obtenir l'historique d'activité
  - GET `/api/progression/trainer-dashboard/learners_summary/` - Résumé de tous les apprenants
  - GET `/api/progression/trainer-dashboard/recent_activity/` - Activité récente
  - GET `/api/progression/trainer-dashboard/{id}/learner_detail/` - Détails d'un apprenant
- Interface admin minimale pour debug

**Backend - Contenu de Démonstration:**
- Commande Django `load_demo_content` pour charger du contenu de cours
- 3 chapitres de démonstration créés:
  - "Introduction au HTML" (4 leçons: 2 théories, 1 exercice, 1 quiz)
  - "CSS Fondamentaux" (2 leçons: 1 théorie, 1 exercice)
  - "JavaScript pour Débutants" (2 leçons: 1 théorie, 1 exercice)
- Exercices avec starter_code, solution, tests automatisés, hints
- Quiz avec questions à choix multiples et scoring
- Commande `create_demo_users` pour créer des utilisateurs de test:
  - 1 Trainer: trainer@test.com / trainer123
  - 3 Learners: alice@test.com, bob@test.com, charlie@test.com / learner123

**Frontend - Dashboard Trainer:**
- Redux slice `trainerSlice` pour la gestion de l'état
- Service API `progressionApi.js` avec tous les endpoints
- Composant `TrainerDashboard`: Dashboard principal avec onglets
  - Stats globales (total apprenants, activités récentes, taux de complétion moyen)
  - Onglet "Apprenants" avec liste et détails
  - Onglet "Activité Récente"
- Composant `LearnersList`: Liste des apprenants avec:
  - Progress bars pour chapitres débloqués et leçons complétées
  - Temps passé et score moyen
  - Leçon en cours
  - Sélection pour afficher les détails
- Composant `LearnerDetail`: Vue détaillée d'un apprenant avec:
  - Informations du profil (nom, email, points, niveau)
  - Progression par chapitre avec taux de complétion
  - Boutons pour débloquer/verrouiller les chapitres (🔓/🔒)
  - Historique des 5 dernières activités
- Composant `RecentActivity`: Liste des activités récentes avec:
  - Icônes par type d'activité
  - Couleurs différenciées par type
  - Affichage du nom de l'utilisateur, type d'activité, leçon/chapitre, date/heure
- Route `/trainer` ajoutée (protégée)
- Bouton "Dashboard Trainer" dans le Dashboard principal (visible uniquement pour TRAINER/ADMIN)

### 🔧 Modifié

- Ajout du reducer `trainer` au Redux store
- Mise à jour du Dashboard principal avec bouton conditionnel pour trainers/admins
- Désactivation de l'admin Django pour la création de contenu (utilisé uniquement pour debug)

### 📝 Documentation

- CLAUDE.md mis à jour avec l'état actuel du développement
- Nouvelle section "App Progression" dans la structure
- Documentation des nouveaux endpoints API
- Instructions pour charger le contenu et créer les utilisateurs de test
- Guide de test complet du dashboard trainer

### 🎯 Changement de Direction

**Important:** L'interface admin Django ne doit **PAS** servir à créer du contenu de cours. Elle est utilisée uniquement pour le debug. Les fonctionnalités principales:
- **Contenu de cours**: Créé via des fixtures/migrations pendant le développement (`load_demo_content`)
- **Dashboard Admin/Trainer**: Interface React dédiée pour:
  - Monitorer l'avancement des apprenants
  - Voir leur progression détaillée
  - Débloquer/bloquer des chapitres au fur et à mesure
  - Consulter l'activité en temps réel

---

## [0.2.0] - 2025-12-12

### ✨ Ajouté

**Backend - App Courses:**
- Création de l'app `courses` avec 5 modèles:
  - `Chapter`: Organisation des cours en chapitres
  - `Lesson`: Contenu des leçons (3 types: THEORY, EXERCISE, QUIZ)
  - `Exercise`: Exercices de code avec tests automatisés
  - `Quiz`: Quiz avec questions à choix multiples
  - `Project`: Projets finaux avec critères d'évaluation
- Serializers pour tous les modèles avec gestion des permissions
- ViewSets read-only avec filtres et ordering
- Routes API: `/api/courses/chapters/`, `/api/courses/lessons/`, etc.
- Interface admin complète avec inline editing pour exercises/quiz
- Champs JSONB pour tests (Exercise) et questions (Quiz)

**Frontend - Courses:**
- Redux slice `chaptersSlice` pour la gestion de l'état
- Service API `coursesApi.js` avec tous les endpoints
- Composant `ChaptersList`: Grille de cartes affichant tous les chapitres
- Composant `ChapterDetail`: Vue détaillée d'un chapitre avec ses leçons
- Composant `LessonView`: Affichage du contenu selon le type (Theory/Exercise/Quiz)
- Navigation breadcrumb pour améliorer l'UX
- Bouton "Accéder aux chapitres" dans le Dashboard

**Documentation:**
- Section complète "État Actuel du Développement" dans CLAUDE.md
- Documentation des endpoints API disponibles
- Guide de test de l'application
- Liste des prochaines étapes par ordre de priorité

### 🔧 Modifié

- Ajout du reducer `chapters` au Redux store
- Mise à jour du Dashboard avec lien vers les chapitres
- Routes ajoutées: `/chapters`, `/chapters/:slug`, `/lessons/:slug`

### 📝 Documentation

- Mise à jour de CLAUDE.md avec progression complète
- Création de CHANGELOG.md pour historique des versions

---

## [0.1.0] - 2025-12-12

### ✨ Ajouté

**Infrastructure:**
- Configuration Docker Compose avec 7 services (postgres, redis, backend, daphne, celery, celery-beat, frontend)
- Dockerfiles pour backend (Python 3.11) et frontend (Node 18)
- Scripts de démarrage `start.bat` (Windows) et `start.sh` (Linux/Mac)
- Requirements Python organisés (base, development, production)

**Backend - Configuration:**
- Settings Django modulaires (base.py, development.py, production.py)
- Configuration JWT avec SimpleJWT (access 1h, refresh 7j)
- CORS configuré pour développement (localhost:5173)
- Logging en console pour Docker
- Configuration Redis pour cache et Celery
- Django REST Framework avec filtres et pagination

**Backend - App Accounts:**
- Modèle User personnalisé avec UUID et email-based auth
- Modèle Profile avec gamification (points, level)
- Système de rôles (LEARNER, TRAINER, ADMIN)
- API complète d'authentification:
  - Register (POST /api/auth/register/)
  - Login (POST /api/auth/login/)
  - Logout avec blacklist (POST /api/auth/logout/)
  - Token refresh (POST /api/auth/token/refresh/)
  - Current user (GET/PUT /api/auth/me/)
  - Change password (PUT /api/auth/change-password/)
- Interface admin Django configurée
- Signal pour création automatique du Profile

**Frontend - Configuration:**
- Projet Vite + React 18
- Redux Toolkit configuré
- React Router v6
- Tailwind CSS
- Axios avec intercepteurs JWT pour auto-refresh

**Frontend - Authentification:**
- Page Login avec validation de formulaire
- Page Register avec confirmation de mot de passe
- Gestion des tokens JWT dans localStorage
- Auto-refresh des tokens sur 401
- PrivateRoute pour protéger les routes
- Redux slice `authSlice` avec async thunks
- Dashboard utilisateur avec affichage du profil

### 🔧 Résolu

- **Logging Error**: Suppression du handler 'file', utilisation uniquement de console pour Docker
- **Docker Compose Warning**: Retrait de la ligne obsolète `version: '3.8'`
- **Migration Error**: Correction de l'ordre d'exécution (makemigrations avant migrate)
- **Rate Limiting**: Désactivation du throttling en développement pour éviter 429
- **Infinite Loop Frontend**: Ajout de state `hasFetched` pour éviter les appels API infinis

### 📝 Documentation

- Création de CLAUDE.md avec guide complet du projet
- Documentation de l'architecture backend et frontend
- Guide des commandes de développement
- Patterns et conventions du projet
- Troubleshooting des problèmes courants

---

## Format

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

### Types de changements

- `✨ Ajouté` pour les nouvelles fonctionnalités
- `🔧 Modifié` pour les changements aux fonctionnalités existantes
- `🗑️ Déprécié` pour les fonctionnalités bientôt retirées
- `❌ Retiré` pour les fonctionnalités retirées
- `🔒 Sécurité` pour les corrections de vulnérabilités
- `🐛 Corrigé` pour les corrections de bugs
- `📝 Documentation` pour les changements de documentation
