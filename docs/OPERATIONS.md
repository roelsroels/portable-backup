# Operations

## Retention

Edit the host's `retention` object. The generic sample keeps 7 daily, 4 weekly and 6 monthly points. To configure a smaller illustrative policy:

```json
"retention": {"daily": 5, "weekly": 2, "monthly": 3}
```

For exactly the latest five snapshots in each group, use `{"last": 5}` alone. At least one supported positive integer is required. Daily/weekly/monthly categories overlap, so their counts do not sum to a fixed number of snapshots. Scope is explicitly filtered by host alias and framework tag and grouped by host and paths.

```bash
sudo /opt/portable-backup/bin/pb retention-preview server-a
```

Review this dry run before reducing history. The next successful run applies `forget --prune`, then checks the repository. Pruning reclaims unreferenced repository data and can be slow. Prefer a separate repository per source. Encryption credentials able to prune also permit destructive access; use offline or immutable independent copies for protection against coordinator compromise. See [Restic retention documentation](https://restic.readthedocs.io/en/stable/060_forget.html).

## Reports

```bash
sudo /opt/portable-backup/bin/pb report
sudo /opt/portable-backup/bin/pb report --email
sudo journalctl -u portable-backup@server-a.service -n 100 --no-pager
sudo systemctl show portable-backup@server-a.service -p Result -p ExecMainStatus
```

Reports query Restic snapshots and persisted full-pipeline status. A fresh snapshot does not hide a later prune/check failure. Missing snapshots, query/config errors, missing/failed/running status, future times and stale status/snapshots are CRITICAL. Set `max_age_hours` per host longer than the expected interval plus run time. Report exit codes are 0 OK, 1 ALERT, 2 CRITICAL/error; non-OK makes the report service appear failed intentionally.

Configured local capacity paths are OK below 80%, ALERT from 80%, CRITICAL from 90%. Capacity lookup failure is CRITICAL. Add the mounted storage path as well as staging to report.json. Generic remote SFTP quota is not measurable with local disk_usage: integrate a provider-specific monitor separately. A configured email address receives all critical reports and the weekly report (weekday 5 means Saturday); `--email` forces delivery. Empty email_to disables email explicitly. A working MTA is required, and delivery errors fail the command. No mail credentials or real recipient is supplied.

## Stale-lock recovery

A coordinator-wide flock protects all framework commands except read-only reporting; a source flock covers both preparation and streaming. Restic retains its repository locking and waits up to two minutes. There is no automatic unlock retry or forced unlock.

1. Stop relevant timers on every client that can access the repository. Wait for active jobs to finish; do not kill pruning casually.
2. Inspect Restic processes on ALL those clients and repository lock details. The local process check cannot prove remote clients are idle. Account for clock skew and disconnected clients.
3. Only once idle is established:

```bash
sudo /opt/portable-backup/bin/pb unlock-stale server-a --confirm-idle
sudo /opt/portable-backup/bin/pb check server-a
sudo /opt/portable-backup/bin/pb run server-a
```

The helper runs ordinary `restic unlock` only. It never uses `--remove-all` or `--no-lock`. Locks still considered active remain intact. Investigate unresolved locks rather than bypassing them. Re-enable stopped timers after verification. See [Restic troubleshooting](https://restic.readthedocs.io/en/stable/077_troubleshooting.html).

## Cache and failure recovery

Every Restic invocation uses the shared environment builder. Empty/unset HOME becomes `/root`; empty/unset XDG_CACHE_HOME becomes `/var/cache/portable-backup`. Units also set both. This covers backup, reports, initialization, retention preview, check, unlock and restore.

Failed preparation/transfer leaves no new snapshot; failed retention/check can leave a valid new snapshot but records failed pipeline status. Temporary exports are cleaned on normal failure. SIGKILL or power loss may leave private temporary directories under `/var/lib/portable-backup`; remove only identified orphan export directories after stopping jobs. Coordinator staging under `staging/HOST/source` is replaced on the next run while the coordinator lock is held. Preserve `.lock` files and status files. Never remove staging during an active transfer.

Metadata checks are run after each backup. Schedule `pb check server-a --read-data` periodically to read all repository data, and budget bandwidth/time. Neither checksum verification nor a Restic check proves application recovery; perform restore drills.
