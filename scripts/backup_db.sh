#!/usr/bin/env bash
#
# Sauvegarde de la base PostgreSQL de la plateforme.
#
#   ./scripts/backup_db.sh [répertoire_de_destination]
#
# Pensé pour cron sur le VPS :
#   0 3 * * *  cd /home/lory/apps/learning && ./scripts/backup_db.sh >> ~/logs/backup.log 2>&1
#
# ─────────────────────────────────────────────────────────────────────────────
# Ce qui n'est PAS sauvegardé, et pourquoi
# ─────────────────────────────────────────────────────────────────────────────
#
# - **Les illustrations des cours** (`backend/media/`) : elles sont versionnées
#   dans le dépôt. Les sauvegarder reviendrait à sauvegarder git.
# - **Le contenu pédagogique** : il vit dans le code (`apps/courses/content/`),
#   pas en base — un `load_course_content` le reconstruit à l'identique.
# - **Redis** : il ne porte que du cache et une file Celery. Sa perte coûte au
#   pire une tâche en vol, jamais une donnée d'apprenant.
#
# Ce qui compte, et qui n'existe qu'ici : les comptes, la progression, le grand
# livre de points, les badges obtenus, les classes et le journal d'audit.

set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
SERVICE="${SERVICE:-postgres}"
DEST="${1:-${BACKUP_DIR:-$HOME/backups/learning}}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"

# Les identifiants viennent du même .env que la pile : une sauvegarde qui a sa
# propre copie des mots de passe finit toujours par diverger.
if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

: "${DB_NAME:?DB_NAME manquant — lancer depuis la racine du projet, à côté du .env}"
: "${DB_USER:?DB_USER manquant}"

mkdir -p "$DEST"
HORODATAGE="$(date +%Y%m%d-%H%M%S)"
CIBLE="$DEST/learning-$HORODATAGE.sql.gz"

echo "[$(date -Is)] Sauvegarde de $DB_NAME vers $CIBLE"

# `--clean --if-exists` rend le dump rejouable sur une base déjà peuplée, ce
# qui est le cas d'une restauration d'urgence : sans lui, la restauration
# échoue sur des objets existants et laisse une base à moitié écrasée.
docker compose -f "$COMPOSE_FILE" exec -T "$SERVICE" \
  pg_dump --clean --if-exists --no-owner --no-privileges \
          -U "$DB_USER" "$DB_NAME" \
  | gzip -9 > "$CIBLE.partiel"

# Renommage seulement en cas de succès : un fichier au nom définitif est un
# fichier complet. Sans cette étape, une coupure en cours d'écriture laisse une
# archive tronquée qui *ressemble* à une sauvegarde valide.
mv "$CIBLE.partiel" "$CIBLE"

TAILLE="$(du -h "$CIBLE" | cut -f1)"
echo "[$(date -Is)] OK — $TAILLE"

# Garde-fou : un dump anormalement petit signale une base vide ou une erreur
# d'authentification silencieuse.
OCTETS="$(stat -c %s "$CIBLE" 2>/dev/null || stat -f %z "$CIBLE")"
if (( OCTETS < 10240 )); then
  echo "[$(date -Is)] ⚠️  ATTENTION : sauvegarde de $OCTETS octets seulement." >&2
  echo "    Vérifier les identifiants et le contenu de la base." >&2
  exit 1
fi

# Rotation
SUPPRIMES="$(find "$DEST" -name 'learning-*.sql.gz' -mtime "+$RETENTION_DAYS" -print -delete | wc -l)"
if (( SUPPRIMES > 0 )); then
  echo "[$(date -Is)] $SUPPRIMES sauvegarde(s) de plus de $RETENTION_DAYS jours supprimée(s)"
fi

echo "[$(date -Is)] Sauvegardes présentes : $(find "$DEST" -name 'learning-*.sql.gz' | wc -l)"
