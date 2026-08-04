# Roadmap de mise en production — VPS OVH

Établie le 2026-08-04, en réponse au `guide-hebergement-ovh.md` (étape 6.3).
Chaque constat ci-dessous a été vérifié dans le code, référence à l'appui.

> **Convention :** ✅ fait · 🟡 partiel · ❌ à faire · ⛔ bloquant

## ⏩ Où reprendre

**Tout le code est fait et éprouvé. Il ne reste que les étapes sur le serveur.**

La pile de production a été montée en local avec Traefik le 2026-08-04 et les
dix contrôles d'ouverture passent (voir « Répétition locale — résultats »). Ce qui manque ne peut se faire que sur
le VPS, avec vos secrets :

| # | À faire | Où |
|---|---|---|
| 1 | Enregistrement DNS du sous-domaine (ou wildcard déjà en place) | espace client OVH |
| 2 | `cp .env.production.example .env` puis remplir `SECRET_KEY`, `DB_PASSWORD`, `DOMAIN`, `CERT_RESOLVER` | VPS |
| 3 | `docker compose -f docker-compose.prod.yml up -d --build` | VPS |
| 4 | Amorcer le contenu, puis `createsuperuser` — **jamais `create_demo_users`** | VPS |
| 5 | Vérifier les contrôles d’ouverture | navigateur |
| 6 | SMTP réel (sans lui, « mot de passe oublié » échoue en silence) | `.env` |
| 7 | Cron des sauvegardes + externalisation des archives hors du VPS | VPS |

La commande exacte de chaque étape est à la section « Mise en service, concrètement ».

⚠️ **À vérifier en premier sur place** : le nom du certresolver de votre
Traefik. Le nôtre suppose `myresolver`, celui du guide. S'il diffère, la
variable `CERT_RESOLVER` du `.env` suffit — ne pas toucher à la compose.

⚠️ **Ne jamais restaurer un dump de développement en production** : il contient
des comptes dont les mots de passe sont publiés dans le dépôt. Le garde-fou de
`create_demo_users` ne peut rien contre une restauration.

---

## Infrastructure cible (constatée)

| | |
|---|---|
| VPS | VPS-3 2027 — **6 vCores, 12 Go, 100 Go** |
| Déjà en place | Un premier projet, servi par **Traefik** sur le réseau externe `proxy` |
| Empreinte de ce projet | ~1 Go au repos, +128 Mo et ½ cœur par exécution de code |
| Verdict capacité | **Large marge.** Aucun réglage d'économie nécessaire : ni réduction des workers gunicorn, ni Redis mutualisé. |

**Décision révisée le 2026-08-04 : l'exécution de code est activée.** Elle
devait d'abord rester désactivée, l'hôte étant partagé. Deux barrières l'ont
rendue acceptable — un mandataire de socket qui n'ouvre que les routes du bac à
sable, et un conteneur d'exécution durci (non-root, sans capacité, en lecture
seule). Voir « Le bac à sable sur un hôte mutualisé » dans CLAUDE.md, y compris
ce que ces barrières **ne** protègent pas.

Le drapeau `CODE_EXECUTION_ENABLED` reste le moyen de tout désactiver
proprement en cas de doute : l'API répond 503 et la progression n'est jamais
bloquée.

---

## 1. Ce que l'étape 6.3 suppose, et ce qui est vrai

L'étape 6.3 tient en trois lignes :

> Le repo contient déjà un `docker-compose.yml` de base — reprends-le et
> ajoute le réseau `proxy`, les labels Traefik (en pointant vers le port du
> service Channels/ASGI), et vérifie que Traefik route les WebSockets.

Appliquée telle quelle, elle **ne produit pas un site qui fonctionne**. Quatre
hypothèses sont fausses pour ce dépôt, et un cinquième point manque.

