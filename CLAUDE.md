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

## Où en est le projet (2026-08-06)

**La plateforme est fonctionnellement complète pour un premier usage réel.**
Deux chantiers ouverts en parallèle : la **mise en production** (bloquée sur des
étapes serveur) et une **série d'illustrations de leçon**, en cours.

> ⏩ **Reprise du 2026-08-06.** Le chantier actif à la reprise est la série
> d'illustrations : **4 leçons sur 68** sont dessinées, toutes dans le
> chapitre 1. La prochaine est `quiz-structure-html`, le premier **quiz** — il
> doit recevoir un signe de type qui lui soit propre, comme le vert des
> exercices : carte de question et pastilles de réponse, dans le violet `quiz`
> du thème. Voir « Illustrations de leçon — une série, une grammaire ».
>
> Chaque illustration est **validée une par une** par l'exploitant avant d'être
> intégrée. Méthode de travail éprouvée sur les six dernières : dessiner, poser
> une page d'aperçu jetable dans `frontend/public/` (servie par Vite sans
> authentification, elle charge les vraies feuilles de style), **regarder**,
> corriger, supprimer la page. Elle a attrapé une dizaine de défauts
> invisibles à la lecture du code.

| | |
|---|---|
| Backend | 7 apps : `accounts`, `administration`, `cohorts`, `courses`, `gamification`, `progression`, `validation` |
| Frontend | 12 features, 18 routes |
| Contenu | 4 chapitres, 68 leçons, 25 exercices, 5 quiz, 31 figures de cours |
| Illustrations de leçon | 4 sur 68 (chapitre 1), série en cours |
| Tests | **328 backend** (+7 marqués `docker`, hors CI), **114 frontend**, 12 bout-en-bout |
| CI | Verte sur `main` et sur chaque *pull request* |

### Reprendre en trois commandes

```bash
docker-compose up -d
docker-compose exec backend python manage.py load_course_content   # contenu
docker-compose exec backend python manage.py create_demo_users     # comptes de dev
```

Puis http://localhost:5173 et http://localhost:8000/admin/.

### Ce qui reste, par ordre de priorité

1. **Illustrations de leçon** — le chantier en cours, 4 sur 68. Validation une
   par une, la suivante est le premier quiz.
2. **Mise en production** — tout le code est prêt et éprouvé par une répétition
   locale ; ne restent que les étapes sur le serveur, qui demandent les secrets
   de l'exploitant. **Point d'entrée :
   [`06_ROADMAP_DEPLOIEMENT.md`](06_ROADMAP_DEPLOIEMENT.md)**, qui contient
   aussi la confrontation de `guide-hebergement-ovh.md` au code réel.
3. **CI qui construit les images** — elle n'en construit aucune aujourd'hui.
4. **Produit, après ouverture** : WebSockets (rien n'existe, voir la section
   dédiée), soumission de projets, forum.

⚠️ La branche `chore/fusion-monpc-design` porte **treize commits locaux non
poussés** au 2026-08-06, et aucune *pull request* n'est ouverte vers `main`.

### Les pièges qui coûtent le plus cher

Chacun a fait perdre du temps au moins une fois. Ils sont détaillés dans leur
section, cette liste sert d'index.

| Piège | Section |
|---|---|
| `load_demo_content` a effacé tout le contenu des cours | « Contenu des cours — architecture » |
| `/media/` n'est servi par personne en production | `06_ROADMAP_DEPLOIEMENT.md` §1 |
| `SIMPLE_JWT` copie `SECRET_KEY` à l'import | « SECRET_KEY — garde-fou de production » |
| `development.py` **mute** les réglages de `base.py` en place | « Testing Strategy » |
| `login.fulfilled` ne peuple ni `user` ni `initialized` | « Gardes de rôle côté front » |
| Supprimer un chapitre reverrouille les apprenants en classe | « Contenu des cours — architecture » |
| `VITE_*` est figée à la construction, pas lue à l'exécution | « Ressources statiques » |
| `--reuse-db` de pytest masque une migration manquante | « Testing Strategy » |
| `--` dans un commentaire XML rend un SVG entier muet | « Illustrations de leçon » |
| `next_lesson` proposait une leçon de chapitre verrouillé | « Continuer l'apprentissage suit l'ordre du parcours » |

### Conventions non négociables

1. **Docker pour tout** — ne rien installer localement, sauf `npm` côté front
   (le conteneur est en Node 18, la CI et les tests en Node 22).
2. **Écrire en français** : commentaires, tests, messages de commit.
3. **Valider par sabotage** : casser volontairement le code pour vérifier que
   le test rougit. Un test vert sur du code cassé ne protège rien.
4. **UUID partout**, jamais d'entiers séquentiels. Slugs pour les URL.
5. **JSONB** pour `Exercise.tests` et `Quiz.questions` — toujours lus via
   `test_cases` et `questions_list`, jamais directement.
6. Les points ne se créditent que par `services.award_points`, jamais par
   `Profile.add_points`.

## Contenu des cours — architecture

Le contenu pédagogique **ne vit pas en base de données** : il vit dans le code,
sous `apps/courses/content/`. La base n'en est qu'une projection,
reconstructible à tout moment. C'est ce qui a permis de récupérer les deux
incidents décrits plus bas sans perdre une ligne.

```
backend/apps/courses/
├── content/                       ← la source du contenu
│   ├── illustrations.py           règles déclaratives de rattachement des figures
│   ├── pipeline.py                assemblage d'un chapitre (compléments + figures)
│   ├── section1_html_extra.py     12 leçons complémentaires HTML
│   ├── section1_html_quiz.py      quiz HTML (20 questions, positions mélangées)
│   ├── section2_css_extra.py      12 leçons complémentaires CSS
│   ├── section3_javascript.py     le chapitre JavaScript (17 leçons)
│   ├── section3_javascript_quiz.py
│   └── images/                    dessin des illustrations (Pillow)
│       ├── palette.py             couleurs, polices, primitives — le socle commun
│       ├── section1_html.py       13 figures
│       ├── section2_css.py        11 figures
│       └── section3_javascript.py  7 figures
└── management/commands/
    ├── load_course_content.py     ← orchestrateur, le point d'entrée
    ├── load_section_1_html.py     un chapitre complet chacune
    ├── load_section_2_css.py
    ├── load_section_3_javascript.py
    ├── load_section_4_site_vitrine.py
    ├── load_demo_content.py       3 chapitres maigres, pour les démos
    └── generate_course_images.py  régénère les 31 PNG
```

### Une commande = un chapitre complet

```bash
python manage.py load_course_content              # tout le parcours
python manage.py load_course_content --section 3  # un seul chapitre
python manage.py load_course_content --list
```

**C'est l'invariant central.** Une commande de section construit son chapitre
*entier* : contenu de base, leçons complémentaires, quiz et illustrations. Il
n'y a plus d'étape à ne pas oublier.

| Chapitre | Commande | Contenu |
|---|---|---|
| 1 — HTML | `load_section_1_html` | 18 leçons, 8 exercices, 2 quiz |
| 2 — CSS | `load_section_2_css` | 17 leçons, 8 exercices, 1 quiz |
| 3 — JavaScript | `load_section_3_javascript` | 18 leçons, 9 exercices, 1 quiz |
| 4 — Site vitrine | `load_section_4_site_vitrine` | 15 leçons, 1 quiz |

⚠️ `load_section_3_javascript` **supprime le chapitre de démonstration**
`javascript-debutants` : les deux occupent la même place dans le parcours.

### Les illustrations sont rattachées au chargement, pas après coup

`content/illustrations.py` déclare 32 règles « ancre → figure », appliquées par
`pipeline.finish()` juste avant l'enregistrement. Deux propriétés, chacune
couverte par un test (`tests/test_illustrations.py`) :

- **Idempotent** — l'image déjà présente ⇒ la règle ne fait rien. Recharger un
  chapitre n'empile pas les figures.
- **Bruyant** — ancre introuvable ⇒ `IllustrationError`. Une figure qui
  disparaît casse le chargement au lieu de produire une leçon amputée.

Les PNG sont **versionnés** (`backend/media/courses/`, 31 fichiers, 710 Ko) :
un clone affiche les illustrations sans rien exécuter. `.gitignore` ignore le
reste de `backend/media/` (les téléversements d'exécution) mais ré-inclut
`courses/`.

`generate_course_images` ne sert qu'à **retoucher** une figure — on la relance
et on commite le PNG. Elle exige Pillow et les polices DejaVu, installés dans
l'**étage development** du Dockerfile seulement. ⚠️ Ne pas remonter Pillow dans
`requirements/base.txt` : il en a été retiré avec le dernier `ImageField` (cf.
« Avatars : catalogue, pas téléversement »), et la production sert des PNG
versionnés — elle n'a rien à dessiner.

### Ajouter du contenu

- **Une leçon** → dans le module `content/sectionN_*.py` correspondant, puis
  recharger la section.
- **Une figure** → dessiner dans `content/images/sectionN_*.py`, lancer
  `generate_course_images`, ajouter la règle dans `illustrations.py`, recharger.
- **Un chapitre** → un module dans `content/`, une commande, et une entrée dans
  `SECTIONS` de `load_course_content.py`.

### L'incident du 2026-08-04 : 17 scripts à la racine

Avant cette réorganisation, `backend/` portait **17 scripts** hors de toute
commande Django, formant un pipeline manuel non documenté. Construire le seul
chapitre 1 demandait six étapes dans un ordre précis : `load_section_1_html`,
`expand_section_1_html.py`, `add_html_quiz.py`, `fix_html_quiz_option_order.py`,
puis deux scripts d'images qui faisaient un `str.replace()` **sur la base**.

Quatre conséquences, toutes constatées :

- **L'étape 1 défaisait les étapes 2 à 8.** Recharger une section réécrivait le
  contenu depuis la source, donc sans les figures — silencieusement.
- **L'ordre était piégeux** : `expand_section_1_html.py` échouait si
  `add_html_quiz.py` n'était pas passé *avant*, ce qu'aucun fichier ne disait.
- **Le chapitre JavaScript était invisible** : ses 17 leçons existaient dans
  `backend/load_section_3_javascript.py`, jamais promu en commande, donc jamais
  lancé. Le parcours servait les 2 leçons squelettiques de la démo à sa place.
- **Les illustrations n'étaient ni versionnées ni régénérables** : `media/`
  était dans `.gitignore`, et l'image Docker n'avait ni Pillow ni les polices.
  État mesuré au moment du diagnostic : **0 image référencée en base, 31 PNG
  orphelins sur le disque**.

Bilan après réorganisation : **43 leçons manquantes restaurées** (27 → 70), les
17 scripts supprimés, `backend/` ne contenant plus que `manage.py`.

⚠️ **Cette suppression a été défaite une fois, et il faut savoir pourquoi.** La
fusion des copies `-MonPC` du 2026-08-06 a **ressuscité les 18 fichiers**
(16 scripts + 2 sondes de débogage) en même temps que `viewport.avif` : une
copie OneDrive antérieure à la réorganisation les contenait encore, et la
fusion a réintroduit tout ce qu'elle portait. Ils ont été re-supprimés le
2026-08-06 après vérification que chaque contrepartie existe
(`content/`, `content/images/`, `management/commands/`) et qu'aucun code ne
les importe. Le même mécanisme peut avoir ramené d'autres fichiers morts :
**au moindre doute sur un fichier réapparu, chercher d'abord s'il a une
contrepartie dans `apps/`, avant de le lancer.**

⚠️ La refonte a été validée par **empreinte avant/après** : le pipeline manuel a
d'abord été rejoué en entier pour figer un état de référence (hachage du contenu
de chaque leçon), puis la nouvelle commande unique a dû le reproduire à
l'identique. Elle a attrapé une vraie régression au passage — une transformation
qui indentait l'intérieur des chaînes multilignes et décalait donc tout le
contenu des leçons de 4 espaces. Refaire cette vérification avant toute
manipulation de masse du contenu.

