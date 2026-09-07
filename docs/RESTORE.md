# Restore and disaster recovery

## Interactive restore

Run `sudo backup restore` in an attached terminal. The original assistant selects host, snapshot and restore area, browses directories or accepts an exact logical path, shows a summary and requests confirmation. It restores with `--overwrite never`. The default destination is under `/var/tmp/backup-restore`; the alternate allowed root is `/tmp`. These are anonymized replacements for the installed restore-root literals.

## Non-interactive restore and mount

```bash
sudo backup snapshots server-a
sudo backup restore server-a latest /var/tmp/recovery-review
sudo backup mount server-a /mnt/recovery-browser
```

Explicitly pass `latest` or a snapshot ID. The installed non-interactive parser does not actually support omitting the snapshot positional argument. This path does not use the interactive browser's destination restrictions or `--overwrite never`; choose a new empty destination. Restored snapshots contain the original staged hierarchy. Inspect it before copying files into production. `mount` is a foreground Restic/FUSE browser; unmount with the appropriate FUSE unmount command when finished.

Stop applications before applying recovered files, preserve current data for rollback, and verify numeric ownership, ACLs and extended attributes. Do not overlay an entire system filesystem on a running machine.

## Application recovery

Test compressed dumps with `zstd -t` before import. Restore MariaDB all-database SQL into a suitable clean instance. PostgreSQL all-database dumps already contain globals; do not import separate globals again without a specific recovery plan. The coordinator creates per-cluster exports, while the remote helper uses its configured/default cluster. MongoDB archives require mongorestore and deployment-appropriate consistency/authentication options.

Use compatible clients/server versions and test in isolation. Raw Docker volume copies and SQLite files may be inconsistent while applications are writing. Restore application-level exports where available; recreate containers/volumes, restore stopped data with correct numeric ownership, then validate application behavior. Do not assume an integrity check establishes application consistency.

## Source or coordinator loss

Keep offline copies of repository/password locations, credentials, private configs, verified SSH keys and these instructions. Rebuild a coordinator, install this distribution, recover its private configuration, reconnect the existing mounted storage and credentials, and run snapshots/verify/restore before enabling timers. Do not initialize the recovered repository.

Rebuild a source with compatible accounts/applications, restore selected files and databases in isolation, validate, then cut over services and re-enroll SSH trust. Keep independent offsite/immutable copies in case a writable repository or coordinator is compromised. Rehearse both source and coordinator loss at least annually and after major changes, recording private recovery results and credential access.