| # | Hypothèse du guide | Réalité |
|---|---|---|
| 1 | Router vers « le port du service Channels/ASGI » | Daphne **ne sert rien** : `config/asgi.py:30` a un `URLRouter` vide et `backend/channels/consumers/` est un dossier vide. L'application est servie par **Gunicorn (WSGI) sur 8000**. Router vers 8001 donnerait une page morte. |
| 2 | Un jeu de labels suffit | Front et API sont **deux services**. `frontend/nginx.conf` (étage production) ne sert que la SPA — aucun proxy vers `/api`, `/admin`, `/media`, `/static`. Un routeur unique casse tous les appels d'API. |
| 3 | « Reprends le `docker-compose.yml` de base » | Il est **strictement de développement** : `target: development` sur les 5 services Python, sources montées en volume, `gunicorn --reload`, `npm run dev`, mot de passe Postgres `postgres/postgres` en clair (`docker-compose.yml:9`), ports 5432/6379/8000/8001 publiés. |
| 4 | Vérifier que Traefik route les WebSockets | Exact pour Traefik, **sans objet ici** : il n'y a aucun consumer à router. |
| 5 | *(absent du guide)* | **Les médias ne sont servis par personne en production** — voir ci-dessous. C'est le défaut le plus coûteux. |

### ⛔ Le trou principal : les illustrations disparaissent en ligne

`config/urls.py:22` ne sert `/media/` **que si `DEBUG`** :

