#!/usr/bin/env bash

set -Eeuo pipefail
umask 077

export LC_ALL=C
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# PORTABLE_BACKUP_RUNTIME_ENV_V1
# Systemd does not always supply HOME to system services. Restic uses these
# variables for its cache, including backup reports and manual framework calls.
export HOME="${HOME:-/root}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-${HOME}/.cache}"

GLOBAL="/etc/portable-backup/global.conf"

rb_log() {
    printf '[%s] %s\n' "$(date --iso-8601=seconds)" "$*"
}

rb_die() {
    rb_log "ERROR: $*" >&2
    exit 1
}

rb_have() {
    command -v "$1" >/dev/null 2>&1
}

require_programs() {
    local missing=()
    local program

    for program in "$@"; do
        if ! rb_have "$program"; then
            missing+=("$program")
        fi
    done

    if (( ${#missing[@]} > 0 )); then
        printf 'Missing required program(s):\n' >&2

        for program in "${missing[@]}"; do
            printf '  - %s\n' "$program" >&2
        done

        printf '\nInstall the missing package(s) and retry.\n' >&2
        exit 1
    fi
}

require_root() {
    if (( EUID != 0 )); then
        printf '\nThis command must be run as root.\n\n' >&2

        if (( $# > 0 )); then
            printf 'Run:\n  sudo %q' "$1" >&2
            shift

            printf ' %q' "$@" >&2
            printf '\n\n' >&2
        else
            printf 'Run the command again with sudo.\n\n' >&2
        fi

        exit 1
    fi
}

load_global_config() {
    if [[ ! -e "$GLOBAL" ]]; then
        rb_die "Global configuration file does not exist: $GLOBAL"
    fi

    if [[ ! -f "$GLOBAL" ]]; then
        rb_die "Global configuration path is not a regular file: $GLOBAL"
    fi

    if [[ ! -r "$GLOBAL" ]]; then
        rb_die "Global configuration is not readable: $GLOBAL"
    fi

    # shellcheck source=/etc/portable-backup/global.conf
    source "$GLOBAL"

    : "${WORK_ROOT:?WORK_ROOT is not configured in $GLOBAL}"
    : "${STAGING_ROOT:?STAGING_ROOT is not configured in $GLOBAL}"
    : "${LOCK_ROOT:?LOCK_ROOT is not configured in $GLOBAL}"
    : "${RESTIC_CHECK_SUBSET:?RESTIC_CHECK_SUBSET is not configured in $GLOBAL}"
}

rb_load_host() {
    local host="${1:-}"
    local cfg

    [[ -n "$host" ]] || rb_die "No host name supplied"

    cfg="/etc/portable-backup/hosts/${host}.conf"

    if [[ ! -e "$cfg" ]]; then
        rb_die "Host configuration does not exist: $cfg"
    fi

    if [[ ! -f "$cfg" ]]; then
        rb_die "Host configuration is not a regular file: $cfg"
    fi

    if [[ ! -r "$cfg" ]]; then
        rb_die "Host configuration is not readable: $cfg"
    fi

    # Reset variables that could otherwise leak between host configurations.
    unset HOST_NAME MODE
    unset RESTIC_REPOSITORY RESTIC_PASSWORD_FILE
    unset REMOTE REMOTE_SSH_KEY REMOTE_PREPARE REMOTE_CLEAN REMOTE_EXPORT
    unset REMOTE_CLEAN_AFTER_PULL
    unset KEEP_DAILY KEEP_WEEKLY KEEP_MONTHLY MAX_AGE_HOURS

    # shellcheck disable=SC1090
    source "$cfg"

    : "${HOST_NAME:?HOST_NAME is not configured in $cfg}"
    : "${MODE:?MODE is not configured in $cfg}"
    : "${RESTIC_REPOSITORY:?RESTIC_REPOSITORY is not configured in $cfg}"
    : "${RESTIC_PASSWORD_FILE:?RESTIC_PASSWORD_FILE is not configured in $cfg}"
    : "${KEEP_DAILY:?KEEP_DAILY is not configured in $cfg}"
    : "${KEEP_WEEKLY:?KEEP_WEEKLY is not configured in $cfg}"
    : "${KEEP_MONTHLY:?KEEP_MONTHLY is not configured in $cfg}"
    : "${MAX_AGE_HOURS:?MAX_AGE_HOURS is not configured in $cfg}"

    case "$MODE" in
        local)
            ;;
        remote)
            : "${REMOTE:?REMOTE is not configured in $cfg}"
            : "${REMOTE_SSH_KEY:?REMOTE_SSH_KEY is not configured in $cfg}"
            : "${REMOTE_PREPARE:?REMOTE_PREPARE is not configured in $cfg}"
            : "${REMOTE_EXPORT:?REMOTE_EXPORT is not configured in $cfg}"
            ;;
        *)
            rb_die "Invalid MODE '$MODE' in $cfg; expected 'local' or 'remote'"
            ;;
    esac

    export RESTIC_REPOSITORY
    export RESTIC_PASSWORD_FILE
}

rb_lock() {
    local host="${1:-}"
    local lock_file

    [[ -n "$host" ]] || rb_die "Cannot acquire a lock without a host name"

    mkdir -p "$LOCK_ROOT"
    lock_file="${LOCK_ROOT}/portable-backup-${host}.lock"

    exec 9>"$lock_file"

    if ! flock -n 9; then
        rb_die "A backup operation for '$host' is already running"
    fi
}

rb_require_repository_parent() {
    local parent

    parent="$(dirname "$RESTIC_REPOSITORY")"

    if [[ ! -d "$parent" ]]; then
        rb_die "Restic repository parent directory is unavailable: $parent"
    fi
}

rb_require_storage_mount() {
    local repository_parent

    repository_parent="$(dirname "$RESTIC_REPOSITORY")"

    if [[ "$repository_parent" == /mnt/backup-storage/* ]] ||
       [[ "$repository_parent" == /mnt/backup-storage ]]; then
        if ! mountpoint -q /mnt/backup-storage; then
            rb_die "Backup storage volume is not mounted at /mnt/backup-storage"
        fi
    fi
}

rb_require_repo() {
    require_programs restic

    if [[ ! -e "$RESTIC_PASSWORD_FILE" ]]; then
        rb_die "Restic password file does not exist: $RESTIC_PASSWORD_FILE"
    fi

    if [[ ! -f "$RESTIC_PASSWORD_FILE" ]]; then
        rb_die "Restic password path is not a regular file: $RESTIC_PASSWORD_FILE"
    fi

    if [[ ! -r "$RESTIC_PASSWORD_FILE" ]]; then
        rb_die "Restic password file is not readable: $RESTIC_PASSWORD_FILE"
    fi

    rb_require_repository_parent
    rb_require_storage_mount

    if ! restic snapshots >/dev/null 2>&1; then
        rb_die "Restic repository is unavailable, locked, or not initialized: $RESTIC_REPOSITORY"
    fi
}

rb_check_remote() {
    require_programs ssh

    [[ "${MODE:-}" == "remote" ]] ||
        rb_die "Remote connectivity check requested for a non-remote host"

    if [[ ! -r "$REMOTE_SSH_KEY" ]]; then
        rb_die "SSH private key is missing or unreadable: $REMOTE_SSH_KEY"
    fi

    if ! ssh \
        -i "$REMOTE_SSH_KEY" \
        -o BatchMode=yes \
        -o ConnectTimeout=10 \
        "$REMOTE" \
        true
    then
        rb_die "Unable to connect to remote host: $REMOTE"
    fi
}

rb_latest_snapshot_id() {
    require_programs restic python3

    restic snapshots \
        --host "$HOST_NAME" \
        --tag portable-backup \
        --json |
        python3 -c '
import json
import sys

snapshots = json.load(sys.stdin)

if not snapshots:
    print("")
else:
    snapshots.sort(key=lambda item: item["time"])
    print(snapshots[-1]["short_id"])
'
}

rb_latest_snapshot_epoch() {
    require_programs restic python3

    restic snapshots \
        --host "$HOST_NAME" \
        --tag portable-backup \
        --json |
        python3 -c '
import datetime
import json
import sys

snapshots = json.load(sys.stdin)

if not snapshots:
    print(0)
else:
    snapshots.sort(key=lambda item: item["time"])
    timestamp = snapshots[-1]["time"].replace("Z", "+00:00")
    print(int(datetime.datetime.fromisoformat(timestamp).timestamp()))
'
}

load_global_config

