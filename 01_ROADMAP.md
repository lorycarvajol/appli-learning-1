# 🚀 ROADMAP - Plateforme d'Apprentissage Web

## Vue d'ensemble
Plateforme interactive d'apprentissage de la programmation web avec système de progression contrôlée, gamification et suivi temps réel.

---

## 📍 État réel au 2026-07-21

> ⚠️ **Avertissement.** Jusqu'à cette date, ce document marquait **tous** les
> livrables en ✅ — y compris ceux dont aucune ligne de code n'existait
> (WebSockets, forum, soumission de projets). C'était un modèle rempli
> d'avance, pas un état d'avancement. Les statuts ci-dessous ont été vérifiés
> ligne par ligne contre le code.
>
> **Convention :** ✅ fait et vérifié · 🟡 partiel · ❌ non commencé
> · ⏸️ écarté volontairement (raison indiquée)

| Phase | État | Commentaire |
|---|---|---|
| 1 — Fondations | ✅ | Complète, avec 112 tests backend |
| 2 — Temps réel | 🟡 | Interfaces faites, **WebSockets inexistants** |
| 3 — Gamification | ✅ | Badges, points, validation de code |
| 4 — Projets & social | ❌ | Modèle `Project` seul ; ni soumission, ni forum |
| 5 — Production | 🟡 | Sécurité avancée ; ni CI/CD, ni déploiement |

**Hors roadmap initiale, livré depuis :** classes (cohortes) avec liens
d'invitation, espace d'administration, réinitialisation de mot de passe,
gardes de rôle côté front, conformité RGPD (anonymisation).

**Les trois manques les plus structurants**, par ordre de valeur :

1. **Aucune infrastructure de test frontend** — ni Vitest, ni Playwright. Tout
   le React se vérifie à la main.
2. **Aucun WebSocket** — la sauvegarde automatique et le suivi « temps réel »
   annoncés reposent en réalité sur du HTTP par intervalles.
3. **Aucune CI/CD** — rien n'exécute les 112 tests automatiquement.

---

## 📅 PHASE 1 : FONDATIONS (Semaines 1-3)

### Sprint 1.1 : Infrastructure & Authentification (1 semaine)
**Objectifs :**
- Setup projet Django + PostgreSQL + Redis
- Système d'authentification multi-rôles
- Models de base (User, Role, Profile)

**Livrables :**
- ✅ Projet Django configuré avec settings dev/prod
- ✅ Modèle User custom avec rôles (Apprenant, Formateur, Admin)
- ✅ API d'authentification (JWT)
- ✅ Permissions par rôle (`IsTrainerOrAdmin`, `IsAdmin`)
  — ⏸️ groupes Django non utilisés : le champ `role` fait autorité
- ✅ Tests unitaires authentification (`apps/accounts/tests/`)

**Ajouté hors périmètre initial :**
- ✅ Réinitialisation de mot de passe (jeton sans état, anti-énumération)
- ✅ Unicité d'email insensible à la casse (contrainte en base)
- ✅ Synchronisation `role` ⇄ `is_staff`
- ✅ Garde-fou `SECRET_KEY` en production (refus de démarrage)

**User Stories concernées :** US-001, US-002, US-003

---

### Sprint 1.2 : Structure Pédagogique (1 semaine)
**Objectifs :**
- Modélisation du contenu (Chapitre, Leçon, Exercice, QCM, Projet)
- Relations et contraintes
- Admin Django pour gestion contenu

**Livrables :**
- ✅ Models : Chapter, Lesson, Exercise, Quiz, Project
- ⏸️ ~~Relations Many-to-Many avec tables intermédiaires~~ — clés étrangères
  simples retenues : la hiérarchie chapitre → leçon est stricte, un M2M
  n'aurait rien apporté
- ✅ Interface Admin Django customisée (avec inlines)
- ✅ Fixtures de contenu (`apps/courses/fixtures/`)
- ✅ API REST endpoints (lecture seule)

**User Stories concernées :** US-004, US-005, US-011

---

### Sprint 1.3 : Système de Progression (1 semaine)
**Objectifs :**
- Tracking de progression utilisateur
- Déblocage conditionnel de chapitres
- Sauvegarde de l'état

**Livrables :**
- ✅ Models : UserProgress, ChapterAccess, ActivityLog
- ✅ Logique de déblocage de contenu — **réellement appliquée depuis 2026-07-21**
  ⚠️ `ChapterAccess` existait depuis le début mais n'était consulté par aucune
  vue apprenant : la « progression contrôlée » était décorative, tout le monde
  ouvrait tous les chapitres. Le verrou est désormais dans
  `LessonViewSet.retrieve` (403), avec deux régimes — piloté par le formateur
  en classe, rythme libre auto-débloqué en autonomie.
