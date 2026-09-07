#!/usr/bin/env bash
set -Eeuo pipefail
[[ $EUID -eq 0 ]] || { echo 'Run as root' >&2; exit 1; }
cd -- "$(dirname -- "$0")"
for cmd in python3 restic rsync tar flock ssh; do command -v "$cmd" >/dev/null; done
python3 -c 'import sys; assert sys.version_info >= (3,11), "Python 3.11+ required"'
# No host configuration, repository initialization or timer activation happens automatically.
install -d -m 755 /opt/portable-backup/{bin,lib,hooks,templates}
install -d -m 700 /etc/portable-backup/{hosts,secrets} /var/lib/portable-backup /var/cache/portable-backup
install -m 755 bin/* /opt/portable-backup/bin/
install -m 644 lib/*.py /opt/portable-backup/lib/
install -m 644 templates/*.html /opt/portable-backup/templates/
install -m 755 hooks/* /opt/portable-backup/hooks/
for f in source.json report.json extra-paths.txt; do
  [[ -e /etc/portable-backup/$f ]] || install -m 600 "config/$f" "/etc/portable-backup/$f"
done
install -m 644 systemd/* /etc/systemd/system/
systemctl daemon-reload
echo 'Installed. Configure hosts, source scope, credentials and storage before enabling timers.'
