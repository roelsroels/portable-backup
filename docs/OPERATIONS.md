# Operations

## Retention and checks

Host files keep `KEEP_DAILY=5`, `KEEP_WEEKLY=2`, `KEEP_MONTHLY=3`, and `MAX_AGE_HOURS=30`. Daily/weekly/monthly categories overlap; this is not exactly ten snapshots. The installed framework has no KEEP_LAST option and no retention-preview command. To review changes without applying them:

```bash
sudo bash -c '
source /opt/portable-backup/lib/common.sh
rb_load_host server-a
rb_require_repo
restic forget --host "$HOST_NAME" --tag portable-backup --keep-daily "$KEEP_DAILY" --keep-weekly "$KEEP_WEEKLY" --keep-monthly "$KEEP_MONTHLY" --dry-run
'
```

A successful run copies/prepares data, verifies export/metadata checksums, writes a snapshot, applies retention with prune, reads the configured repository-data subset and cleans coordinator staging. Failures remain fatal. The source cleanup timing is preserved: remote exports can be removed after pull, before coordinator verification/snapshot creation.

`RESTIC_CHECK_SUBSET="5%"` controls `backup verify HOST` and the post-backup check. `backup health HOST` checks freshness and regular repository integrity. For a full-data check, source the library/load the host as above and run `restic check --read-data`.

## Report and email

```bash
sudo backup report
sudo backup report --email
sudo backup report --email operator@example.invalid
sudo backup report --email-on-critical
sudo backup report --email-on-critical operator@example.invalid
```

Use your real address in place of the reserved example. Plain `report` prints only; the timer decides email policy. Reports include snapshot count/age/data size, repository usage, timer enabled/active state, next run, last service result/exit/finish, mounted-storage usage and overall status. `REPORT_EMAIL`, `REPORT_FROM`, `REPORT_SUBJECT_PREFIX`, `STORAGE_ALERT_PERCENT` and `STORAGE_CRITICAL_PERCENT` retain their original meanings. ALERT and CRITICAL report results return 2; critical-only mail sends only for overall CRITICAL, not ALERT.

The HTML format is the original renderer in `bin/backup`: status-colored header, badge, storage metrics/progress bar and the complete escaped text report. A sendmail-compatible MTA is required. Report and inventory output contains private runtime identifiers: do not commit it.

```bash
sudo systemctl show portable-backup@server-a.service -p Result -p ExecMainStatus
sudo journalctl -u portable-backup@server-a.service -n 100 --no-pager
```

## Stale locks

The installed `backup unlock HOST` uses ordinary `restic unlock`; it does not force removal or automatically retry backups. Its preflight can itself fail when the repository is locked. In that case, stop relevant timers on all clients, wait for operations and inspect all clients to establish that the repository is idle. Then use:

```bash
sudo bash -c '
source /opt/portable-backup/lib/common.sh
rb_load_host server-a
if pgrep -x restic >/dev/null; then
  echo "A local Restic process is active" >&2
  exit 1
fi
restic list locks
restic unlock
restic list locks
'
```

The local process check cannot establish that remote clients are idle. Never use `--remove-all` or bypass locking as routine recovery. After resolving the stale lock, verify, rerun the backup and re-enable timers. This procedure is documentation; it does not change the installed unlock function.

## Cache and concurrency

The shared library supplies `HOME=${HOME:-/root}` and `XDG_CACHE_HOME=${XDG_CACHE_HOME:-${HOME}/.cache}`. The service drop-in supplies the same values explicitly. All administration/report calls use that library. Per-host coordinator locking and separate remote preparation locking are preserved. There is no new global lock or stream protocol.
