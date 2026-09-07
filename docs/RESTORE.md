# Restore and verification

```bash
sudo /opt/portable-backup/bin/pb snapshots server-a
sudo /opt/portable-backup/bin/pb ls server-a --snapshot latest
sudo /opt/portable-backup/bin/pb restore server-a --snapshot latest --target /var/tmp/recovery-review
```

The target must be absolute and must not already exist, which prevents accidental in-place restoration. `latest` is filtered by source alias and framework tag. Use an actual snapshot identifier from your own snapshot listing to select an older point. No real identifiers are shipped.

Use `ls` to discover exact stored paths before filtering:

```bash
sudo /opt/portable-backup/bin/pb restore server-a --snapshot latest --target /var/tmp/recovery-subset --include '/filesystem/srv/**'
```

Restic include patterns follow its own matching rules. A partial restore's full manifest contains entries for files not selected; do not interpret those missing entries as corruption. Full exports have a manifest of regular files; it does not validate ownership, ACLs, symlinks or application consistency. Check these separately. See [Restic restore documentation](https://restic.readthedocs.io/en/stable/050_restore.html).

Inspect recovered data before copying it into production. Stop the affected application, preserve its current state for rollback, compare ownership/numeric IDs, ACLs and extended attributes, then copy only the selected recovered files to their intended location. Never copy the entire restored filesystem tree over a running host. Restore credentials and executables only from a trusted recovery point.

## Databases

Use a disposable database instance first and review the SQL before importing. These examples assume you changed directory to the recovered tree:

```bash
zstd -dc exports/mariadb/all-databases.sql.zst | mariadb
zstd -dc exports/postgresql/5432/all-databases.sql.zst | runuser -u postgres -- psql --set ON_ERROR_STOP=on -d postgres
zstd -dc exports/mongodb/all-databases.archive.zst | mongorestore --archive
```

Run pipelines from a shell with `set -o pipefail`. Imports require suitable administrative access and compatible database versions. pg_dumpall includes globals and databases; pre-existing roles/databases can conflict. Restore into a deliberately prepared clean instance and review errors rather than ignoring them. Do not import a separate globals dump again. Adapt MongoDB consistency/authentication options to the actual deployment. These commands are recovery examples, not automatic production restore steps.

For containers, rebuild definitions/images, recreate volumes, stop services, restore selected volume files with appropriate numeric ownership, then start and validate. Inspect configuration/environment secrets separately. Rootless mappings and alternate runtimes need their own procedures.

## Acceptance drill

Recover a known file and compare its bytes; test symlinks, hard links, modes, ACLs and xattrs on Linux. Import each enabled database into a disposable instance and query meaningful records. Launch the recovered application with networking isolated and verify its behavior. Record actual elapsed recovery time, missing prerequisites and outcomes in private operational records. Delete the disposable recovery tree when no longer needed.

The original interactive restore browser was unavailable; this implementation supplies explicit list-and-restore commands instead.
