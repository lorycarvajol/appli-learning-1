# 🚀 ROADMAP - Plateforme d'Apprentissage Web

## Vue d'ensemble
Plateforme interactive d'apprentissage de la programmation web avec système de progression contrôlée, gamification et suivi temps réel.

---

## 📍 État réel au 2026-08-04

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
| 1 — Fondations | ✅ | Complète |
| 2 — Temps réel | 🟡 | Interfaces faites, **WebSockets inexistants** |
| 3 — Gamification | ✅ | Badges, points, validation de code |
| 4 — Projets & social | ❌ | Modèle `Project` seul ; ni soumission, ni forum |
| 5 — Production | 🟡 | **Tout le code est prêt et éprouvé en répétition locale.** Ne restent que les étapes sur le serveur — voir [`06_ROADMAP_DEPLOIEMENT.md`](06_ROADMAP_DEPLOIEMENT.md) |

**Le sujet actif est la mise en production, pas le produit.** Le contenu
pédagogique est passé de 27 à 68 leçons et vit désormais dans le code
(`apps/courses/content/`), reconstructible par une commande.

**Hors roadmap initiale, livré depuis :** classes (cohortes) avec liens
d'invitation, espace d'administration avec journal d'audit, réinitialisation de
mot de passe, gardes de rôle côté front, conformité RGPD (anonymisation),
profil personnalisable (avatars, thème rattaché au compte).

### Filet de sécurité : 349 tests

| Périmètre | Tests | Remarque |
|---|---|---|
| `accounts` | 72 | comptes, mot de passe, profil, limitation des connexions, comptes de démonstration |
| `administration` | 53 | journal d'audit, garde-fous, bridage de l'admin Django |
| `progression` | 35 | verrou de chapitre, quiz, temps — validés par sabotage |
| `validation` | 24 | isolement du bac à sable, désactivation de l’exécution (+ 7 tests Docker réels, hors CI) |
| `cohorts` | 30 | classes, invitations, cloisonnement |
| `courses` | 29 | normalisation JSONB, masquage des solutions, chargeurs, illustrations |
| `gamification` | 29 | badges, points, anti-double-validation |
| **Backend** | **272** | pytest-django — 270 passants, 2 ignorés (contrôles réservés à la production) |
| **Frontend** | **65** | Vitest + Testing Library, jsdom |
| **Bout-en-bout** | **12** | Playwright, en local — pas encore en CI |
| ESLint | — | zéro erreur **et zéro avertissement**, porte de CI |

Toutes les apps backend sont désormais couvertes.

### Les trois manques les plus structurants

Par ordre de valeur, révisés après les chantiers de juillet :

1. **Aucun WebSocket** — la sauvegarde automatique et le suivi « temps réel »
   annoncés reposent en réalité sur du HTTP par intervalles. Rien n'en dépend
   aujourd'hui : c'est une brique prévue, jamais posée.
2. **Rien n'est déployé** — la CI construit et teste, mais ne livre nulle part.
   Aucun environnement de production n'existe.
3. **Phase 4 entière non commencée** — ni soumission de projets, ni forum.
   C'est le dernier gros bloc fonctionnel manquant.

*(Les deux premiers manques de la version précédente de cette liste — tests
frontend et CI/CD — sont faits.)*

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
- ✅ Engine de validation code (sandbox Docker isolé, réseau coupé) —
  **couvert par 27 tests depuis le 2026-07-21**, dont 20 simulés qui vérifient
  les arguments de lancement du conteneur (plus strict que d'en regarder
  tourner un) et 7 réels
- ✅ Correction QCM **côté serveur** avec explications — les bonnes réponses ne
  sont jamais envoyées au client avant soumission. Un test vérifie qu'un score
  envoyé par le client est ignoré
- ✅ Système de hints progressifs
- ✅ Celery tasks pour corrections lourdes (queue `validation` dédiée)
- ❌ Notifications en temps réel — dépend du sprint 2.1

⚠️ Le worker `celery` est le **seul** service à monter `/var/run/docker.sock` :
c'est lui qui pilote le bac à sable. Les tests réels ne tournent donc que là
(`docker-compose exec celery pytest -m docker`), et jamais en CI.

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
- ✅ Optimisation N+1 sur les vues d'administration (pilotage, formateurs,
  résumé des apprenants) — verrouillée par des tests qui **comparent le nombre
  de requêtes à deux volumes** et exigent l'égalité, plutôt qu'un plafond
  chiffré qu'un N+1 modéré traverserait
  🟡 Pas d'audit systématique sur le reste
