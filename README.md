# Portable Backup

The installed Bash backup framework, anonymized by literal substitutions. The original `backup` command, interactive restore assistant, local/remote rsync workflow, HTML email renderer, shell configurations and systemd units are preserved.

The earlier Python reconstruction has been replaced. See [source parity](docs/PARITY.md) for the verified scope, retained behavior and anonymization boundaries. The installer and documentation are packaging additions; the runtime scripts are directly derived from the installed implementation.

## Commands

```text
backup init <server-a|server-b> --confirm-init
backup run <server-a|server-b>
backup status <server-a|server-b>
backup snapshots <server-a|server-b>
backup verify <server-a|server-b>
backup health <server-a|server-b>
backup restore
backup restore <server-a|server-b> latest <target-directory>
backup mount <server-a|server-b> <mountpoint>
backup unlock <server-a|server-b>
backup report
backup report --email [recipient-address]
backup report --email-on-critical [recipient-address]
```

`backup restore` opens the original interactive selection menu. For a non-interactive restore, explicitly supply `latest` or a snapshot ID before the destination: the installed implementation requires that positional argument even though its usage text describes it as optional.

## Documentation

- [Install coordinator and source](docs/SETUP.md)
- [Operations, reports, retention and stale locks](docs/OPERATIONS.md)
- [Restore and disaster recovery](docs/RESTORE.md)
- [Application export behavior](docs/APPLICATIONS.md)
- [CLI screens and original HTML email example](docs/examples/README.md)
- [Parity and anonymization review](docs/PARITY.md)
- [Validation and limitations](docs/VALIDATION.md)

## Architecture

```text
server-a (remote source) → prepare export → rsync pull → optional remote cleanup
server-b (local coordinator) → local prepare → rsync copy
  → verify export checksums → Restic snapshot → retention/prune → 5% data check
  → scheduled report of snapshots, timers, service results and storage
```

Both repositories are directories under mounted `/mnt/backup-storage`, with separate credentials. Local staging is on a filesystem supporting Linux ownership, ACLs and extended attributes. This is the original mounted-storage arrangement with neutral names, not a new direct-SFTP backend design.

## Platform

Linux with Bash 4+, GNU utilities, systemd, Restic, Python 3, rsync, OpenSSH, ACL tools, zstd and the relevant optional database/container tools. The implementation uses Debian-family inventory and PostgreSQL-cluster utilities. Restic 0.18.1 is the observed runtime version; use a compatible release supporting `restore --overwrite never` and snapshot subfolder restoration. Test on a disposable Linux system before deployment.

No private keys, password files, repository data, server inventories, historical logs or actual email messages are shipped. Runtime inventories and reports will naturally contain the operator's own private data.