```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

En production `DEBUG = False` (`production.py:8`), WhiteNoise ne sert que
`STATIC_ROOT`, et `USE_S3` vaut `False` par défaut (`production.py:73`).
Résultat : **les 31 illustrations des cours renvoient 404**. Tout le contenu
illustré — deux chapitres sur quatre en dépendent — s'affiche sans une seule
figure.

Le `nginx/nginx.conf` racine croit régler le problème en proxyfiant `/media/`
vers Django (`nginx.conf:64`), mais Django ne répondra pas.

**Trois issues, par ordre de simplicité :**

1. Servir `/media/` **par le conteneur front** (nginx, `alias` sur un volume
   partagé) — pas de dépendance externe, les PNG étant versionnés.
2. Ajouter WhiteNoise sur `MEDIA_ROOT` en plus de `STATIC_ROOT`.
3. Activer `USE_S3` — inutilement lourd pour 710 Ko de fichiers statiques
   versionnés, et fait dépendre le cours d'un service tiers.

**Retenu : option 1.** Les illustrations sont du contenu versionné, pas du
téléversement d'utilisateur ; les servir comme des fichiers statiques est
exact. (Cf. « Avatars : catalogue, pas téléversement » — il n'y a **aucun**
`ImageField` dans le projet, donc rien n'écrit dans `media/` à l'exécution.)

---

## 2. Ce que le guide sous-estime : la socket Docker

L'étape 7.2 vérifie le cloisonnement réseau entre projets. C'est nécessaire et
insuffisant.

`docker-compose.yml:97` monte `/var/run/docker.sock` dans le worker Celery,
parce que c'est ainsi qu'il pilote le bac à sable d'exécution de code.
**Qui contrôle ce worker contrôle le démon Docker, donc l'hôte, donc les quatre
projets du VPS.** Sur une machine dédiée c'était un risque circonscrit ; sur un
VPS mutualisé, la frontière de sécurité du projet devient celle de tous.

S'y ajoute que la liste noire de motifs a été retirée (à raison — elle bloquait
du code d'apprenant légitime sans arrêter un contournement) : **il n'y a plus
aucun filtre en amont du conteneur**. Le conteneur *est* la frontière, et il
tourne encore en `root` (`user=` n'est jamais passé).

C'est le sujet à trancher **avant** d'ouvrir le site, pas après.

---

## 3. Roadmap

### Phase D0 — Rendre l'application déployable ⛔

*Sans cette phase, le site ne fonctionne pas du tout.*

| # | Tâche | État |
|---|---|---|
| D0.1 | `docker-compose.prod.yml` : étages `production`, aucun volume de source, aucun port publié, mots de passe par variables, `daphne` retiré (il ne servait rien) | ✅ |
| D0.2 | Réseau `proxy` externe sur les deux services exposés, `internal` pour les données | ✅ |
| D0.3 | **Deux** routeurs Traefik : `learning-api` (priorité 100) → backend:8000, `learning-web` (priorité 1) → frontend:80 | ✅ |
| D0.4 | `/media/` servi par le nginx du front, `backend/media` monté en lecture seule | ✅ |
| D0.5 | `VITE_API_URL` passée en `ARG` de construction — la valeur est **figée dans le bundle**, pas lue à l'exécution | ✅ |
| D0.6 | `.env.production.example` complet et commenté | ✅ |
| D0.7 | Amorcer le contenu : `load_course_content`, `seed_badges`, `sync_gamification`, `backfill_chapter_access` | ❌ |

⚠️ **D0.3 — la priorité, mesurée.** Les deux routeurs répondent au même hôte.
Trois cas ont été éprouvés sur une pile réelle (voir « Répétition locale — résultats ») :

| Priorités | `/api/courses/chapters/` |
|---|---|
| Aucune — Traefik calcule d'après la **longueur de règle** (95 vs 22) | ✅ JSON |
| **Égales** (1 et 1) | ❌ `text/html` : la SPA répond à la place de l'API |
| Explicites (100 et 1) | ✅ JSON |

Contrairement à ce que ce document affirmait d'abord, *omettre* la priorité ne
casse rien : le défaut de Traefik favorise déjà la règle la plus longue, donc
celle de l'API. Mais s'y fier est fragile — c'est une propriété **émergente**
de la longueur des règles, pas une intention déclarée. Retirer `/admin` et
`/static` de la règle API la raccourcirait, et le basculement se ferait en
silence. D'où les priorités explicites, avec une seule règle absolue : **ne
jamais leur donner la même valeur**.

⚠️ **D0.6 — deux pièges déjà documentés.** `production.py` refuse de démarrer
sans `SECRET_KEY` propre : c'est voulu, l'échec au démarrage vaut mieux qu'une
compromission silencieuse. Et `FRONTEND_URL` n'est pas cosmétique : il
construit les liens de réinitialisation de mot de passe et le lien de l'admin
Django (`config/urls.py:46`).

### Phase D1 — Sécuriser avant d'ouvrir ⛔

| # | Tâche | État |
|---|---|---|
| D1.1 | **Sort de la socket Docker** (§2) : le worker passe par un mandataire limité aux routes du bac à sable, sur un réseau `internal`. Mesuré : `exec`, volumes, réseaux, `info` et `build` refusés | ✅ |
| D1.2 | Conteneur d'exécution durci : non-root, sans capacité, `no-new-privileges`, racine en lecture seule, `/tmp` en `noexec`, `pids_limit`. Vérifié sur les quatre langages | ✅ |
| D1.2b | **Exercices réactivés** (`CODE_EXECUTION_ENABLED=True`) — les 25 exercices redeviennent validables | ✅ |
| D1.3 | **Comptes de démonstration.** `create_demo_users` **refuse désormais de s'exécuter** quand `ENVIRONMENT=production`, et oriente vers `createsuperuser` | ✅ |
| D1.4 | `purge_test_accounts` recense et supprime les comptes de démo et les jetables `e2e-*`. Sans `--apply`, il se contente de recenser | ✅ |

⚠️ **Le garde-fou porte sur `settings.ENVIRONMENT`, pas sur `DEBUG`** : le
lanceur de tests de Django force `DEBUG = False`, ce qui aurait rendu le
comportement intestable, alors qu'`ENVIRONMENT` est la variable qui sélectionne
réellement les réglages de production.

⚠️ `purge_test_accounts` **ne touche jamais à un compte administrateur**, même
s'il porte une adresse de test — c'est le cas de `trainer@test.com`, promu
ADMIN à la main sur la base de développement. Le supprimer alors qu'il serait
le seul administrateur rendrait l'instance impilotable (même logique que le
garde-fou « dernier administrateur actif »). Il est signalé, à traiter à la
main après avoir promu un remplaçant.

> 💡 Sur une instance neuve, D1.3 et D1.4 n'ont rien à nettoyer : le garde-fou
> suffit. Ces commandes servent surtout à ne pas propager une base de
> développement — **ne jamais restaurer un dump de dev en production**, il
> contient un administrateur au mot de passe public.
| D1.5 | Throttling verrouillé par test — `development.py` le **vide entièrement**, un oubli en production passerait inaperçu | ✅ |
| D1.6 | SMTP réel : sans lui, « mot de passe oublié » échoue silencieusement (l'envoi est **synchrone**, par choix) | ❌ |
| D1.7 | Relire `ufw` : Postgres et Redis ne doivent être joignables que par le réseau Docker interne | ❌ |

⚠️ **D1.3 est la plus urgente de la phase** : un administrateur dont le mot de
passe est publié dans un dépôt GitHub, sur un site accessible publiquement,
donne l'espace d'administration complet — rôles, anonymisation RGPD, journal
d'audit.

### Phase D2 — Exploitation

| # | Tâche | État |
|---|---|---|
| D2.1 | `scripts/backup_db.sh` — dump compressé, rétention 14 j, garde-fou sur les dumps anormalement petits | ✅ |
| D2.2 | Restauration **testée** : cycle complet rejoué dans une base jetable, comparaison table par table, **zéro écart** | ✅ |
| D2.1b | Poser le cron sur le VPS (une ligne, voir le script) | ❌ |
| D2.1c | Externaliser les archives hors du VPS (OVH Object Storage) — une sauvegarde sur la machine qu'elle protège ne protège pas de sa perte | ❌ |

**Ce qui est sauvegardé, et ce qui ne l'est pas.** Seule la base l'est, et c'est
délibéré : les illustrations sont versionnées dans le dépôt, le contenu
pédagogique vit dans le code (`load_course_content` le reconstruit à
l'identique), et Redis ne porte que du cache et une file. Ce qui n'existe
qu'en base — comptes, progression, grand livre de points, badges, classes,
journal d'audit — est exactement le périmètre du dump.

⚠️ Deux détails du script qui évitent la fausse sauvegarde : l'écriture se fait
sous `.partiel` puis est renommée (un fichier au nom définitif est un fichier
complet, une coupure ne laisse pas d'archive tronquée qui *ressemble* à une
sauvegarde), et un dump de moins de 10 Ko fait échouer la commande — c'est la
signature d'une base vide ou d'une authentification refusée en silence.
| D2.3 | Activer Sentry — déjà câblé (`production.py:90`), il suffit de fournir `SENTRY_DSN` | 🟡 |
| D2.4 | Rotation des journaux Docker (`max-size`, `max-file`) | ❌ |
| D2.5 | Page d'erreur correcte si le backend est absent (aujourd'hui : écran blanc) | ❌ |

Les médias n'ont pas besoin de sauvegarde : ils sont versionnés dans le dépôt.

### Phase D3 — Automatiser

| # | Tâche | État |
|---|---|---|
| D3.1 | La CI construit et publie les images (elle ne construit **aucune** image aujourd'hui) | ❌ |
| D3.2 | Déploiement en une commande (`git pull && docker compose up -d --build`) puis, si besoin, sur registre | ❌ |
| D3.3 | Lancer la suite E2E en CI — reportée volontairement jusqu'ici | ❌ |
| D3.4 | Migrations jouées au déploiement, pas à la main | ❌ |

### Phase D4 — Produit, après la mise en ligne

Volontairement **après** : rien de tout cela n'empêche d'ouvrir le site.

| # | Sujet | État |
|---|---|---|
| D4.1 | WebSockets — `asgi.py` a un routeur vide, aucun consumer, `wsService.js` n'existe pas. Rien n'en dépend | ❌ |
| D4.2 | Soumission et correction de projets — modèle `Project` seul, aucun modèle de soumission | ❌ |
| D4.3 | Forum — l'app n'existe pas | ❌ |
| D4.4 | Leaderboard — reporté par choix produit, trivial grâce au grand livre de points | ⏸️ |
| D4.5 | Chapitre 3 JavaScript en version riche — il n'a pas de `load_section_3` d'auteur, seulement le contenu promu en commande | 🟡 |
| D4.6 | Régénérer les illustrations en double résolution (elles s'adoucissent en plein écran) | ❌ |

---

## 3 bis. Mise en service, concrètement

```bash
# Sur le VPS, à côté du premier projet
mkdir -p ~/apps/learning && cd ~/apps/learning
git clone https://github.com/lorycarvajol/appli-learning-1.git .