- ✅ API endpoints progression
- ✅ Mesure du temps d'apprentissage
  ⚠️ `time_spent` était lu par trois interfaces mais **jamais écrit**. Écriture
  par incréments plafonnés + suivi du temps réellement actif côté client.
- ✅ Tests logique métier (`apps/cohorts/tests/`, `apps/gamification/tests/`)

**User Stories concernées :** US-006, US-007, US-008

---

## 📅 PHASE 2 : TEMPS RÉEL & INTERACTIVITÉ (Semaines 4-6)

### Sprint 2.1 : WebSockets & Channels — ❌ NON COMMENCÉ
**Objectifs :**
- Django Channels configuration
- WebSocket pour sauvegarde temps réel
- Redis comme message broker

**Livrables :**
- 🟡 Django Channels installé, Daphne tourne, Redis Layer configuré
  — mais `config/asgi.py` contient un `URLRouter([])` **vide**, avec un simple
  commentaire « WebSocket URL patterns will be added here »
- ❌ Consumer WebSocket pour progression — **aucun fichier `consumers.py`**
- ❌ Système de groupes par chapitre/session
- ❌ Heartbeat & reconnexion automatique
- ❌ Aucun code WebSocket côté React

> **Ce que fait réellement l'application aujourd'hui :** la sauvegarde des
> réponses de quiz passe par du HTTP avec anti-rebond de 800 ms, et le suivi
> du temps par un envoi HTTP toutes les 30 s. Cela fonctionne, mais ce n'est
> pas du temps réel : le formateur ne voit rien se mettre à jour en direct.

**User Stories concernées :** US-009, US-010

---

### Sprint 2.2 : Interface Apprenant (React) (1.5 semaines)
**Objectifs :**
- Interface de navigation des chapitres
- Lecteur de leçons
- Interface exercices avec éditeur de code
- Interface QCM

**Livrables :**
- ✅ Setup React + Redux Toolkit
- ✅ Composants : ChapterList, LessonViewer, CodeEditor, QuizInterface
- ❌ Intégration WebSocket côté client — dépend du sprint 2.1
- 🟡 Sauvegarde auto — faite, mais **en HTTP** (anti-rebond 800 ms), pas en
  WebSocket toutes les 3 s comme spécifié
- ✅ Design responsive, thème clair/sombre
- ✅ Page d'invitation, mot de passe oublié, affichage du mot de passe

**User Stories concernées :** US-012, US-013, US-014, US-015

---

### Sprint 2.3 : Interface Formateur (React) (0.5 semaine)
**Objectifs :**
- Dashboard de suivi des apprenants
- Gestion des déblocages
- Vue temps réel de l'activité

**Livrables :**
- ✅ Dashboard formateur avec statistiques
- ✅ Liste apprenants avec progression
- ✅ Contrôles de déblocage de chapitres (individuel **et** par classe entière)
- ❌ Vue temps réel — l'onglet « Activité récente » affiche un historique
  rechargé à la demande, pas un flux direct
- 🟡 Filtres et recherche — présents dans l'espace admin, pas côté formateur

**Ajouté hors périmètre initial :**
- ✅ Classes (cohortes) : création, liens d'invitation, membres
- ✅ Cloisonnement — un formateur ne voit que **ses** apprenants
  ⚠️ Avant cela, `learners_summary` renvoyait tous les apprenants de la
  plateforme à n'importe quel formateur

**User Stories concernées :** US-016, US-017, US-018

---

## 📅 PHASE 3 : GAMIFICATION & ENGAGEMENT (Semaines 7-8)

### Sprint 3.1 : Système de Points & Badges (1 semaine)
**Objectifs :**
- Système de points
- Badges et achievements
- Classement (leaderboard)

**Livrables :**
- ✅ Models : Badge, UserBadge, PointTransaction, UserStreak
- ⏸️ **Leaderboard écarté volontairement** — choix produit : privilégier la
  progression personnelle, moins décourageante pour un débutant. Le grand
  livre de points rend l'ajout trivial si besoin.
- ✅ Règles d'attribution automatique (23 badges, dont 8 objectifs secrets)
- ✅ API endpoints gamification
- ✅ Composants React : page trophées, prochains objectifs, série de jours
- ✅ Animations et feedback visuel (modale de révélation avec confettis)

**Invariant central, verrouillé par les tests :** aucun achievement ni crédit
de points ne peut être validé deux fois — garanti par des contraintes
d'unicité en base, des règles monotones et un grand livre de points
idempotent.

**User Stories concernées :** US-019, US-020, US-021

---

