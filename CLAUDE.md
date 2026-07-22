# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **web-based learning platform** for teaching web development, featuring:
- Controlled progression system (trainer unlocks chapters for learners)
- Interactive code exercises with automatic validation in Docker sandbox
- Gamification (badges, points, leaderboard)
- Real-time activity tracking via WebSocket
- Community forum
- Project submission and review system

**Target Users:** 3 roles - Learner (students), Trainer (instructors), Admin
**Tech Stack:** Django 5.0+ (backend), React 18+ (frontend), PostgreSQL, Redis, Celery, Django Channels

## État Actuel du Développement (Mis à jour: 2025-12-12)

### ✅ Fonctionnalités Complétées

#### Infrastructure Docker
- **Docker Compose configuré** avec 7 services:
  - `postgres` (PostgreSQL 15)
  - `redis` (Redis 7)
  - `backend` (Django + Gunicorn)
  - `daphne` (ASGI server pour WebSocket)
  - `celery` (async tasks)
  - `celery-beat` (scheduled tasks)
  - `frontend` (React + Vite)
- **Scripts de démarrage**: `start.bat` (Windows) et `start.sh` (Linux/Mac)
- **Volumes persistants**: Base de données et médias conservés entre redémarrages

#### Backend Django (100% Fonctionnel)

**Configuration:**
- Settings modulaires: `base.py`, `development.py`, `production.py`
- JWT authentication avec SimpleJWT (access 1h, refresh 7j)
- CORS configuré pour localhost:5173
- Rate limiting désactivé en développement
- Logging en console (pas de fichiers pour Docker)

**App Accounts (Authentification):**
- ✅ Modèle User personnalisé avec UUID et email-based auth
- ✅ Modèle Profile avec gamification (points, level)
- ✅ Rôles: LEARNER, TRAINER, ADMIN
- ✅ API complète: register, login, logout, token refresh, current user
- ✅ Admin interface configurée
- ✅ Migrations appliquées et testées
- ✅ Système de blacklist des tokens lors du logout

**App Courses (Gestion du contenu):**
- ✅ 5 Modèles créés et migrés:
  - `Chapter`: Chapitres avec ordre, durée estimée, publication
  - `Lesson`: Leçons (3 types: THEORY, EXERCISE, QUIZ)
  - `Exercise`: Exercices de code avec starter_code, solution, tests (JSONB)
  - `Quiz`: Quiz avec questions (JSONB), passing_score, randomisation
  - `Project`: Projets finaux avec évaluation et critères
- ✅ Serializers pour tous les modèles avec permissions
- ✅ ViewSets read-only avec filtres et ordering
- ✅ URLs configurées: `/api/courses/chapters/`, `/api/courses/lessons/`, etc.
- ✅ Admin interface complète avec inline editing
- ✅ Relations: Chapter → Lessons, Lesson ↔ Exercise/Quiz

**Endpoints Backend Disponibles:**
```
POST   /api/auth/register/           - Inscription
POST   /api/auth/login/              - Connexion (retourne JWT)
POST   /api/auth/logout/             - Déconnexion (blacklist token)
POST   /api/auth/token/refresh/      - Rafraîchir access token
GET    /api/auth/me/                 - Infos utilisateur courant
PUT    /api/auth/me/                 - Modifier profil
PUT    /api/auth/change-password/    - Changer mot de passe

GET    /api/courses/chapters/        - Liste des chapitres
GET    /api/courses/chapters/{slug}/ - Détails chapitre avec leçons
GET    /api/courses/lessons/         - Liste des leçons
GET    /api/courses/lessons/{slug}/  - Détails leçon avec exercise/quiz
GET    /api/courses/exercises/{id}/  - Détails exercice
GET    /api/courses/quizzes/{id}/    - Détails quiz
GET    /api/courses/projects/        - Liste des projets
GET    /api/courses/projects/{slug}/ - Détails projet

GET    /admin/                       - Interface admin Django
```

#### Frontend React (100% Fonctionnel)

**Configuration:**
- Vite + React 18
- Redux Toolkit pour state management
- React Router v6 pour navigation
- Tailwind CSS pour styling
- Axios avec intercepteurs JWT

**Features Authentification:**
- ✅ Page Login avec formulaire et validation
- ✅ Page Register avec confirmation password
- ✅ Stockage tokens dans localStorage
- ✅ Auto-refresh des tokens sur 401
- ✅ PrivateRoute pour protection des routes
- ✅ Redux slice authSlice avec async thunks
- ✅ Dashboard utilisateur avec profil et stats
- ✅ Logout fonctionnel avec redirection

**Features Courses:**
- ✅ Redux slice chaptersSlice pour state management
- ✅ API service coursesApi.js avec tous les endpoints
- ✅ Page ChaptersList: Grille de cartes avec tous les chapitres
- ✅ Page ChapterDetail: Détails chapitre + liste des leçons
- ✅ Page LessonView: Affichage du contenu selon le type
  - Théorie: Contenu Markdown + vidéo optionnelle
  - Exercice: Instructions + code de départ (éditeur à venir)
  - Quiz: Instructions + métadonnées (interface à venir)
- ✅ Navigation breadcrumb fonctionnelle
- ✅ Bouton "Accéder aux chapitres" dans le Dashboard

**Routes Frontend Disponibles:**
```
/login              - Connexion
/register           - Inscription
/dashboard          - Dashboard utilisateur (protected)
/chapters           - Liste des chapitres (protected)
/chapters/:slug     - Détails d'un chapitre (protected)
/lessons/:slug      - Visualisation d'une leçon (protected)
```

### 🔧 Problèmes Résolus

1. **Logging Error** (FileNotFoundError: django.log)
   - Solution: Supprimé handler 'file', gardé uniquement console pour Docker

2. **Docker Compose Warning** (version obsolete)
   - Solution: Supprimé la ligne `version: '3.8'`

3. **Migration Error** (relation 'accounts_user' does not exist)
   - Solution: Exécuté makemigrations avant migrate

4. **Rate Limiting en développement** (429 Too Many Requests)
   - Solution: Désactivé throttling dans development.py

5. **Infinite Loop Frontend** (ERR_INSUFFICIENT_RESOURCES)
   - Cause: fetchCurrentUser() appelé à chaque render
   - Solution: Ajouté state `hasFetched` pour appeler une seule fois

### 📝 Comment Tester l'Application

**1. Démarrer l'environnement:**
```bash
.\start.bat  # Windows
# ou
./start.sh   # Linux/Mac
```

**2. Créer un superuser (si pas déjà fait):**
```bash
docker-compose exec backend python manage.py createsuperuser
```

**3. Accéder à l'admin Django:**
- URL: http://localhost:8000/admin/
- Créer des chapitres et leçons
- Marquer `is_published = True` pour les rendre visibles

**4. Tester le frontend:**
- URL: http://localhost:5173/
- S'inscrire ou se connecter
- Cliquer sur "Accéder aux chapitres"
- Naviguer dans les chapitres et leçons

### 🚧 Prochaines Étapes (Par Ordre de Priorité)

#### Phase 1: Progression Tracking
- [ ] Créer app `progression` avec modèles:
  - `UserProgress`: État progression par leçon
  - `ChapterAccess`: Contrôle d'accès aux chapitres
  - `ActivityLog`: Historique des activités
- [ ] API endpoints pour marquer leçons comme complétées
- [ ] Frontend: Bouton "Marquer comme terminé" fonctionnel
- [ ] Affichage de la progression dans ChaptersList

#### Phase 2: Validation de Code
- [ ] Créer app `validation` avec sandbox Docker
- [ ] Service `code_runner.py` pour exécution sécurisée
- [ ] API endpoint `/api/exercises/{id}/submit/`
- [ ] Frontend: Éditeur Monaco pour écrire du code
- [ ] Affichage des résultats de tests
- [ ] Système de hints progressifs

#### Phase 3: Interface Quiz
- [ ] Frontend: Composant QuizInterface
- [ ] Affichage questions avec options multiples
- [ ] Soumission et calcul du score
- [ ] Feedback immédiat sur les réponses
- [ ] Randomisation questions/options si configuré

