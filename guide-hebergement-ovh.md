# Guide pas-à-pas : héberger tes 4 projets e-learning sur un VPS OVH

Ce guide part de zéro (aucun VPS, aucun nom de domaine) et t'amène jusqu'aux 4 projets en ligne, chacun sur son sous-domaine, avec HTTPS automatique. Chaque étape explique le **pourquoi**, pas seulement le **comment**.

---

## Étape 1 — Choisir et commander le VPS OVH

### Quelle offre choisir ?
Le projet le plus lourd (`appli-learning-1` : Django + Channels + Celery + PostgreSQL + Redis) dimensionne le choix. Pour faire tourner les 4 projets simultanément sans lenteurs :

- **VPS Value** (2 vCPU / 4 Go RAM / 80 Go SSD) : le minimum confortable. Suffisant pour démarrer et observer la charge réelle.
- **VPS Essential** (4 vCPU / 8 Go RAM) : plus de marge si tu comptes ajouter d'autres projets par la suite, ou si Celery/Channels consomment plus que prévu.

Démarre avec le Value — tu pourras faire évoluer la ressource (upscale) depuis l'espace client OVH sans réinstaller quoi que ce soit si besoin.

### Système d'exploitation
Choisis **Ubuntu 24.04 LTS** à l'installation du VPS (image proposée par OVH). C'est la distribution la plus documentée pour Docker et la plus stable dans la durée (support à long terme).

### Ce que tu récupères après commande
- Une **adresse IP publique** (ex. `51.xxx.xxx.xxx`) — tu en auras besoin à l'étape DNS.
- Des identifiants de connexion SSH (souvent envoyés par email, avec un mot de passe root initial).

---

## Étape 2 — Sécuriser l'accès au serveur

Ne saute pas cette étape même si tu es pressé : un VPS avec un accès root par mot de passe exposé sur internet est scanné par des bots en quelques minutes.

### 2.1 Première connexion
```bash
ssh root@TON_IP_VPS
```

### 2.2 Créer un utilisateur non-root
```bash
adduser lory
usermod -aG sudo lory
```

### 2.3 Configurer une clé SSH (au lieu du mot de passe)
Sur ta machine locale :
```bash
ssh-keygen -t ed25519 -C "vps-ovh"
ssh-copy-id lory@TON_IP_VPS
```

### 2.4 Désactiver la connexion root et par mot de passe
Édite `/etc/ssh/sshd_config` :
```
PermitRootLogin no
PasswordAuthentication no
```
Puis redémarre le service :
```bash
sudo systemctl restart sshd
```

### 2.5 Activer le pare-feu
```bash
sudo ufw allow OpenSSH
sudo ufw allow 80,443/tcp
sudo ufw enable
```
Seuls SSH, HTTP et HTTPS sont accessibles depuis l'extérieur — tout le reste (ports internes des conteneurs, MySQL, PostgreSQL, Redis) reste invisible depuis internet, ce qui est essentiel puisque tu vas héberger un sandbox d'exécution de code.

---

## Étape 3 — Installer Docker et Docker Compose

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker lory
```
Déconnecte-toi et reconnecte-toi pour que le groupe `docker` s'applique. Vérifie :
```bash
docker --version
docker compose version
```

---

## Étape 4 — Acheter le nom de domaine et configurer le DNS

### 4.1 Achat
Si tu n'as pas encore de domaine : achète-le directement dans l'espace client OVH (section "Noms de domaine") — c'est plus simple d'avoir domaine et VPS chez le même hébergeur pour la gestion DNS (interface unique, propagation généralement plus rapide en interne).

### 4.2 Créer les enregistrements DNS
Dans l'espace client OVH → ton domaine → zone DNS, ajoute une entrée **A** par sous-domaine, pointant vers l'IP de ton VPS :

| Type | Sous-domaine | Valeur |
|---|---|---|
| A | `qcm` | TON_IP_VPS |
| A | `learning` | TON_IP_VPS |
| A | `js` | TON_IP_VPS |
| A | `poo-php` | TON_IP_VPS |

Ou plus simple : un seul enregistrement **A wildcard** (`*`) pointant vers l'IP, qui couvre tous les sous-domaines présents et futurs sans repasser par le DNS à chaque nouveau projet.

> ⏳ La propagation DNS peut prendre de quelques minutes à quelques heures. Vérifie avec `nslookup qcm.tondomaine.fr` depuis ta machine avant de passer à la suite.

---

## Étape 5 — Mettre en place le reverse proxy (Traefik)

Traefik va écouter sur les ports 80/443, router chaque requête vers le bon conteneur selon le sous-domaine, et gérer automatiquement les certificats HTTPS (Let's Encrypt) sans configuration manuelle par projet.

### 5.1 Créer l'arborescence
```bash
mkdir -p ~/infra/traefik && cd ~/infra/traefik
```

### 5.2 Fichier `docker-compose.yml` de Traefik
```yaml
services:
  traefik:
    image: traefik:v3.1
    command:
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.httpchallenge=true"
      - "--certificatesresolvers.myresolver.acme.httpchallenge.entrypoint=web"
      - "--certificatesresolvers.myresolver.acme.email=TON_EMAIL@example.com"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./letsencrypt:/letsencrypt"
    networks:
      - proxy

networks:
  proxy:
    external: true
