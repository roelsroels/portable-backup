#!/usr/bin/env bash
set -Eeuo pipefail
source /etc/source-backup.conf
rm -rf -- "$EXPORT_ROOT"
