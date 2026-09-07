# Portable Backup

Scheduled, encrypted backups for Linux servers, with application exports, interactive recovery and HTML email reports.

Portable Backup brings filesystem copies, database dumps, Restic snapshots and systemd scheduling together behind a single `backup` command. It is designed for administrators who want one Linux server to collect backups from a remote server while also protecting its own data.

## When to use it

Use Portable Backup to protect server configuration, application files, home directories and supported database exports, then recover individual files or a complete prepared backup bundle when needed. Scheduled health reports help you spot stale backups, failed services, disabled timers and storage nearing capacity.

The supplied setup has two roles:

- **Remote source (`server-a`):** prepares a private export for the coordinator to collect over SSH.
- **Coordinator (`server-b`):** collects that export, backs up its own selected data, manages encrypted repositories and sends reports.

Each host has a separate Restic repository on mounted backup storage. Hostnames and paths in the configuration are examples to adapt to your environment. The report and interactive restore menu explicitly list these two hosts; adding more requires updating those lists as well as adding configurations and timers.

## What it provides

- **Encrypted, deduplicated snapshots** using Restic, with configurable daily, weekly and monthly retention.
- **Filesystem and application exports**, including optional MariaDB, PostgreSQL, MongoDB and Docker-volume support; availability differs between local and remote preparation.
- **Scheduled backups and integrity checks** through systemd services and timers.
- **Interactive restore browsing** to select a host, snapshot, directory or file before confirming recovery.
- **HTML email reports** showing backup freshness, timer and service status, repository usage and storage capacity.
- **Operational commands** for snapshot listings, health checks, repository verification, mounting snapshots and ordinary stale-lock removal.

## How a backup works

```text
Remote source → prepare export → SSH/rsync pull ─┐
                                               ├→ coordinator staging
Local files  → prepare export → rsync copy ─────┘
  → verify export/metadata checksums
  → create an encrypted Restic snapshot
  → apply retention and prune unused data
  → check a configured subset of repository data
  → report snapshot, service, timer and storage health
```

Backup storage is mounted at `/mnt/backup-storage` in the examples. Local staging must support Linux ownership, ACLs and extended attributes and have room for both preparation and transfer copies.

## Get started

1. Follow the [setup guide](docs/SETUP.md) to install dependencies and configure mounted storage, SSH access and the two server roles.
2. Review source paths, repository locations, retention and email settings in the supplied shell configuration files.
3. Initialize **new repositories only**, then run a manual backup.
4. Complete a restore drill before enabling the backup and report timers.

```bash
# Install the appropriate role on each machine.
sudo bash install.sh coordinator
# On the remote source instead:
# sudo bash install.sh source

# After configuring storage, credentials and source paths:
sudo backup init server-a --confirm-init
sudo backup run server-a
sudo backup snapshots server-a
sudo backup verify server-a
sudo backup restore
```

Initialization requires an additional typed confirmation. To protect the coordinator itself, repeat the initialization and backup steps for `server-b`. The installer does not activate timers or configure mail delivery automatically.

## Everyday commands

| Task | Command |
| --- | --- |
| Run a backup | `sudo backup run server-a` |
| List snapshots | `sudo backup snapshots server-a` |
| Check freshness and integrity | `sudo backup health server-a` |
| Verify the configured data subset | `sudo backup verify server-a` |
| Browse and restore interactively | `sudo backup restore` |
| Restore a complete snapshot | `sudo backup restore server-a latest /var/tmp/recovery-review` |
| Browse snapshots through FUSE | `sudo backup mount server-a /mnt/recovery-browser` |
| Display the health report | `sudo backup report` |
| Send an email report | `sudo backup report --email` |
| Email only when critical | `sudo backup report --email-on-critical` |

For non-interactive restores, always supply `latest` or a snapshot ID and choose a new, empty destination. Read the [restore guide](docs/RESTORE.md) before applying recovered data to a running system. See [operations](docs/OPERATIONS.md) for recipient overrides, retention previews and safe stale-lock handling.

## Email reporting

Configure the recipient, sender and subject prefix in `/etc/portable-backup/global.conf`. A working sendmail-compatible mail service is required.

The sample schedule sends critical reports Sunday–Friday and a full report every Saturday. Storage thresholds default to 80% for an alert and 90% for critical status. Backup retention defaults to 5 daily, 2 weekly and 3 monthly points; the post-backup integrity check reads a 5% data subset.

![Example HTML backup report with synthetic data](docs/examples/email-report.png)

See the [example gallery](docs/examples/README.md) for CLI screens, interactive restore and a downloadable HTML report example.

## Requirements and recovery scope

Use a Debian-family Linux environment with Bash 4+, GNU utilities, systemd, Restic, Python 3, rsync, OpenSSH, ACL tools and zstd. Optional exports require the relevant database or container tools. Snapshot mounting requires FUSE. Use a Restic release supporting `restore --overwrite never` and snapshot subfolder restoration; see the [setup guide](docs/SETUP.md) for details.

This is a file and application-export backup workflow. Rebuilding a server also requires reinstalling its operating system and applications, restoring credentials and validating recovered services. Live database and container files need application-appropriate consistency measures; review [export behavior](docs/APPLICATIONS.md) and test database recovery separately.

Keep repository passwords and recovery instructions offline, and maintain an independent protected copy of important backups. Review the [validation record](docs/VALIDATION.md) and perform a disposable restore drill before relying on a deployment.

## Documentation

- [Installation and configuration](docs/SETUP.md)
- [Operations, reporting, retention and locks](docs/OPERATIONS.md)
- [Restore and disaster recovery](docs/RESTORE.md)
- [Filesystem and application exports](docs/APPLICATIONS.md)
- [CLI and email examples](docs/examples/README.md)
- [Security considerations](SECURITY.md)
- [Contributing](CONTRIBUTING.md)

MIT licensed. See [LICENSE](LICENSE).