### L'incident du 2026-07-22 : la commande qui écrasait tout

`load_demo_content` faisait `Chapter.objects.all().delete()` — il ne supprimait
pas *son* contenu mais **tout** le contenu, puis recréait trois chapitres
maigres. Les chapitres HTML et CSS riches ont ainsi disparu, remplacés par leur
version de démonstration ; seul `site-vitrine`, rechargé cinq heures plus tard,
a survécu. Symptôme rapporté : « les cours étaient beaucoup plus développés,
avec des illustrations et des exercices, et là c'est très vide ».

Le déclencheur était documenté et recommandé : l'amorçage de la suite Playwright
demandait de lancer `load_demo_content`. **Lancer les tests bout-en-bout
détruisait le contenu des cours.**

Trois règles en découlent, à ne pas défaire :

- **Une commande de chargement ne supprime que les slugs qu'elle crée.** Les
  `load_section_*` le faisaient déjà (`filter(slug=…)`) ; `load_demo_content`
  est désormais borné par `DEMO_CHAPTER_SLUGS`. Une nouvelle commande qui
  ajoute un chapitre doit ajouter son slug à sa propre liste de suppression,
  jamais élargir la portée. La seule exception est assumée et documentée :
  `load_section_3_javascript` retire `javascript-debutants`, le chapitre de
  démonstration qu'il remplace au même rang du parcours.
- **L'amorçage E2E passe par `load_section_1_html --force`**, pas par
  `load_demo_content`. Le loader de section fournit le même slug, le même titre
  et la même première leçon que ce qu'attend `navigation.spec.js`, en plus
  complet et sans rien détruire d'autre.
