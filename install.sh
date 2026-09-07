#!/usr/bin/env bash
set -Eeuo pipefail
[[ $EUID -eq 0 ]] || { echo 'Run as root' >&2; exit 1; }
cd -- "$(dirname -- "$0")"
role="${1:-}"
case "$role" in
  coordinator)
    install -d -m 755 /opt/portable-backup/bin /opt/portable-backup/lib
    install -d -m 700 /etc/portable-backup/hosts /var/lib/portable-backup /root/.cache/restic
    install -m 755 bin/* /opt/portable-backup/bin/
    install -m 644 lib/common.sh /opt/portable-backup/lib/
    [[ -e /etc/portable-backup/global.conf ]] || install -m 600 config/global.conf /etc/portable-backup/global.conf
    for f in config/hosts/*.conf; do
      dest="/etc/portable-backup/hosts/${f##*/}"
      [[ -e "$dest" ]] || install -m 600 "$f" "$dest"
    done
    if [[ -e /usr/local/bin/backup || -L /usr/local/bin/backup ]]; then
      [[ "$(readlink /usr/local/bin/backup || true)" == /opt/portable-backup/bin/backup ]] || {
        echo 'An unrelated backup command already exists; resolve it before installing the command link.' >&2; exit 1;
      }
    else
      ln -s /opt/portable-backup/bin/backup /usr/local/bin/backup
    fi
    install -m 644 systemd/*.service systemd/*.timer /etc/systemd/system/
    install -d -m 755 /etc/systemd/system/portable-backup@.service.d
    install -m 644 systemd/portable-backup@.service.d/environment.conf /etc/systemd/system/portable-backup@.service.d/
    systemctl daemon-reload
    ;;
  source)
    install -m 755 source/*.sh /usr/local/sbin/
    for f in source-backup.conf source-backup-extra-paths; do
      [[ -e /etc/$f ]] || install -m 600 "source/config/$f" "/etc/$f"
    done
    install -d -m 700 /var/lib/source-backup
    ;;
  *) echo 'Usage: sudo bash install.sh coordinator|source' >&2; exit 1 ;;
esac
echo 'Installed. Configure the neutral examples before use. No repository, timer, account or mail setup was activated.'