- 🟡 `CACHES` Redis configuré ; utilisé par le throttling, par aucune vue
- ✅ Rate limiting API (global, scopes `password_reset`, `invite`, `login`)
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
- ✅ **Journal d'audit** des actions d'administration, en lecture seule
- ✅ **Admin Django bridé** — il pouvait changer un rôle ou supprimer un compte
  en contournant les garde-fous et le journal
- ✅ **Limitation des échecs de connexion**, comptés par compte visé et non par
  IP : une classe entière partage le NAT de son établissement
- ✅ **Bac à sable de code testé** — l'isolement du conteneur (réseau coupé,
  aucun montage, ressources plafonnées) est désormais verrouillé par 27 tests.
  La liste noire de motifs a été **retirée** : elle rejetait du code d'élève
  légitime tout en laissant passer les vrais contournements

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
- ✅ **Intégration continue** (`.github/workflows/ci.yml`) sur `main` et sur
  chaque *pull request*, en deux jobs indépendants :
  - **backend** — PostgreSQL et Redis en services, puis
    `makemigrations --check` → `migrate` sur base vierge → `manage.py check`
    → `pytest --create-db`
  - **frontend** — `npm ci` → `lint` → `test` → `build`

  ⚠️ Les deux premières étapes backend ne sont pas décoratives : `pytest.ini`
  fixe `--nomigrations`, donc la suite peut passer au vert alors qu'il manque
  une migration. La CI est le seul endroit où ce décalage se voit.

  ⚠️ Le `build` frontend attrape les **chemins dont la casse ne correspond
  pas** — invisibles sur Windows, fatals sur le runner Linux.
- ❌ **Livraison continue** — la CI teste, elle ne déploie rien
- ❌ Déploiement Railway/Render
- ❌ Documentation API (Swagger) — ni `drf-spectacular` ni `drf-yasg` installé
- 🟡 Documentation — `CLAUDE.md` tient lieu de référence technique ; pas de
  guide utilisateur ni de guide de déploiement

**Technical Stories :** TS-004, TS-005

---

## 📊 MÉTRIQUES DE SUCCÈS

### Phase 1
- [x] Tests d'authentification — **52 tests** (comptes, mot de passe oublié,
      profil, limitation des connexions, réglages de sécurité)
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

> 📄 Le détail du chantier de mise en ligne (VPS OVH, Traefik, et les points où
> `guide-hebergement-ovh.md` se trompe sur ce dépôt) vit dans
> [`06_ROADMAP_DEPLOIEMENT.md`](06_ROADMAP_DEPLOIEMENT.md).

### Métriques (2026-08-04)
- [x] **270 tests backend** (+ 7 marqués `docker`, hors CI)
- [x] **65 tests frontend** (Vitest + Testing Library)
- [x] **12 tests bout-en-bout** (Playwright, en local)
- [x] **ESLint à zéro** — erreurs *et* avertissements, en porte de CI
- [x] **CI verte** sur `main` et sur chaque *pull request*
- [x] Toutes les apps backend couvertes, `courses` comprise
- [ ] La CI ne lance pas encore l'E2E et ne construit aucune image

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

Par valeur décroissante, indépendamment du découpage en phases d'origine.
Révisé le 2026-07-21 : les deux premières entrées de la liste précédente
(tests frontend, CI) sont faites.

1. **Déploiement** — c'est ce qui manque pour que tout le reste serve à
   quelqu'un. La CI construit déjà les deux moitiés du projet ; il reste à
   choisir un hébergeur, écrire la variante production du Compose et brancher
   la livraison. Le garde-fou `SECRET_KEY` est prêt à refuser un démarrage mal
   configuré.
2. **Soumission de projets** — le modèle `Project` attend depuis le début, sans
   rien pour rendre ni corriger. C'est le chaînon manquant entre « suivre des
   leçons » et « être évalué », donc la fonctionnalité qui donne un but au
   parcours.
3. **WebSockets** — dernier élément du MVP d'origine. À relativiser : la
   sauvegarde et le suivi fonctionnent en HTTP, et rien n'est cassé. Le gain
   réel est le confort, pas une capacité nouvelle.
4. **Tests de `courses`** — dernière app backend sans test propre. C'est là que
   vivait `Exercise.total_points`, cassé depuis l'origine et découvert par
   hasard.
5. **Forum** — le plus gros chantier, le moins critique.

