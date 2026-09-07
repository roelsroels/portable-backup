# Portable Backup

A small Linux backup framework combining Restic, filesystem staging, application exports, SSH and systemd. Supports local sources and remote sources collected by a coordinator, encrypted snapshots, retention/pruning, integrity checks, health reports and isolated restores.

**Status:** reconstructed reference implementation, ready for repository review and disposable Linux acceptance testing. It is not a byte-for-byte release of an existing deployment. Read [provenance and review](docs/REVIEW.md) and [validation](docs/VALIDATION.md) before adoption.

## Start here

1. Follow [installation and setup](docs/SETUP.md).
2. Choose source directories and optional [application exports](docs/APPLICATIONS.md).
3. Run a backup and a [restore drill](docs/RESTORE.md) before enabling schedules.
4. Review [operations, reports and retention](docs/OPERATIONS.md).
5. Keep the [disaster recovery plan](docs/DISASTER-RECOVERY.md) with offline credentials.

```text
source directories + application exports
  → private temporary export + SHA-256 manifest
  → strict local/SSH tar stream while source lock is held
  → coordinator checksum verification
  → Restic snapshot → retention/prune → repository check
  → persistent pipeline status → report
```

The source tree contains no live configuration, passwords, logs, inventories, repository data, personal identities or deployment history. All domains use reserved examples. Runtime backups necessarily contain the operator's actual data and must remain private.

## Requirements

Linux with systemd, Python 3.11+, GNU tar with ACL/xattr support, rsync with ACL/xattr support, Restic supporting `--retry-lock`, OpenSSH and util-linux. Debian 12+ or comparable distributions are the intended starting point; no production compatibility certification is claimed. Optional exports require their database clients and zstd. Email requires a configured local sendmail-compatible MTA.

## Commands

Run `/opt/portable-backup/bin/pb --help` for options. Commands: `init`, `run`, `snapshots`, `ls`, `restore`, `retention-preview`, `check`, `unlock-stale`, `report`. All commands execute as root. The source helper has one fixed command: `pb-source stream`.

MIT licensed; see [LICENSE](LICENSE). No hosting account or Git remote is embedded.