cp .env.production.example .env
$EDITOR .env          # DOMAIN, SECRET_KEY, DB_PASSWORD, SMTP…

docker compose -f docker-compose.prod.yml up -d --build

# Amorçage (D0.7)
docker compose -f docker-compose.prod.yml exec backend \
  sh -c "python manage.py load_course_content &&
         python manage.py seed_badges &&
         python manage.py sync_gamification &&
         python manage.py backfill_chapter_access"

# Créer le premier administrateur — surtout PAS create_demo_users (D1.3)
docker compose -f docker-compose.prod.yml exec backend \
  python manage.py createsuperuser
```

Le réseau `proxy` existe déjà (créé par la pile Traefik du premier projet) :
la compose le déclare `external: true` et ne cherche donc pas à le recréer.

**Vérifications d'ouverture :**

| Contrôle | Attendu |
|---|---|
| `https://DOMAIN/` | la SPA, certificat valide |
| `https://DOMAIN/api/courses/chapters/` | du JSON, **pas** `index.html` (piège de priorité, D0.3) |
| `https://DOMAIN/media/courses/html/section1/html-css-js-comparison.png` | **200**, `image/png` |
| `https://DOMAIN/admin/` | l'admin Django |
| `docker ps --format '{{.Names}}\t{{.Ports}}'` | aucun port publié par ce projet |
| Soumettre un exercice | **503** avec le message d'indisponibilité, pas une erreur générique |
| Terminer les leçons de théorie du chapitre 1 | le chapitre 2 s'ouvre malgré les exercices non faits |

