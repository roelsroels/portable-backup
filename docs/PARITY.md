# Source parity and anonymization

## Source of truth

The current runtime was copied read-only from the active coordinator and source installations. It replaces the earlier reconstruction. Twenty delivered files were compared byte-for-byte with their installed counterparts after applying a deterministic list of literal anonymization substitutions. Every comparison passed. `SOURCE-PARITY.json` records the delivered paths and sanitized hashes; the private original-to-placeholder map and original hashes are deliberately not published.

The verified files include the full administration command, common library, local preparation script, remote preparation/cleanup/status helpers, global/host/source configuration, source sudoers rule, all backup/report units and timers, and the cache environment drop-in.

No runtime functions were rewritten, added or removed. Control flow, command arguments, HTML layout, compression level 10, 5/2/3 retention, 30-hour age threshold, 5% data-check setting, 80/90 storage thresholds and timer schedules are preserved. Host aliases and sensitive path/branding literals are changed consistently.

## What was anonymized

Personal account/home-directory names, hostnames, mail addresses, domain names, backup-account names, framework branding, unit names, repository/credential paths, storage-provider names, storage mount paths, restore-root paths, legacy export paths and identifiable application data paths now use neutral examples. Application-specific configuration paths retain their positions in the arrays but refer to example application/mail/certificate directories. Adapt these placeholders before use.

Standard software commands and their runtime inventory collectors remain where required for behavior: database clients, container commands and mail/web configuration collectors are features, not supplied records of a real deployment. No collected inventory was downloaded or shipped. No private keys/password files or storage data were retrieved. Historical logs, report attachments and timestamps are not included. The schedules and runtime timestamp-formatting code are functional behavior and are retained.

The package retains two explicit host choices: server-a is the remote source and server-b is the local coordinator. The installed report loop and interactive menu hard-code those choices. Adding a third host requires editing those locations as well as adding its config and timer; automatic discovery was not silently introduced.

## Preserved distinctions and limitations

- Local preparation tolerates only rsync exit 24. The installed remote preparation helper uses strict rsync and has no exit-24 exception. Completed-export transfers remain strict.
- Export checksums cover `exports` and `metadata`, not all copied filesystem files.
- The common cache fix supplies HOME and XDG_CACHE_HOME for all commands sourcing the library.
- `verify` and post-backup checks use the configured data subset; `health` performs freshness plus a regular repository check.
- `status` and `snapshots` are aliases. Reporting reads systemd status, not reconstructed status JSON files.
- HTML email is embedded in `bin/backup`, with the original storage bar and full-report panel, not the previous separate template.
- Non-interactive restore requires an explicit snapshot argument; its safeguards differ from the interactive browser. No stronger behavior is claimed.
- `backup unlock` calls the repository-access preflight before ordinary unlock; a lock that blocks that preflight may require the manual ordinary-unlock procedure documented in OPERATIONS.md.
- Remote preparation and later pull are separate SSH operations, exactly as installed; no stream protocol or longer-lived lock was introduced.

## Packaging additions

The installer, README, operational guides, synthetic examples, tests, workflow and checksum/parity manifests were created for redistribution. They are not claimed to have been installed on the original servers. The installer leaves configuration/timer activation to the operator and preserves existing config files. It is for deploying this anonymized distribution, not for migrating live repositories that use other host/tag/path identities.

A normal corrective commit replaces the reconstruction on the default branch; earlier reconstruction commits remain in Git history. No original server content is uploaded before anonymization. Neither server was modified or used to run a backup/restore test during collection.