### Sprint 3.2 : Système de Validation & Feedback (1 semaine)
**Objectifs :**
- Correction automatique exercices
- Validation QCM
- Feedback instantané

**Livrables :**
- ✅ Engine de validation code (sandbox Docker isolé, réseau coupé)
- ✅ Correction QCM **côté serveur** avec explications — les bonnes réponses ne
  sont jamais envoyées au client avant soumission
- ✅ Système de hints progressifs
- ✅ Celery tasks pour corrections lourdes (queue `validation` dédiée)
- ❌ Notifications en temps réel — dépend du sprint 2.1

**User Stories concernées :** US-022, US-023, US-024

---

## 📅 PHASE 4 : PROJETS & COLLABORATION (Semaines 9-10)

### Sprint 4.1 : Gestion des Projets Finaux — ❌ NON COMMENCÉ
**Objectifs :**
- Soumission de projets
- Review par formateur
- Versioning simple

**Livrables :**
- 🟡 Modèle `Project` défini et exposé en **lecture seule**
  (`ProjectViewSet`) — aucun modèle de soumission n'existe
- ❌ Upload de fichiers projet
- ❌ Interface de review formateur
- ❌ Système de commentaires
- ❌ Validation finale de chapitre
- ❌ Historique des soumissions

**User Stories concernées :** US-025, US-026, US-027

---

### Sprint 4.2 : Fonctionnalités Sociales — ❌ NON COMMENCÉ
**Objectifs :**
- Forum de discussion par chapitre
- Entraide entre apprenants
- Modération

**Livrables :**
- ❌ Forum simple — **l'app `apps/forum` n'existe pas**
- ❌ Système de votes
- ❌ Notifications mentions
- ❌ Modération formateur
- ❌ Recherche dans le forum

**User Stories concernées :** US-028, US-029

---

## 📅 PHASE 5 : OPTIMISATION & PRODUCTION (Semaines 11-12)

### Sprint 5.1 : Performance & Sécurité (1 semaine)
**Objectifs :**
- Optimisation requêtes DB
- Cache stratégique
- Sécurité renforcée

**Livrables :**
- 🟡 Optimisation N+1 — `select_related`/`prefetch_related` appliqués aux
  chemins chauds ; pas d'audit systématique
- 🟡 `CACHES` Redis configuré, mais **aucune vue ne l'utilise**
- ✅ Rate limiting API (global, plus scopes `password_reset` et `invite`)
  ⚠️ `development.py` désactive tout throttling : les limites ne s'appliquent
  qu'en production
- ✅ Validation entrées renforcée (serializers DRF partout)
- ❌ Tests de charge (20+ utilisateurs simultanés)
- 🟡 Sentry configuré dans `production.py` (si `SENTRY_DSN` fourni) ; logs en
  console pour les conteneurs

**Sécurité livrée hors périmètre initial :**
- ✅ Garde-fou `SECRET_KEY` : refus de démarrage en production sans clé propre
- ✅ Révocation des sessions JWT (réinitialisation de mot de passe,
  désactivation de compte)
- ✅ Anti-énumération sur le mot de passe oublié et les liens d'invitation
- ✅ Anonymisation RGPD

**Technical Stories :** TS-001, TS-002, TS-003

---

### Sprint 5.2 : Déploiement & Documentation — 🟡 PARTIEL
**Objectifs :**
- Setup production
- CI/CD
- Documentation

**Livrables :**
- 🟡 Docker Compose — fonctionnel en développement ; pas de variante
  production dédiée
- ❌ CI/CD GitHub Actions — **aucun `.github/workflows/`**, rien n'exécute
  les 112 tests automatiquement
- ❌ Déploiement Railway/Render
- ❌ Documentation API (Swagger) — ni `drf-spectacular` ni `drf-yasg` installé
- 🟡 Documentation — `CLAUDE.md` tient lieu de référence technique ; pas de
  guide utilisateur ni de guide de déploiement

**Technical Stories :** TS-004, TS-005

---

## 📊 MÉTRIQUES DE SUCCÈS

### Phase 1
- [x] Tests d'authentification — 28 tests (comptes, mot de passe oublié,
      réglages de sécurité)
- [x] Admin Django opérationnel — 3 chapitres publiés à ce jour
- [ ] API REST documentée — aucun Swagger installé

### Phase 2
- [x] Sauvegarde rapide — mais en HTTP, la métrique WebSocket ne s'applique pas
- [ ] Support 20 connexions WebSocket simultanées — **0 connexion possible**
- [x] UI responsive sur mobile

