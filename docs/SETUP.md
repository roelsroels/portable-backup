# Setup

## Dependencies and roles

Use a Debian-family Linux system with Bash 4+, systemd, GNU coreutils/findutils, Restic 0.18.1 or compatible, Python 3, rsync, OpenSSH, util-linux, openssl, zstd, acl and iproute2. Install optional database/container clients used by your configured exports. `mount` also requires a working FUSE setup. A sendmail-compatible local MTA handles report delivery.

```bash
sudo apt-get install bash python3 rsync openssh-client util-linux openssl zstd acl iproute2
```

Install Restic through a source that supplies the required restore features; verify its version. Configure the underlying storage filesystem/mount through your storage provider's procedure. Credentials and mount secrets belong in root-only local files, never in this repository. This package preserves the mounted directory backend, with a mountpoint check at `/mnt/backup-storage`. It does not embed provider-specific mount credentials.

## Coordinator (server-b)

```bash
sudo bash install.sh coordinator
sudoedit /etc/portable-backup/global.conf
sudoedit /etc/portable-backup/hosts/server-a.conf
sudoedit /etc/portable-backup/hosts/server-b.conf
```

Review every neutral placeholder, especially `/home/example-user`, example application paths, `/mnt/backup-storage`, SSH identities and email settings. Configurations are sourced as root shell code and must remain root-owned and mode 600. Create storage and private local staging with enough capacity for export and copied staging together. The mount guard and reporting code use `/mnt/backup-storage` literally: if you choose another mountpoint, update both runtime files and host configs consistently.

The command link is `/usr/local/bin/backup` → `/opt/portable-backup/bin/backup`. The installer refuses to replace an unrelated command. Do not run this anonymized installer over another live backup installation as a migration.

## Remote source (server-a)

```bash
sudo bash install.sh source
sudoedit /etc/source-backup.conf
sudoedit /etc/source-backup-extra-paths
```

Create a dedicated `backup-reader` SSH account and install a dedicated coordinator public key. The remote helper grants that account ACL traversal/read access to its prepared export. Verify SSH host keys through a trusted channel and establish the known_hosts entry before unattended runs. Keep private keys mode 600; configure the coordinator's `REMOTE` and `REMOTE_SSH_KEY` accordingly.

Install the supplied `source/config/sudoers.conf` with `visudo -f /etc/sudoers.d/portable-backup`, then validate it with `visudo -cf /etc/sudoers.d/portable-backup`. It grants only the three named preparation/cleanup/status commands. Keep those helpers and config root-owned. The helper's export contains sensitive data; possession of this SSH credential grants access to that data. Use the same trusted-coordinator/source arrangement as intended by the scripts.

Use the source config for remote filesystem scope and the coordinator host config for local scope. Replace neutral certificate/mail/application paths with your own or remove unnecessary examples. Missing source paths are skipped by the original scripts, so inspect actual exports carefully before relying on coverage.

## Initialize NEW repositories only

```bash
sudo backup init server-a --confirm-init
sudo backup init server-b --confirm-init
```

Each command requires typing `INITIALIZE HOST` in a terminal and generates a password only when appropriate. Never initialize an existing repository as a recovery step. Save repository passwords, SSH credentials and private configuration offline. These filenames are configured in the host files; actual password files are not shipped.

Before first backups, validate source helper access, data selection, filesystem mount and capacity. Then run the two jobs manually and complete a restore drill:

```bash
sudo backup run server-a
sudo backup run server-b
sudo backup snapshots server-a
sudo backup verify server-a
sudo backup restore
```

## Schedules and email

```bash
sudo systemctl enable --now portable-backup-server-a.timer portable-backup-server-b.timer
sudo systemctl enable --now portable-backup-report.timer portable-backup-report-email.timer
sudo systemctl list-timers --all
sudo backup report --email operator@example.invalid
```

Replace the example recipient with your actual address before sending. Configure `REPORT_EMAIL`, `REPORT_FROM` and `REPORT_SUBJECT_PREFIX` in global.conf. The original HTML renderer sends multipart email with HTML and text alternatives. Configure and test the MTA separately; no SMTP password is embedded. The renderer is the heredoc in `send_report_email` in `bin/backup`.

Schedules are preserved: remote backup at 03:15, local backup at 04:15, each with up to 20 minutes of jitter; reports at 06:00 with critical-only email Sunday–Friday and unconditional email Saturday. Times follow the host timezone. Customize with systemd timer drop-ins and reload systemd. Ensure jobs finish before reporting.

## Upgrade / removal

Stop timers and wait for jobs before replacing installed code. Preserve a private copy for rollback; the installer updates runtime scripts/units and preserves existing configs. To remove a source, stop/disable its timer, remove its config and adjust the two explicit host lists in `bin/backup`, then revoke its SSH/sudo access. Repository deletion is a separate decision. Uninstall by disabling units and removing framework files only after retaining recovery credentials; never delete backup storage as part of uninstall.