- **Après toute recréation de chapitre, lancer `backfill_chapter_access`.**
  Supprimer un `Chapter` cascade sur `ChapterAccess` et `UserProgress` : les
  apprenants autonomes se rouvrent seuls le chapitre 1 (via
  `ensure_self_paced_access`, appelé à chaque contrôle d'accès), mais un
  apprenant **en classe** perd les accès que son formateur lui avait ouverts et
  ne les récupère pas tout seul. C'est un reverrouillage accidentel, contraire
  à l'invariant « on ne reverrouille jamais » — il faut le réparer à la main
  (`unlock_chapter_for`) si le backfill ne le couvre pas.

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

### Le catalogue : 30 badges, 20 visibles et 10 secrets

Réparti par catégorie (maîtrise 11, progression 8, régularité 6, exploration 5)
et par palier (argent 10, or 9, bronze 7, légendaire 4).

⚠️ **`CHAPTER_MASTERED` était une règle morte.** Elle existait dans
`Badge.RuleType` **et** dans le registre `rules.RULES` depuis l'origine, sans
qu'aucun badge ne s'en serve. Quatre badges l'emploient désormais — un par
chapitre du parcours — et ils disent ce que `chapitre-boucle` (un chapitre,
n'importe lequel) et `trois-chapitres` ne disent pas : **lequel**.

⚠️ Le `chapter_slug` de ces badges doit correspondre à un slug réellement posé
par une commande `load_section_*`. Un slug erroné donne un badge **inatteignable
et muet** : la règle renvoie « 0 sur 1 » pour toujours, sans que le semis ni
l'API ne s'en plaignent. `test_les_badges_de_chapitre_visent_un_slug_reellement_charge`
lit les **sources des chargeurs** plutôt que la base de test — peupler la base
dans le test n'aurait vérifié que sa cohérence avec lui-même, alors que c'est
le lien avec `load_section_*` qui doit tenir.

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

## Classement — ✅ Fait

`apps/gamification/leaderboard.py`, `GET /api/gamification/leaderboard/`, route
front `/classement`. **Aucun modèle, aucune écriture** : le grand livre
garantissait déjà l'exactitude des soldes, il ne restait qu'à les ordonner.

L'enjeu n'était donc pas le calcul mais la **discrétion**. C'est la seule page
où un apprenant voit les autres, donc la seule qui puisse transformer une
plateforme scolaire en annuaire. Quatre décisions en découlent, chacune
couverte par un test (`apps/gamification/tests/test_leaderboard.py`, 18 tests,
validés par sabotage) :

- **Rien d'identifiant ne sort de l'API.** Le nom est réduit à « Prénom N. »
  **côté serveur**, y compris pour soi-même — le client repère sa ligne par
  `is_me`, pas par son nom. Aucun email n'est transmis, même en repli : un
  compte sans identité renseignée est « Apprenant ». Un test lit la réponse
  brute et refuse le moindre `@`.
- **Le retrait est possible** (`Profile.show_in_leaderboard`, défaut `True`,
  éditable depuis `/profil`). Se comparer motive les uns et décourage les
  autres. Un compte retiré garde points et badges ; il ne voit **plus non plus
  son propre rang**, sinon le retrait serait cosmétique.
- **Qui n'a aucun point n'est pas classé.** Un compte neuf n'arrive pas 57ᵉ ex
  æquo avec quarante autres — on lui dit qu'il n'est pas encore entré.
- **Les ex æquo partagent leur rang** (1, 2, 2, 4). Départager deux soldes
  identiques sur la date d'inscription afficherait une hiérarchie qui n'existe
  pas. Le rang personnel suit la même règle (nombre d'apprenants strictement
  devant, plus un), donc reste cohérent avec le tableau.

⚠️ **`leaderboard.participants()` est le point unique de filtrage** — le
tableau, le rang personnel et le total sont tous construits dessus. Une règle
ajoutée d'un seul côté produirait un rang incohérent avec la liste affichée.
Exclus : comptes inactifs, non-`LEARNER` (un formateur qui parcourt son propre
cours trusterait la tête), anonymisés RGPD, retirés, à zéro point.

Le **rang personnel est renvoyé même hors du top** : un palmarès qui ne parle
qu'à ses vingt premiers ne sert à rien au vingt-et-unième — c'est pourtant lui
qu'il devrait motiver.

Coût : **cinq requêtes quel que soit le nombre d'apprenants**. Comme ailleurs,
le test compare deux volumes et exige l'égalité plutôt que de fixer un plafond
chiffré. C'est la page que toute une promo ouvre en même temps.

Deux portées : `?scope=global` (défaut) et `?scope=cohort`. Sans classe, la
seconde répond `available: false` **avec une raison** plutôt qu'un tableau
vide, qui se lirait comme une panne. Côté front, le store garde une entrée par
portée : la bascule ne vide pas l'écran le temps d'un aller-retour réseau.

⚠️ `Avatar` retombe sur `display_name` — pour les initiales *et* pour la graine
de couleur — puisque le classement ne transmet aucun email. Sans ce repli,
toutes les lignes à initiales auraient la même couleur.

## Le verrou de chapitre s'applique aussi aux écritures

⚠️ **Il ne protégeait que la lecture.** `LessonViewSet.retrieve` renvoyait bien
403, mais `mark_completed`, `track_time` et `submit_quiz` acceptaient
n'importe quelle leçon — et `mark_completed` acceptait n'importe quel *type*,
exercice et quiz compris, dont il créditait les points.

Mesuré sur un compte neuf avant correction : **68 appels à `mark_completed`,
aucun refusé**, le compte passant de 1 à 4 chapitres accessibles, de 0 à
1485 points et de 0 à 11 badges, **sans jamais ouvrir une leçon**. Les trois
invariants centraux tombaient ensemble : progression contrôlée par le
formateur, grand livre de points, badges.

Deux règles distinctes, et il faut les deux
(`apps/progression/tests/test_ecriture_verrouillee.py`) :

1. **Le chapitre doit être ouvert** — `_refus_si_chapitre_verrouille` sur les
   trois vues. La décision vivait déjà dans `services.can_access_lesson`, elle
   n'était simplement pas consultée.
2. **Seule la théorie se déclare terminée.** Un exercice se valide en passant
   ses tests, un quiz en atteignant son score : ce sont les deux seuls
   contenus dont la réussite est objectivement vérifiable. Les déclarer
   terminés revenait à s'en attribuer les points sans le travail. Une leçon de
   théorie, elle, n'a pas de critère vérifiable — on ne peut pas prouver
   qu'elle a été lue.

Après correction, le même scénario donne **60 refus sur 68**, le chapitre 2 ne
s'ouvre plus, et les points tombent de 1485 à 110 — les seules leçons de
théorie du chapitre légitimement accessible.

⚠️ **Corollaire : la réussite d'un exercice se constate côté serveur.** Le
front appelait `mark_completed` depuis `onSubmit` dès que `result.success`
était vrai — le client décidait donc de l'attribution des points. La
complétion se fait maintenant dans `validation.tasks._constater_la_reussite`,
via `progression.services.complete_lesson` partagé avec `mark_completed`.

## Validation d'une leçon — constatée, plus déclarée

Il n'y a **plus de bouton « Marquer comme terminé »**. Demander à l'apprenant
de déclarer une progression que l'application peut observer était contre-
intuitif : la leçon était lue, mais restait « en cours » tant qu'on n'avait pas
pensé à cliquer.

| Type de leçon | Condition de validation |
|---|---|
| **THEORY** | Le bas du contenu reste visible 2 secondes (`useScrollCompletion`) |
| **EXERCISE** | Tous les tests passent (déjà le cas — `onSubmit` d'`ExerciseInterface`) |
| **QUIZ** | Score requis atteint (déjà le cas — `submit_quiz`, côté serveur) |

### Trois décisions, chacune couverte par un test

- **Le défilement ne valide que la théorie.** `LessonView` ne monte le hook et
  ne rend le repère que pour `THEORY`. Un exercice ou un quiz validé en faisant
  défiler la page distribuerait ses points sans le travail —
  `POST /progress/mark_completed/` crédite les points **sans vérifier** qu'un
  exercice a été résolu ni qu'un quiz a été réussi. Le bouton retiré était donc
  aussi une porte dérobée. ⚠️ Cette vérification manque toujours côté serveur :
  aujourd'hui c'est le front qui n'appelle plus la route pour ces types-là, pas
  l'API qui la refuse.
- **Un repère observé, pas un calcul de défilement.** Un élément vide en fin de
  contenu confié à un `IntersectionObserver` répond exactement à la question
  posée, sans écouteur `scroll` global à amortir, et suit les changements de
  mise en page — les illustrations qui finissent de charger rallongent la page
  après coup.
- **Le délai de 2 secondes n'est pas cosmétique.** Une leçon courte tient
  entièrement à l'écran : son repère est visible dès l'ouverture, et valider
  aussitôt marquerait la leçon terminée avant qu'elle soit lue. Quitter le bas
  avant la fin du délai annule le compte à rebours.

Sans `IntersectionObserver` (très vieux navigateur, jsdom sans polyfill), le
hook **s'abstient** : mieux vaut ne rien valider que valider à tort.

Le bouton est remplacé par une région `role="status"` nommée « Statut de la
leçon » qui dit ce qui reste à faire. ⚠️ Le nom accessible n'est pas décoratif :
`PageLoader` porte lui aussi `role="status"`, et sans lui les requêtes de test
trouvent deux régions.

## Tableau de bord — vue d'ensemble et conseil du jour

### Le pourcentage ne mesurait pas ce qu'il annonçait

⚠️ La « progression globale » valait `terminées / (terminées + en cours)`,
calculée **côté client sur les seules leçons déjà touchées**. Deux
conséquences, visibles dès le premier jour :

- une première leçon terminée affichait **100 %** — le programme entier
  n'était pas au dénominateur ;
- **ouvrir une leçon faisait *baisser* la barre** : elle entrait au
  dénominateur sans entrer au numérateur. Le chiffre reculait au moment précis
  où l'apprenant se remettait au travail.

Le client ne pouvait pas corriger ça seul : **il ignore combien de leçons
existent**. D'où `GET /api/progression/progress/overview/`, qui renvoie les
totaux, le détail par chapitre, le temps cumulé et la moyenne des notes.

Trois décisions, chacune couverte par un test
(`apps/progression/tests/test_overview.py`, 12 tests, validés par sabotage) :

- **Le périmètre est exactement celui de `next_lesson`** : `is_published` sur
  la leçon *et* sur son chapitre. Deux blocs voisins du même écran se
  contrediraient sinon. ⚠️ **Ne pas utiliser `Chapter.lesson_count` pour un
  pourcentage** : il compte aussi les leçons non publiées.
- **Les leçons non notées sortent de la moyenne.** `UserProgress.score` est
  `null` sur une leçon de théorie — il n'y a rien à y noter. Le tableau de bord
  les comptait comme des zéros : deux quiz parfaits et huit leçons lues
  affichaient « 20 % de score moyen », ce qu'un débutant lit comme un échec.
- **`average_score` vaut `null`, jamais `0`, quand rien n'est noté**, et le
  client affiche un tiret. Zéro et « pas encore évalué » ne veulent pas dire la
  même chose.

Le détail par chapitre accompagne le total, chapitres verrouillés compris
(même règle que le sommaire : on montre la suite du parcours, on ne l'ouvre
pas). « 12 sur 68 » ne dit pas où l'on en est ; « chapitre 2 à moitié fait »,
si.

### « Continuer l'apprentissage » suit l'ordre du parcours

⚠️ **Règle inversée le 2026-08-06.** `next_lesson` proposait la leçon **entamée
la plus récemment**, où qu'elle soit dans le programme. Constaté en usage réel :
un compte ayant ouvert une leçon du dernier chapitre — ce que fait tout auteur
ou formateur qui relit son contenu — se voyait proposer « Mettre son site en
ligne » avec un chapitre 1 intact, et le conseil du jour reprenait le même
titre.

L'intention (« reprendre où l'on en était ») était bonne, mais **« où l'on en
était » ne peut pas être plus loin que le premier trou du parcours**. La vue
rend donc la **première leçon non terminée dans l'ordre du programme**, et
`is_resuming` dit seulement si elle était déjà entamée.

⚠️ **Second défaut, corrigé en même temps : le verrou de chapitre n'était pas
consulté.** La vue proposait la première leçon non terminée *tous chapitres
confondus* — le bouton « Commencer » pouvait mener droit à un 403. Elle passe
maintenant par `accessible_chapter_ids`, ce qui a un effet de bord voulu :
`ensure_self_paced_access` ouvre le chapitre 1 d'un apprenant au rythme libre
qui n'a encore rien fait. Le tableau de bord d'un compte neuf a donc toujours
quelque chose à proposer, et c'est le début du parcours.

Trois absences que le client doit distinguer, et qui ne s'affichent pas pareil :

| Réponse | Situation | Ce que dit l'écran |
|---|---|---|
| `all_completed: true` | Tout le programme est fait | Félicitations + trophées |
| `locked: true` | Tout ce qui est **ouvert** est fait, la suite est verrouillée | « La suite viendra de votre formateur » |
| ni l'un ni l'autre, `lesson: null` | Aucun contenu publié | « Aucune leçon disponible » |

Les confondre ferait annoncer « parcours terminé » à un apprenant qui n'a vu
qu'un chapitre sur quatre — ou une panne de plateforme à celui qui attend
simplement son formateur. Couvert par `apps/progression/tests/test_next_lesson.py`
(11 tests, validés par sabotage).

### Illustrations de leçon — une série, une grammaire

`frontend/src/assets/lessons/*.svg`, indexées par
`features/chapters/illustrations.js` (clé = **slug de la leçon en base**,
reprise telle quelle comme nom de fichier).

Même format 16/9, même fond dégradé clair, mêmes teintes de marque et
d'accent, et une composition en trois plans — un halo coloré, un objet
central, des signes flottants. Seuls le motif et la dominante changent, la
dominante suivant le chapitre :

| Leçon | Motif | État |
|---|---|---|
| `quest-ce-que-le-html` | Le document et ses balises, chevrons | ✅ |
| `structure-base-page-html` | L'imbrication : tête et corps, et l'arbre qu'ils forment | ✅ |
| `html-texte-titres-paragraphes` | La hiérarchie typographique, et l'échelle des titres | ✅ |
| `exercice-texte-titres-paragraphes` | L'éditeur et le panneau de tests | ✅ |
| *les 64 autres* | — | ❌ |

⚠️ **Le vert est réservé au type « exercice »** (le panneau de tests réussis).
C'est le seul écart de couleur de la série, et il ne dit pas le sujet mais le
type : il se repère au premier coup d'œil dans le parcours, même flouté. Les
illustrations d'exercice suivantes doivent le reprendre — et les autres s'en
abstenir.

Le parcours compte **68 leçons** : la table se remplit au fil des dessins, et
une leçon sans entrée s'affiche simplement sans illustration.

**Du SVG écrit à la main**, pas du PNG : net à toute taille (quelques centaines
de pixels en fond de carte, plus de mille en tête de leçon), quelques
kilo-octets, relisible en diff, aucune dépendance ni question de licence. Et
comme ce sont des ressources d'interface, elles vivent dans `src/assets/` —
donc hachées par Vite — et **non** dans `backend/media/`, qui n'est servi par
personne en production et dont le contenu doit être cité par une règle
d'`illustrations.py` (un fichier orphelin y fait rougir un test).

⚠️ **Aucun texte dans ces fichiers.** Une illustration posée en
`background-image` n'hérite d'aucune police du document : un `<text>` rendrait
n'importe quoi selon la machine. Tout est tracé en formes.

⚠️ **`--` est interdit dans un commentaire XML.** Citer une variable CSS avec
son préfixe dans le cartouche d'un SVG rend le fichier **entier** mal formé :
le navigateur n'affiche alors *rien*, sans le moindre message. C'est arrivé au
premier fichier de la série.

**Deux emplacements, un seul composant de style** :
`styles/components/_lesson-illustration.scss`. La classe `lesson-illustration`
s'ajoute à un bloc qui porte l'URL en variable (`--lesson-illus`) ; sans elle,
rien n'est dessiné.

| Emplacement | Réglages |
|---|---|
| Carte « Continuer l'apprentissage » | 85 %, masque 15→70 % (défauts) |
| En-tête de leçon (`.lesson-header`) | 55 %, masque 40→75 % |

Les réglages passent par des variables (`--illus-taille`, `--illus-flou`,
`--illus-opacite`, `--illus-depart`, `--illus-fin`) parce qu'ils dépendent des
proportions du bloc, pas de l'illustration. Trois d'entre eux tiennent
ensemble et se règlent **à l'œil**, jamais au raisonnement :

- **un dégradé de masquage** efface l'image du côté du texte — c'est ce qui
  rend l'idée tenable, il n'y a alors aucun contraste à défendre ;
- **une taille en pourcentage, pas `cover`** : dans un bloc très large et bas,
  une image 16/9 en `cover` se réduit à une bande centrale démesurément
  agrandie, où le motif n'est plus reconnaissable ;
- **un flou de 3 px** : au-delà de 5 px le motif n'est plus identifiable du
  tout. Réglé à 3 px après comparaison à l'écran — à 5 px le dessin se
  devinait à peine. C'est le **dégradé de masquage** qui protège la
  lisibilité du texte, pas le flou : l'image disparaît complètement du côté
  où l'on lit.
- **opacité réduite en thème sombre** (0,3 contre 0,7) : ces illustrations sont
  claires, elles éclairciraient le bloc.

Sous 768 px, l'illustration **disparaît** : un bloc étroit n'a pas de tiers
droit libre, et c'est une décoration — elle n'a rien à défendre.

⚠️ **En tête de leçon, la place du dessin est réservée par une marge**
(`padding-right: 32%`), pas déduite de la longueur du titre. « Structure de
base d'une page HTML » suffisait à traverser toute la largeur et à se poser
sur l'illustration. Le titre porte en plus `text-wrap: balance`, sans quoi la
réserve renvoyait le « ? » de « Qu'est-ce que le HTML ? » seul sur une
deuxième ligne.

Une leçon sans illustration n'a simplement pas la classe. ⚠️ Renommer un slug
de leçon la fait disparaître **en silence** — le repli est volontairement
discret, rien ne le signalera.

⚠️ **Un `max-width: 68ch` a été posé sur la description d'un chapitre**
(`.chapter-detail-header__description`) en chemin. Il ne sert plus
l'illustration — l'en-tête de chapitre n'en porte pas — mais il reste : la
description courait sur toute la largeur du conteneur, près de 140 caractères
par ligne, bien au-delà du confort de lecture.

### Le bandeau d'accueil parle de code, pas de cercles flottants

`DashboardHero` (`Dashboard.jsx`). L'ancien bandeau ouvrait sur « Bonjour X ! 👋 »,
une phrase figée identique pour tout le monde et tous les jours, et **trois
cercles translucides flottants** — le fond qu'on trouve sur n'importe quel
produit. Rien n'y disait qu'on est sur une plateforme d'apprentissage du code.

Ce qu'il porte désormais, et pourquoi :

| Élément | Raison |
|---|---|
| Date + **série de jours** (chasse fixe) | La série n'apparaît **nulle part ailleurs** sur cet écran ; les cinq cartes couvrent points, leçons, temps, score et trophées |
| « Bonsoir, **Prénom** » | Salutation selon l'heure, le prénom en gras : la salutation est la même pour tous, le prénom non |
| Une phrase d'**orientation** | « Vous reprenez Les bases du CSS, leçon 6 sur 17 » |
| **Trois fichiers ouverts** en fond | `script.js`, `style.css`, `index.html` — les trois premiers chapitres, en chasse fixe, onglet nommé et gouttière de numéros |

Quatre décisions, chacune couverte par un test validé par sabotage
(`Dashboard.test.jsx`) :

- **Aucun chiffre de progression.** Ils sont dans les cinq cartes juste en
  dessous. Les répéter en gros aurait reconstitué l'en-tête de tableau de bord
  générique qu'on remplaçait.
- **L'orientation est au chapitre, pas à la leçon.** La carte « Continuer
  l'apprentissage » dit quoi faire maintenant ; le bandeau dit où l'on se
  trouve. Le titre de la leçon deux fois à dix centimètres d'écart, c'est du
  doublon. ⚠️ Les trois absences de `next_lesson` gardent leurs trois phrases
  distinctes (terminé / en attente du formateur / rien de publié).
- **La série ne s'annonce qu'à partir de deux jours.** Un jour n'est pas encore
  une série ; l'afficher banaliserait le signal au moment où il commence à
  valoir quelque chose.
- **Le fond est décoratif et le reste** : `aria-hidden` sur le bloc entier — un
  lecteur d'écran qui énoncerait trente lignes de balisage avant d'atteindre
  « Bonsoir » rendrait la page inutilisable. Opacité 0,20, deux fondus
  (horizontal pour écarter le texte, vertical **par le bas seulement** : le
  haut porte les noms de fichiers, qui sont précisément ce qui fait lire
  « éditeur »). Les colonnes cèdent une à une, de la plus proche du texte à la
  plus lointaine (1560, 1320, 1080 px).

⚠️ Le contenu des trois fichiers **n'est pas du décor abstrait** : c'est le
code des premières leçons — la page squelette, une règle de style, un écouteur
de clic — et l'ordre des colonnes va du chapitre 3 au chapitre 1, de gauche à
droite, parce que le fondu efface la gauche : c'est donc le point de départ du
parcours qui se lit le plus nettement. Le reste se perd dans le fond.

`segmenter()` donne trois niveaux de blanc (balises et mots-clés, valeurs entre
guillemets, le reste). ⚠️ **Ce n'est pas une coloration syntaxique et il ne
faut pas la faire grandir vers ça** : le fond est illisible par construction, et
une vraie palette de couleurs derrière le titre deviendrait du bruit.

Le fond utilise `--banner-*`, comme le profil : il était en `--brand` →
`--brand-strong`, donc à **2,6:1** de contraste en thème sombre (cf. la section
sur les tokens de bandeau). L'entrée en fondu respecte
`prefers-reduced-motion` ; l'ancienne animation de flottement a disparu avec
les cercles.

### Le conseil du jour est calculé, plus écrit en dur

Le bloc affichait une phrase unique, la même pour tout le monde et tous les
jours. Un conseil qui ne regarde ni ce que vous avez fait ni où vous en êtes
n'est pas un conseil : on cesse de le lire au deuxième jour.

`features/dashboard/dailyTips.js` est un **module pur** — un contexte entre, un
conseil sort. Aucun appel réseau (tout est déjà chargé par le tableau de bord),
aucun accès au store, donc testable sans monter un composant.

- Chaque règle porte une **priorité** ; la plus prioritaire des règles
  applicables gagne. **L'urgence prime sur l'encouragement** : trois leçons
  laissées ouvertes se disent avant qu'on félicite une belle série.
- **À priorité égale, rotation selon le jour** — sinon le premier déclaré
  gagnerait pour toujours. La rotation est *déterministe* : un tirage au sort
  changerait le texte à chaque rendu de React, et la page semblerait clignoter.
- Un conseil dit **quoi faire ensuite, avec les chiffres de la personne**.
  « Bravo, continuez » n'aide personne.
- Un **filet de conseils toujours applicables** garantit qu'il y a toujours
  quelque chose à afficher, et une règle qui trébuche sur un contexte partiel
  s'efface au lieu de casser la page.

⚠️ **`streak.active_today` ne sert à rien comme signal ici.** Le tableau de
bord appelle `syncGamification()` à son montage, qui appelle `touch_streak` :
**ouvrir la page suffit à rendre le drapeau vrai**. Les règles s'appuient donc
sur la longueur de la série et sur le record, jamais sur « a été actif
aujourd'hui ». Même piège pour toute règle future.

Ajouter un conseil : une entrée dans `TIP_RULES` (`id` unique, `priorite`,
`quand`, `texte`, `lien` optionnel). Les tests vérifient l'unicité des `id`,
qu'aucune règle ne lève sur un contexte brut, et qu'aucun conseil général
n'est inatteignable dans la rotation.

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

Le choix d'avatar se fait par `Profile.avatar_key`, une clé `<visage>-<palette>`
prise dans une liste close (`apps/accounts/avatars.py`, 42 × 6 = 252
combinaisons), et le rendu se fait en SVG côté client. **Aucun téléversement
d'image** : un ancien champ `Profile.avatar` (`ImageField`) jamais alimenté a
été supprimé (migration `0007`) après vérification qu'aucune base ne le
renseignait. Il n'y a **plus aucun `ImageField` dans le projet**, et `Pillow` —
sa seule raison d'être — a été retiré de `requirements/base.txt`. Ne pas le
réintroduire sans réintroduire d'abord un vrai besoin d'image serveur.

Le raisonnement, à ne pas défaire à la légère : sur une plateforme scolaire
sans outil de modération, un téléversement libre signifie que n'importe quelle
image peut apparaître à côté d'un nom dans le tableau de bord du formateur, et
que personne ne dispose du moyen de la retirer. S'y ajoutent la liste blanche
de formats (un SVG téléversé est un vecteur de XSS), les bombes de
décompression et un stockage à sauvegarder. Le catalogue supprime tout cela.

Le repli — initiales sur une couleur **dérivée du nom**, donc stable d'une
session à l'autre — est l'état par défaut de tout compte, pas un pis-aller.

#### Des visages illustrés, depuis le 2026-08-06

Le catalogue était auparavant **volontairement abstrait** (orbit, prism, wave,
bloom, spark, mesh) : des formes plutôt que des personnages, pour ne pas avoir
à arbitrer des représentations — teintes de peau, genres, cultures — qu'une
poignée de dessins ne peut pas rendre justement.

Ce parti a été levé au profit de visages illustrés, plus conformes à l'attente
d'un avatar de profil. L'objection d'origine tient toujours ; elle est traitée
par le volume : chaque graine combine coiffure, traits, teint et accessoires.
Migration `0008` : les anciennes clés ont été remises à vide (retour aux
initiales), car elles sont désormais **refusées en écriture** — les laisser
aurait fait échouer l'enregistrement d'un profil sur un champ que l'apprenant
n'a pas touché.

#### Sept familles, depuis le 2026-08-07

Le catalogue s'est d'abord limité au seul style **Notionists**, jugé peu
attrayant à l'usage. Il en compte désormais **sept, de six visages chacune** :

| Famille | Auteur | Licence |
|---|---|---|
| Notionists | Zoish | CC0 1.0 |
| Adventurer, Adventurer Neutral | Lisa Wischofsky | **CC BY 4.0** |
| Avataaars | Pablo Stanley | libre, usage personnel et commercial |
| Big Smile | Ashley Seo | **CC BY 4.0** |
| Bottts | Pablo Stanley | libre, usage personnel et commercial |
| ToonHead | Johan Melin | **CC BY 4.0** |

⚠️ **Quatre familles sont en CC BY 4.0 : l'attribution est une obligation, pas
une politesse.** Elle est portée à deux endroits, et il faut les deux — sous
chaque famille du sélecteur (là où l'œuvre est utilisée) et dans les mentions
légales, page publique (là où on la retrouve). Un test front rougit si le
crédit disparaît du sélecteur ; **rien ne surveille la page légale**, il faut y
penser à la main en ajoutant une famille.

`frontend/src/features/profile/avatarCatalog.js` est la **source unique** :
familles, graines, réglages de cadrage et crédits. Il est volontairement
**dépourvu d'imports**, pour que le script de génération — qui tourne sous Node
et ne sait pas charger un `.svg` — lise le même fichier. Sans lui, la liste
aurait été recopiée trois fois.

⚠️ Un identifiant de visage **ne peut pas contenir de tiret** : `parseAvatarKey`
découpe la clé dessus. D'où `adventurerneutral1`, et non `adventurer-neutral-1`.
Verrouillé des deux côtés par un test.

⚠️ **Les visages sont pré-générés à la construction**, pas à l'exécution, et
**jamais** servis par l'API HTTP de DiceBear. Un appel distant enverrait l'IP de
chaque apprenant à un tiers à chaque affichage de page — et ferait tomber la
raison même pour laquelle l'application n'a pas de bannière de consentement
(cf. « Pages légales et cookies »). Ne pas « simplifier » en pointant une URL.

```bash
npm run avatars   # scripts/generate-avatars.mjs → src/assets/avatars/*.svg
```

Les 42 SVG produits (273 ko) sont **versionnés** : la construction ne dépend
donc pas de DiceBear, qui est en `devDependencies`. Relancer la commande après
toute modification d'`avatarCatalog.js` — le test front « sait dessiner chaque
clé du catalogue » rougit si un visage manque, et le script **supprime** les
fichiers d'un visage retiré du catalogue.

Le script **confronte les crédits déclarés à `collection[style].meta`** et
échoue en cas d'écart. Ce n'est pas un luxe : une mise à jour de DiceBear
pourrait changer un auteur ou une licence sans que rien ne le signale, et
l'application afficherait alors une attribution fausse — pire que pas
d'attribution.

⚠️ **Les réglages de cadrage (`options.scale`) se jugent à l'œil, jamais au
calcul.** Chaque style dessine son sujet à sa propre échelle, et la vignette a
des coins arrondis qui rognent. Constaté sur les deux familles concernées :
Adventurer Neutral ne dessine que les traits — ni crâne, ni buste — et sortait
la bouche par le bas (ramené à 62) ; Big Smile débordait par le haut sur les
coiffures volumineuses (ramené à 78).

⚠️ **Ne pas réintroduire `@dicebear/core` dans le code d'exécution.** Le
catalogue est fermé : quarante-deux visages connus d'avance. Embarquer le
générateur pour les recalculer à chaque affichage ajoutait **~380 ko au morceau
d'entrée** — `Avatar` est tiré par le `Header`, donc structurel et jamais
différé — faisant passer le bundle de 261 ko à 640 ko et refranchir le seuil
d'alerte de Vite.

⚠️ **Piège voisin, rencontré en passant à 42 visages : `assetsInlineLimit`.**
Vite intègre en base64 tout asset de moins de 4 ko. Douze visages passaient
sous le seuil et atterrissaient **dans le morceau d'entrée** : +58 ko bruts,
+13 ko gzip, téléchargés par chaque visiteur pour douze visages qu'il ne verra
jamais. `vite.config.js` exclut donc `assets/avatars/` de l'intégration.
Mesuré : entrée à 319 ko avant, **267 ko après**. (Le suffixe `?no-inline`,
qui dirait la même chose au point d'usage, n'existe qu'à partir de Vite 6.)

Le visage est posé en `<image href="…">` par-dessus le dégradé de palette, et
non injecté en balisage : un SVG référencé par `<image>` est rendu en mode
image, sans script — donc aucun `dangerouslySetInnerHTML` à surveiller.

⚠️ Les listes `VISAGES` / `PALETTES` sont **dupliquées** entre
`backend/apps/accounts/avatars.py` (autorité) et
`frontend/src/features/profile/avatarCatalog.js` (rendu). En modifier une seule
donne soit un avatar vide, soit un choix refusé à l'enregistrement. Un test
front vérifie que chaque clé sait se dessiner.

⚠️ Chaque valeur de `VISAGES` est **par défaut** la graine DiceBear, et c'est
ce qui est stocké en base : la renommer invalide la clé enregistrée de tous
ceux qui l'avaient choisie. Ajouter, oui ; renommer, non.

**Pour remplacer un visage jugé raté, ne pas le renommer** : déclarer une
graine dans le `graines` de sa famille (`graines: { avataaars2: 'maya' }`).
L'identifiant — donc la clé en base — ne bouge pas, seul le dessin change.
C'est le seul moyen de corriger un choix esthétique sans reverser aux
initiales ceux qui avaient choisi ce visage. `avataaars2` a été échangé ainsi.

#### Le bandeau du profil dit qui est la personne, pas ce qu'elle a marqué

`ProfileHero` (`ProfilePage.jsx`) présente le nom, le pseudo, le rôle, la
classe et la **bio**. Il ne porte **aucun chiffre**, et c'est délibéré : points,
niveau, série et trophées sont dans la carte « Ma progression », juste
en dessous. Les remonter en gros dans le bandeau aurait donné l'en-tête de
tableau de bord qu'on voit partout, et relégué la seule chose que l'apprenant
écrit lui-même — sa bio — au rang de sous-titre.

Trois décisions à ne pas défaire :

- **Le pseudo est `github_username`**, le seul identifiant pseudonyme que le
  profil enregistre. Il est rendu en **chasse fixe** (`--font-mono`) et mène au
  compte GitHub. C'est le seul écart typographique du bandeau. ⚠️ Si un vrai
  champ « pseudo » indépendant est voulu un jour, c'est un ajout au modèle, une
  migration et une entrée dans `EDITABLE_PROFILE_FIELDS`.
- **L'accent coloré vient de l'avatar choisi** : `--hero-accent` est posée en
  ligne depuis la palette d'`avatar_key` (repli sur la couleur dérivée du nom,
  celle de l'avatar à initiales). Anneau, lueur et filet de pied la reprennent.
  ⚠️ Elle ne touche **que du décor** — ces six palettes sont claires, sous du
  texte blanc elles ne tiendraient pas le contraste.
- **La bio vide invite au lieu de constater** : « Ajoutez une phrase pour vous
  présenter », pas « Aucune bio ».

⚠️ **`profile.cohort_name` n'était pas sérialisé.** Le composant l'affichait
depuis toujours, `ProfileSerializer` ne le produisait pas : la ligne était
morte, aucun apprenant n'a jamais vu sa classe sur cette page. Le champ est
maintenant exposé **en lecture seule** — le rattachement à une classe passe par
une invitation ou par `assign_cohort` (audité), jamais par un formulaire de
profil. Trois tests le verrouillent, dont celui du « pas d'écriture ».

⚠️ **Piège de refonte, rencontré ici :** un bloc `@media` **antérieur** stylait
encore `.profile__hero` comme conteneur flex (`flex-direction: column;
text-align: center`). La disposition ayant déménagé sur `.profile__hero-inner`,
il ne restait qu'un `text-align: center` orphelin — invisible au bureau, il
centrait tout le bandeau sous 640 px, bio de cinq lignes comprise. **Quand on
déplace la mise en page d'un élément vers un enfant, relire ses media queries.**

#### Le sélecteur : replié, puis en deux temps

Le catalogue **ne s'affiche qu'à la demande**, derrière un bouton « Changer
d'avatar » (`aria-expanded` / `aria-controls`), à côté de l'avatar courant.
Déplié d'emblée, il repoussait hors de vue tout le reste du profil — nom, mot
de passe, retrait du classement — alors qu'on ne change d'avatar qu'une fois.

Une fois ouvert, le choix se fait **en deux temps**. 252 combinaisons à plat
donneraient une planche illisible où chaque visage reviendrait six fois :
`AvatarPicker` présente les visages **groupés par famille** (crédit sous le
titre), puis une rangée de palettes appliquée au visage retenu — quarante-huit
boutons au lieu de deux cent cinquante-deux, et la palette redevient un
réglage plutôt qu'une variante.

La rangée de palettes **n'apparaît pas** tant qu'aucun visage n'est choisi :
sur le repli à initiales, la couleur vient du nom, et des palettes sans effet
se liraient comme une panne.

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

## Comptes de démonstration — jamais en production

`create_demo_users` crée un formateur et trois apprenants dont les mots de
passe (`trainer123`, `learner123`) sont écrits dans le dépôt et repris dans
plusieurs fichiers de documentation. Rien n'empêchait de lancer cette commande
sur une instance réelle : recopier la ligne d'amorçage de
`frontend/e2e/README.md` sur le serveur suffisait à ouvrir, à quiconque lit le
dépôt, un compte formateur — qui voit la progression de ses apprenants,
débloque des chapitres et consulte sa classe.

La commande **refuse maintenant de s'exécuter** quand
`settings.ENVIRONMENT == 'production'`, et oriente vers `createsuperuser`.

⚠️ Le contrôle porte sur `ENVIRONMENT`, **pas sur `DEBUG`** : le lanceur de
tests de Django force `DEBUG = False`, ce qui aurait rendu le comportement
intestable, alors qu'`ENVIRONMENT` est la variable qui sélectionne réellement
les réglages de production (`config/settings/__init__.py`).

`purge_test_accounts` fait le ménage sur une base existante : il recense par
défaut, ne supprime qu'avec `--apply`. Deux règles :

- **Suppression, pas anonymisation** — l'inverse du choix fait pour un
  apprenant réel. L'anonymisation préserve des statistiques de classe qui ont
  un sens ; ici les comptes ne désignent personne et leur progression est du
  bruit qui fausserait les taux de complétion.
- **Jamais un administrateur**, même à adresse de test (`trainer@test.com` a
  été promu ADMIN à la main en développement). Le supprimer alors qu'il serait
  le seul rendrait l'instance impilotable — même logique que le garde-fou
  « dernier administrateur actif ».

Une adresse en `e2e-` que le motif ne reconnaît pas est **signalée et
conservée** : l'écarter en silence serait le pire des deux mondes.

## Sauvegardes

`scripts/backup_db.sh` (dump + rotation) et `scripts/restore_db.sh`
(restauration, avec confirmation par saisie du nom de la base).

**Seule la base PostgreSQL est sauvegardée**, et c'est un choix : les
illustrations sont versionnées dans le dépôt, le contenu pédagogique vit dans
le code (`load_course_content` le reconstruit à l'identique), Redis ne porte
que du cache et une file Celery. Ce qui n'existe qu'en base — comptes,
progression, grand livre de points, badges, classes, journal d'audit — est
exactement le périmètre du dump.

Deux garde-fous contre la **fausse sauvegarde**, celle qui existe mais ne
restaure rien :

- écriture sous `.partiel` puis renommage — un fichier au nom définitif est un
  fichier complet ; sans cela une coupure laisse une archive tronquée qui
  *ressemble* à une sauvegarde ;
- échec si le dump fait moins de 10 Ko — signature d'une base vide ou d'une
  authentification refusée en silence.

⚠️ `pg_dump --clean --if-exists` et `psql -v ON_ERROR_STOP=1` ne sont pas
décoratifs : sans le premier, la restauration sur une base peuplée échoue sur
les objets existants et la laisse à moitié écrasée ; sans le second, `psql`
poursuit après une erreur et **signale un succès** sur une base partiellement
restaurée.

Le cycle a été rejoué en conditions réelles (sauvegarde, restauration dans une
base jetable, comparaison table par table : zéro écart). À refaire après tout
changement de schéma important — une sauvegarde jamais restaurée n'est pas une
sauvegarde.

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

⚠️ **`Quiz` avait exactement le même bug, non corrigé jusqu'ici.**
`Quiz.total_points` et `question_count` itéraient `self.questions` sur la forme
`{'questions': [...]}` (celle des commandes `load_section_*`) → `AttributeError`
à la **sérialisation de toute leçon QUIZ** (les propriétés sont des
`ReadOnlyField`). Corrigé de la même façon : `Quiz.questions_list` normalise, et
`QuizSerializer.to_representation` **renvoie toujours une liste** (le front fait
`Array.isArray(quiz.questions)` — un dictionnaire brut afficherait « aucune
question »). Le scoring de `apps/progression/views.py` normalisait déjà de son
côté. Couvert par des tests en **forme enveloppée** dans `apps/courses/tests/`
(l'ancien test utilisait la forme liste et passait donc à côté). **Même règle :
tout lecteur des questions passe par `questions_list`.**

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
`ROLE_LABELS`) — miroir de `User.Role` côté Django.

Même principe pour les **types d'activité** : `src/constants/activity.js`
(`ACTIVITY_TYPES`, `ACTIVITY_META`, `describeActivity`) est le miroir de
`ActivityLog.ActivityType`. Le tableau était auparavant recopié dans trois
écrans, et les trois avaient divergé — `ProgressionPage` ignorait
`LESSON_STARTED` et affichait la clé brute sans icône, tandis que
`LearnerDetail` et `RecentActivity` fabriquaient leur libellé avec
`activity_type.replace('_', ' ').toLowerCase()`, soit « lesson started » en
anglais dans une interface française. `describeActivity` garantit qu'aucune
clé technique n'atteint l'écran, y compris pour un type inconnu.
⚠️ Ajouter une valeur à `ActivityType` côté Django impose d'ajouter une entrée
ici ; un test compare les deux listes. Le header filtre ses liens
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

⚠️ **Qui positionne `initialized` (et `user`) — piège de la connexion.**
`initialized` et `user` ne sont peuplés que par `fetchCurrentUser`,
`register.fulfilled` ou `logoutUser.fulfilled`. **`login.fulfilled` ne les
touche pas** : l'endpoint `/login` (SimpleJWT) ne renvoie que les jetons, pas le
profil. Le thunk `login` **doit donc enchaîner `dispatch(fetchCurrentUser())`
et l'attendre** avant de rendre la main. Sans cela, `PrivateRoute` reste bloqué
à l'infini sur `hasToken && !initialized`, et seul un rafraîchissement (qui
redéclenche `fetchCurrentUser` au montage de `App`) débloque — c'était le bug
« connexion qui charge sans fin » : la session s'ouvrait bien (jetons stockés),
mais l'écran restait en chargement jusqu'au reload.

⚠️ **Corollaire pour les tests E2E** : asserter seulement l'URL `/dashboard`
**ne suffit pas** — pendant ce bug, l'URL passait à `/dashboard` un instant
avant de rebondir, et une assertion d'URL pouvait donc passer à tort. Vérifier
un élément de l'en-tête authentifié (`.header__user-button`, rendu par `Layout`
seulement quand `user` est chargé) — voir `e2e/helpers.expectAuthenticatedDashboard`.

### Routage : la page 404 et les redirections

⚠️ **`<Routes>` n'avait aucune route `*`.** Une adresse inconnue ne rendait
**rien** : page blanche, sans erreur ni message. C'est le pire des cas — on la
lit comme une panne du site alors qu'il s'agit presque toujours d'une faute de
frappe. `features/errors/NotFound.jsx` la remplit, et affiche **le chemin
demandé** en chasse fixe : c'est la seule information qui permet à quelqu'un de
repérer sa propre coquille.

Le tour complet des redirections, telles qu'elles sont aujourd'hui :

| Situation | Où l'on atterrit | Qui décide |
|---|---|---|
| `/` | `/dashboard` | `App.jsx` — puis `PrivateRoute` tranche la session |
| Adresse inconnue | page 404 | `App.jsx`, route `*` |
| Lien profond (`/chapters/html` tapé directement) | la SPA | `try_files … /index.html`, `frontend/nginx.conf` |
| Route privée sans session | `/login` | `PrivateRoute` |
| Rôle insuffisant | `/dashboard` | `PrivateRoute` |
| Session expirée en cours d'usage | `/login` | intercepteur axios |
| `/login` ou `/register` **déjà connecté** | `?next=`, sinon `/dashboard` | `PublicOnlyRoute` |

Trois décisions à ne pas défaire :

- **La racine ne regarde pas la session.** `PrivateRoute` est le seul endroit
  qui tranche l'authentification ; dupliquer la décision créerait un second
  chemin, qui oublierait `initialized`.
- **`PublicOnlyRoute` n'attend *pas* `initialized`, contrairement à
  `PrivateRoute`.** Les deux gardes sont asymétriques parce que leurs
  décisions le sont : `PrivateRoute` prononce un **refus**, il doit donc
  attendre de savoir qui est là ; `PublicOnlyRoute` ne redirige que sur une
  **présence** d'utilisateur. Attendre y aurait posé un écran de chargement sur
  la page de connexion de quiconque traîne un jeton périmé — la famille de
  symptômes « la connexion charge sans fin » déjà payée une fois. Avec un jeton
  mort, le formulaire s'affiche : c'est le bon comportement.
- **`PublicOnlyRoute` respecte `?next=`** (via `safeRedirectPath`). Sans cela,
  quelqu'un de déjà connecté suivant un lien d'invitation repartirait au
  tableau de bord **sans jamais être rattaché à la classe**, et rien ne le lui
  dirait.

⚠️ Le test qui compte n'est pas celui qui monte `<NotFound />` — c'est celui
qui monte **`<App />`** sur une adresse inconnue. Le bug d'origine n'était pas
un composant manquant mais une route manquante ; seul le second rougit si la
route `*` disparaît.

⚠️ **`window.matchMedia` est bouché dans `src/test/setup.js`.** jsdom ne
l'implémente pas du tout, et tout test qui monte `Layout` → `Header` →
`ThemeProvider` levait « matchMedia is not a function » au montage, avant la
première assertion. Aucun test ne montait le thème jusqu'à la page 404.

### Une erreur de rendu ne laisse plus un écran blanc

⚠️ Il n'existait **aucune frontière d'erreur**. Une seule exception pendant le
rendu démontait tout l'arbre React : ni message, ni sortie, indistinguable
d'une panne réseau ou d'une page qui n'a pas fini de charger.

`components/ui/ErrorBoundary.jsx` est montée **deux fois**, et c'est voulu :

| Où | Ce qu'elle couvre |
|---|---|
| Dans `Layout`, autour de `{children}` | une page qui casse — **l'en-tête et le pied restent**, donc la navigation |
| Dans `App`, autour de `<Routes>` | les pages publiques (hors `Layout`), et le cas où `Layout` casserait |

React s'arrête toujours à la frontière la plus proche ; l'imbrication fait donc
exactement ce qu'on veut, et un test le vérifie.

⚠️ **Une frontière ne se réarme pas toute seule.** Sans la clé sur
`location.pathname`, cliquer « Retour au tableau de bord » changerait l'URL et
laisserait le même message à l'écran — une sortie qui ne sort de rien. Vérifié
par sabotage : retirer la clé fait rougir le test dédié.

⚠️ Ce qu'elle **n'attrape pas**, et qu'il ne faut pas croire couvert : les
erreurs asynchrones (promesses, `setTimeout`, gestionnaires d'événements) et
le rendu serveur. Elle ne voit que le rendu et les cycles de vie de ses
descendants. Les échecs d'appels réseau restent gérés par les thunks Redux.

Le détail technique n'apparaît qu'en développement (`import.meta.env.DEV`) :
en production il n'apprendrait rien à un apprenant et exposerait des noms de
composants internes.

### Décision actée : stockage des jetons

Rester en `localStorage`. Migrer vers des cookies `httpOnly` impliquerait de
refaire l'intercepteur axios, CORS et la protection CSRF pour un gain réel
seulement en cas de XSS par ailleurs. Réduire `ACCESS_TOKEN_LIFETIME` couvre
l'essentiel du risque pour une ligne.

### L'intercepteur axios distingue identifiants refusés et session expirée

`services/api/apiService.js` rafraîchit le jeton et rejoue la requête sur un
401 — comportement correct pour un jeton d'accès expiré. Mais il l'appliquait à
**tous** les 401, y compris celui d'un `POST /auth/login/` avec un mauvais mot
de passe. Déconnecté, il n'y a pas de refresh token : l'intercepteur basculait
alors sur `window.location.href = '/login'`, un **rechargement complet qui
effaçait le message d'erreur Redux** avant tout affichage. Symptôme : se
tromper de mot de passe faisait « clignoter » la page sans rien expliquer.

La correction est une liste d'exceptions (`isAuthEndpoint`) : sur `/auth/login/`,
`/auth/token/refresh/` et `/auth/register/`, un 401 est une **réponse métier**
(« identifiants refusés »), pas un signal d'expiration — l'intercepteur laisse
donc l'erreur remonter à l'appelant. Verrouillé à deux niveaux :
`apiService.test.js` (le prédicat, en CI) et deux tests Playwright de login raté
qui exigent l'affichage du `role="alert"`.

⚠️ Toute nouvelle route où un 401 est une réponse normale (et non « votre
session a expiré ») doit être ajoutée à `AUTH_ENDPOINTS`.

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

## Reste à faire — audit du 2026-08-04

Inventaire vérifié dans le code, pas recopié du roadmap. Classé par risque,
pas par visibilité.

### Risque réel

*Vide.* Les entrées qui s'y trouvaient sont faites : throttle de connexion,
tests de `courses`, comptes de démonstration à mot de passe public (voir
« Comptes de démonstration — jamais en production ») et absence de sauvegardes
(voir « Sauvegardes »).

### Dette structurelle

*Vide.* Contrat des services API, découpage de bundle, champ mort
`Profile.avatar`, et les **17 scripts hors commande à la racine de `backend/`**
(voir « Contenu des cours — architecture ») : tout est traité. `backend/` ne
contient plus que `manage.py`.

### Mise en production — le chantier actif

Le code est prêt et **éprouvé par une répétition locale complète** (pile de
production + Traefik, dix contrôles d'ouverture). Ne restent que les étapes qui
demandent le serveur : DNS, `.env` avec les secrets, SMTP, `ufw`, cron des
sauvegardes, et l'externalisation des archives hors du VPS.

⚠️ **Point d'entrée : [`06_ROADMAP_DEPLOIEMENT.md`](06_ROADMAP_DEPLOIEMENT.md).**
Il contient l'état détaillé de chaque tâche, la procédure de mise en service,
les contrôles d'ouverture, et la confrontation de `guide-hebergement-ovh.md` au
code réel — quatre de ses hypothèses sont fausses pour ce dépôt.

Décision **révisée** le 2026-08-04 : l'exécution de code est **activée**
(`CODE_EXECUTION_ENABLED=True` dans `.env.production.example`). Elle devait
d'abord rester coupée, l'hôte étant partagé avec d'autres projets ; deux
barrières l'ont rendue acceptable — un mandataire de socket limité aux routes
du bac à sable, et un conteneur d'exécution durci. Voir « Le drapeau
`CODE_EXECUTION_ENABLED` » et « Le bac à sable sur un hôte mutualisé », y
compris ce que ces barrières **ne** protègent pas.

### Fonctionnalités jamais commencées

- **WebSocket / temps réel** — `asgi.py` a un routeur vide et
  `channels/consumers/` est un dossier vide. Rien n'en dépend ; le service
  `daphne` a d'ailleurs été retiré de la compose de production.
- **Soumission et correction de projets** — le modèle `Project` existe dans
  `courses`, mais aucun modèle de soumission nulle part.
- **Forum** — l'app n'existe pas, ni dans `INSTALLED_APPS` ni sur le disque.
- **CI qui construit les images** — elle n'en construit aucune.
- **Chapitre 3 JavaScript en version d'auteur** — il n'a pas de
  `load_section_3` d'origine, seulement le contenu promu en commande.
- **Illustrations en double résolution** — elles s'adoucissent en plein écran.

### Ce qui vient d'être fait (session du 2026-08-06)

Treize commits, sur la branche `chore/fusion-monpc-design`, **non poussés**.

- [x] **Classement** des apprenants, avec retrait volontaire — la dernière
      fonctionnalité produit jamais commencée qui restait bon marché
- [x] Re-suppression des **18 fichiers vestiges** de `backend/`, ressuscités
      par la fusion des copies OneDrive
- [x] Tableau de bord : **avancement réel** (le pourcentage ne mesurait pas ce
      qu'il annonçait) et **conseil du jour contextuel** (16 règles)
- [x] « Continuer l'apprentissage » suit l'**ordre du parcours** et respecte le
      verrou de chapitre — il proposait « mettre son site en ligne » sur un
      compte vierge, et une leçon sur deux menait à un 403
- [x] Grille du tableau de bord réorganisée en trois colonnes, conseil du jour
      habillé
- [x] **4 illustrations de leçon** et leur intégration (fond de carte, en-tête
      de leçon), composant de style partagé
- [x] Outillage éditeur : `.devcontainer/` et venv local en Python 3.11

### Session du 2026-08-04

- [x] Contenu des cours restauré et réorganisé — 27 → **68 leçons**, 17 scripts
      supprimés, une commande par chapitre, illustrations rattachées au
      chargement
- [x] Illustrations versionnées (31 PNG) et régénérables
- [x] Validation d'une leçon **constatée** au défilement, plus déclarée par un
      bouton
- [x] Table des types d'activité centralisée (`constants/activity.js`)
- [x] Visionneuse d'images : agrandissement réel et zone cliquable exacte
- [x] Pile de production complète, éprouvée en répétition locale
- [x] Garde-fou des comptes de démonstration + `purge_test_accounts`
- [x] Sauvegardes : script, rotation, **restauration testée** (zéro écart)
- [x] Logo et favicon intégrés

## Intégration continue

`.github/workflows/ci.yml`, sur `push` vers `main` et sur chaque *pull
request*. Deux jobs indépendants qui échouent séparément.

**Backend** — PostgreSQL 15 et Redis 7 en services, puis :

| Étape | Ce qu'elle attrape |
|---|---|
| `makemigrations --check --dry-run` | Un modèle modifié sans migration |
| `migrate` sur base vierge | Une migration qui ne s'applique pas dans l'ordre |
| `manage.py check` | Erreurs de configuration |
| `pytest --create-db` | Les 328 tests |

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

# Tests bout-en-bout (Playwright) — tranche mince, en local (cf. frontend/e2e/)
npm run e2e          # toute la suite, headless (stack docker-compose requise)
npm run e2e:ui       # mode interactif
npx playwright test e2e/auth.spec.js   # un fichier
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

### L'éditeur a besoin d'un interpréteur, et c'est la seule exception

Corollaire de « Docker pour tout » : longtemps, **aucun Python n'existait sur
le poste**. L'extension Python de VS Code affichait « An invalid Python
interpreter is selected » — `.vscode/settings.json` désignait
`backend/venv/Scripts/python.exe`, un chemin jamais créé — et Django, DRF et
pytest ressortaient introuvables : ni auto-complétion, ni aller-à-la-définition,
ni tests lançables depuis l'éditeur.

Deux réponses, complémentaires plutôt que concurrentes :

| | Pour quoi |
|---|---|
| **`.devcontainer/`** | La référence. F1 → « Dev Containers: Reopen in Container » : l'éditeur voit **exactement** l'interpréteur et les versions de la CI. |
| **`backend/venv`** (Python 3.11) | Le dépannage : l'éditeur reste utile Docker éteint. Ignoré par git. |

⚠️ **Le venv doit être en 3.11, comme le conteneur.** Les versions épinglées
(`psycopg2-binary==2.9.9`, `Pillow==10.2.0`) n'ont **pas de roues** pour un
Python plus récent : créé avec le 3.13 du PATH, l'installation échoue.

```bash
py -3.11 -m venv venv                                       # depuis backend/
venv\Scripts\python.exe -m pip install -r requirements\development.txt
```

⚠️ **Lancer les tests depuis l'éditeur demande une redirection réseau.**
`backend/.env` désigne les services par leur nom sur le réseau Docker
(`DB_HOST=postgres`), qui ne résout pas depuis le poste ; `.vscode/pytest.env`
les remplace par `localhost`, où la pile publie les mêmes ports.
**`docker compose exec backend pytest` reste la référence** — c'est ce que fait
la CI, et le seul environnement où les tests marqués `docker` s'exécutent.

⚠️ `.vscode/` est **ignoré par git** : ces réglages ne voyagent pas avec le
dépôt, seul `.devcontainer/` est versionné. Les recréer après un clone.

Deux points d'attention dans `.devcontainer/` :

- `compose.devcontainer.yml` n'ajoute qu'**un montage**, le dépôt entier sur
  `/workspace` — sans lui, la fenêtre ne verrait que `backend/` (seul dossier
  monté par la pile) et perdrait le frontend et la documentation. ⚠️ Son chemin
  relatif est résolu depuis le **répertoire du projet**, pas depuis le fichier :
  écrire `..` y montait tout le dossier parent, projets voisins compris. À
  vérifier d'un `docker compose -f docker-compose.yml -f
  .devcontainer/compose.devcontainer.yml config`.
- `"shutdownAction": "none"` : fermer VS Code ne doit pas couper Postgres,
  Redis et Celery, qui servent aussi le `npm run dev` lancé à côté.

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
- Styling : **design system SCSS maison uniquement**, aucun framework CSS
  (voir « Tailwind a été retiré » plus bas)

⚠️ Deux éléments listés ici auparavant n'existent toujours pas : `wsService.js`
et `useAutosave` / `useWebSocket` (cf. « WebSocket — RIEN N'EXISTE »). Le
découpage par `React.lazy`, lui, **est fait** — voir ci-dessous.

### Découpage de bundle (`React.lazy`) — ✅ Fait

`App.jsx` chargeait tout statiquement : un bundle d'entrée d'un seul tenant
(~549 kB / 168 kB gzip). Chaque page de route est désormais un `lazy(() =>
import(...))`, et `<Routes>` est enveloppé d'un `<Suspense>` unique dont le
repli est `components/ui/PageLoader` (réutilise `.route-guard` +
`.loading-spinner`, comme la garde de route — pas de troisième style d'attente).

Résultat : **bundle d'entrée ramené à ~261 kB / 87 kB gzip** (−52 %), chaque
route sortie dans son propre morceau, chargé à la demande. Le seuil d'alerte
Vite des 500 kB n'est plus franchi.

Restent **structurels et donc chargés d'emblée** : `PrivateRoute`, `Layout`,
`PageLoader`, le hook `useThemePreferenceSync`, les constantes de rôles.

⚠️ **Double découpage pour Monaco.** L'éditeur (`@monaco-editor/react`, la plus
lourde dépendance) est tiré par `LessonView → ExerciseInterface`. `ExerciseInterface`
est donc **lui-même** en `lazy` *à l'intérieur* de `LessonView` (avec son propre
`Suspense`) : ouvrir une leçon de théorie ou un quiz ne télécharge pas Monaco —
seule une leçon de type EXERCICE le fait. Ne pas réintroduire un import statique
d'`ExerciseInterface` dans `LessonView`, cela réunirait les deux morceaux.

Toute nouvelle page doit suivre le même moule : `lazy()` dans `App.jsx`, jamais
un import statique de page.

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

Le conteneur s'exécutait autrefois en `root`, sans capacité retirée et avec un
système de fichiers inscriptible. C'est corrigé — voir « Le bac à sable sur un
hôte mutualisé » ci-dessous.

⚠️ **Défaut corrigé au passage : la branche Python ne produisait aucune sortie.**
`_create_validation_script` concaténait le code de l'apprenant et les
`assert`, **sans rien imprimer** : le conteneur sortait sans JSON et
`run_code` échouait invariablement sur « Erreur lors du parsing des
résultats ». Le défaut est resté invisible parce qu'aucun exercice n'utilise ce
langage — les 25 existants sont en HTML ou en JavaScript. Il aurait accueilli
le premier exercice Python écrit.

### Le bac à sable sur un hôte mutualisé

Le VPS héberge d'autres projets. Deux barrières ont donc été posées pour que
l'exécution de code reste activable sans les exposer.

**1. Le worker n'a plus la socket Docker.** Il parle à un mandataire
(`tecnativa/docker-socket-proxy`, service `docker-proxy` de
`docker-compose.prod.yml`) placé sur un réseau `internal: true` que lui seul
atteint. Mesuré en conditions réelles :

| Appel | Résultat |
|---|---|
| Créer, démarrer, attendre, lire, supprimer un conteneur | autorisé (le bac à sable en a besoin) |
| Inspecter une image | autorisé |
| **`exec` dans un autre conteneur** | **refusé** |
| **Lister volumes / réseaux** | **refusé (403)** |
| **`info` système** (chemins de l'hôte) | **refusé (403)** |
| **Construire une image** | **refusé (403)** |

**2. Le conteneur d'exécution est durci.** Chaque réglage retire un moyen
d'évasion, et chacun est verrouillé par un test sur les arguments passés à
Docker — lancer un vrai conteneur ne dirait pas si l'un a disparu d'un appel :

| Réglage | Ce qu'il retire |
|---|---|
| `user='65534:65534'` | le code ne s'exécute plus en `root` |
| `cap_drop=['ALL']` | toutes les capacités Linux, jusqu'à `CAP_SETUID` |
| `no-new-privileges` | l'élévation par binaire setuid |
| `read_only=True` | l'écriture hors `/tmp` |
| `tmpfs` `noexec,size=16m` | déposer puis exécuter un binaire |
| `pids_limit=64` | la bombe à fork |
| `network_disabled=True` | toute sortie — **y compris vers le mandataire** |

⚠️ **Ce que cela ne protège pas, et il faut le savoir.** Le mandataire filtre
par **route**, pas par contenu de requête : `CONTAINERS=1` autorise donc encore
la création d'un conteneur privilégié montant `/`. Quelqu'un qui obtiendrait
l'exécution de code **dans le worker** (une faille Django ou une dépendance
compromise) pourrait le faire.

Ce n'est pas le scénario contre lequel ces barrières sont dressées. Le code
d'apprenant s'exécute dans un conteneur **sans réseau** : il ne peut pas
joindre le mandataire. Pour en abuser il faudrait d'abord compromettre le
worker lui-même, ce qui n'est plus une évasion de bac à sable mais une prise de
contrôle de l'application.

La barrière suivante, si le besoin s'en fait sentir, serait un **runtime à
isolation renforcée** (gVisor, Sysbox) — installation sur l'hôte, donc hors de
portée d'une modification du dépôt.

⚠️ `user='65534:65534'` est donné en **numérique** et non `nobody` : le nom
n'est pas garanti d'une image à l'autre (`python:slim` est Debian,
`node:alpine` est Alpine). Vérifié sur les quatre langages.

### Le drapeau `CODE_EXECUTION_ENABLED`

Le bac à sable exige que le worker Celery pilote un démon Docker. Sur une
machine dédiée le risque reste circonscrit ; sur un **hôte mutualisé** (le VPS
héberge d'autres projets), qui contrôle ce worker contrôle le démon, donc
l'hôte, donc *tous* les projets. C'est pour cette raison que le drapeau existe.

**État actuel : l'exécution est activée.** `settings.CODE_EXECUTION_ENABLED`
vaut `True` par défaut (`base.py`) et `.env.production.example` le laisse à
`True`. La compose de production **ne le pose pas** : la valeur vient du `.env`
du serveur, par `env_file`. Le durcissement décrit dans « Le bac à sable sur un
hôte mutualisé » — mandataire de socket, conteneur non privilégié — a levé
l'objection d'origine ; le worker n'a plus la socket Docker.

⚠️ Ce paragraphe a affirmé le contraire pendant un temps (« désactivée à
l'ouverture, mise à `False` par `docker-compose.prod.yml` »). C'était faux sur
les deux points, et dangereux : un exploitant déployait en croyant les
exercices coupés alors qu'ils tournaient. **Avant de décrire ici la valeur d'un
réglage, la lire dans `base.py` et dans `.env.production.example`.**

Le drapeau reste le moyen de tout couper proprement en cas de doute sur
l'isolement. Mis à `False`, il a **deux** effets, et le second est celui qu'on
oublie :

1. `validation.views.submit_exercise_code` renvoie **503** avec un message
   explicite, *avant* toute mise en file — sinon la tâche partirait vers un
   worker sans démon Docker et échouerait en `DockerException`, que l'apprenant
   lirait comme un bug de son propre code.
2. `progression.services._required_lessons` **retire les leçons d'exercice**
   des conditions d'ouverture du chapitre suivant. Sans cela, un exercice
   devenu insoumettable resterait éternellement inachevé : le chapitre 1
   comptant 8 exercices sur 18 leçons, **plus aucun apprenant au rythme libre
   n'atteindrait le chapitre 2**, et rien ne l'aurait signalé.

Quatre tests verrouillent les deux effets, dans les deux positions du drapeau
(`apps/validation/tests/test_execution_disabled.py`). Ni le contenu ni la
publication ne sont modifiés : remettre le drapeau à `True` rétablit la règle
d'origine, et les exercices déjà terminés le restent.

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
7. Styler en BEM, soit dans un partiel `src/styles/components/_notifications.scss`
   enregistré dans `main.scss`, soit dans une feuille de feature importée par le
   composant. **Aucune classe utilitaire** : les couleurs viennent des tokens de
   `_theme.scss`, jamais d'une valeur en dur.

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

### Contrat des services API — uniforme (données déballées)

**Tous** les modules de `services/api/` renvoient les **données déjà déballées**
(`response.data`), jamais la réponse axios brute. Un thunk écrit donc
`return await xApi.methode()`, jamais `.data` par-dessus.

⚠️ **Une exception de forme** : quand on a besoin d'autre chose que le corps —
`validationApi.getTaskResult` lit `response.status` (202 = tâche en cours) — la
méthode consomme la réponse en interne mais renvoie quand même une valeur
**déjà façonnée** (`{done, result}`), pas la réponse brute. Le contrat « ce qui
sort est de la donnée, pas une enveloppe axios » tient donc partout.

Historique : `authApi` et `coursesApi` renvoyaient autrefois la réponse brute,
les autres non. Un `.data` de trop (ou de moins) donnait `undefined` — c'est ce
qui a vidé le state de `trainerSlice` et rendu `/trainer` blanc pendant des
mois. Uniformisé d'un bloc, avec un test de contrat par module
(`services/api/contract.test.js`) qui rougirait au moindre retour vers la
réponse brute.

### Tailwind a été retiré — un seul système de style (2026-08-06)

Le constat qui figurait ici était juste : Tailwind ne servait plus que **4
fichiers**, tous dans `features/trainer/`, et son `tailwind.config.js` n'était
plus qu'un pont remappant `bg-white`, `text-gray-900`, `bg-blue-500` vers les
tokens maison. Les écrans formateur sont désormais dans
`styles/components/_trainer.scss` et **Tailwind est entièrement retiré** :
`tailwind.config.js`, `styles/tailwind.css`, l'import dans `main.jsx` et la
dépendance npm. `postcss.config.js` ne garde qu'`autoprefixer`, qui n'a jamais
eu de rapport avec Tailwind.

Deux emplacements coexistent pour le style, et c'est voulu :

| Emplacement | Pour quoi |
|---|---|
| `styles/components/_*.scss` | Partiels enregistrés dans `main.scss`, qui **réutilisent les mixins** (`card`, `button-base`, `respond-to`, `heading-*`) |
| `features/*/X.css` | Feuille de feature importée par son composant, en CSS simple avec les `var(--…)` |

Règle commune : **BEM, et les couleurs viennent toujours des tokens** de
`styles/base/_theme.scss` — jamais une valeur en dur (sauf le blanc posé sur un
fond de marque). C'est ce qui fait fonctionner le thème sombre gratuitement.

⚠️ **« Gratuitement » a une limite : un fond qui porte du texte blanc ne peut
pas suivre n'importe quel token.** Le bandeau du profil était dégradé de
`var(--ink)` vers `var(--brand-strong)`, deux tokens qui **s'éclaircissent** en
thème sombre (`--ink` y vaut `#edebf8`, presque blanc). Le titre blanc s'y
retrouvait à **1,18:1** de contraste — invisible — et le sous-titre à 2,56:1.
D'où `--banner-from` / `--banner-to`, tenus sombres dans les deux thèmes
(16,9:1 et 7,6:1 en sombre, le thème clair inchangé). **Tout nouveau bandeau de
marque doit les utiliser**, jamais `--ink` ni `--brand-strong`.

Les **quatre bandeaux** de l'application les utilisent : `.profile__hero`,
`.dashboard__hero`, `.badges-page__hero` et `.leaderboard__hero`. Tous
portaient le même défaut.

#### `--brand-ink` : l'encre posée sur un aplat de marque

⚠️ **Le même piège, autrement.** Les boutons pleins (`.profile__submit`,
`.quiz-start`, `.badges-filter--active`, `.admin-tab--active`, treize règles en
tout) posaient `#fff` sur `var(--brand)` : **3,7:1** en thème sombre, et
**2,6:1** au bout d'un dégradé vers `--brand-strong`.

La racine est que ces deux tokens ont **deux emplois contradictoires** : ils
servent de couleur de texte et de lien sur les surfaces sombres — où ils
doivent être clairs — et de fond de bouton sous du texte blanc — où ils
devraient être sombres.

⚠️ **Assombrir l'aplat n'était pas une option**, et c'est le calcul qui l'a
tranché : un bouton à 0,08 de luminance sur une surface à 0,01 tombe à
**2,1:1** contre son propre fond, sous les 3:1 exigés d'une limite de
composant. Le bouton cesse alors de se détacher de la carte qui le porte. C'est
donc **l'encre** qui s'inverse : `--brand-ink` vaut `#fff` en thème clair et
`#140f26` en sombre — aplat clair, texte sombre, comme le fait tout thème
sombre moderne.

Mesuré dans le navigateur après correction, pas seulement calculé :
**5,03:1** sur `--brand`, **7,29:1** sur `--brand-strong`. Le thème clair est
inchangé au pixel près, l'encre y valant toujours `#fff`.

**Tout nouvel aplat de marque portant du texte doit utiliser `--brand-ink`**,
jamais `#fff` en dur. Les barres de progression et autres remplissages sans
texte, eux, gardent `var(--brand)` seul — rien n'y est écrit.

⚠️ **La dette Preflight a été reprise dans `styles/base/_reset.scss`.**
L'avertissement qui figurait ici — Preflight fournit `border-style: solid`, et
les bordures disparaissent sans lui — était fondé, et vaut au-delà des
bordures : Preflight neutralisait aussi le chrome natif des `<button>` et
l'héritage des contrôles de formulaire, et **les 50 boutons de l'application
ont été écrits en le supposant actif**. Ces règles, marquées `[preflight]`, ont
été ajoutées **avant** de couper Tailwind. Ne pas les « nettoyer ».

⚠️ **Ces règles sont enveloppées dans `:where()`, et ce n'est pas cosmétique.**
`:where()` force la spécificité à zéro. Sans lui, `[type='button']` pèse autant
qu'une classe (0,1,0) et fait jeu égal avec `.scroll-to-top`, `.admin-tab`… ;
comme `main.scss` est importé **en dernier** dans `main.jsx`, c'est le reset qui
gagnait, et tout `<button type="button">` stylé par une feuille de feature
perdait son fond. Symptôme observé : la flèche « remonter » devenue blanche sur
fond transparent, invisible en thème clair. **Un reset ne doit jamais pouvoir
battre le style d'un composant.**

### Ressources statiques : `public/` ou `src/assets/` ?

| | Emplacement | Pourquoi |
|---|---|---|
| Favicons | `frontend/public/` | Référencés par un chemin **absolu** dans `index.html`, que le bundler ne traite pas : il leur faut une URL stable, ce que `public/` garantit (copié tel quel à la racine de `dist/`). |
| Logos affichés par un composant | `frontend/src/assets/` | Importés (`import logo from '@/assets/logo.png'`), donc **hachés** par Vite : cache long terme *et* invalidation automatique au changement. |

Placer un logo dans `public/` conserverait son nom d'un déploiement à l'autre,
et les visiteurs de retour continueraient de voir l'ancienne image.

⚠️ **Ni l'un ni l'autre dans `backend/media/`** : ce dossier porte les
illustrations de cours, du contenu pédagogique référencé par
`content/illustrations.py`, et un fichier étranger dans `media/courses/` fait
échouer `test_aucune_illustration_orpheline`.

Deux déclinaisons du même sigle, et ce n'est pas de la redondance :
`logo.png` porte le nom « CODE ACADEMY » gravé dans l'image — illisible à 24 ou
34 px, donc réservé aux pages d'authentification (`components/ui/BrandLogo`).
L'en-tête et le pied de page utilisent `logo-mark.png`, le sigle seul, le nom
restant du texte HTML : net à toute densité, et déjà masqué sur mobile.

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

**Backend — en place.** pytest-django, 270 tests. Couvre désormais **tous** les
modules : `accounts`, `administration`, `cohorts`, `courses`, `gamification`,
`progression`, `validation`.

Les tests de `courses` (`apps/courses/tests/`) verrouillent deux familles
d'invariants, choisies pour leur coût réel et non pour la couverture de ligne :

- **La normalisation du champ JSONB `tests`** — les deux formes qui coexistent
  en base (`{'tests': [...]}` et `[...]`), et le filtrage des entrées mal
  formées. C'est là que vivait le bug `Exercise.total_points`.
- **Le masquage du contenu sensible côté apprenant** — la solution et les tests
  d'un exercice, les bonnes réponses d'un quiz, ne sortent jamais de l'API pour
  un apprenant ; formateurs et admins voient tout. Plus la règle « seul le
  contenu publié est servi ».

Comme `progression`, ils ont été validés **par sabotage** : `total_points`
remis à sa forme buguée et le masquage de la solution retiré ont chacun fait
rougir exactement le test attendu.

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
| `features/progression/useScrollCompletion.test.jsx` | Le bas doit rester visible `DWELL_MS` ; quitter avant annule ; une seule validation par montage |
| `features/chapters/LessonView.test.jsx` | Le repère de fin n'existe que sur la théorie — jamais sur un exercice ni un quiz |
| `constants/activity.test.js` | La table des types d'activité couvre tous ceux du backend ; aucune clé technique n'atteint l'écran |
| `features/administration/AdminSpace.test.jsx` | L'anonymisation exige une confirmation ; le journal affiche l'identité **figée**, pas l'identité courante |
| `features/profile/avatars.test.js` | Chaque clé du catalogue sait se dessiner ; une clé inconnue retombe sur les initiales |
| `features/profile/ProfilePage.test.jsx` | Le formulaire n'envoie ni `role` ni les points ; les erreurs DRF imbriquées restent lisibles ; le retrait du classement part bien au serveur |
| `features/gamification/LeaderboardPage.test.jsx` | Aucun email à l'écran ; sa propre ligne est repérable ; le rang personnel survit hors du tableau ; « retiré » ≠ « pas encore classé » |
| `features/dashboard/Dashboard.test.jsx` | La progression se compte sur tout le programme ; un tiret, pas « 0 % », quand rien n'est noté |
| `features/dashboard/dailyTips.test.js` | Le conseil suit le comportement ; stable dans la journée, tournant d'un jour à l'autre ; jamais vide |

Écrire les tests **en français**, comme le reste des commentaires du dépôt.

Conventions utiles :

- Pour un hook à minuterie, utiliser `vi.useFakeTimers()` et avancer par
  `vi.advanceTimersByTime` dans un `act()`. `document.visibilityState` n'est pas
  assignable en jsdom : passer par `Object.defineProperty` (voir le helper
  `setVisibility`).
- Pour une garde de route, monter un store jetable via `configureStore` avec un
  réducteur constant plutôt que le vrai store : le test décrit un état, il n'a
  pas à rejouer les thunks pour y arriver.

**Tests bout-en-bout (Playwright) — tranche mince en place** (`frontend/e2e/`,
12 tests). Ils pilotent un vrai navigateur (Chromium) contre la **stack
complète en marche** — la stack n'est pas démarrée par Playwright, on suppose
`docker-compose up` déjà lancé (cf. `frontend/e2e/README.md`).

Périmètre **volontairement restreint** aux parcours qui ne dépendent pas du bac
à sable : consentement RGPD bloquant à l'inscription, inscription → tableau de
bord, déconnexion/reconnexion, accès refusé sur mauvais mot de passe, pages
légales publiques, navigation chapitre → leçon, et le trio RGPD (profil expose
export + suppression, l'export télécharge un JSON, la suppression déconnecte et
empêche la reconnexion).

Conventions, chacune apprise en écrivant la suite :

- **Comptes jetables à email unique** (`e2e/helpers.uniqueEmail`) : la suite est
  ré-exécutable sans purger la base, et la suppression de compte ne touche
  jamais un compte partagé.
- **Un login raté affiche un message.** C'est la régression corrigée par
  l'exception d'auth de l'intercepteur (voir « L'intercepteur axios distingue
  identifiants refusés et session expirée » ci-dessous) : les deux tests de
  login raté (mauvais mot de passe, compte supprimé) asservissent désormais la
  présence du `role="alert"` — ils rougiraient si l'intercepteur se remettait à
  recharger `/login` sur un 401 d'auth.
- **`navigation.spec.js` dépend de `load_course_content --section 1`** ; les
  autres non. ⚠️ **Ne pas amorcer avec `load_demo_content`** : voir « Contenu
  des cours — architecture » plus haut.

⚠️ **La CI ne lance pas encore l'E2E** — choix assumé (stabiliser en local
d'abord). Le jour venu : un job qui monte la stack, amorce, puis lance
Playwright headless. **Reporté à part** (comme les tests backend `-m docker`) :
la soumission d'exercice, qui exige le sandbox celery/docker.sock.

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

All detailed documentation is in the root directory.

**Pour reprendre le travail, deux fichiers suffisent :** la section « Où en est
le projet » plus haut, et `06_ROADMAP_DEPLOIEMENT.md` si le sujet est la mise
en ligne. Le reste est de la référence, à consulter au besoin.

- **06_ROADMAP_DEPLOIEMENT.md** — ⏩ **le chantier actif.** Mise en production
  sur VPS OVH : état de chaque tâche, procédure de mise en service, contrôles
  d'ouverture, et résultats de la répétition locale. ⚠️ Contient aussi la
  confrontation de `guide-hebergement-ovh.md` (étape 6.3) au code réel — quatre
  de ses hypothèses sont fausses pour ce dépôt, et il passe sous silence le
  fait que **`/media/` n'est servi par personne en production**
  (`config/urls.py:22` le conditionne à `DEBUG`), donc que les 31 illustrations
  des cours renverraient 404. À lire avant tout déploiement.
- **guide-hebergement-ovh.md** — le guide d'origine, fourni par l'exploitant.
  Bon sur l'infrastructure (SSH, Traefik, DNS), **faux sur ce projet** :
  toujours le lire à travers `06_ROADMAP_DEPLOIEMENT.md`.
- **01_ROADMAP.md** - 12-week project roadmap with sprints and deliverables
- **02_USER_STORY_MAPPING.md** - User stories for all 3 personas with acceptance criteria
- **03_DIAGRAMMES_UML.md** - UML diagrams (use cases, class, sequence, deployment)
- **04_ARCHITECTURE_TECHNIQUE.md** - Complete technical architecture with code examples
- **05_GUIDE_DEVELOPPEMENT_INITIAL.md** - Step-by-step initial setup guide
- **README.md** - Project overview and quick start

When implementing features, cross-reference these documents for requirements and design decisions.
