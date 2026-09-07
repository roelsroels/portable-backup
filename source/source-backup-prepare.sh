#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
export LC_ALL=C
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

CONF="/etc/source-backup.conf"
[[ -r "$CONF" ]] || { echo "Missing $CONF" >&2; exit 1; }
# shellcheck source=/etc/source-backup.conf
source "$CONF"

LOCK="/run/lock/source-backup-prepare.lock"
LOG="${STAGING_ROOT}/prepare.log"
NEW="${STAGING_ROOT}/export.new"
OLD="${STAGING_ROOT}/export.old"

exec 9>"$LOCK"
flock -n 9 || { echo "Another backup preparation is already running" >&2; exit 75; }

mkdir -p "$STAGING_ROOT"
exec > >(tee -a "$LOG") 2>&1

log() { printf '[%s] %s\n' "$(date --iso-8601=seconds)" "$*"; }
have() { command -v "$1" >/dev/null 2>&1; }
fail() { log "ERROR: $*"; exit 1; }

cleanup() { rm -rf "$NEW"; }
trap cleanup ERR INT TERM

rm -rf "$NEW"
mkdir -p "$NEW"/{filesystem,exports,metadata,docker-volumes}

copy_path() {
  local src="$1"
  [[ -e "$src" || -L "$src" ]] || return 0
  log "Copying $src"
  rsync -aHAX --numeric-ids --relative "$src" "$NEW/filesystem/"
}

log "Preparing server-a export"

for p in "${BASE_PATHS[@]}"; do copy_path "$p"; done
[[ "$BACKUP_SITES" == yes ]] && { copy_path /home/example-user/sites; copy_path /var/www; }
[[ "$BACKUP_MAILDIR" == yes ]] && copy_path /home/example-user/Maildir