### Phase 3
- [x] 10 badges différents — **23 implémentés**, dont 8 objectifs secrets
- [x] Validation automatique des exercices (sandbox Docker)
- [ ] ~~Leaderboard~~ — écarté volontairement (voir sprint 3.1)

### Phase 4
- [ ] Upload projets < 50MB — sprint non commencé
- [ ] Forum avec recherche fonctionnelle — sprint non commencé

### Phase 5
- [ ] Temps de réponse API < 300ms (p95) — jamais mesuré
- [ ] Uptime 99.5% — pas de déploiement
- [ ] Documentation complète

### Métriques ajoutées
- [x] **112 tests backend** passants
- [ ] **0 test frontend** — aucune infrastructure (ni Vitest, ni Playwright)

---

## 🎯 PRIORITÉS

### Must Have (MVP)
- [x] Authentification multi-rôles
- [x] Structure chapitres/leçons
- [x] Exercices avec validation
- [x] Déblocage contrôlé
- [ ] Sauvegarde temps réel — **seul élément du MVP encore manquant**
      (fonctionne en HTTP, pas en WebSocket)
- [x] Dashboard formateur basique

### Prochaines étapes recommandées

Par valeur décroissante, indépendamment du découpage en phases d'origine :

1. **Infrastructure de test frontend (Vitest)** — rien n'est vérifiable
   automatiquement côté React. Chaque modification se teste à la main, et
   deux bugs de page blanche sont déjà passés inaperçus faute de filet.
2. **CI/CD** — 112 tests existent mais rien ne les exécute. Le coût est faible
   et le bénéfice immédiat.
3. **WebSockets** — dernier élément du MVP. Débloque aussi les notifications
   temps réel et la vue d'activité du formateur.
4. **Soumission de projets** — le modèle `Project` attend depuis le début.
5. **Forum** — le plus gros chantier, le moins critique.

### Should Have
- Gamification complète
- Forum communauté
- Projets finaux avec review
- Analytics détaillées

### Could Have
- Mode hors-ligne
- Export progression PDF
- Intégration Slack/Discord
- Générateur de certificats
- API publique pour extensions

### Won't Have (V1)
- Visioconférence intégrée
- Éditeur collaboratif en temps réel
- Marketplace de cours
- Support multi-langues

---

## 📦 DÉPENDANCES TECHNIQUES

### Backend
- Django 5.0+
- Django Channels 4.0+
- Django REST Framework 3.14+
- PostgreSQL 15+
- Redis 7.0+
- Celery 5.3+

### Frontend
- React 18+
- Redux Toolkit 2.0+
- Monaco Editor (éditeur code)
- Socket.io-client
- Tailwind CSS

### DevOps
- Docker & Docker Compose
- GitHub Actions
- Railway/Render
- Sentry (monitoring)

---

## 🚨 RISQUES & MITIGATIONS

| Risque | Impact | Probabilité | Statut |
|--------|--------|-------------|--------|
| Performance WebSocket à grande échelle | Élevé | Moyen | ⏸️ Sans objet : aucun WebSocket implémenté |
| Correction automatique complexe | Moyen | Élevé | ✅ Maîtrisé — sandbox Docker + Celery |
| Sécurité éditeur de code | Élevé | Moyen | ✅ Maîtrisé — conteneur isolé, réseau coupé, limites CPU/RAM |
| Complexité gamification | Faible | Faible | ✅ Maîtrisé — invariants garantis en base |

### Risques identifiés en cours de route

| Risque | Impact | Statut |
|--------|--------|--------|
| **Documentation affirmant des fonctionnalités inexistantes** | Élevé | 🟡 Corrigé ici et dans `CLAUDE.md`, mais c'est un risque récurrent : vérifier contre le code, pas contre les documents |
| Absence totale de tests frontend | Élevé | ❌ Ouvert — deux pages blanches déjà passées en production locale |
| Absence de CI/CD | Moyen | ❌ Ouvert — les tests ne protègent que si on les lance |
| Fonctionnalités « décoratives » (code présent, jamais appelé) | Élevé | 🟡 Trois cas trouvés et corrigés (`ChapterAccess`, `time_spent`, tableau de bord formateur). En chercher d'autres avant de bâtir dessus |

---

## 🔄 RÉVISIONS

| Version | Date | Auteur | Changements |
|---------|------|--------|-------------|
| 1.0 | 2025-12-12 | Équipe | Version initiale |
| 2.0 | 2026-07-21 | Équipe | **Remise à plat des statuts.** Tous les livrables étaient marqués ✅ sans vérification, y compris des sprints entiers jamais commencés (WebSockets, projets, forum). Statuts revérifiés contre le code, ajout des livrables hors périmètre initial (classes, administration, sécurité), et des écarts volontaires (leaderboard, M2M). |