```

### 5.3 Créer le réseau partagé et lancer Traefik
```bash
docker network create proxy
docker compose up -d
```

Ce réseau `proxy` est celui que chaque projet rejoindra pour être visible de Traefik — les autres services internes (MySQL, PostgreSQL, Redis) resteront sur des réseaux séparés, invisibles les uns des autres.

---

## Étape 6 — Déployer chaque projet

Principe commun : chaque projet a son propre `docker-compose.yml`, ses propres conteneurs (backend, frontend, base de données si besoin), rejoint le réseau `proxy`, et déclare des **labels Traefik** indiquant son sous-domaine.

### 6.1 QCM-python-react (le plus simple)
```bash
mkdir -p ~/apps/qcm && cd ~/apps/qcm
git clone https://github.com/lorycarvajol/QCM-python-react.git .
```
`docker-compose.yml` :
```yaml
services:
  backend:
    build: .
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./data:/app/data     # persiste le fichier TinyDB
    networks:
      - proxy
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.qcm.rule=Host(`qcm.tondomaine.fr`)"
      - "traefik.http.routers.qcm.entrypoints=websecure"
      - "traefik.http.routers.qcm.tls.certresolver=myresolver"
      - "traefik.http.services.qcm.loadbalancer.server.port=8000"

networks:
  proxy:
    external: true
```
Le `.env` (non commité) contient les vraies valeurs de `ANTHROPIC_API_KEY` et `SECRET_KEY`.

Pense à **désactiver les comptes de démonstration** (`formateur@test.com` / `password123`) avant la mise en ligne — mot de passe documenté publiquement dans le README.

### 6.2 apprentissage-JS et apprentissage-POO-PHP (MySQL partagé)
Ces deux projets partagent une seule instance MySQL. Crée d'abord ce service commun :
```bash
mkdir -p ~/apps/mysql-shared && cd ~/apps/mysql-shared
```
`docker-compose.yml` :
```yaml
services:
  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - db-shared

networks:
  db-shared:
    external: true

volumes:
  mysql_data:
```
```bash
docker network create db-shared
docker compose up -d
docker exec -it mysql-shared-mysql-1 mysql -u root -p -e "
  CREATE DATABASE apprentissage_js CHARACTER SET utf8mb4;
  CREATE DATABASE apprentissage_poo CHARACTER SET utf8mb4;
  CREATE USER 'user_js'@'%' IDENTIFIED BY 'MOT_DE_PASSE_JS';
  CREATE USER 'user_poo'@'%' IDENTIFIED BY 'MOT_DE_PASSE_POO';
  GRANT ALL ON apprentissage_js.* TO 'user_js'@'%';
  GRANT ALL ON apprentissage_poo.* TO 'user_poo'@'%';
"
```
Chaque projet a son propre utilisateur MySQL — même instance, permissions séparées.

Ensuite, pour chaque projet PHP (`apprentissage-JS` puis `apprentissage-POO-PHP`), même logique que le QCM : `Dockerfile` PHP-FPM + Nginx, rejoint à la fois `proxy` (pour Traefik) et `db-shared` (pour MySQL), avec ses propres labels de sous-domaine (`js.tondomaine.fr` / `poo-php.tondomaine.fr`).

> ⚠️ **Spécifique à apprentissage-POO-PHP** : le sandbox d'exécution de code (`proc_open`) doit tourner dans un **conteneur à part**, sans accès au réseau `db-shared` ni `proxy`, avec des limites strictes (`mem_limit`, `cpus`, utilisateur non-root dans le `Dockerfile`). Ne branche jamais ce sandbox directement sur le conteneur applicatif principal.

### 6.3 appli-learning-1 (le plus lourd)
Le repo contient déjà un `docker-compose.yml` de base (Postgres + Redis + Django + Celery + Channels) — reprends-le et :
- ajoute le réseau `proxy` externe au service qui expose le frontend/l'API,
- ajoute les labels Traefik comme pour les autres (sous-domaine `learning.tondomaine.fr`, en pointant vers le port du service Channels/ASGI),
- vérifie que Traefik route bien les WebSockets : Traefik le fait nativement dès lors que l'entrypoint est `websecure` avec TLS, aucune config supplémentaire n'est nécessaire pour l'upgrade WebSocket.

---

## Étape 7 — Vérifications finales

1. **DNS** : `qcm.tondomaine.fr`, `learning.tondomaine.fr`, `js.tondomaine.fr`, `poo-php.tondomaine.fr` répondent tous en HTTPS avec un certificat valide (cadenas vert).
2. **Isolation** : depuis un conteneur PHP, tente de joindre PostgreSQL (`appli-learning-1`) — ça ne doit pas passer, les réseaux Docker sont bien cloisonnés.
3. **Sandbox POO-PHP** : teste une soumission de code volontairement gourmande (boucle infinie) et vérifie que le conteneur sandbox est bien tué/limité sans affecter les autres projets.
4. **Sauvegardes** : programme une sauvegarde régulière des volumes (`mysql_data`, PostgreSQL, `data/db.json` du QCM) — un simple script cron avec `docker exec mysqldump` / `pg_dump` suffit pour démarrer, à externaliser vers un stockage OVH Object Storage si tu veux plus de sécurité.

---

## Récapitulatif de l'architecture finale

```
Internet
   │
   ▼
Traefik (80/443, Let's Encrypt automatique)
   │
   ├── qcm.tondomaine.fr       → conteneur FastAPI + volume TinyDB
   ├── learning.tondomaine.fr  → Django + Channels + Celery + Postgres + Redis
   ├── js.tondomaine.fr        → PHP-FPM + MySQL partagé (base apprentissage_js)
   └── poo-php.tondomaine.fr   → PHP-FPM + MySQL partagé (base apprentissage_poo)
                                  + conteneur sandbox isolé (proc_open)
```

Un seul VPS OVH, un seul nom de domaine, quatre projets isolés les uns des autres mais mutualisant les ressources serveur.