if [[ -r "$EXTRA_PATHS_FILE" ]]; then
  while IFS= read -r p; do
    [[ -n "$p" && "$p" != \#* ]] || continue
    [[ "$p" = /* ]] || fail "Extra path is not absolute: $p"
    copy_path "$p"
  done < "$EXTRA_PATHS_FILE"
fi

log "Capturing system inventory"
dpkg --get-selections > "$NEW/metadata/dpkg-selections.txt"
apt-mark showmanual | sort > "$NEW/metadata/apt-manual.txt"
systemctl list-unit-files --no-pager > "$NEW/metadata/systemd-unit-files.txt"
systemctl list-timers --all --no-pager > "$NEW/metadata/systemd-timers.txt"
systemctl list-units --type=service --all --no-pager > "$NEW/metadata/systemd-services.txt"
ss -lntup > "$NEW/metadata/listening-sockets.txt" 2>&1 || true
ip -brief address > "$NEW/metadata/ip-addresses.txt"
ip route > "$NEW/metadata/ip-routes.txt"
nft list ruleset > "$NEW/metadata/nftables.conf" 2>&1 || true
ufw status verbose > "$NEW/metadata/ufw-status.txt" 2>&1 || true
uname -a > "$NEW/metadata/uname.txt"
cat /etc/os-release > "$NEW/metadata/os-release.txt"
lsblk -f > "$NEW/metadata/lsblk.txt"
findmnt > "$NEW/metadata/findmnt.txt"

have nginx && nginx -T > "$NEW/metadata/nginx-effective.conf" 2>&1 || true
have postconf && postconf -n > "$NEW/metadata/postfix-main-effective.conf" 2>&1 || true
have postconf && postconf -M > "$NEW/metadata/postfix-master-effective.conf" 2>&1 || true
have doveconf && doveconf -n > "$NEW/metadata/dovecot-effective.conf" 2>&1 || true

if [[ "$BACKUP_MARIADB" == yes ]] && have mariadb-dump; then
  log "Creating MariaDB logical dump"
  mkdir -p "$NEW/exports/mariadb"
  mariadb-dump \
    --all-databases --single-transaction --quick \
    --routines --events --triggers --hex-blob \
    --default-character-set=utf8mb4 \
    | zstd -T0 -"${ZSTD_LEVEL}" -o "$NEW/exports/mariadb/all-databases.sql.zst"
  zstd -t "$NEW/exports/mariadb/all-databases.sql.zst"
  mariadb --batch --skip-column-names -e 'SHOW DATABASES' \
    > "$NEW/exports/mariadb/storagebase-list.txt"
fi

if [[ "$BACKUP_POSTGRESQL" == yes ]] && have pg_dumpall && id postgres >/dev/null 2>&1; then
  log "Creating PostgreSQL logical dump"
  mkdir -p "$NEW/exports/postgresql"
  sudo -u postgres pg_dumpall --globals-only \
    | zstd -T0 -"${ZSTD_LEVEL}" -o "$NEW/exports/postgresql/globals.sql.zst"
  sudo -u postgres pg_dumpall \
    | zstd -T0 -"${ZSTD_LEVEL}" -o "$NEW/exports/postgresql/all-databases.sql.zst"
  zstd -t "$NEW/exports/postgresql/globals.sql.zst"
  zstd -t "$NEW/exports/postgresql/all-databases.sql.zst"
  sudo -u postgres psql -Atc \
    "SELECT datname FROM pg_database WHERE datistemplate=false ORDER BY datname" \
    > "$NEW/exports/postgresql/storagebase-list.txt" || true
  have pg_lsclusters && pg_lsclusters > "$NEW/exports/postgresql/clusters.txt" || true
fi

if [[ "$BACKUP_DOCKER" == yes ]] && have docker; then
  log "Capturing Docker metadata and named volumes"
  mkdir -p "$NEW/exports/docker"
  docker info > "$NEW/exports/docker/info.txt" 2>&1 || true
  docker ps -a --no-trunc > "$NEW/exports/docker/containers.txt"
  docker image ls --digests --no-trunc > "$NEW/exports/docker/images.txt"
  docker volume ls > "$NEW/exports/docker/volumes.txt"
  docker network ls > "$NEW/exports/docker/networks.txt"

  while read -r id; do
    [[ -n "$id" ]] || continue
    name="$(docker inspect --format '{{.Name}}' "$id" | sed 's#^/##')"
    docker inspect "$id" > "$NEW/exports/docker/container-${name}.json"
  done < <(docker ps -aq)

  while read -r vol; do
    [[ -n "$vol" ]] || continue
    mp="$(docker volume inspect --format '{{.Mountpoint}}' "$vol")"
    [[ -d "$mp" ]] || continue
    mkdir -p "$NEW/docker-volumes/$vol"
    rsync -aHAX --numeric-ids "$mp/" "$NEW/docker-volumes/$vol/"
    docker volume inspect "$vol" > "$NEW/exports/docker/volume-${vol}.json"
  done < <(docker volume ls -q)

  find /home /root /opt /srv /etc -xdev -type f \
    \( -iname 'compose.yml' -o -iname 'compose.yaml' -o \
       -iname 'docker-compose.yml' -o -iname 'docker-compose.yaml' \) \
    -print > "$NEW/exports/docker/compose-files.txt" 2>/dev/null || true
fi

find /etc /var/lib /var/www /srv /home -xdev -type f \
  \( -iname '*.sqlite' -o -iname '*.sqlite3' -o -iname '*.db' \) \
  -printf '%s %u:%g %p\n' 2>/dev/null | sort -n \
  > "$NEW/metadata/sqlite-files.txt" || true

if have sa-learn && id spamass-milter >/dev/null 2>&1; then
  sudo -u spamass-milter sa-learn --dump magic \
    > "$NEW/metadata/spamassassin-bayes.txt" 2>&1 || true
fi

date --iso-8601=seconds > "$NEW/PREPARED_AT"
hostname -f > "$NEW/HOSTNAME"

(
  cd "$NEW"
  find exports metadata -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS
  sha256sum -c SHA256SUMS
)

rm -rf "$OLD"
[[ -e "$EXPORT_ROOT" ]] && mv "$EXPORT_ROOT" "$OLD"
mv "$NEW" "$EXPORT_ROOT"
rm -rf "$OLD"

if id backup-reader >/dev/null 2>&1 && have setfacl; then
  # Permit traversal through the private staging directory.
  setfacl -m u:backup-reader:rx "$STAGING_ROOT"

  # Make newly created export trees inherit backup-user access.
  setfacl -m d:u:backup-reader:rx "$STAGING_ROOT"

  # Ensure the currently published export is readable.
  setfacl -R -m u:backup-reader:rX "$EXPORT_ROOT"
fi

log "Export ready at $EXPORT_ROOT"