**Dette technique à traiter en chemin** (aucune n'est bloquante) :

- Le contrat des services API est incohérent — certains modules rendent la
  réponse axios brute, d'autres les données déballées. A déjà coûté une page
  blanche. Écrire un test de contrat par module **avant** d'uniformiser.
- Aucun découpage de bundle : `App.jsx` importe tout statiquement, ~535 kB d'un
  bloc. `React.lazy` par route est mécanique.
- Le conteneur du bac à sable s'exécute en `root` ; `user='nobody'` serait un
  durcissement peu coûteux, à valider sur les quatre langages.

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
| Sécurité éditeur de code | Élevé | Moyen | ✅ Maîtrisé — conteneur isolé (réseau coupé, aucun montage, limites CPU/RAM), vérifié par 27 tests |
| Complexité gamification | Faible | Faible | ✅ Maîtrisé — invariants garantis en base |

### Risques identifiés en cours de route

| Risque | Impact | Statut |
|--------|--------|--------|
| **Documentation affirmant des fonctionnalités inexistantes** | Élevé | 🟡 Trois cas corrigés (tests frontend, WebSockets, découpage de bundle). Risque **récurrent** : vérifier contre le code, jamais contre les documents |
| Absence totale de tests frontend | Élevé | ✅ Fermé — Vitest, 65 tests |
| Absence de CI/CD | Moyen | 🟡 CI faite ; **CD toujours absente**, et la CI ne construit aucune image |
| **Données de développement propagées en production** | Élevé | 🟡 `create_demo_users` refuse désormais de tourner en production et `purge_test_accounts` nettoie une base existante. **Reste ouvert** : rien n'empêche de restaurer un dump de développement, qui contient des comptes à mot de passe public |
| **Contenu pédagogique détruit par une commande** | Élevé | ✅ Fermé — `load_demo_content` avait effacé les 4 chapitres ; chaque chargeur ne supprime plus que ses propres slugs, et deux tests le verrouillent |
| Fonctionnalités « décoratives » (code présent, jamais appelé) | Élevé | 🟡 Cinq cas trouvés et corrigés (`ChapterAccess`, `time_spent`, tableau de bord formateur, `ProfileView` jamais appelée, `change-password` jamais branchée). En chercher d'autres avant de bâtir dessus |
| **Garde-fous contournables par un autre chemin** | Élevé | 🟡 Deux cas fermés : l'admin Django écrivait rôles et points sans passer par les services ni le journal ; le bac à sable n'avait aucun test. Se demander systématiquement : *quelle autre porte ouvre sur cette table ?* |
| **Sécurité qui gêne l'usage sans protéger** | Moyen | ✅ Un cas trouvé et retiré : la liste noire de motifs du bac à sable rejetait du code d'élève légitime et laissait passer les vrais contournements. Mesurer avant de garder |
| **Tests verts sur du code cassé** | Élevé | 🟡 Traité par sabotage volontaire sur `progression`. À refaire pour toute suite critique : un test jamais vu rouge ne prouve rien |

---

## 🔄 RÉVISIONS

| Version | Date | Auteur | Changements |
|---------|------|--------|-------------|
| 1.0 | 2025-12-12 | Équipe | Version initiale |
| 2.0 | 2026-07-21 | Équipe | **Remise à plat des statuts.** Tous les livrables étaient marqués ✅ sans vérification, y compris des sprints entiers jamais commencés (WebSockets, projets, forum). Statuts revérifiés contre le code, ajout des livrables hors périmètre initial (classes, administration, sécurité), et des écarts volontaires (leaderboard, M2M). |
| 2.1 | 2026-07-21 | Équipe | **Filet de sécurité posé.** Vitest (37 tests), CI GitHub Actions, ESLint ramené à zéro, couverture de `progression` (33 tests, validés par sabotage) et du bac à sable (27 tests). Sécurité : journal d'audit, admin Django bridé, limitation des échecs de connexion, retrait de la liste noire du bac à sable. Priorités réordonnées : le déploiement passe en tête, les WebSockets reculent — rien n'en dépend. |
| 3.0 | 2026-08-04 | Équipe | **Contenu restauré, production préparée.** `load_demo_content` avait effacé tous les cours ; contenu remonté de 27 à 68 leçons et réorganisé (17 scripts hors commande supprimés, une commande par chapitre, illustrations rattachées au chargement et versionnées). Produit : validation d'une leçon au défilement au lieu d'un bouton, visionneuse d'images corrigée, logo et favicon. Production : pile complète éprouvée en répétition locale (Traefik, 10 contrôles), sauvegardes avec restauration testée, garde-fou des comptes de démonstration. Détail dans [`06_ROADMAP_DEPLOIEMENT.md`](06_ROADMAP_DEPLOIEMENT.md). |
