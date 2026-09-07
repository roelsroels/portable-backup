#!/usr/bin/env bash
set -Eeuo pipefail
source /etc/source-backup.conf
if [[ ! -d "$EXPORT_ROOT" ]]; then
  echo "No prepared export exists."
  exit 1
fi
echo "Prepared: $(cat "$EXPORT_ROOT/PREPARED_AT" 2>/dev/null || echo unknown)"
du -sh "$EXPORT_ROOT"
find "$EXPORT_ROOT" -maxdepth 2 -type f | sort | sed -n '1,80p'