#### Phase 4: Gamification — ✅ Fait (voir section dédiée plus bas)
- [x] App `gamification` (Badge, UserBadge, PointTransaction, UserStreak)
- [x] Attribution automatique idempotente des badges
- [x] Objectifs secrets masqués côté serveur + révélation animée
- [x] Frontend: page Trophées, prochains objectifs, série de jours
- [ ] Leaderboard — volontairement reporté (choix produit : progression
      personnelle d'abord, le grand livre de points le rend trivial à ajouter)

#### Phase 5: Fonctionnalités Trainer
- [ ] Dashboard trainer avec statistiques élèves
- [ ] Système de déblocage de chapitres
- [ ] Review de projets soumis
- [ ] Tableau de bord activité en temps réel

#### Phase 6: WebSocket & Real-time
- [ ] Configuration Django Channels complète
- [ ] Consumers pour auto-save code
- [ ] Consumer pour activité en temps réel
- [ ] Frontend: WebSocket service
- [ ] Auto-save toutes les 3 secondes

#### Phase 7: Forum Communautaire
- [ ] Créer app `forum`:
  - `Post`: Questions/discussions
  - `Reply`: Réponses
  - `Vote`: Système de votes
- [ ] API CRUD complète
- [ ] Frontend: Liste posts, création, réponses
- [ ] Système de recherche et tags

### 📁 Structure des Fichiers Importants

**Backend:**
```
backend/
├── config/
│   ├── settings/
│   │   ├── base.py          ✅ Settings partagés
│   │   ├── development.py   ✅ Rate limiting désactivé
│   │   └── production.py    ✅ Config production
│   ├── urls.py              ✅ URLs principales
│   ├── wsgi.py              ✅ WSGI pour Gunicorn
│   └── asgi.py              🚧 ASGI pour Channels
├── apps/
│   ├── accounts/            ✅ 100% Complet
│   │   ├── models.py        ✅ User, Profile
│   │   ├── serializers.py   ✅ Register, User, Profile, ChangePassword
│   │   ├── views.py         ✅ Register, CurrentUser, Logout
│   │   ├── urls.py          ✅ Routes auth
│   │   ├── admin.py         ✅ Admin interface
│   │   └── signals.py       ✅ Auto-create Profile
│   ├── courses/             ✅ 100% Complet
│   │   ├── models.py        ✅ Chapter, Lesson, Exercise, Quiz, Project
│   │   ├── serializers.py   ✅ Tous les serializers
│   │   ├── views.py         ✅ ViewSets read-only
│   │   ├── urls.py          ✅ Routes courses
│   │   └── admin.py         ✅ Admin avec inlines
│   ├── progression/         ⏳ À créer
│   ├── gamification/        ⏳ À créer
│   ├── validation/          ⏳ À créer
│   └── forum/               ⏳ À créer
├── requirements/
│   ├── base.txt            ✅ Django, DRF, psycopg2, etc.
│   ├── development.txt     ✅ Debug tools
│   └── production.txt      ✅ Gunicorn, etc.
└── Dockerfile              ✅ Python 3.11-slim

Frontend:
```
frontend/
├── src/
│   ├── app/
│   │   └── store.js         ✅ Redux store (auth, chapters)
│   ├── features/
│   │   ├── auth/            ✅ 100% Complet
│   │   │   ├── authSlice.js       ✅ Redux slice
│   │   │   ├── Login.jsx          ✅ Page login
│   │   │   ├── Register.jsx       ✅ Page register
│   │   │   └── PrivateRoute.jsx   ✅ Route protection
│   │   └── chapters/        ✅ 100% Complet
│   │       ├── chaptersSlice.js   ✅ Redux slice
│   │       ├── ChaptersList.jsx   ✅ Liste chapitres
│   │       ├── ChapterDetail.jsx  ✅ Détails chapitre
│   │       └── LessonView.jsx     ✅ Vue leçon
│   ├── components/
│   │   ├── Dashboard.jsx    ✅ Dashboard utilisateur
│   │   ├── layout/          ⏳ Navbar, Footer à créer
│   │   └── ui/              ⏳ Composants réutilisables
│   ├── services/
│   │   └── api/
│   │       ├── apiService.js      ✅ Axios + JWT interceptor
│   │       └── coursesApi.js      ✅ API courses
│   ├── App.jsx              ✅ Routes configurées
│   └── main.jsx             ✅ Redux Provider
├── package.json             ✅ Dependencies
├── vite.config.js           ✅ Config Vite
├── tailwind.config.js       ✅ Config Tailwind
└── Dockerfile               ✅ Node 18 multi-stage
```

### 💾 État de la Base de Données

**Tables existantes:**
- ✅ `accounts_user` - Utilisateurs avec email-based auth
- ✅ `accounts_profile` - Profils avec points et niveau
- ✅ `courses_chapter` - Chapitres
- ✅ `courses_lesson` - Leçons (THEORY/EXERCISE/QUIZ)
- ✅ `courses_exercise` - Exercices de code
- ✅ `courses_quiz` - Quiz
- ✅ `courses_project` - Projets finaux
- ✅ `token_blacklist_*` - Gestion tokens JWT

**Migrations appliquées:**
- ✅ accounts: 0001_initial
- ✅ courses: 0001_initial

### 🐛 Bugs Connus

Aucun bug connu actuellement. Toutes les fonctionnalités implémentées sont testées et fonctionnelles.

### 💡 Notes Importantes pour Reprise

1. **Environnement Docker**: Tout passe par Docker, ne pas installer Python/Node localement
2. **Admin Django**: Créer du contenu via http://localhost:8000/admin/ avant de tester le frontend
3. **Rate Limiting**: Désactivé en dev, à réactiver en production
4. **Tokens JWT**: Access token 1h, refresh 7j, rotation activée
5. **State Management**: Redux pour auth et chapters, expandable pour autres features
6. **JSONB Fields**: Utilisés pour tests (Exercise) et questions (Quiz), flexible pour évolution
7. **UUID everywhere**: Tous les IDs sont des UUID, pas d'entiers séquentiels
8. **Slugs**: Chapitres, leçons, projets utilisent des slugs pour URLs lisibles

## Système de Gamification

App `apps/gamification`. Objectif : encourager sans jamais récompenser deux fois.

### L'invariant central

**Aucun achievement ni crédit de points ne peut être validé deux fois.** Cette
garantie ne repose pas sur du code prudent mais sur trois mécanismes cumulés :

1. **Contraintes d'unicité en base** (la seule défense fiable en concurrence) :
   - `UserBadge (user, badge)` → un badge est gagné au plus une fois
   - `PointTransaction (user, source_key)` → une source ne crédite qu'une fois
2. **Règles monotones** : chaque règle compare un *compteur cumulatif* à un
   seuil. Réévaluer tous les badges est donc idempotent et ne peut jamais faire
   régresser un apprenant, même si sa progression est modifiée ou supprimée.
3. **Grand livre de points** : `Profile.total_points` est toujours égal à la
   somme de `PointTransaction`. Le solde est vérifiable et reconstructible
   (`services.recompute_profile_points`).

Conséquence pratique : `sync_user_gamification(user)` peut être appelé
n'importe quand, autant de fois qu'on veut, depuis n'importe quelle route.
C'est ce qui permet l'endpoint d'auto-réparation `POST /summary/sync/`.

**Toute nouvelle attribution de points doit passer par
`services.award_points(user, amount, reason, source_key)`** — jamais par
`Profile.add_points()` directement, sinon le grand livre décroche.

### Modèles

| Modèle | Rôle |
|---|---|
| `Badge` | Définition : règle, critère JSONB, palier, récompense, `is_secret`, `hint` |
| `UserBadge` | Badge obtenu (unique par user+badge), `is_seen` pour la révélation |
| `PointTransaction` | Grand livre idempotent, clé `source_key` (`lesson:<uuid>`, `badge:<code>`) |
| `UserStreak` | Série de jours consécutifs, idempotente à la journée |

### Objectifs cachés

Le catalogue mêle **objectifs visibles** (avec barre de progression, pour
baliser le parcours) et **objectifs secrets** (révélés à l'obtention).

Le masquage se fait **côté serveur**, dans `serializers.BadgeSerializer` : un
badge secret non obtenu sort de l'API sans son `code`, son nom, sa description,
sa récompense ni ses critères — seule l'énigme `hint` est exposée. Impossible
de les découvrir en inspectant les requêtes réseau. Un test verrouille ça
(`test_api_masque_les_badges_secrets_non_obtenus`).

### Ajouter un badge

1. Ajouter une entrée dans `management/commands/seed_badges.py` (liste
   `VISIBLE` ou `SECRET` — la présence d'un `hint` marque le badge comme secret)
2. Si la règle n'existe pas : ajouter une valeur à `Badge.RuleType`, un
   compteur dans `rules.UserStats` / `build_user_stats`, et une entrée dans le
   registre `rules.RULES` (une lambda `(stats, criteria) -> (courant, cible)`)
3. `python manage.py seed_badges` puis `python manage.py sync_gamification`

### Commandes

```bash
# Crée/met à jour le catalogue de badges (idempotent)
docker-compose exec backend python manage.py seed_badges

# Réconcilie tous les apprenants : report des soldes historiques dans le
# grand livre + réévaluation des badges. Idempotent, relançable à volonté.
docker-compose exec backend python manage.py sync_gamification

# Tests de l'invariant anti-double-validation
docker-compose exec backend pytest apps/gamification/tests/
```

### Endpoints

```
GET  /api/gamification/badges/            Catalogue (secrets masqués)
GET  /api/gamification/badges/mine/       Badges obtenus
POST /api/gamification/badges/mark_seen/  Acquitte une révélation
GET  /api/gamification/summary/           Points, niveau, série, prochains objectifs
POST /api/gamification/summary/sync/      Resynchronise (auto-réparation)
GET  /api/gamification/points/            Grand livre personnel
```

`mark_completed` et `submit_quiz` renvoient désormais aussi `points_earned`,
`total_points` et `new_badges`.

### Temps d'apprentissage

`UserProgress.time_spent` était un champ mort : lu par le dashboard, la page
progression et le dashboard trainer, mais **jamais écrit** — donc toujours à 0.

L'écriture se fait via `POST /api/progression/progress/track_time/`
`{lesson_id, seconds}`, avec trois garde-fous :

- **Incrément, jamais valeur absolue** (`F('time_spent') + n`) : deux onglets
  ouverts sur la même leçon s'additionnent au lieu de s'écraser.
- **Plafond serveur** (`MAX_TIME_INCREMENT_SECONDS = 120`) : le compteur
  alimente les badges `TIME_SPENT` et `FAST_LESSONS`, il doit rester crédible.
  `time_spent` a été retiré de `UserProgressUpdateSerializer` pour la même
  raison — sinon un PATCH permettait de poser un total arbitraire.
- **Temps réellement actif** côté client (`features/progression/useTimeTracker.js`) :
  le compteur n'avance que si l'onglet est visible *et* qu'il y a eu une
  interaction dans les 90 s. L'accumulation se fait par tics d'une seconde,
  pas par différence de timestamps, pour qu'une mise en veille ne crédite rien.

Effet de bord voulu : ouvrir une leçon crée sa progression en `IN_PROGRESS`,
journalise `LESSON_STARTED` et entretient la série de jours — la simple
lecture d'une leçon de théorie compte désormais comme activité.

### Frontend

- `features/gamification/` : slice, `BadgesPage`, `BadgeCard`,
  `BadgeRevealModal`, `NextObjectives`
- La modale de révélation est montée **une seule fois** dans `Layout.jsx` et
  consomme la file `revealQueue` du store. La file est dédupliquée par id et
  chaque fermeture appelle `mark_seen` : une célébration ne rejoue jamais.
- Route `/badges`, lien « Trophées » dans le header.

## Comptes, Rôles et Classes

### Invariants en place

- **Le rôle ne vient jamais du client.** `role` est en `read_only` dans
  `UserSerializer` : pas d'auto-promotion via `PATCH /api/auth/me/`.
  `RegisterSerializer` n'expose pas le champ. Verrouillé par un test.
- **Un email = un compte, quelle que soit la casse.** `User.save()` normalise
  en minuscules, une contrainte `UniqueConstraint(Lower('email'))` tient même
  face à un `update()` qui court-circuite le modèle, et
  `UserManager.get_by_natural_key` fait un `__iexact` pour que la connexion
  reste possible quelle que soit la saisie.
- **Le profil et le User s'écrivent séparément.** Ne jamais rétablir un signal
  qui sauve `instance.profile` depuis `post_save` sur User (cf. le commentaire
  dans `signals.py`) : il écrase les points en mémoire.

## Profil personnalisable — ✅ Fait

Route front `/profil` (`features/profile/ProfilePage.jsx`), accessible depuis le
menu utilisateur de l'en-tête. Avant ce chantier, **aucun écran ne permettait
d'éditer son profil** : `bio`, `timezone` et `github_username` existaient dans
le modèle depuis l'origine mais `UserSerializer` déclarait
`profile = ProfileSerializer(read_only=True)`, donc l'API elle-même les
refusait en écriture.

La page couvre l'identité, l'avatar, le thème, le mot de passe (l'endpoint
`change-password/` existait et n'était appelé nulle part — changer son mot de
passe imposait de passer par « mot de passe oublié ») et un récapitulatif de
progression en lecture seule.

### Avatars : catalogue, pas téléversement

`Profile.avatar` (un `ImageField`) reste dans le modèle mais **n'est pas
alimenté**. Le choix se fait par `Profile.avatar_key`, une clé
`<motif>-<palette>` prise dans une liste close (`apps/accounts/avatars.py`,
6 × 6 = 36 combinaisons), et le rendu se fait en SVG côté client.

Le raisonnement, à ne pas défaire à la légère : sur une plateforme scolaire
sans outil de modération, un téléversement libre signifie que n'importe quelle
image peut apparaître à côté d'un nom dans le tableau de bord du formateur, et
que personne ne dispose du moyen de la retirer. S'y ajoutent la liste blanche
de formats (un SVG téléversé est un vecteur de XSS), les bombes de
décompression et un stockage à sauvegarder. Le catalogue supprime tout cela.

Le repli — initiales sur une couleur **dérivée du nom**, donc stable d'une
session à l'autre — est l'état par défaut de tout compte, pas un pis-aller.

⚠️ Les listes `MOTIFS` / `PALETTES` sont **dupliquées** entre
`backend/apps/accounts/avatars.py` (autorité) et
`frontend/src/features/profile/avatars.js` (rendu). En modifier une seule donne
soit un avatar vide, soit un choix refusé à l'enregistrement. Un test front
vérifie que chaque clé sait se dessiner.

### L'écriture imbriquée du profil et le piège des points

`PATCH /api/auth/me/` accepte désormais un objet `profile`. C'est exactement le
terrain du bug documenté dans `signals.py` — un enregistrement du profil entier
écrase un solde mis à jour entre-temps par `award_points`.

`UserSerializer.update` n'écrit donc **que les champs effectivement reçus**,
via `update_fields`, et uniquement ceux de `EDITABLE_PROFILE_FIELDS` :
`bio`, `avatar_key`, `theme`, `timezone`, `github_username`. `total_points`,
`level`, `cohort` et `anonymized_at` restent hors d'atteinte d'un formulaire de
profil. Un test reproduit le scénario concurrent.

### Thème rattaché au compte

`Profile.theme` vaut `AUTO`, `LIGHT` ou `DARK`. `AUTO` n'est pas un troisième
thème : c'est l'absence de choix, qui suit le système **et continue de le
suivre** s'il change en cours de session. L'ancien `ThemeContext` confondait
les deux et ne permettait plus d'y revenir une fois un choix fait.

⚠️ `ThemeProvider` est monté **au-dessus du store Redux** (`main.jsx`) : il ne
peut pas lire le profil. La synchronisation passe par
`features/profile/useThemePreferenceSync.js`, monté dans `App`. Les deux flux
sont asymétriques (le compte gagne à la connexion, l'utilisateur gagne quand il
bascule) et `appliedRef` empêche la boucle serveur → contexte → serveur. Ne pas
« simplifier » en un effet bidirectionnel.

```
GET  /api/auth/avatars/   catalogue (motifs, palettes, clés)
PATCH /api/auth/me/       { first_name, last_name, profile: { … } }
```

## Classes (cohortes) — ✅ Fait

App `apps/cohorts`. Modèles : `Cohort`, `CohortInvite`, plus `Profile.cohort`
(clé étrangère : **une seule classe active par apprenant**).

### Le verrou de chapitre existe désormais vraiment

⚠️ Avant ce chantier, `ChapterAccess` n'était consulté par **aucune vue
apprenant** : l'API cours ne filtrait rien, le front ne l'affichait pas. La
« progression contrôlée par le formateur » était décorative.

Désormais :

- `LessonViewSet.retrieve` renvoie **403** si le chapitre n'est pas débloqué.
  C'est le verrou réel.
- Les chapitres verrouillés restent **listés** avec `is_accessible: false` —
  masquer la suite du parcours priverait l'apprenant de la vue d'ensemble qui
  lui donne envie d'avancer. C'est l'ouverture qui est bloquée, pas le sommaire.
- `apps/progression/services.py` centralise la décision
  (`accessible_chapter_ids`, `can_access_lesson`).

**Après toute mise en service du verrou sur une base existante, lancer
`python manage.py backfill_chapter_access`** (option `--dry-run` disponible) :
sans ce rattrapage, les apprenants se retrouvent enfermés hors des chapitres
qu'ils suivaient déjà.

### Deux régimes de progression

| Situation | Qui ouvre les chapitres |
|---|---|
| Apprenant **en classe** | Le formateur, explicitement |
| Apprenant **autonome** (sans classe) | Rythme libre : le chapitre 1 est ouvert, le N+1 s'ouvre quand le N est entièrement terminé |

**On ne reverrouille jamais.** Un accès obtenu le reste, qu'on rejoigne une
classe ensuite ou qu'on la quitte. Même logique de monotonie que les badges :
elle rend les recalculs sûrs et évite de punir celui qui avait avancé seul.

### Cloisonnement formateur

Un formateur ne voit et ne pilote que **ses** classes. `visible_learners()`
dans `apps/progression/views.py` est le point unique : il borne
`learners_summary`, `learner_detail`, `recent_activity`, `unlock_chapter`,
`lock_chapter`, ainsi que les querysets de progression et d'activité. Avant,
n'importe quel formateur voyait tous les apprenants de la plateforme et
pouvait débloquer pour n'importe qui.

Les apprenants autonomes ne sont visibles que d'un admin : ils n'ont, par
définition, pas de formateur référent.

### Invitations

```
GET  /api/cohorts/join/<token>/           résolution publique
POST /api/cohorts/join/<token>/register/  crée le compte et rattache
POST /api/cohorts/join/<token>/attach/    rattache une session existante
```
Front : `/rejoindre/:token`, avec les trois cas (visiteur inconnu, déjà
connecté, compte existant → `?next=` sur la connexion).

Règles non négociables, chacune couverte par un test :

- **Ni `role` ni `cohort` ne viennent du formulaire** : le rôle est forcé à
  `LEARNER`, la classe est déduite du jeton côté serveur.
- **Seul un admin peut émettre une invitation `TRAINER`** — sinon le rôle
  formateur s'auto-réplique.
- **Révoqué, expiré, épuisé et inexistant sont indistinguables** côté public
  (`{valid: false}`), pour ne pas confirmer qu'un jeton a existé. Le détail
  (`invalid_reason`) n'est visible que du formateur.
- **Jeton stocké en clair**, à l'inverse de celui du mot de passe oublié : le
  formateur doit pouvoir réafficher son lien pour le recopier. Acceptable car
  le pouvoir du jeton est minuscule, et expiration + révocation sont
  obligatoires. Ne pas « uniformiser » avec le hachage sans retirer
  l'affichage du lien.
- Throttle `invite` (30/h) sur les routes publiques (énumération).

Supprimer une invitation la **révoque** sans l'effacer : on garde trace de ce
qui a été diffusé.

## SECRET_KEY — garde-fou de production

`base.py` définit une valeur de repli publique (`INSECURE_DEV_SECRET_KEY`) pour
ne pas imposer de configuration en développement. Cette clé signe **les JWT,
les sessions, les jetons CSRF et les liens de réinitialisation de mot de
passe** : la connaître permet de forger un jeton pour n'importe quel compte,
administrateur compris.

`production.py` **refuse donc de démarrer** si `SECRET_KEY` est absente, égale
à la valeur de développement, ou plus courte que 50 caractères. Échouer au
démarrage vaut mieux qu'une compromission silencieuse — sans ce garde-fou,
l'application tournerait normalement tout en étant ouverte à quiconque lit le
dépôt.

⚠️ **Piège associé.** `SIMPLE_JWT` est un dictionnaire construit dans `base.py`
qui **copie** la valeur de `SECRET_KEY` au moment de l'import. Redéfinir
`SECRET_KEY` dans `production.py` ne le met pas à jour : sans la ligne
`SIMPLE_JWT['SIGNING_KEY'] = SECRET_KEY`, les jetons resteraient signés avec la
clé de développement, alors même que `settings.SECRET_KEY` affiche la bonne
valeur. Le test `test_les_jwt_sont_signes_avec_la_cle_courante`
(`apps/accounts/tests/test_settings_security.py`) verrouille cette égalité.

La même précaution vaut pour tout réglage dérivé de `SECRET_KEY` ajouté plus
tard : le redéfinir dans un settings d'environnement ne suffit jamais.

Générer une clé :
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Administration — ✅ Fait

App `apps/administration` (**vues seulement, aucun modèle**), route front
`/administration`, réservée au rôle `ADMIN`.

### Parti pris : hybride, pas de remplacement de l'admin Django

Le CRUD de contenu (chapitres, leçons, exercices, quiz, badges) reste dans
`/admin/`, qui le fait mieux et gratuitement — recherche, filtres, inlines,
historique. L'espace React ne couvre que ce que l'admin Django ne sait pas
faire, et un lien y renvoie explicitement depuis l'en-tête de la page.

**Ne pas reconstruire de CRUD de contenu en React.** Ce serait des semaines de
travail pour une capacité inférieure.

### L'admin Django a été bridé — et pourquoi ce n'était pas cosmétique

Tant que les deux espaces pouvaient écrire les mêmes tables, l'admin Django
était une **porte dérobée à côté de la porte blindée** : changer un rôle depuis
`/admin/` n'écrivait aucune entrée d'`AuditLog`, échappait à la règle du
« dernier administrateur actif » et ne révoquait aucune session. Supprimer un
compte y détruisait la progression en cascade au lieu de l'anonymiser. Et
`Profile.total_points` y était éditable, alors que le solde doit toujours
égaler la somme des `PointTransaction`.

Le mixin `apps/administration/admin_readonly.ReadOnlyAdmin` applique la règle.
Son `get_readonly_fields` énumère les champs **du modèle**, pas une liste
figée : un champ ajouté plus tard ne redevient pas éditable en silence.

| Modèle | Régime | Raison |
|---|---|---|
| Chapter, Lesson, Exercise, Quiz, Project, Badge | **CRUD complet** | C'est du contenu — la raison d'être de cet espace |
| User | Création + mot de passe uniquement | `role`, `is_active`, `is_staff`, `is_superuser` en lecture seule ; suppression interdite |
| Cohort | Nom, description, archivage | `trainer` en lecture seule (voie auditée : `set_trainer`) ; suppression interdite |
| Profile, CohortInvite | Lecture seule | Pilotés par React / l'espace formateur |
| UserProgress, ChapterAccess, ActivityLog | Lecture seule | Données dérivées du parcours |
| PointTransaction, UserBadge, UserStreak | Lecture seule | Le grand livre se lit, il ne se corrige pas |
| AuditLog | **Non enregistré** | Rien ne doit pouvoir le réécrire |

On a préféré la **lecture seule au retrait** : répondre à « pourquoi cet
apprenant a-t-il 340 points ? » demande de pouvoir fouiller la table. C'est le
pouvoir d'écrire qu'on retire, pas celui d'inspecter.

Ce qui reste sur `User` est exactement ce que React ne sait pas faire : créer
un compte à la main et définir un mot de passe. `role` reste saisissable **à la
création** (il faut bien amorcer un compte ; aucun état antérieur n'est écrasé).

Neuf tests verrouillent ce partage dans `apps/administration/tests/test_audit.py`.
⚠️ Ils interrogent `django.contrib.admin.site._registry` : **enregistrer un
nouveau modèle sensible sans le brider les fera passer quand même**. Ajouter
une entrée au tableau ci-dessus et un cas au test paramétré.

### Bug corrigé au passage : `Exercise.total_points`

La propriété itérait `self.tests` directement. Or le champ JSONB est stocké
sous la forme `{'tests': [...]}` — celle que produit l'admin et que documente
ce fichier — donc elle parcourait les **clés** du dictionnaire et levait
`AttributeError`. La liste des exercices de l'admin Django était inaccessible.

La normalisation des deux formes vit désormais sur le modèle
(`Exercise.test_cases`) ; `apps/validation/services.py` la réutilise au lieu de
refaire le test dans son coin. **Tout nouveau lecteur du champ doit passer par
`test_cases`.**

### `role` et `is_staff` sont désormais synchronisés

⚠️ L'application avait **deux notions d'administrateur** que rien ne reliait :
`role == ADMIN` (privilèges API) et `is_staff` (accès à `/admin/`). Promouvoir
quelqu'un en ADMIN produisait un administrateur incapable d'ouvrir l'admin
Django ; rétrograder un admin lui laissait cet accès.

`User.save()` impose maintenant `is_staff = is_superuser or role == ADMIN`.
Conséquences à connaître :

- Cocher `is_staff` à la main sur un non-ADMIN **ne tient pas** — changer le rôle.
- Les superutilisateurs gardent l'accès quoi qu'il arrive (filet anti-enfermement).
- `apps/progression/services.py` : `is_staff_user` a été renommée
  `has_staff_role` — elle teste le **rôle**, pas le champ Django, et son
  ancien nom induisait en erreur.

### Cycle de vie des comptes

```
POST /api/administration/users/<id>/set_role/
POST /api/administration/users/<id>/set_active/
POST /api/administration/users/<id>/anonymize/
POST /api/administration/users/<id>/assign_cohort/
```

Garde-fous dans `services.py`, chacun couvert par un test :

- **Impossible de supprimer le dernier administrateur actif** (rétrogradation,
  désactivation, anonymisation) — sinon la plateforme devient impilotable.
- **Impossible d'agir sur son propre compte** (rôle, désactivation,
  anonymisation).
- Désactiver **révoque les refresh tokens** : l'effet doit être immédiat.

Les quatre actions passent par `services.py` — `assign_cohort` y a été remontée
depuis la vue pour que **toutes** les actions de compte soient auditées au même
endroit.

### Journal d'audit — ce qui rend le pouvoir redevable

`AuditLog` (`apps/administration/models.py`), consultable sur
`GET /api/administration/audit/` et sous l'onglet « Journal ».

Avant ce chantier, `set_role`, `set_active`, `anonymize` et `assign_cohort` — dont
une strictement irréversible — ne laissaient **aucune trace**. L'admin Django
tient bien un `LogEntry`, mais tout ce qui passe par `/api/administration/` le
court-circuitait. Impossible de répondre à « qui a anonymisé ce compte ? », ni
de prouver qu'une demande d'effacement RGPD avait été honorée.

Trois propriétés à ne pas casser, chacune couverte par un test
(`apps/administration/tests/test_audit.py`) :

- **Les libellés sont dénormalisés** (`actor_label`, `target_label`) en plus des
  clés étrangères. Ce n'est pas une redondance : la cible d'une anonymisation
  perd son email par définition, et sans identité figée *au moment de l'acte* le
  journal dirait « un compte anonyme a été anonymisé ». Pour la même raison
  `actor` est en `SET_NULL` — un journal qui s'efface avec son auteur ne prouve
  rien.
- **Lecture seule, sans exception.** `AuditLogViewSet` est un
  `ReadOnlyModelViewSet` et le modèle n'est **pas** enregistré dans l'admin
  Django. Un journal réécrivable par ceux qu'il surveille n'est pas un journal.
- **Seul ce qui a eu lieu est consigné.** L'écriture est dans la transaction de
  l'action ; un refus métier (dernier admin, auto-action) ne laisse rien.

Pour auditer une nouvelle action : `from apps.administration.audit import record`.
Ce module est volontairement séparé de `services.py` pour que `progression` et
`cohorts` puissent journaliser sans importer le cycle de vie des comptes.

⚠️ Dans `anonymize()`, l'identité est capturée **avant** l'écrasement de
l'email (`identity_before`). Journalisée après coup, elle enregistrerait
l'adresse anonymisée.

### Affectation des formateurs

`CohortViewSet.perform_create` forçait `trainer=request.user`. Correct pour un
formateur — il ne doit pas créer de classe au nom d'un collègue — mais faux
pour un admin : il devenait formateur de chaque classe qu'il créait, sans aucun
moyen d'en désigner un autre. Le compteur « classes orphelines » du pilotage
signalait donc un problème sans offrir de moyen de le corriger.

- Un **admin** peut passer `trainer_id` à la création, et réaffecter ensuite via
  `POST /api/cohorts/cohorts/<id>/set_trainer/` (**`IsAdmin`**, pas
  `IsTrainerOrAdmin` : laisser un formateur se réaffecter une classe casserait
  le cloisonnement de `get_queryset`).
- Un **formateur** voit son `trainer_id` ignoré, pas honoré.
- On ne peut confier une classe qu'à un compte de rôle `TRAINER` — sinon un
  apprenant hériterait, via `visible_learners`, de la vue sur ses camarades.

### Le pilotage voit désormais le temps et les personnes

`AdminOverviewViewSet` expose en plus :

- `activity.trend` — 30 jours d'activité quotidienne. Les jours creux sont
  réintroduits côté Python : la base ne renvoie que les jours présents, et une
  courbe à trous se lit comme une courbe qui remonte.
- `activity.stalled_learners` / `never_started_learners` — les deux seuls
  chiffres qui désignent des **personnes** plutôt que des volumes. Un total
  d'activités en hausse peut parfaitement masquer une moitié de promo à l'arrêt.

### N+1 corrigés — ils frappaient l'admin en premier

Trois boucles faisaient des requêtes par élément. Ce n'était pas un détail de
style : ce sont les vues de l'administrateur, donc les seules qui portent sur
*toutes* les classes ou *tous* les apprenants à la fois.

| Emplacement | Avant | Après |
|---|---|---|
| `AdminOverviewViewSet` (par classe) | 2 requêtes | 2 agrégations globales (`_per_cohort`) |
| `TrainerSerializer` via `Cohort.member_count` | 1 requête | `annotate(members_total=…)`, `_member_count()` en repli |
| `TrainerDashboardViewSet.learners_summary` | **4 par apprenant** | 4 agrégations groupées par `user_id` |

Les tests comparent le **nombre de requêtes à deux volumes différents** et
exigent l'égalité, plutôt que de fixer un plafond chiffré : un plafond se
contente d'être « assez grand » et laisserait repasser un N+1 modéré.

⚠️ `Cohort.member_count` reste une propriété qui interroge la base à chaque
appel. Ne pas l'utiliser dans une boucle sans annoter le queryset en amont.

### RGPD : anonymisation, pas suppression en cascade

Le droit à l'effacement porte sur les données personnelles, pas sur les
agrégats. `anonymize()` vide l'identité (email remplacé par
`anonyme-xxx@anonymized.invalid`, nom, mot de passe, bio, avatar, classe) et
**conserve la progression, les points et les badges**, désormais rattachés à un
compte qui ne désigne plus personne.

Effacer en cascade fausserait rétroactivement les statistiques des classes : un
formateur verrait le taux de complétion de sa promo changer sans explication.

L'opération est **irréversible** et marquée par `Profile.anonymized_at` — sans
ce marqueur, impossible de distinguer un compte anonymisé d'un compte étrange.
La désactivation, elle, reste réversible.

### Décisions d'architecture actées

Prises en session du 2026-07-21 :

1. **Classes explicites** (`Cohort`) plutôt que rattachement plat ou
   mono-formateur. Les requêtes formateur doivent se filtrer dessus —
   aujourd'hui `learners_summary` renvoie *tous* les apprenants de la
   plateforme et n'importe quel formateur peut débloquer pour n'importe qui.
2. **Une seule classe active par apprenant** (clé étrangère, pas de table de
   liaison) : garde le déblocage de chapitre non ambigu.
3. **Inscription par lien d'invitation généré**, pas par email envoyé par
   l'app. Le formateur produit une URL et la diffuse par le canal qu'il veut
   (Teams, Discord…). Aucune dépendance SMTP en production.
   - Jeton stocké **en clair** (le formateur doit pouvoir réafficher son lien),
     avec expiration et révocation obligatoires.
   - L'endpoint public de résolution du jeton ne renvoie que le nom de la
     classe et du formateur — jamais la liste des élèves — et doit être limité
     en débit (énumération).
   - Ni `role` ni `cohort` ne viennent du formulaire : rôle forcé à `LEARNER`,
     classe déduite du jeton côté serveur.
   - Le même mécanisme sert à créer des formateurs, avec une règle stricte :
     seul un admin peut émettre une invitation `TRAINER`.
4. **L'inscription autonome reste possible.** Un apprenant sans classe
   progresse en **rythme libre auto-débloqué** : terminer le chapitre N ouvre
   le N+1. En classe, c'est le formateur qui donne le tempo. Rejoindre une
   classe plus tard ne retire jamais un accès déjà obtenu.

### Connexion : limitation des échecs — ✅ Fait

`apps/accounts/throttling.FailedLoginThrottle`, appliqué par
`views.LoginView` (qui remplace `TokenObtainPairView` dans `urls.py`).
Débit : **`login: 10/hour`**. Avant cela, seul le plafond anonyme global de
100 requêtes/heure s'appliquait — de quoi essayer cent mots de passe par heure
sur un compte.

Trois décisions, chacune couverte par un test :

- **On compte par compte visé, pas par adresse IP.** C'est le piège propre à
  cette application : une classe entière se connecte depuis le NAT de son
  établissement, donc depuis **une seule IP**. Un plafond par IP mettrait la
  promo dehors chaque matin. Compter par compte arrête en prime une attaque
  répartie sur plusieurs machines, qu'un compteur par IP ne voit pas.
- **Seuls les échecs consomment le quota**, et une réussite l'efface. Compter
  toutes les tentatives ouvrirait un déni de service trivial : brûler le quota
  d'un camarade suffirait à l'empêcher d'entrer. Là, quiconque connaît son mot
  de passe passe toujours.
- **La clé est normalisée en minuscules**, comme les emails le sont par
  `User.save()` : sinon varier la casse offrirait un compteur neuf.

L'implémentation sépare la vérification de la consommation :
`allow_request` regarde sans décompter, et `LoginView.post` appelle
`record_failure()` ou `reset()` selon l'issue. `LoginView` conserve pour cela
les instances de throttle dans `check_throttles` — `APIView` les jette
autrement.

⚠️ **Deux pièges rencontrés, tous deux verrouillés par un test :**

1. `development.py` vide `DEFAULT_THROTTLE_RATES`. Le throttle étant déclaré
   sur la vue, il est instancié quand même ; `SimpleRateThrottle.get_rate`
   aurait levé `ImproperlyConfigured` et **cassé la connexion en
   développement**. D'où la tolérance à un débit absent.
2. `SimpleRateThrottle.THROTTLE_RATES` est un instantané pris à l'import de
   DRF, qu'`override_settings` **ne restaure pas** : un débit posé par un test
   fuyait sur les suivants. `get_rate` relit donc `api_settings` à chaque
   appel. Toute nouvelle classe de throttle devrait faire de même.

### Mot de passe oublié — ✅ Fait

```
POST /api/auth/password-reset/          demande un lien  (public)
GET  /api/auth/password-reset/validate/ vérifie un lien  (public)
POST /api/auth/password-reset/confirm/  définit le mdp   (public)
```
Front : `/forgot-password` et `/reset-password/:uid/:token`.

**Jeton sans état** : on utilise `default_token_generator` de Django, signé
sur le hash du mot de passe et `last_login`. Rien n'est stocké en base, et on
obtient gratuitement l'usage unique (le hash change) et l'invalidation si
l'utilisateur se reconnecte entre-temps. C'est le choix inverse de celui prévu
pour les invitations de classe (stockées en clair, car le formateur doit
pouvoir réafficher son lien) : ici le lien part une fois par email et n'est
jamais réaffiché, donc il n'y a rien à voler dans la base.

Trois propriétés à ne pas casser, chacune couverte par un test :

- **Aucun oracle d'énumération** : `POST /password-reset/` répond exactement la
  même chose que le compte existe, soit inexistant, soit désactivé. Ne jamais
  « améliorer » l'UX en signalant qu'un email est inconnu.
- **Révocation des sessions** : `revoke_refresh_tokens` blackliste les refresh
  tokens après réinitialisation. Sans ça, un compte compromis reste accessible
  7 jours malgré le changement de mot de passe.
- **Throttle `password_reset`** (5/h) sur les trois vues publiques : elles sont
  anonymes et déclenchent des envois de mail. Note : `development.py` désactive
  tout throttling, la limite ne s'applique donc qu'en production.

Configuration : `PASSWORD_RESET_TIMEOUT` (défaut 3600 s), `FRONTEND_URL`,
`DEFAULT_FROM_EMAIL`. En dev, l'email s'affiche dans `docker-compose logs
backend` ; le SMTP de production était déjà câblé dans `production.py`.

L'envoi est **synchrone** : une réinitialisation est rare, et passer par Celery
rendrait un échec d'envoi invisible. Le throttle borne le risque de blocage
worker. À revoir si le volume augmente.

### Gardes de rôle côté front — ✅ Fait

`PrivateRoute` accepte une prop `roles` :

```jsx
<PrivateRoute roles={STAFF_ROLES}>   // TRAINER + ADMIN
```

Rôles centralisés dans `src/constants/roles.js` (`ROLES`, `STAFF_ROLES`,
`ROLE_LABELS`) — miroir de `User.Role` côté Django. Le header filtre ses liens
sur la même liste : un lien vers une page interdite n'est jamais affiché.

**Ces gardes sont un confort d'affichage, pas une sécurité.** Elles évitent
qu'un apprenant tombe sur une page vide criblée de 403. L'autorité reste
`IsTrainerOrAdmin` côté API. Ne jamais déplacer une décision d'autorisation
ici.

`authSlice` expose un drapeau **`initialized`**, passé à `true` dès que la
question « qui est connecté ? » a reçu une réponse, succès *ou* échec. Sans
lui, deux bugs : trancher sur le rôle avant chargement du profil renverrait un
formateur vers `/dashboard` à chaque rafraîchissement, et une panne réseau
laisserait un écran de chargement infini. Toute nouvelle garde doit attendre
`initialized` avant de décider.

### Décision actée : stockage des jetons

Rester en `localStorage`. Migrer vers des cookies `httpOnly` impliquerait de
refaire l'intercepteur axios, CORS et la protection CSRF pour un gain réel
seulement en cas de XSS par ailleurs. Réduire `ACCESS_TOKEN_LIFETIME` couvre
l'essentiel du risque pour une ligne.

## Conformité RGPD côté apprenant — ✅ Fait

Avant ce chantier, le RGPD n'existait que **côté administrateur**
(anonymisation par un admin, journal d'audit). L'apprenant lui-même ne pouvait
ni consentir explicitement, ni emporter ses données, ni supprimer son compte.
Trois briques ajoutées, chacune couverte par un test
(`apps/accounts/tests/test_rgpd.py`) :

### Consentement à l'inscription

`RegisterSerializer` **et** `InviteAcceptSerializer` (inscription par
invitation) exigent désormais `accept_terms=True`. La case n'est pas
cosmétique : elle est validée côté serveur (refus sinon), et
`Profile.terms_accepted_at` fige la date d'acceptation comme preuve. Les deux
chemins de création de compte le font — **toute nouvelle voie d'inscription
doit horodater le consentement de la même façon** (via le profil créé par
signal, jamais en réenregistrant le User, cf. `signals.py`).

Front : case obligatoire dans `Register.jsx` et `JoinCohort.jsx`, avec liens
vers les pages légales ; le bouton reste désactivé tant qu'elle n'est pas
cochée.

### Portabilité — export des données

`GET /api/auth/export/` (authentifié) renvoie un JSON de **toutes** les données
personnelles : compte, profil, progression, grand livre de points, badges,
série de jours, activité. Réservé au compte courant — aucun paramètre ne
permet de viser un tiers (un test le vérifie). Construit par
`accounts.services.build_user_export`, qui importe les modèles de
`progression`/`gamification` **localement** (pas de dépendance au niveau
module, chemin froid). Front : bouton dans `/profil` → « Mes données », qui
télécharge le fichier via un `Blob` côté client.

### Effacement en self-service

`POST /api/auth/delete-account/` (authentifié, exige le mot de passe courant)
déclenche l'anonymisation du compte **par l'apprenant lui-même**. Point clé :
la logique d'effacement **n'a pas été dupliquée**. `administration/services.py`
a été refactoré — le cœur `_erase_identity(user)` est partagé entre
`anonymize(actor, user)` (par un admin) et `self_delete_account(user)`
(self-service). Différences assumées :

- `self_delete_account` **n'a pas** le garde-fou « pas sur soi-même » (il
  n'aurait aucun sens), mais **garde** celui du dernier administrateur actif :
  un admin isolé doit d'abord promouvoir un remplaçant.
- La trace d'audit utilise une action distincte
  (`AuditLog.Action.ACCOUNT_DELETED`) et nomme l'utilisateur comme acteur *et*
  cible — c'est bien lui qui a demandé son effacement. Le libellé fige
  l'identité **avant** écrasement (même piège que `anonymize`).

Même parti que côté admin : **anonymisation, pas suppression en cascade** — la
progression est conservée sous une forme non ré-identifiante pour ne pas
fausser les statistiques des classes.

Front : section « zone dangereuse » dans `/profil`, confirmation par mot de
passe, puis `window.location.href = '/login'` (rechargement complet, comme
l'intercepteur axios) pour ne laisser aucun état résiduel.

### Pages légales et cookies

Trois pages **publiques** (avant toute session) : `/confidentialite`,
`/mentions-legales`, `/cgu` (`features/legal/`). Elles portent des marqueurs
`[À COMPLÉTER : …]` (composant `Todo`) pour l'identité de l'exploitant,
l'hébergeur et le DPO — informations que seul l'exploitant connaît. Liens en
pied de page (`Footer.jsx`) et dans les formulaires d'inscription.

⚠️ **Pas de bannière de consentement cookies, et c'est délibéré.** L'app ne
pose **aucun traceur** : l'auth passe par `localStorage`, les seuls cookies
(`session`, `csrf`) sont strictement nécessaires — donc dispensés de
consentement au sens CNIL. La politique de confidentialité l'explique dans une
notice. **Le jour où un analytics ou un traceur tiers est introduit, une vraie
bannière (accepter/refuser, blocante) devient obligatoire.**

## Reste à faire — audit du 2026-07-21

Inventaire vérifié dans le code, pas recopié du roadmap. Classé par risque,
pas par visibilité.

### Risque réel

1. **`courses` n'a toujours aucun test propre.** Le verrou de chapitre est
   désormais couvert depuis `apps/progression/tests/`, mais rien ne teste les
   modèles et sérialiseurs de contenu eux-mêmes — c'est là que vivait le bug
   `Exercise.total_points`, invisible depuis l'origine.
*(Le throttle de connexion, longtemps second de cette liste, est fait — voir
« Connexion : limitation des échecs ».)*

### Dette structurelle

4. **Contrat incohérent des services API** — `authApi` et `coursesApi` rendent
   la réponse axios brute, les autres les données déballées (cf. la section
   dédiée). A déjà coûté une page blanche. Uniformiser demande un test de
   contrat par module d'abord, puis un changement d'un seul bloc.
5. **Aucun découpage de bundle** — `App.jsx` importe tout statiquement, ~535 kB
   d'un tenant. `React.lazy` par route est mécanique.
6. **`Profile.avatar` (ImageField) est mort** — conservé pour d'éventuels
   téléversements historiques, jamais alimenté. À supprimer si l'on confirme
   qu'aucune base n'en contient.

### Fonctionnalités jamais commencées

7. **WebSocket / temps réel** — voir la section dédiée : `asgi.py` a un routeur
   vide et `channels/consumers/` est un dossier vide. Rien n'en dépend
   aujourd'hui.
8. **Soumission et correction de projets** (Phase 4) — le modèle `Project`
   existe dans `courses`, mais **aucun modèle de soumission** nulle part, donc
   rien à rendre ni à corriger.
9. **Forum** (Phase 4) — l'app n'existe pas, ni dans `INSTALLED_APPS` ni sur le
   disque.
10. **Leaderboard** — reporté volontairement (choix produit : progression
    personnelle d'abord). Le grand livre de points le rend trivial à ajouter.
11. **Déploiement** (Phase 5) — le garde-fou `SECRET_KEY` de production est en
    place et testé, mais rien n'est déployé et la CI ne construit aucune image.

### Ce qui vient d'être fait

- [x] Infrastructure de test frontend (Vitest) — 37 tests
- [x] Intégration continue (`.github/workflows/ci.yml`)
- [x] `npm run lint` ramené à zéro erreur **et zéro avertissement**
- [x] Couverture du bac à sable — 20 tests simulés (en CI) + 7 tests réels
- [x] Retrait de la liste noire de motifs (voir « Security Considerations »)
- [x] Limitation des échecs de connexion
- [x] Couverture de `progression` — 33 tests : verrou de chapitre, deux
      régimes de progression, notation des quiz, suivi du temps

## Intégration continue

`.github/workflows/ci.yml`, sur `push` vers `main` et sur chaque *pull
request*. Deux jobs indépendants qui échouent séparément.

**Backend** — PostgreSQL 15 et Redis 7 en services, puis :

| Étape | Ce qu'elle attrape |
|---|---|
| `makemigrations --check --dry-run` | Un modèle modifié sans migration |
| `migrate` sur base vierge | Une migration qui ne s'applique pas dans l'ordre |
| `manage.py check` | Erreurs de configuration |
| `pytest --create-db` | Les 155 tests |

⚠️ Les deux premières étapes ne sont pas décoratives. `pytest.ini` fixe
**`--nomigrations`** : le schéma de test est bâti directement depuis les
modèles, donc la suite complète peut passer au vert alors qu'il manque une
migration — et casser au déploiement. La CI est le seul endroit où ce décalage
est visible.

`ENVIRONMENT: development` est explicite dans le workflow :
`config/settings/__init__.py` bascule sur `production.py` dès que la variable
vaut `production`, et ce module **refuse de démarrer** sans vraie `SECRET_KEY`.

**Frontend** — Node 22, `npm ci`, puis `lint`, `test`, `build`.

Le `build` n'est pas redondant avec les tests : il attrape les imports cassés
et surtout les **chemins dont la casse ne correspond pas**. Le runner Linux est
sensible à la casse, contrairement au poste Windows de développement — c'est
exactement le piège qui a fait renommer `ThemeContext.jsx` en
`ThemeProvider.jsx`, pour ne pas cohabiter avec `themeContext.js`.

⚠️ `npm run lint` tourne avec `--max-warnings 0` et le dépôt est à zéro.
**Un simple avertissement casse la CI** — c'est voulu : c'est ce qui empêche de
revenir aux 15 erreurs tolérées pendant des mois. Si une règle gêne
légitimement, la désactiver avec un commentaire qui explique pourquoi (voir
`ExerciseInterface.jsx`, où inclure la dépendance suggérée effacerait le
travail de l'apprenant), jamais relever le seuil.

## Development Commands

### Backend (Django)

```bash
cd backend

# Environment setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements/development.txt

# Database operations
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver  # http://localhost:8000

# Run tests
pytest                              # All tests
pytest --cov=apps                   # With coverage
pytest apps/accounts/tests/         # Specific app tests
pytest -k test_user_registration    # Single test

# Code quality
black .                             # Format code
flake8 .                            # Lint
isort .                             # Sort imports

# Celery workers (for async tasks)
celery -A config worker -l info
celery -A config beat -l info       # Scheduler
```

### Frontend (React + Vite)

```bash
cd frontend

# Setup
npm install

# Development
npm run dev                         # http://localhost:5173

# Build
npm run build
npm run preview                     # Preview production build

# Linting — zéro erreur ET zéro avertissement (porte de CI)
npm run lint        # ⚠️ `--max-warnings 0` : un avertissement casse la CI.
                    # Ne jamais relever le seuil ; désactiver la règle au cas
                    # par cas, avec un commentaire qui justifie.

# Tests (Vitest + Testing Library, environnement jsdom)
npm test            # une passe
npm run test:watch  # mode veille
npx vitest run src/features/auth   # un dossier
npx vitest run -t "file de révélation"  # un test par son nom

# ⚠️ Toujours pas de tests bout-en-bout (Playwright) : les parcours complets
# se vérifient encore à la main dans le navigateur.
```

### Infrastructure (Docker)

```bash
# Start PostgreSQL + Redis
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Reset everything
docker-compose down -v
```

## Architecture Overview

### Backend Structure

Django project organized by feature modules in `backend/apps/`:

- **accounts/** - User authentication (custom User model), JWT tokens, profiles
- **courses/** - Content management (Chapter, Lesson, Exercise, Quiz, Project models)
- **progression/** - User progress tracking (UserProgress, ChapterAccess, ActivityLog)
- **gamification/** - Badges, points, leaderboard system
- **forum/** - Community Q&A forum (posts, replies, votes)
- **validation/** - Code execution sandbox (Docker-based, runs user submissions)

**Key patterns:**
- Custom User model: `accounts.User` with UUID primary keys and role-based access (LEARNER/TRAINER/ADMIN)
- Service layer: Business logic in `services.py` files (e.g., `badge_service.py`, `code_runner.py`)
- Settings split: `config/settings/` has `base.py`, `development.py`, `production.py`
- API: Django REST Framework with JWT authentication
- WebSocket: Django Channels with Redis channel layer for real-time updates
- Async tasks: Celery for code validation, badge awards, batch operations

### Frontend Structure

React app organized by features in `frontend/src/features/`:

- **auth/** - Login, Register, JWT token management
- **chapters/** - Chapter list, cards, progress display
- **lessons/** - Lesson viewer, navigation, Markdown rendering
- **exercises/** - Monaco code editor, test results, hints
- **quizzes/** - Quiz interface, questions, results
- **progression/** - Progress dashboard, charts, activity timeline
- **gamification/** - Badge gallery, leaderboard, points display
- **forum/** - Forum posts, replies, voting
- **trainer/** - Trainer dashboard, student tracking, live activity, project reviews

**Key patterns:**
- Redux Toolkit for state management with slices per feature
- Axios interceptors for JWT token refresh on 401
- Hooks maison : `useTimeTracker` (temps réellement actif),
  `useThemePreferenceSync` (thème rattaché au compte)
- Tailwind CSS **et** SCSS par feature — les deux coexistent

⚠️ Trois éléments listés ici auparavant n'existent pas : `wsService.js`,
`useAutosave` / `useWebSocket`, et le découpage par `React.lazy`. `App.jsx`
importe tout statiquement, d'où un bundle de ~535 kB en un seul morceau.

### Database Schema

PostgreSQL with UUID primary keys throughout:

**Core tables:**
- `accounts_user` - Custom user model with email-based auth, role field
- `accounts_profile` - User profile with points, level, avatar
- `courses_chapter` - Chapters with order_index, estimated_duration
- `courses_lesson` - Lessons (type: THEORY/EXERCISE/QUIZ)
- `courses_exercise` - Exercises with starter_code, tests (JSONB), solution
- `courses_quiz` - Quizzes with questions (JSONB), passing_score
- `progression_userprogress` - Per-user/lesson progress (status, attempts, time_spent, last_code)
- `progression_chapteraccess` - Chapter unlock tracking (is_unlocked, unlocked_by_id)
- `gamification_badge` - Badge definitions with criteria (JSONB)
- `gamification_userbadge` - User-earned badges
- `gamification_pointtransaction` - Points history
- `forum_post` and `forum_reply` - Forum content with votes

**Important indexes:**
- User lookups: `idx_user_email`, `idx_user_role`
- Progress queries: `idx_progress_user_lesson`, `idx_progress_status`
- Activity logs: `idx_activity_created` (DESC for recent activity)

### WebSocket — ⚠️ RIEN N'EXISTE

**Cette section décrivait une architecture temps réel complète qui n'a jamais
été écrite.** Vérifié le 2026-07-21 :

- `config/asgi.py` : l'`URLRouter` est **vide**, avec un commentaire
  « WebSocket URL patterns will be added here ».
- `backend/channels/consumers/` : **dossier vide**, aucun consumer.
- `frontend/src/services/websocket/wsService.js` : **n'existe pas**.
- Le service Docker `daphne` démarre, écoute sur 8001 et ne sert rien.

Aucune fonctionnalité de l'application ne dépend du temps réel : l'auto-save de
code, l'activité formateur et les notifications de badges passent tous par des
appels HTTP classiques. Il n'y a donc rien de cassé — seulement une brique
prévue et jamais posée.

Cible souhaitée, si le chantier est repris un jour :

| Endpoint | Rôle |
|---|---|
| `ws/progress/{exercise_id}/` | Sauvegarde du code en cours |
| `ws/activity/chapter/{chapter_id}/` | Activité des élèves, vue formateur |
| `ws/notifications/` | Badges obtenus, chapitres débloqués |

L'authentification devra passer par le JWT dans la poignée de main
(`scope['user']`), et le *channel layer* Redis est déjà configuré.

⚠️ **Ne pas décrire ici ce qui n'est pas construit.** Cette section a induit en
erreur pendant des mois, comme l'a fait la mention d'une infrastructure de test
frontend inexistante. Documenter une intention est utile ; la documenter au
présent de l'indicatif ne l'est pas.

### Security Considerations

**Bac à sable d'exécution de code** (`apps/validation/services.py`)

La frontière de sécurité, c'est **le conteneur** — et rien d'autre :

- `network_disabled=True` : aucun accès réseau depuis le code d'apprenant
- `mem_limit='128m'`, `cpu_quota=50000` (50 % d'un cœur)
- `container.wait(timeout=5)`, puis `kill()` + `remove()` quoi qu'il arrive
- Conteneur jetable, recréé à chaque soumission

Ces quatre réglages sont verrouillés par des tests
(`apps/validation/tests/test_sandbox.py`) qui vérifient **les arguments passés
à Docker**. C'est délibéré : lancer un vrai conteneur ne dirait pas si
`network_disabled` a disparu d'un appel.

S'y ajoute un garde-fou moins évident, devenu le plus important :

- **Aucun montage** (`volumes` / `mounts`) dans le conteneur d'exécution. Le
  worker Celery, lui, a `/var/run/docker.sock` monté — c'est ainsi qu'il pilote
  le bac à sable. Monter quoi que ce soit de l'hôte donnerait au code
  d'apprenant un chemin vers cette socket, donc le contrôle du démon, donc
  l'hôte entier. Un test vérifie qu'aucun montage n'est passé.

### Il n'y a plus de filtrage du code en amont — c'est délibéré

Une liste noire `DANGEROUS_PATTERNS` (`eval`, `exec`, `open(`, `require(`…) a
existé. **Retirée le 2026-07-21**, après mesure de ses deux effets :

- Elle **rejetait du code d'apprenant légitime** : `exec` déclenchait sur
  `executeTask`, `eval` sur `evaluation` et jusque dans le mot français
  « evaluer » d'un commentaire, `open(` sur `document.open()`. L'élève voyait
  sa soumission refusée par un message l'accusant d'une faute inexistante.
- Elle **n'arrêtait aucun contournement** : `new Function("…")()` et
  `this["ev"+"al"]("…")` passaient sans encombre.

Une recherche de sous-chaîne ne gêne que ceux qui ne cherchent pas à la
contourner. Sur une plateforme d'apprentissage, c'est exactement la population
à ne pas gêner.

Ce que du code arbitraire peut faire aujourd'hui : lire et écrire dans le
système de fichiers **du conteneur** — une image publique, jetée aussitôt — et
consommer ses propres ressources plafonnées. Vérifié en conditions réelles :
une tentative de requête HTTP sortante n'aboutit pas et l'exécution est coupée
au délai, sans laisser de conteneur derrière elle.

⚠️ **Corollaire : toute atténuation de l'isolement du conteneur est désormais
une régression de sécurité directe.** Il n'y a plus de filet en amont pour
rattraper l'erreur. Ne pas ajouter de `volumes=`, ne pas retirer
`network_disabled`, ne pas allonger le délai sans y penser à deux fois.

**Piste de durcissement non faite** : le conteneur s'exécute en `root` (aucun
`user=` n'est passé). Ajouter `user='nobody'` serait peu coûteux, mais c'est un
changement de comportement à valider sur les quatre langages.

**Authentication:**
- JWT tokens: 1-hour access token, 7-day refresh token with rotation
- Token blacklist after refresh (requires `rest_framework_simplejwt.token_blacklist` in INSTALLED_APPS)
- CORS configured for specific origins only
- Rate limiting: 100 req/hour (anon), 1000 req/hour (authenticated), 10/min (submissions)

**Data protection:**
- All user input validated via DRF serializers
- HTML/Markdown sanitized with `bleach` library (whitelist tags)
- Django ORM used exclusively (parameterized queries)
- HTTPS enforced in production
- Passwords hashed with Django's default (PBKDF2)

## Development Workflow

### Creating a New Feature Module

When adding a new Django app (e.g., `notifications`):

```bash
cd backend/apps
mkdir notifications
cd notifications
touch __init__.py models.py views.py serializers.py urls.py admin.py services.py tests.py
```

1. Define models in `models.py` with UUID primary keys
2. Create serializers in `serializers.py` for API validation
3. Implement business logic in `services.py` (not in views)
4. Create API endpoints in `views.py` using DRF ViewSets
5. Register URLs in `urls.py`, then include in `config/urls.py`
6. Register admin interface in `admin.py`
7. Write tests in `tests/` directory
8. Add app to `INSTALLED_APPS` in `config/settings/base.py`
9. Run migrations: `python manage.py makemigrations notifications`

### Adding a React Feature

When adding a new frontend feature (e.g., `notifications`):

1. Create feature directory: `frontend/src/features/notifications/`
2. Create Redux slice: `notificationsSlice.js` with async thunks
3. Add reducer to store: `frontend/src/app/store.js`
4. Create components: `NotificationList.jsx`, `NotificationItem.jsx`
5. Add API service: `frontend/src/services/api/notificationsApi.js`
6. Add routes in `frontend/src/App.jsx`
7. Style with Tailwind utility classes

### Working with WebSocket

Sans objet aujourd'hui : aucun consumer n'existe (cf. « WebSocket — RIEN
N'EXISTE » plus haut). Ce guide décrivait comment brancher un consumer sur un
`wsService.js` qui n'a jamais été écrit. Il sera à rédiger *avec* le chantier,
pas avant.

### Code Validation System

When adding new exercise types:

1. Define test structure in `Exercise.tests` JSONB field:
```json
{
  "tests": [
    {
      "name": "Test 1",
      "code": "assert solution(2, 3) == 5",
      "points": 10
    }
  ]
}
```

2. Validation happens in `apps/validation/services/code_runner.py`
3. Docker sandbox limits are configurable in `sandbox.py`
4. Results sent via WebSocket to user's channel

## Important Patterns and Conventions

### Django Models
- Always use UUID for primary keys: `id = models.UUIDField(primary_key=True, default=uuid.uuid4)`
- Add timestamps: `created_at`, `updated_at` with auto triggers
- Use explicit `db_table` names: `class Meta: db_table = 'app_model'`
- Complex data in JSONB fields (PostgreSQL): `tests = models.JSONField()`

### API Endpoints
- Follow REST conventions: `/api/{resource}/` for list, `/api/{resource}/{id}/` for detail
- Custom actions: `/api/exercises/{id}/submit/`, `/api/chapters/{id}/unlock/`
- Use DRF ViewSets for CRUD, APIView for custom logic
- Permissions: Combine `IsAuthenticated`, `IsOwnerOrTrainer`, `IsTrainerOrReadOnly`
- Pagination: Default 20 items per page
- Query params: `?search=`, `?ordering=`, `?chapter=`, `?status=`

### ⚠️ Contrat des services API — incohérent, à connaître

Les modules de `services/api/` ne renvoient **pas tous la même chose** :

| Module | Renvoie |
|---|---|
| `authApi`, `coursesApi` | la **réponse axios brute** → faire `.data` |
| `progressionApi`, `gamificationApi`, `cohortsApi` | les **données déjà déballées** → ne pas refaire `.data` |

Cette incohérence a déjà coûté une page blanche : `trainerSlice` faisait un
`.data` sur un tableau déjà déballé, obtenait `undefined`, et le rendu plantait
sur `.length`. Le bug est resté invisible des mois faute de lien vers
`/trainer` dans le header.

Vérifier le module avant d'écrire un thunk. Uniformiser serait souhaitable,
mais c'est un changement transverse à faire d'un bloc, pas à moitié.

### Frontend State Management
- Redux slices per feature with createAsyncThunk for API calls
- Loading states: `{ loading: false, error: null, data: null }`
- Optimistic updates for better UX (e.g., auto-save indicator)
- WebSocket updates dispatched as Redux actions

### Performance Optimization
- **Backend:** Use `select_related()` / `prefetch_related()` to avoid N+1 queries
- **Backend:** Cache frequently accessed data in Redis (TTL: 30min-1h)
- **Backend:** Celery for slow operations (code validation, email, badge calculations)
- **Frontend:** React.memo for expensive components
- **Frontend:** Code splitting with lazy() for large features
- **Frontend:** Debounce user input (search, auto-save) with custom hooks

### Testing Strategy

**Backend — en place.** pytest-django, 216 tests. Couverts : `accounts`,
`administration`, `cohorts`, `gamification`, `progression`, `validation`.
**Non couvert : `courses`.**

Les tests de `progression` (`apps/progression/tests/`) ont été validés **par
sabotage** : le verrou de chapitre, l'ouverture au rythme libre, le plafond de
temps et le recalcul du score de quiz ont chacun été cassés volontairement pour
vérifier que la suite passait au rouge. Un test vert sur du code cassé ne
protège rien — le vérifier une fois coûte cinq minutes.

⚠️ **Deux modes d'exécution.** `pytest.ini` exclut par défaut les tests marqués
`docker` (`-m "not docker"`) : ils lancent de vrais conteneurs et exigent
`/var/run/docker.sock`, monté **uniquement sur le service `celery`**.

```bash
docker-compose exec backend pytest              # tout sauf les tests Docker
docker-compose exec celery pytest -m docker     # les tests de bout en bout
```

Ce n'est pas un contournement : lancer le bac à sable depuis `backend` échoue
sur `DockerException`, car ce conteneur n'a pas accès au démon. Les tests
marqués sont *ignorés* ailleurs, jamais en échec — un test rouge faute
d'environnement finit désactivé, et emporte les autres avec lui.

⚠️ `pytest.ini` contient `--reuse-db`. **Après toute migration, lancer au moins
une fois `pytest --create-db`**, sinon les tests tournent contre un schéma
périmé et peuvent passer à tort (c'est arrivé sur la contrainte d'unicité des
emails).

**Frontend — en place depuis le 2026-07-21.** Vitest + Testing Library, en
environnement jsdom. Configuration dans le bloc `test` de `vite.config.js`,
amorce dans `src/test/setup.js` (matchers `jest-dom`, `cleanup` et purge du
`localStorage` après chaque test — sans cette purge, un jeton posé par un test
fait passer le suivant à tort).

Les fichiers de test vivent **à côté du code qu'ils couvrent**
(`PrivateRoute.test.jsx` face à `PrivateRoute.jsx`), pas dans un dossier
`__tests__` séparé : un test qu'on voit en éditant le fichier est un test qu'on
met à jour.

Ce qui est couvert aujourd'hui — délibérément les **invariants déjà décrits
dans ce document**, pas la couverture de ligne :

| Fichier | Invariant verrouillé |
|---|---|
| `features/auth/PrivateRoute.test.jsx` | La garde attend `initialized` avant de trancher sur le rôle (sinon un formateur est éjecté à chaque rafraîchissement) |
| `features/gamification/gamificationSlice.test.js` | Une célébration ne rejoue jamais, même si `unseen_badges` et `newly_earned` mentionnent le même badge |
| `features/progression/useTimeTracker.test.jsx` | Onglet caché ou inactif depuis 90 s ⇒ aucun temps crédité (le compteur alimente des badges) |
| `features/administration/AdminSpace.test.jsx` | L'anonymisation exige une confirmation ; le journal affiche l'identité **figée**, pas l'identité courante |
| `features/profile/avatars.test.js` | Chaque clé du catalogue sait se dessiner ; une clé inconnue retombe sur les initiales |
| `features/profile/ProfilePage.test.jsx` | Le formulaire n'envoie ni `role` ni les points ; les erreurs DRF imbriquées restent lisibles |

Écrire les tests **en français**, comme le reste des commentaires du dépôt.

Conventions utiles :

- Pour un hook à minuterie, utiliser `vi.useFakeTimers()` et avancer par
  `vi.advanceTimersByTime` dans un `act()`. `document.visibilityState` n'est pas
  assignable en jsdom : passer par `Object.defineProperty` (voir le helper
  `setVisibility`).
- Pour une garde de route, monter un store jetable via `configureStore` avec un
  réducteur constant plutôt que le vrai store : le test décrit un état, il n'a
  pas à rejouer les thunks pour y arriver.

**Cible non atteinte :** Playwright pour les parcours critiques (inscription
par invitation, déblocage de chapitre, soumission d'exercice).

⚠️ **Piège Windows/OneDrive.** Juste après un `npm install`, `npm test` peut
échouer sur `Error: UNKNOWN: unknown error, read` (errno -4094) : OneDrive
n'a pas encore hydraté les fichiers fraîchement écrits dans `node_modules`.
Ce n'est pas une erreur de configuration — relancer la commande suffit.

## Project Phases (from Roadmap)

This project follows a 12-week roadmap:

**Phase 1 (Weeks 1-3) - Foundations:** User auth, content models, progression system, Django admin
**Phase 2 (Weeks 4-6) - Real-time:** WebSocket integration, auto-save, trainer dashboard with live activity
**Phase 3 (Weeks 7-8) - Gamification:** Badges, points, leaderboard, code validation
**Phase 4 (Weeks 9-10) - Collaboration:** Final projects, trainer review, forum
**Phase 5 (Weeks 11-12) - Production:** Performance optimization, CI/CD, deployment

Current focus should align with the roadmap phase. Check `01_ROADMAP.md` for sprint breakdown.

## Common Issues and Solutions

**"Module not found: apps.accounts"**
- Ensure `apps/` directory has `__init__.py`
- Check `INSTALLED_APPS` includes `'apps.accounts'` (full path)

**Database migration conflicts:**
```bash
# Reset migrations (development only!)
python manage.py migrate {app} zero
rm apps/{app}/migrations/000*.py
python manage.py makemigrations {app}
python manage.py migrate
```

**CORS errors in development:**
- Verify `corsheaders` in `INSTALLED_APPS` and first in `MIDDLEWARE`
- Check `CORS_ALLOWED_ORIGINS` includes `http://localhost:5173`
- Ensure `CORS_ALLOW_CREDENTIALS = True` for JWT cookies

**WebSocket connection failed:**
- Ensure Redis is running: `docker-compose ps`
- Check Daphne ASGI server is running on port 8001 (separate from Django WSGI)
- Verify JWT token is passed in connection auth headers

**Code validation timeout:**
- Default timeout is 5 seconds (configurable in `sandbox.py`)
- Check Docker daemon is running and accessible
- Review sandbox resource limits if needed

## Reference Documentation

All detailed documentation is in the root directory:

- **01_ROADMAP.md** - 12-week project roadmap with sprints and deliverables
- **02_USER_STORY_MAPPING.md** - User stories for all 3 personas with acceptance criteria
- **03_DIAGRAMMES_UML.md** - UML diagrams (use cases, class, sequence, deployment)
- **04_ARCHITECTURE_TECHNIQUE.md** - Complete technical architecture with code examples
- **05_GUIDE_DEVELOPPEMENT_INITIAL.md** - Step-by-step initial setup guide
- **README.md** - Project overview and quick start

When implementing features, cross-reference these documents for requirements and design decisions.
