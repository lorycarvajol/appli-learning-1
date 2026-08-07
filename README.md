# CodeAcademy

**Une plateforme d'apprentissage du développement web, du premier `<h1>` à la mise en ligne.**

Les apprenants suivent un parcours de quatre chapitres, écrivent du vrai code
corrigé automatiquement, et progressent à leur rythme ou au tempo de leur
formateur. Les formateurs suivent leur classe et ouvrent les chapitres.

### 🌐 [codelearning.lorycarvajol.dev](https://codelearning.lorycarvajol.dev/login)

![Le tableau de bord d'un apprenant](docs/images/tableau-de-bord.jpg)

---

## Ce que c'est, en chiffres

| | |
|---|---|
| **Parcours** | 4 chapitres · 68 leçons · 25 exercices corrigés · 5 quiz |
| **Récompenses** | 30 trophées, dont 10 secrets |
| **Personnalisation** | 42 visages d'avatar, 7 familles · thème clair et sombre |
| **Illustrations** | 31 figures de cours · 4 illustrations de leçon |
| **Application** | 7 apps Django · 13 features React · 20 routes |
| **Tests** | **332** backend · **146** frontend · 11 bout-en-bout |

---

## Le parcours

| # | Chapitre | Contenu |
|---|---|---|
| 1 | Introduction au HTML | 18 leçons, 8 exercices, 2 quiz |
| 2 | Introduction au CSS | 17 leçons, 8 exercices, 1 quiz |
| 3 | Introduction à JavaScript | 18 leçons, 9 exercices, 1 quiz |
| 4 | Créer et mettre en ligne un site vitrine | 15 leçons, 1 quiz |

Le contenu pédagogique **ne vit pas en base de données** : il vit dans le code,
sous `backend/apps/courses/content/`. La base n'en est qu'une projection,
reconstructible à tout moment par une commande. C'est ce qui a permis de
récupérer deux incidents sans perdre une ligne.

---

## Ce que chacun peut faire

### 🎓 Apprenant

Lire les leçons — validées **à la lecture**, pas par un bouton à cocher.
Écrire du code dans un éditeur Monaco, soumis à des tests qui s'exécutent
dans un bac à sable isolé. Passer des quiz. Gagner des points, des niveaux et
des trophées. Se comparer aux autres, ou s'en retirer d'un clic. Exporter
toutes ses données, ou supprimer son compte, sans passer par personne.

![Un exercice corrigé automatiquement](docs/images/exercice.jpg)

Le code part dans un conteneur jetable, sans réseau ; chaque critère est
vérifié séparément et le retour dit **quoi corriger**, pas seulement que
c'est faux.

![Les trophées, dont dix secrets](docs/images/trophees.jpg)

Les objectifs visibles balisent le parcours avec leur barre de progression.
Les secrets ne montrent qu'une énigme — et le masquage se fait **côté
serveur** : impossible de les découvrir en inspectant les requêtes réseau.

### 👩‍🏫 Formateur

Créer des classes et inviter par lien — aucun envoi d'e-mail requis. Suivre
la progression de ses apprenants, leçon par leçon. Ouvrir les chapitres au
rythme qu'il choisit. Il ne voit **que ses propres classes**.

![L'espace formateur](docs/images/espace-formateur.jpg)

### 🛠️ Administrateur

Piloter les comptes (rôle, activation, anonymisation RGPD, affectation de
classe), le tout **tracé dans un journal d'audit** que rien ne peut réécrire.
Le CRUD de contenu reste dans l'admin Django, qui le fait mieux.

---

## Décisions techniques qui méritent le détour

Le projet documente ses choix plutôt que ses fonctionnalités. Quelques-uns
valent d'être lus :

- **Rien ne peut être récompensé deux fois.** Ce n'est pas garanti par du code
  prudent mais par trois mécanismes cumulés : des contraintes d'unicité en
  base, des règles monotones, et un grand livre de points où le solde est
  toujours égal à la somme des transactions. `sync_gamification` peut donc
  être relancé n'importe quand.

- **Le bac à sable est la seule frontière.** La liste noire de motifs a été
  retirée : elle refusait du code d'apprenant légitime (`evaluer` déclenchait
  sur `eval`) sans arrêter le moindre contournement. Le conteneur, lui, est
  sans réseau, non privilégié, sans capacité, en lecture seule, et le worker
  ne voit le démon Docker qu'à travers un mandataire qui n'ouvre que les
  routes du bac à sable.

- **Aucun traceur, donc aucune bannière de consentement.** Les avatars sont
  pré-générés à la construction, les polices et les images sont servies par
  la plateforme. C'est ce qui rend la politique de confidentialité tenable.

- **Anonymisation, jamais suppression en cascade.** Effacer un compte
  fausserait rétroactivement les statistiques de sa classe. L'identité part,
  la progression reste, rattachée à un compte qui ne désigne plus personne.

- **On ne reverrouille jamais un chapitre.** Un accès obtenu le reste, qu'on
  rejoigne une classe ensuite ou qu'on la quitte.

Le raisonnement complet — y compris les erreurs commises et ce qu'elles ont
coûté — est dans [`CLAUDE.md`](./CLAUDE.md).

---

## La pile

| | |
|---|---|
| **Backend** | Django 5.2 · Django REST Framework · SimpleJWT · Celery · PostgreSQL 15 · Redis 7 |
| **Frontend** | React 18 · Vite 5 · Redux Toolkit · React Router 7 · Monaco Editor |
| **Style** | SCSS maison, BEM, tokens de thème — **aucun framework CSS** |
| **Exécution de code** | Conteneurs Docker jetables, pilotés par Celery via un mandataire de socket |
| **Production** | Docker Compose · Traefik · Let's Encrypt · WhiteNoise |

---

## Démarrer en local

```bash
docker compose up -d

docker compose exec backend python manage.py load_course_content   # le parcours
docker compose exec backend python manage.py seed_badges           # les trophées
docker compose exec backend python manage.py create_demo_users     # comptes de dev
```

Puis [localhost:5173](http://localhost:5173) et
[localhost:8000/admin](http://localhost:8000/admin/).

> **Tout passe par Docker.** Seul `npm` s'utilise en local, côté front — le
> conteneur est en Node 18, la CI et les tests en Node 22.

> ⚠️ `create_demo_users` **refuse de s'exécuter en production** : ses mots de
> passe sont écrits dans le dépôt.

### Les tests

```bash
docker compose exec backend pytest          # 332 tests
docker compose exec celery pytest -m docker # + 7 tests du bac à sable réel

cd frontend && npm test                     # 146 tests
cd frontend && npm run e2e                  # 11 tests Playwright (pile requise)
```

Les tests sont **validés par sabotage** : on casse volontairement le code pour
vérifier que le test rougit. Un test vert sur du code cassé ne protège rien.

---

## Structure

```
backend/
  apps/          accounts · administration · cohorts · courses
                 gamification · progression · validation
  config/        settings/{base,development,production}.py
frontend/
  src/features/  auth · chapters · cohorts · dashboard · errors · exercises
                 gamification · legal · profile · progression · quizzes · trainer
  src/styles/    design system SCSS
scripts/         sauvegarde et restauration PostgreSQL
```

---

## Documentation

| Fichier | Pour quoi |
|---|---|
| [**CLAUDE.md**](./CLAUDE.md) | **L'essentiel.** État du projet, décisions, pièges et leur histoire |
| [06_ROADMAP_DEPLOIEMENT.md](./06_ROADMAP_DEPLOIEMENT.md) | Mise en production : procédure, contrôles d'ouverture, répétitions |
| [04_ARCHITECTURE_TECHNIQUE.md](./04_ARCHITECTURE_TECHNIQUE.md) | Architecture détaillée |
| [02_USER_STORY_MAPPING.md](./02_USER_STORY_MAPPING.md) | User stories des trois rôles |
| [03_DIAGRAMMES_UML.md](./03_DIAGRAMMES_UML.md) | Diagrammes UML |
| [01_ROADMAP.md](./01_ROADMAP.md) | Roadmap produit d'origine |

---

## Ce qui n'existe pas encore

Dit franchement, parce qu'une documentation qui promet ce qui n'est pas
construit fait perdre plus de temps qu'elle n'en fait gagner :

- **Temps réel / WebSockets** — `asgi.py` a un routeur vide, aucun consumer.
  Rien n'en dépend : l'auto-sauvegarde, l'activité formateur et les
  notifications passent par HTTP.
- **Forum** — l'app n'existe pas.
- **Soumission de projets** — le modèle `Project` existe, aucun modèle de
  soumission.

---

## Crédits

Visages d'avatar issus de [DiceBear](https://www.dicebear.com/) :
*Notionists* (Zoish, CC0 1.0) · *Adventurer* et *Adventurer Neutral*
(Lisa Wischofsky, CC BY 4.0) · *Avataaars* et *Bottts* (Pablo Stanley) ·
*Big Smile* (Ashley Seo, CC BY 4.0) · *ToonHead* (Johan Melin, CC BY 4.0).
Ils sont générés à la construction et servis par la plateforme — aucune
requête vers un tiers.

Édité par **Lory Carvajol** (`lorycarvajol.dev`).
