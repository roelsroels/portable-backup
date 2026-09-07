# Source selection and application exports

`include` is a JSON array of absolute paths. Every required path must exist. `/` and parent traversal are rejected. `extra_paths_file` adds one absolute path per line; blank lines and comments are ignored. Avoid overlapping parent/child sources. Directory copies preserve numeric owners, hard links within each copy, ACLs, extended attributes and relative hierarchy. Symlinks are copied as links. Hard links between separately copied trees may not remain linked.

Copies stay within one filesystem. List separate mounted data directories explicitly. `exclude` contains absolute subtrees; private staging and cache are always excluded. Add all local repository/storage locations to exclusions if a source is their ancestor. Do not select remote storage, pseudo filesystems or backup trees as sources. The sample scope is deliberately generic and is not a complete inventory of any installation.

## rsync exit 24

Only live filesystem and live Docker-volume copies accept rsync exit 24, logging a warning for vanished source files. Every other nonzero code fails preparation. A source that changes during copying is not a consistent application snapshot. Exit 24 acceptance does not make databases transactionally safe. The subsequent completed-export tar stream is strict: any nonzero producer or receiver exit fails, and the receiver verifies SHA-256 checksums before Restic runs. Restic nonzero results, including incomplete-backup results, fail the pipeline and skip retention.

## Database hooks

Add argv arrays to `export_hooks` in source.json, for example:

```json
"export_hooks": [
  ["/opt/portable-backup/hooks/mariadb"],
  ["/opt/portable-backup/hooks/postgresql", "5432"],
  ["/opt/portable-backup/hooks/mongodb"]
]
```

Enable only installed databases. Enabled hooks fail if clients, permissions or services are unavailable; there is no silent auto-detection. Hooks write under `PB_EXPORT_DIR`; their normal output goes to the journal, not the export stream. Pipelines use pipefail, and zstd tests the compressed output.

MariaDB uses a single-transaction all-database logical dump with routines/events/triggers. Nontransactional tables and concurrent schema changes require a maintenance window or suitable locking. Configure client authentication in root-only client option files.

PostgreSQL uses pg_dumpall for one explicit cluster port, including roles and globals. Add an invocation for each cluster. It requires the postgres OS account and local database authentication. Cross-database consistency is not guaranteed while writes continue. Use version-compatible clients; validate restoration into a disposable cluster.

MongoDB uses mongodump archive output. The baseline does not enable replica-set oplog capture or point-in-time recovery. Configure credentials without putting passwords in command arguments, and adapt the hook for the deployment's consistency requirements.

SQLite must be exported using its online backup API/`.backup` command or while the application is stopped. Raw `.db` copies, particularly with WAL activity, are not a substitute. Add a root-owned custom hook with an explicit database path and export filename.

## Containers and other applications

`docker_volumes: true` captures Docker container inspection data, volume inspection data and named volume contents. It requires access to the Docker daemon. Inspection data may contain secrets. Running volume copies have crash-consistency limitations: quiesce applications during the backup window or use application export hooks and exclude raw database files. Compose definitions and bind mounts must be included explicitly. Rootless Docker, Podman, specialized mail stores and application-specific state require explicit paths/hooks; no deployment-specific adapter is shipped.

A hook can export mail/service configuration or collect additional inventory. Do not blindly restore old machine networking or firewall settings. Metadata and backups are private runtime artifacts, not files to contribute to this repository.