---

## 4. Ordre d'exécution conseillé

```
D0 (déployable)  →  D1 (sûr)  →  ouverture  →  D2 (exploitable)  →  D3  →  D4
```

**Ne pas ouvrir le site entre D0 et D1.** À la fin de D0 le site fonctionne,
mais avec un administrateur au mot de passe public et un bac à sable qui donne
la main sur l'hôte. Les deux phases se tiennent.

Une répétition complète en local est possible avant d'acheter le VPS :
`docker-compose.prod.yml` + Traefik + entrées dans `/etc/hosts`. C'est le moyen
le moins cher d'attraper D0.3, D0.4 et D0.5, qui sont exactement les trois
points que l'étape 6.3 du guide passe sous silence.

---

## 5. Répétition locale — résultats

Faite le 2026-08-04 : Traefik local + `docker-compose.prod.yml` monté sous un
nom de projet distinct (`-p learning-repetition`), images de production
construites, contenu amorcé. Tout est validé **avant** d'avoir touché au VPS.

| Contrôle | Résultat |
|---|---|
| SPA `/` | 200 `text/html` |
| API `/api/courses/chapters/` | 200 **`application/json`** |
| Illustration `/media/…png` | 200 **`image/png`**, 35 761 o (taille du fichier) |
| Admin `/admin/login/` | 200 `text/html` |
| Statique `/static/…css` | 200 `text/css` (WhiteNoise) |
| Ports publiés par le projet | **aucun** |
| `VITE_API_URL` dans le bundle | `https://learning.local/api`, aucun `localhost` |
| Inscription + connexion via Traefik | 201 puis jeton obtenu |
| Soumission d'exercice | **503** avec le message d'indisponibilité |
| Chapitre 2 avec 8 exercices non faits | **ouvert** |

⚠️ **Deux pièges d'environnement local**, sans objet sur l'Ubuntu du VPS :

- le **fournisseur Docker de Traefik ne fonctionne pas** sous Docker Desktop /
  Windows (« Error response from daemon: », message vide). La répétition est
  donc passée par le fournisseur fichier, en transcrivant les règles et
  priorités des labels mot pour mot : c'est le moteur de routage qui a été
  éprouvé, seule la voie de découverte changeait ;
- le **rechargement à chaud du fichier de configuration ne se déclenche pas**
  (inotify ne traverse pas la frontière du système de fichiers Windows). Un
  premier essai de sabotage a donc paru réussir alors que Traefik servait
  encore l'ancienne configuration — il a fallu redémarrer le conteneur pour
  mesurer quoi que ce soit. Se méfier de tout test de configuration à chaud
  sur ce poste.

## 6. Ce que le guide traite bien

À conserver tel quel : le choix d'Ubuntu LTS, le durcissement SSH (étape 2),
Traefik avec Let's Encrypt automatique (étape 5), le principe d'un réseau
`proxy` partagé et de réseaux de données séparés, l'enregistrement DNS
wildcard, et l'avertissement sur le bac à sable de `apprentissage-POO-PHP` —
qui vaut mot pour mot pour celui-ci, en plus grave, puisqu'ici le pilote du bac
à sable a la socket Docker.
