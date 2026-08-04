#!/usr/bin/env bash
#
# Restauration d'une sauvegarde PostgreSQL.
#
#   ./scripts/restore_db.sh ~/backups/learning/learning-20260804-030000.sql.gz
#
# ⚠️ **Une sauvegarde jamais restaurée n'est pas une sauvegarde.** C'est le
# sens de l'étape D2.2 de la roadmap : le seul moment acceptable pour
# découvrir qu'un dump est illisible n'est pas le jour où l'on en a besoin.
# Faire l'essai au moins une fois, de préférence sur une base jetable.
#
# Le script exige une confirmation explicite : il ÉCRASE la base cible.

set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
SERVICE="${SERVICE:-postgres}"

ARCHIVE="${1:-}"
if [[ -z "$ARCHIVE" ]]; then
  echo "Usage : $0 <archive.sql.gz>" >&2
  exit 2
fi
if [[ ! -f "$ARCHIVE" ]]; then
  echo "Archive introuvable : $ARCHIVE" >&2
  exit 2
fi

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

: "${DB_NAME:?DB_NAME manquant}"
: "${DB_USER:?DB_USER manquant}"

echo "Archive : $ARCHIVE ($(du -h "$ARCHIVE" | cut -f1))"
echo "Cible   : base « $DB_NAME » du service « $SERVICE »"
echo
echo "⚠️  Le contenu actuel de cette base sera REMPLACÉ."
read -r -p "Taper le nom de la base pour confirmer : " REPONSE
if [[ "$REPONSE" != "$DB_NAME" ]]; then
  echo "Annulé." >&2
  exit 1
fi

echo "[$(date -Is)] Restauration…"

# `ON_ERROR_STOP=1` : sans lui, psql continue après une erreur et laisse une
# base partiellement restaurée en signalant un succès.
gunzip -c "$ARCHIVE" \
  | docker compose -f "$COMPOSE_FILE" exec -T "$SERVICE" \
      psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME"

echo "[$(date -Is)] Restauration terminée."
echo
echo "À vérifier maintenant :"
echo "  - le nombre de comptes et de progressions"
echo "  - la connexion d'un compte connu"
echo "  - les migrations : docker compose -f $COMPOSE_FILE exec backend python manage.py migrate --check"
