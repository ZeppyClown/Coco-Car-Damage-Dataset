#!/bin/sh
# Save a dated copy of the whole workshop database to a folder. Run it daily (cron, launchd or by hand).
# Usage: DATABASE_URL=postgresql://... scripts/backup_workshop.sh /path/to/backup/folder
# To restore into an empty database: pg_restore --no-owner -d "$DATABASE_URL" the-file.dump
set -eu
FOLDER="${1:?Give the folder to keep backups in}"
: "${DATABASE_URL:?Set DATABASE_URL to the database to back up}"
mkdir -p "$FOLDER"
FILE="$FOLDER/workshop-$(date +%Y-%m-%d-%H%M).dump"
pg_dump --format=custom --no-owner --file "$FILE" "$DATABASE_URL"
echo "Saved $FILE"
